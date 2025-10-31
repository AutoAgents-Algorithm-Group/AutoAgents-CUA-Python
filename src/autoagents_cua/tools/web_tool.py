"""
Web Tools for AutoBrowser Agent

每个工具都是独立的函数，可以自由组合使用
"""

from typing import Callable, Optional, Any
from functools import partial
from langchain_core.tools import tool
from ..utils.logging import logger


# ============================================================================
# 工具创建辅助函数
# ============================================================================

def create_tool_with_context(func: Callable, operator: Any, extractor: Any, time_tracker_ref: Optional[Any] = None):
    """
    为工具函数绑定上下文（operator, extractor, time_tracker）
    
    Args:
        func: 原始工具函数（可以是 langchain tool 对象或普通函数）
        operator: WebOperator 实例
        extractor: PageExtractor 实例
        time_tracker_ref: TimeTracker 引用（可选）
    
    Returns:
        绑定了上下文的 langchain tool 对象
    """
    from langchain_core.tools import StructuredTool
    
    # 如果是 langchain tool 对象，获取底层函数和元数据
    if isinstance(func, StructuredTool):
        original_func = func.func
        tool_name = func.name
        tool_description = func.description
        tool_args_schema = func.args_schema if hasattr(func, 'args_schema') else None
    elif hasattr(func, 'func'):
        # 可能是其他类型的 tool 对象
        original_func = func.func
        tool_name = getattr(func, 'name', func.__name__)
        tool_description = getattr(func, 'description', func.__doc__ or '')
        tool_args_schema = getattr(func, 'args_schema', None)
    elif hasattr(func, '__wrapped__'):
        # 装饰器包装的函数
        original_func = func.__wrapped__
        tool_name = func.__name__
        tool_description = func.__doc__ or ''
        tool_args_schema = None
    else:
        # 普通函数
        original_func = func
        tool_name = func.__name__
        tool_description = func.__doc__ or ''
        tool_args_schema = None
    
    # 确保是可调用的
    if not callable(original_func):
        raise TypeError(f"函数对象不可调用: {type(original_func)}")
    
    # 创建包装函数，绑定上下文参数
    def wrapped_func(*args, **kwargs):
        # 将上下文参数添加到 kwargs
        kwargs['operator'] = operator
        kwargs['extractor'] = extractor
        kwargs['time_tracker_ref'] = time_tracker_ref
        # 调用原始函数
        return original_func(*args, **kwargs)
    
    # 保留原始函数的元数据
    wrapped_func.__name__ = tool_name
    wrapped_func.__doc__ = tool_description
    
    # 使用 @tool 装饰器创建新的 tool 对象
    # 如果原始 tool 有 args_schema，需要保留它
    if tool_args_schema:
        new_tool = tool(wrapped_func, args_schema=tool_args_schema)
    else:
        new_tool = tool(wrapped_func)
    
    # 确保新 tool 的名称和描述与原始 tool 一致
    new_tool.name = tool_name
    new_tool.description = tool_description
    
    return new_tool


def _start_timing(time_tracker_ref, category="tool_call"):
    """开始计时"""
    if time_tracker_ref and hasattr(time_tracker_ref, 'current_time_tracker'):
        tracker = time_tracker_ref.current_time_tracker
        if tracker:
            tracker.start(category)


def _end_timing(time_tracker_ref, category="tool_call"):
    """结束计时"""
    if time_tracker_ref and hasattr(time_tracker_ref, 'current_time_tracker'):
        tracker = time_tracker_ref.current_time_tracker
        if tracker:
            elapsed = tracker.end(category)
            logger.debug(f"⏱️  {category}耗时: {elapsed:.2f}s")


# ============================================================================
# Web 工具函数定义
# ============================================================================

@tool
def open_website(url: str, operator=None, extractor=None, time_tracker_ref=None) -> str:
    """
    打开指定的网站
    
    Args:
        url: 网站URL，例如 "https://www.google.com" 或 "https://www.baidu.com"
    
    Returns:
        操作结果
    """
    logger.info(f"🌐 打开网站: {url}")
    
    # 如果用户只说"谷歌"、"百度"等，自动补全URL
    url_mapping = {
        "谷歌": "https://www.google.com",
        "google": "https://www.google.com",
        "百度": "https://www.baidu.com",
        "baidu": "https://www.baidu.com",
        "必应": "https://www.bing.com",
        "bing": "https://www.bing.com",
        "github": "https://github.com",
        "pubmed": "https://pmc.ncbi.nlm.nih.gov/",
    }
    
    # 检查是否需要补全URL
    url_lower = url.lower()
    for key, full_url in url_mapping.items():
        if key in url_lower and not url.startswith('http'):
            url = full_url
            logger.info(f"📝 自动补全URL: {url}")
            break
    
    # 如果还是没有http前缀，添加https://
    if not url.startswith('http'):
        url = 'https://' + url
    
    _start_timing(time_tracker_ref, "tool_call")
    success = operator.navigate(url, wait_time=0.4)
    _end_timing(time_tracker_ref, "tool_call")
    
    if success:
        return f"✅ 成功打开网站: {url}"
    else:
        return f"❌ 打开网站失败: {url}"


@tool
def extract_page_elements(operator=None, extractor=None, time_tracker_ref=None) -> str:
    """
    提取当前页面的所有可交互元素（链接、按钮、输入框等）
    
    Returns:
        提取到的元素列表描述
    """
    logger.info("🔍 提取页面元素...")
    
    _start_timing(time_tracker_ref, "page_extraction")
    elements = extractor.extract_elements(highlight=True, save_to_file=None)
    _end_timing(time_tracker_ref, "page_extraction")
    
    if not elements:
        return "❌ 未找到可交互元素"
    
    # 生成简洁的元素描述
    element_desc = f"✅ 找到 {len(elements)} 个可交互元素：\n\n"
    
    # 按类型分组
    by_type = {}
    for elem in elements:
        tag = elem['tag']
        if tag not in by_type:
            by_type[tag] = []
        by_type[tag].append(elem)
    
    # 生成描述
    for tag, items in by_type.items():
        element_desc += f"【{tag.upper()}】 {len(items)} 个\n"
        for item in items:  
            text = item['text'][:30] if item['text'] else ''
            attrs_str = ''
            if 'id' in item['attrs']:
                attrs_str += f" id={item['attrs']['id']}"
            if 'name' in item['attrs']:
                attrs_str += f" name={item['attrs']['name']}"
            
            element_desc += f"  [{item['index']}] {text}{attrs_str}\n"
        
        
    
    return element_desc


@tool
def click_element(index: int, operator=None, extractor=None, time_tracker_ref=None) -> str:
    """
    点击页面上的元素（通过索引号）
    
    Args:
        index: 元素的索引号（从 extract_page_elements 获取）
    
    Returns:
        操作结果
    """
    logger.info(f"👆 点击元素 [{index}]...")
    
    _start_timing(time_tracker_ref, "tool_call")
    
    elements = extractor.get_elements()
    if not elements:
        _end_timing(time_tracker_ref, "tool_call")
        return "❌ 请先调用 extract_page_elements 提取页面元素"
    
    # 查找对应索引的元素
    target = None
    for elem in elements:
        if elem['index'] == index:
            target = elem
            break
    
    if not target:
        _end_timing(time_tracker_ref, "tool_call")
        return f"❌ 未找到索引为 {index} 的元素"
    
    # 点击元素
    success = operator.click_element(target['selector'], wait_before=0.25, wait_after=0.25)
    _end_timing(time_tracker_ref, "tool_call")
    
    if success:
        return f"✅ 成功点击元素 [{index}]: {target['text'][:30]}"
    else:
        return f"❌ 点击元素失败 [{index}]"


@tool
def input_text_to_element(index: int, text: str, operator=None, extractor=None, time_tracker_ref=None) -> str:
    """
    在输入框中输入文本（通过索引号）
    
    Args:
        index: 输入框的索引号（从 extract_page_elements 获取）
        text: 要输入的文本
    
    Returns:
        操作结果
    """
    logger.info(f"⌨️  在元素 [{index}] 中输入: {text}")
    
    _start_timing(time_tracker_ref, "tool_call")
    
    elements = extractor.get_elements()
    if not elements:
        _end_timing(time_tracker_ref, "tool_call")
        return "❌ 请先调用 extract_page_elements 提取页面元素"
    
    # 查找对应索引的元素
    target = None
    for elem in elements:
        if elem['index'] == index:
            target = elem
            break
    
    if not target:
        _end_timing(time_tracker_ref, "tool_call")
        return f"❌ 未找到索引为 {index} 的元素"
    
    # 输入文本
    success = operator.input_text(target['selector'], text, clear=True)
    _end_timing(time_tracker_ref, "tool_call")
    
    if success:
        return f"✅ 成功输入文本到 [{index}]"
    else:
        return f"❌ 输入文本失败 [{index}]"


@tool
def get_current_url(operator=None, extractor=None, time_tracker_ref=None) -> str:
    """
    获取当前页面的URL
    
    Returns:
        当前页面URL
    """
    url = operator.get_current_url()
    return f"当前页面: {url}"


@tool
def go_back(operator=None, extractor=None, time_tracker_ref=None) -> str:
    """
    返回上一页
    
    Returns:
        操作结果
    """
    logger.info("⬅️  返回上一页...")
    
    _start_timing(time_tracker_ref, "tool_call")
    success = operator.go_back(wait_time=2)
    _end_timing(time_tracker_ref, "tool_call")
    
    if success:
        return "✅ 已返回上一页"
    else:
        return "❌ 返回失败"


@tool
def refresh_page(operator=None, extractor=None, time_tracker_ref=None) -> str:
    """
    刷新当前页面
    
    Returns:
        操作结果
    """
    logger.info("🔄 刷新页面...")
    
    _start_timing(time_tracker_ref, "tool_call")
    success = operator.refresh_page(wait_time=3)
    _end_timing(time_tracker_ref, "tool_call")
    
    if success:
        return "✅ 页面已刷新"
    else:
        return "❌ 页面刷新失败"


@tool
def take_screenshot(operator=None, extractor=None, time_tracker_ref=None) -> str:
    """
    截取当前页面的完整截图，保存到 media 文件夹
    
    Returns:
        操作结果和截图文件路径
    """
    logger.info("📸 截取当前页面...")
    
    _start_timing(time_tracker_ref, "tool_call")
    screenshot_path = operator.take_screenshot()
    _end_timing(time_tracker_ref, "tool_call")
    
    if screenshot_path:
        # 标记当前对话中有截图
        if time_tracker_ref and hasattr(time_tracker_ref, 'recent_screenshot'):
            time_tracker_ref.recent_screenshot = screenshot_path
        logger.info(f"📷 截图已保存: {screenshot_path}")
        return f"✅ 页面截图已保存: {screenshot_path}\n截图文件路径: {screenshot_path}"
    else:
        return "❌ 截图失败"


# ============================================================================
# 工具集合（用于批量导出）
# ============================================================================

# 基础工具集
BASIC_WEB_TOOLS = [
    open_website,
    extract_page_elements,
    click_element,
    input_text_to_element,
    get_current_url,
]

# 导航工具集
NAVIGATION_TOOLS = [
    go_back,
    refresh_page,
]

# 辅助工具集
UTILITY_TOOLS = [
    take_screenshot,
]

# 所有工具
ALL_WEB_TOOLS = BASIC_WEB_TOOLS + NAVIGATION_TOOLS + UTILITY_TOOLS


# ============================================================================
# 工具绑定辅助函数
# ============================================================================

def bind_tools_to_context(tools: list, operator: Any, extractor: Any, time_tracker_ref: Optional[Any] = None) -> list:
    """
    将工具列表绑定到上下文
    
    Args:
        tools: 工具函数列表
        operator: WebOperator 实例
        extractor: PageExtractor 实例
        time_tracker_ref: TimeTracker 引用（可选）
    
    Returns:
        绑定了上下文的工具列表
    
    示例:
        bound_tools = bind_tools_to_context(
            [open_website, click_element],
            operator=my_operator,
            extractor=my_extractor
        )
    """
    return [
        create_tool_with_context(tool, operator, extractor, time_tracker_ref)
        for tool in tools
    ]
