from ..web_operator import WebOperator
from ..page_extractor import PageExtractor
from ..logging import logger
import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.callbacks import BaseCallbackHandler, CallbackManager
from langgraph.checkpoint.memory import InMemorySaver
from typing import Annotated, Any, Dict, List
from langgraph.prebuilt import InjectedState
from ..config_loader import get_autobrowser_agent_config
import time
from collections import defaultdict


class TimeTracker:
    """时间追踪类，用于记录各个阶段的耗时"""
    
    def __init__(self):
        self.start_times = {}
        self.durations = defaultdict[Any, float](float)
        self.execution_start = None
    
    def start(self, name: str = "total"):
        """开始计时"""
        if name == "total":
            self.execution_start = time.time()
        self.start_times[name] = time.time()
    
    def end(self, name: str = "total"):
        """结束计时并记录耗时"""
        if name in self.start_times:
            elapsed = time.time() - self.start_times[name]
            self.durations[name] += elapsed
            del self.start_times[name]
            return elapsed
        return 0
    
    def get_total_time(self):
        """获取总耗时"""
        if self.execution_start:
            return time.time() - self.execution_start
        return 0
    
    def get_summary(self):
        """获取时间统计摘要"""
        total = self.get_total_time()
        return {
            'total': total,
            'llm_invoke': self.durations.get('llm_invoke', 0),
            'tool_call': self.durations.get('tool_call', 0),
            'page_extraction': self.durations.get('page_extraction', 0),
            'other': total - sum(self.durations.values()),
        }


class TokenUsageCallback(BaseCallbackHandler):
    """Token使用情况追踪回调类"""
    
    def __init__(self):
        super().__init__()
        self.total_tokens = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0
    
    def reset(self):
        """重置统计"""
        self.total_tokens = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0
    
    def on_llm_end(self, response: Any, **kwargs: Any) -> None:
        """LLM调用结束时的回调"""
        try:
            # 从 llm_output 中提取 token usage（LangChain/OpenAI 标准位置）
            if hasattr(response, 'llm_output') and response.llm_output:
                llm_output = response.llm_output
                if isinstance(llm_output, dict) and 'token_usage' in llm_output:
                    usage = llm_output['token_usage']
                    if isinstance(usage, dict):
                        self.total_tokens += usage.get('total_tokens', 0)
                        self.prompt_tokens += usage.get('prompt_tokens', 0)
                        self.completion_tokens += usage.get('completion_tokens', 0)
                        logger.debug(f"✅ 累积token: 本次 {usage.get('total_tokens', 0)} | 累计 {self.total_tokens} total tokens")
                        return
            
            logger.debug("⚠️  未找到 token_usage 信息")
                
        except Exception as e:
            logger.debug(f"⚠️  提取token信息时出错: {e}")
            import traceback
            logger.debug(traceback.format_exc())
    
    def get_summary(self):
        """获取token使用摘要"""
        return {
            'total_tokens': self.total_tokens,
            'prompt_tokens': self.prompt_tokens,
            'completion_tokens': self.completion_tokens
        }


class WebAgent:
    """Web 操作 Agent - 结合 LLM 的智能网页操作"""
    
    def __init__(self, headless=False, api_key=None, base_url=None, model=None):
        """
        初始化 Web Agent
        
        Args:
            headless: 是否使用无头模式
            api_key: OpenAI API Key
            base_url: API Base URL
        """
        # 获取配置
        # config = get_autobrowser_agent_config()
        
        # 创建 WebOperator
        self.operator = WebOperator(headless=headless)
        self.extractor = PageExtractor(self.operator.page)
        # 初始化 Token 使用追踪回调
        self.token_callback = TokenUsageCallback()
        
        # 创建回调管理器
        callback_manager = CallbackManager([self.token_callback])
        
        # 初始化 LLM
        self.llm = ChatOpenAI(
            base_url=base_url ,
            api_key=api_key,
            model=model,
            temperature=0,  # 使用确定性输出
            callbacks=callback_manager  # 添加回调
        )
        
        # 创建工具列表
        self.tools = self._create_tools()
        
        # 创建 Agent（带记忆）
        self.checkpointer = InMemorySaver()
        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            checkpointer=self.checkpointer,
        )
        self.graph = self.agent.get_graph()
        # 初始化截图追踪
        self.recent_screenshot = None
        
        logger.success("✅ Web Agent 初始化完成")
    
    def _create_tools(self):
        """创建工具函数列表"""
        
        # 保存 self 引用，供工具函数使用
        operator = self.operator
        extractor = self.extractor
        
        def record_time_tool_call(func, category="tool_call"):
            """装饰器：记录工具函数调用时间"""
            def wrapper(*args, **kwargs):
                if hasattr(self, 'current_time_tracker') and self.current_time_tracker:
                    self.current_time_tracker.start(category)
                result = func(*args, **kwargs)
                if hasattr(self, 'current_time_tracker') and self.current_time_tracker:
                    elapsed = self.current_time_tracker.end(category)
                    logger.debug(f"⏱️  {category}耗时: {elapsed:.2f}s")
                return result
            return wrapper
        
        @tool
        def open_website(url: str) -> str:
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
            
            # 记录工具调用时间
            if hasattr(self, 'current_time_tracker') and self.current_time_tracker:
                self.current_time_tracker.start("tool_call")
            
            success = operator.navigate(url, wait_time=0.4)
            
            if hasattr(self, 'current_time_tracker') and self.current_time_tracker:
                elapsed = self.current_time_tracker.end("tool_call")
                logger.debug(f"⏱️  open_website耗时: {elapsed:.2f}s")
            
            if success:
                return f"✅ 成功打开网站: {url}"
            else:
                return f"❌ 打开网站失败: {url}"
        
        @tool
        def extract_page_elements() -> str:
            """
            提取当前页面的所有可交互元素（链接、按钮、输入框等）
            
            Returns:
                提取到的元素列表描述
            """
            logger.info("🔍 提取页面元素...")
            
            # 记录页面提取时间
            if hasattr(self, 'current_time_tracker') and self.current_time_tracker:
                self.current_time_tracker.start("page_extraction")
            
            elements = extractor.extract_elements(highlight=True, save_to_file=None)
            
            if hasattr(self, 'current_time_tracker') and self.current_time_tracker:
                elapsed = self.current_time_tracker.end("page_extraction")
                logger.debug(f"⏱️  extract_page_elements耗时: {elapsed:.2f}s")
            
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
                for item in items[:5]:  # 只显示前5个
                    text = item['text'][:30] if item['text'] else ''
                    attrs_str = ''
                    if 'id' in item['attrs']:
                        attrs_str += f" id={item['attrs']['id']}"
                    if 'name' in item['attrs']:
                        attrs_str += f" name={item['attrs']['name']}"
                    
                    element_desc += f"  [{item['index']}] {text}{attrs_str}\n"
                
                if len(items) > 5:
                    element_desc += f"  ... 还有 {len(items) - 5} 个\n"
                element_desc += "\n"
            
            return element_desc
        
        @tool
        def click_element(index: int) -> str:
            """
            点击页面上的元素（通过索引号）
            
            Args:
                index: 元素的索引号（从 extract_page_elements 获取）
            
            Returns:
                操作结果
            """
            logger.info(f"👆 点击元素 [{index}]...")
            
            # 记录工具调用时间
            if hasattr(self, 'current_time_tracker') and self.current_time_tracker:
                self.current_time_tracker.start("tool_call")
            
            elements = extractor.get_elements()
            if not elements:
                if hasattr(self, 'current_time_tracker') and self.current_time_tracker:
                    self.current_time_tracker.end("tool_call")
                return "❌ 请先调用 extract_page_elements 提取页面元素"
            
            # 查找对应索引的元素
            target = None
            for elem in elements:
                if elem['index'] == index:
                    target = elem
                    break
            
            if not target:
                if hasattr(self, 'current_time_tracker') and self.current_time_tracker:
                    self.current_time_tracker.end("tool_call")
                return f"❌ 未找到索引为 {index} 的元素"
            
            # 点击元素
            success = operator.click_element(target['selector'], wait_before=0.25, wait_after=0.25)
            
            if hasattr(self, 'current_time_tracker') and self.current_time_tracker:
                elapsed = self.current_time_tracker.end("tool_call")
                logger.debug(f"⏱️  click_element耗时: {elapsed:.2f}s")
            
            if success:
                return f"✅ 成功点击元素 [{index}]: {target['text'][:30]}"
            else:
                return f"❌ 点击元素失败 [{index}]"
        
        @tool
        def input_text_to_element(index: int, text: str) -> str:
            """
            在输入框中输入文本（通过索引号）
            
            Args:
                index: 输入框的索引号（从 extract_page_elements 获取）
                text: 要输入的文本
            
            Returns:
                操作结果
            """
            logger.info(f"⌨️  在元素 [{index}] 中输入: {text}")
            
            # 记录工具调用时间
            if hasattr(self, 'current_time_tracker') and self.current_time_tracker:
                self.current_time_tracker.start("tool_call")
            
            elements = extractor.get_elements()
            if not elements:
                if hasattr(self, 'current_time_tracker') and self.current_time_tracker:
                    self.current_time_tracker.end("tool_call")
                return "❌ 请先调用 extract_page_elements 提取页面元素"
            
            # 查找对应索引的元素
            target = None
            for elem in elements:
                if elem['index'] == index:
                    target = elem
                    break
            
            if not target:
                if hasattr(self, 'current_time_tracker') and self.current_time_tracker:
                    self.current_time_tracker.end("tool_call")
                return f"❌ 未找到索引为 {index} 的元素"
            
            # 输入文本
            success = operator.input_text(target['selector'], text, clear=True)
            
            if hasattr(self, 'current_time_tracker') and self.current_time_tracker:
                elapsed = self.current_time_tracker.end("tool_call")
                logger.debug(f"⏱️  input_text_to_element耗时: {elapsed:.2f}s")
            
            if success:
                return f"✅ 成功输入文本到 [{index}]"
            else:
                return f"❌ 输入文本失败 [{index}]"
        
        @tool
        def get_current_url() -> str:
            """
            获取当前页面的URL
            
            Returns:
                当前页面URL
            """
            url = operator.get_current_url()
            return f"当前页面: {url}"
        
        @tool
        def go_back() -> str:
            """
            返回上一页
            
            Returns:
                操作结果
            """
            logger.info("⬅️  返回上一页...")
            
            if hasattr(self, 'current_time_tracker') and self.current_time_tracker:
                self.current_time_tracker.start("tool_call")
            
            success = operator.go_back(wait_time=2)
            
            if hasattr(self, 'current_time_tracker') and self.current_time_tracker:
                elapsed = self.current_time_tracker.end("tool_call")
                logger.debug(f"⏱️  go_back耗时: {elapsed:.2f}s")
            
            if success:
                return "✅ 已返回上一页"
            else:
                return "❌ 返回失败"
        
        @tool
        def refresh_page() -> str:
            """
            刷新当前页面
            
            Returns:
                操作结果
            """
            logger.info("🔄 刷新页面...")
            
            if hasattr(self, 'current_time_tracker') and self.current_time_tracker:
                self.current_time_tracker.start("tool_call")
            
            success = operator.refresh_page(wait_time=3)
            
            if hasattr(self, 'current_time_tracker') and self.current_time_tracker:
                elapsed = self.current_time_tracker.end("tool_call")
                logger.debug(f"⏱️  refresh_page耗时: {elapsed:.2f}s")
            
            if success:
                return "✅ 页面已刷新"
            else:
                return "❌ 页面刷新失败"
        
        @tool
        def select_option(index: int, value: str) -> str:
            """
            在下拉框中选择选项
            
            Args:
                index: 下拉框的索引号（从 extract_page_elements 获取）
                value: 要选择的值
            
            Returns:
                操作结果
            """
            logger.info(f"📋 在下拉框 [{index}] 中选择: {value}")
            
            if hasattr(self, 'current_time_tracker') and self.current_time_tracker:
                self.current_time_tracker.start("tool_call")
            
            elements = extractor.get_elements()
            if not elements:
                if hasattr(self, 'current_time_tracker') and self.current_time_tracker:
                    self.current_time_tracker.end("tool_call")
                return "❌ 请先调用 extract_page_elements 提取页面元素"
            
            target = None
            for elem in elements:
                if elem['index'] == index:
                    target = elem
                    break
            
            if not target:
                if hasattr(self, 'current_time_tracker') and self.current_time_tracker:
                    self.current_time_tracker.end("tool_call")
                return f"❌ 未找到索引为 {index} 的元素"
            
            result = operator.select_option(target['selector'], value)
            
            if hasattr(self, 'current_time_tracker') and self.current_time_tracker:
                elapsed = self.current_time_tracker.end("tool_call")
                logger.debug(f"⏱️  select_option耗时: {elapsed:.2f}s")
            
            if result:
                return f"✅ 成功选择选项: {value}"
            else:
                return f"❌ 选择失败"
        
        @tool
        def get_element_text(index: int) -> str:
            """
            获取元素的文本内容
            
            Args:
                index: 元素的索引号
            
            Returns:
                元素文本内容
            """
            logger.info(f"📝 获取元素 [{index}] 的文本...")
            
            if hasattr(self, 'current_time_tracker') and self.current_time_tracker:
                self.current_time_tracker.start("tool_call")
            
            elements = extractor.get_elements()
            if not elements:
                if hasattr(self, 'current_time_tracker') and self.current_time_tracker:
                    self.current_time_tracker.end("tool_call")
                return "❌ 请先调用 extract_page_elements 提取页面元素"
            
            target = None
            for elem in elements:
                if elem['index'] == index:
                    target = elem
                    break
            
            if not target:
                if hasattr(self, 'current_time_tracker') and self.current_time_tracker:
                    self.current_time_tracker.end("tool_call")
                return f"❌ 未找到索引为 {index} 的元素"
            
            text = operator.get_element_text(target['selector'])
            
            if hasattr(self, 'current_time_tracker') and self.current_time_tracker:
                elapsed = self.current_time_tracker.end("tool_call")
                logger.debug(f"⏱️  get_element_text耗时: {elapsed:.2f}s")
            
            if text:
                return f"✅ 元素文本: {text}"
            else:
                return "❌ 获取文本失败"
        
        @tool
        def get_element_value(index: int) -> str:
            """
            获取元素的 value 属性
            
            Args:
                index: 元素的索引号
            
            Returns:
                元素的 value 属性值
            """
            logger.info(f"🔢 获取元素 [{index}] 的 value...")
            
            if hasattr(self, 'current_time_tracker') and self.current_time_tracker:
                self.current_time_tracker.start("tool_call")
            
            elements = extractor.get_elements()
            if not elements:
                if hasattr(self, 'current_time_tracker') and self.current_time_tracker:
                    self.current_time_tracker.end("tool_call")
                return "❌ 请先调用 extract_page_elements 提取页面元素"
            
            target = None
            for elem in elements:
                if elem['index'] == index:
                    target = elem
                    break
            
            if not target:
                if hasattr(self, 'current_time_tracker') and self.current_time_tracker:
                    self.current_time_tracker.end("tool_call")
                return f"❌ 未找到索引为 {index} 的元素"
            
            value = operator.get_element_value(target['selector'])
            
            if hasattr(self, 'current_time_tracker') and self.current_time_tracker:
                elapsed = self.current_time_tracker.end("tool_call")
                logger.debug(f"⏱️  get_element_value耗时: {elapsed:.2f}s")
            
            if value is not None:
                return f"✅ 元素 value: {value}"
            else:
                return "❌ 获取 value 失败"
        
        @tool
        def get_element_attribute(index: int, attr_name: str) -> str:
            """
            获取元素的指定属性
            
            Args:
                index: 元素的索引号
                attr_name: 属性名称（如 'href', 'src', 'id' 等）
            
            Returns:
                属性值
            """
            logger.info(f"🔍 获取元素 [{index}] 的属性 [{attr_name}]...")
            
            if hasattr(self, 'current_time_tracker') and self.current_time_tracker:
                self.current_time_tracker.start("tool_call")
            
            elements = extractor.get_elements()
            if not elements:
                if hasattr(self, 'current_time_tracker') and self.current_time_tracker:
                    self.current_time_tracker.end("tool_call")
                return "❌ 请先调用 extract_page_elements 提取页面元素"
            
            target = None
            for elem in elements:
                if elem['index'] == index:
                    target = elem
                    break
            
            if not target:
                if hasattr(self, 'current_time_tracker') and self.current_time_tracker:
                    self.current_time_tracker.end("tool_call")
                return f"❌ 未找到索引为 {index} 的元素"
            
            attr_value = operator.get_element_attribute(target['selector'], attr_name)
            
            if hasattr(self, 'current_time_tracker') and self.current_time_tracker:
                elapsed = self.current_time_tracker.end("tool_call")
                logger.debug(f"⏱️  get_element_attribute耗时: {elapsed:.2f}s")
            
            if attr_value is not None:
                return f"✅ 属性值: {attr_value}"
            else:
                return f"❌ 获取属性失败或属性不存在"
        
        @tool
        def wait_for_element(index: int, timeout: int = 10) -> str:
            """
            等待元素出现
            
            Args:
                index: 元素的索引号
                timeout: 超时时间（秒），默认10秒
            
            Returns:
                操作结果
            """
            logger.info(f"⏳ 等待元素 [{index}] 出现（超时: {timeout}秒）...")
            
            if hasattr(self, 'current_time_tracker') and self.current_time_tracker:
                self.current_time_tracker.start("tool_call")
            
            elements = extractor.get_elements()
            if not elements:
                if hasattr(self, 'current_time_tracker') and self.current_time_tracker:
                    self.current_time_tracker.end("tool_call")
                return "❌ 请先调用 extract_page_elements 提取页面元素"
            
            target = None
            for elem in elements:
                if elem['index'] == index:
                    target = elem
                    break
            
            if not target:
                if hasattr(self, 'current_time_tracker') and self.current_time_tracker:
                    self.current_time_tracker.end("tool_call")
                return f"❌ 未找到索引为 {index} 的元素"
            
            success = operator.wait_for_element(target['selector'], timeout=timeout)
            
            if hasattr(self, 'current_time_tracker') and self.current_time_tracker:
                elapsed = self.current_time_tracker.end("tool_call")
                logger.debug(f"⏱️  wait_for_element耗时: {elapsed:.2f}s")
            
            if success:
                return f"✅ 元素已出现"
            else:
                return f"❌ 等待元素超时"
        
        @tool
        def is_element_visible(index: int) -> str:
            """
            检查元素是否可见
            
            Args:
                index: 元素的索引号
            
            Returns:
                元素是否可见
            """
            logger.info(f"👁️  检查元素 [{index}] 是否可见...")
            
            if hasattr(self, 'current_time_tracker') and self.current_time_tracker:
                self.current_time_tracker.start("tool_call")
            
            elements = extractor.get_elements()
            if not elements:
                if hasattr(self, 'current_time_tracker') and self.current_time_tracker:
                    self.current_time_tracker.end("tool_call")
                return "❌ 请先调用 extract_page_elements 提取页面元素"
            
            target = None
            for elem in elements:
                if elem['index'] == index:
                    target = elem
                    break
            
            if not target:
                if hasattr(self, 'current_time_tracker') and self.current_time_tracker:
                    self.current_time_tracker.end("tool_call")
                return f"❌ 未找到索引为 {index} 的元素"
            
            is_visible = operator.is_element_visible(target['selector'])
            
            if hasattr(self, 'current_time_tracker') and self.current_time_tracker:
                elapsed = self.current_time_tracker.end("tool_call")
                logger.debug(f"⏱️  is_element_visible耗时: {elapsed:.2f}s")
            
            return "✅ 元素可见" if is_visible else "❌ 元素不可见"
        
        @tool
        def scroll_to_element(index: int) -> str:
            """
            滚动到指定元素
            
            Args:
                index: 元素的索引号
            
            Returns:
                操作结果
            """
            logger.info(f"📜 滚动到元素 [{index}]...")
            
            if hasattr(self, 'current_time_tracker') and self.current_time_tracker:
                self.current_time_tracker.start("tool_call")
            
            elements = extractor.get_elements()
            if not elements:
                if hasattr(self, 'current_time_tracker') and self.current_time_tracker:
                    self.current_time_tracker.end("tool_call")
                return "❌ 请先调用 extract_page_elements 提取页面元素"
            
            target = None
            for elem in elements:
                if elem['index'] == index:
                    target = elem
                    break
            
            if not target:
                if hasattr(self, 'current_time_tracker') and self.current_time_tracker:
                    self.current_time_tracker.end("tool_call")
                return f"❌ 未找到索引为 {index} 的元素"
            
            success = operator.scroll_to_element(target['selector'])
            
            if hasattr(self, 'current_time_tracker') and self.current_time_tracker:
                elapsed = self.current_time_tracker.end("tool_call")
                logger.debug(f"⏱️  scroll_to_element耗时: {elapsed:.2f}s")
            
            if success:
                return f"✅ 已滚动到元素 [{index}]"
            else:
                return f"❌ 滚动到元素失败"
        
        @tool
        def take_screenshot() -> str:
            """
            截取当前页面的完整截图，保存到 media 文件夹，并将截图信息传递给 LLM
            
            Returns:
                操作结果和截图文件路径
            """
            logger.info("📸 截取当前页面...")
            
            # 记录工具调用时间
            if hasattr(self, 'current_time_tracker') and self.current_time_tracker:
                self.current_time_tracker.start("tool_call")
            
            # 执行截图
            screenshot_path = operator.take_screenshot()
            
            if hasattr(self, 'current_time_tracker') and self.current_time_tracker:
                elapsed = self.current_time_tracker.end("tool_call")
                logger.debug(f"⏱️  take_screenshot耗时: {elapsed:.2f}s")
            
            if screenshot_path:
                # 标记当前对话中有截图，以便后续传递给 LLM
                if not hasattr(self, 'recent_screenshot'):
                    self.recent_screenshot = None
                self.recent_screenshot = screenshot_path
                logger.info(f"📷 截图已保存: {screenshot_path}")
                return f"✅ 页面截图已保存: {screenshot_path}\n截图文件路径: {screenshot_path}"
            else:
                return "❌ 截图失败"
        
        return [
            open_website,
            extract_page_elements,
            click_element,
            input_text_to_element,
            get_current_url,
            go_back,
            refresh_page,
            select_option,
            get_element_text,
            get_element_value,
            get_element_attribute,
            wait_for_element,
            is_element_visible,
            scroll_to_element,
            take_screenshot,
        ]
    
    def execute(self, instruction: str, thread_id: str = "default", return_tokens=False):
        """
        执行自然语言指令
        
        Args:
            instruction: 自然语言指令，例如 "请帮我打开谷歌"
            thread_id: 会话ID（用于记忆管理）
            return_tokens: 是否在返回结果中包含token使用情况
        
        Returns:
            执行结果（如果return_tokens=True，则返回包含token信息的字典）
        """
        logger.info("=" * 80)
        logger.info(f"💬 用户指令: {instruction}")
        logger.info("=" * 80)
        
        # 重置token统计
        self.token_callback.reset()
        
        # 检查是否有最近的截图，如果有则添加到指令中
        screenshot_info = ""
        if hasattr(self, 'recent_screenshot') and self.recent_screenshot:
            import os
            if os.path.exists(self.recent_screenshot):
                screenshot_info = f"\n\n【当前页面截图已可用】截图文件路径: {self.recent_screenshot}\n注意: Agent 在执行操作后可以参考此截图来辅助判断页面状态和元素位置。"
        
        # 创建时间追踪器
        time_tracker = TimeTracker()
        time_tracker.start("total")
        
        # 存储time_tracker引用供工具函数使用
        self.current_time_tracker = time_tracker
        
        try:
            # 创建回调管理器
            callback_manager = CallbackManager([self.token_callback])
            
            # 配置LangGraph
            config = {
                "configurable": {"thread_id": thread_id}
            }
            
            # 记录LLM调用时间
            time_tracker.start("llm_invoke")
            
            # 构建用户消息，包含截图信息
            user_message_content = instruction + screenshot_info
            if screenshot_info:
                logger.info(f"📷 当前对话包含截图: {self.recent_screenshot}")
            
            try:
                # 尝试两种方式传递callbacks
                try:
                    # 方式1: 作为config的一部分
                    print("传递callbacks方式1: 作为config的一部分")
                    config_with_callbacks = {**config, "callbacks": callback_manager}
                    result = self.agent.invoke(
                        {"messages": [{"role": "user", "content": user_message_content}]},
                        config=config_with_callbacks,
                        recursion_limit=40  # 增加递归限制
                    )
                except TypeError:
                    # 方式2: 作为关键字参数
                    print("传递callbacks方式2: 作为关键字参数")
                    result = self.agent.invoke(
                        {"messages": [{"role": "user", "content": user_message_content}]},
                        config=config,
                        callbacks=[self.token_callback],  # 直接传递callback list
                        recursion_limit=50  # 增加递归限制
                    )
            finally:
                # 记录LLM调用结束（无论是否成功）
                llm_time = time_tracker.end("llm_invoke")
                logger.debug(f"⏱️  LLM invoke耗时: {llm_time:.2f}s")
            
            # 提取最后一条AI消息
            final_message = result['messages'][-1].content
            
            # 从回调中获取token使用情况（已通过回调自动累积多次LLM调用的token）
            token_usage = self.token_callback.get_summary()
            
            # 如果callback没有捕获到token信息，尝试从result中提取
            if token_usage['total_tokens'] == 0:
                logger.debug("⚠️  回调未捕获token，尝试从result消息中提取...")
                try:
                    # 遍历所有消息，累加 AI 响应中的 token
                    accumulated_tokens = {'total_tokens': 0, 'prompt_tokens': 0, 'completion_tokens': 0}
                    
                    for msg in result.get('messages', []):
                        if hasattr(msg, 'response_metadata') and msg.response_metadata:
                            usage = msg.response_metadata.get('token_usage')
                            if usage and isinstance(usage, dict):
                                accumulated_tokens['total_tokens'] += usage.get('total_tokens', 0)
                                accumulated_tokens['prompt_tokens'] += usage.get('prompt_tokens', 0)
                                accumulated_tokens['completion_tokens'] += usage.get('completion_tokens', 0)
                    
                    if accumulated_tokens['total_tokens'] > 0:
                        token_usage = accumulated_tokens
                        logger.debug(f"✅ 从result消息中提取token: {token_usage}")
                    else:
                        logger.warning("⚠️  无法从result中找到token信息")
                        
                except Exception as e:
                    logger.warning(f"❌ 从result中提取token失败: {e}")
            
            logger.success("=" * 80)
            logger.success(f"🤖 Agent 回复: {final_message}")
            logger.success("=" * 80)
            logger.info("📊 Token 使用情况:")
            logger.info(f"   总Token数: {token_usage['total_tokens']}")
            logger.info(f"   Prompt Token: {token_usage['prompt_tokens']}")
            logger.info(f"   Completion Token: {token_usage['completion_tokens']}")
            
            # 输出时间统计
            time_tracker.end("total")
            time_summary = time_tracker.get_summary()
            logger.info("⏱️  执行耗时统计:")
            logger.info(f"   总耗时: {time_summary['total']:.2f}s")
            logger.info(f"   LLM调用: {time_summary['llm_invoke']:.2f}s")
            logger.info(f"   工具调用: {time_summary['tool_call']:.2f}s")
            logger.info(f"   页面提取: {time_summary['page_extraction']:.2f}s")
            logger.info(f"   其他: {time_summary['other']:.2f}s")
            
            if return_tokens:
                return {
                    'message': final_message,
                    'token_usage': token_usage,
                    'time_usage': time_summary
                }
            
            return final_message
            
        except Exception as e:
            logger.error(f"❌ 执行失败: {e}")
            import traceback
            traceback.print_exc()
            
            # 记录失败的耗时
            if time_tracker:
                time_tracker.end("total")
                time_summary = time_tracker.get_summary()
                logger.info("⏱️  执行耗时统计（失败）:")
                logger.info(f"   总耗时: {time_summary['total']:.2f}s")
                logger.info(f"   LLM调用: {time_summary['llm_invoke']:.2f}s")
                logger.info(f"   工具调用: {time_summary['tool_call']:.2f}s")
                logger.info(f"   页面提取: {time_summary['page_extraction']:.2f}s")
            
            # 即使失败也返回token使用情况
            token_usage = self.token_callback.get_summary()
            logger.info(f"📊 Token 使用情况（失败）: {token_usage}")
            
            error_msg = f"执行失败: {e}"
            if return_tokens:
                result = {
                    'message': error_msg,
                    'token_usage': token_usage
                }
                if time_tracker:
                    result['time_usage'] = time_tracker.get_summary()
                return result
            return error_msg
        finally:
            # 清理time_tracker引用
            if hasattr(self, 'current_time_tracker'):
                self.current_time_tracker = None
    
    def get_latest_token_usage(self):
        """
        获取上一次执行的token使用情况
        
        Returns:
            token使用情况字典，包含 total_tokens, prompt_tokens, completion_tokens
        """
        return self.token_callback.get_summary()
    
    def close(self):
        """关闭浏览器"""
        self.operator.close()