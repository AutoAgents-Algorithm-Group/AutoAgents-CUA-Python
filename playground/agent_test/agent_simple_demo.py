"""
Web 操作 Agent - 基于自然语言的网页自动化

功能：
- 支持自然语言指令（如"请帮我打开谷歌"）
- 自动执行网页操作（导航、点击、输入等）
- 智能识别页面元素

SDK 模式示例：实例化时直接传入配置参数
"""
import os
import sys

# 添加项目路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.autoagents_cua.utils.web_operator import WebOperator
from src.autoagents_cua.utils.page_extractor import PageExtractor
from src.autoagents_cua.utils.logging import logger

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from typing import Annotated
from langgraph.prebuilt import InjectedState

from src.autoagents_cua.utils.agent import WebAgent
from dotenv import load_dotenv
# class WebAgent:
#     """Web 操作 Agent - 结合 LLM 的智能网页操作"""
    
#     def __init__(self, headless=False, api_key=None, base_url=None):
#         """
#         初始化 Web Agent
        
#         Args:
#             headless: 是否使用无头模式
#             api_key: OpenAI API Key
#             base_url: API Base URL
#         """
#         # 创建 WebOperator
#         self.operator = WebOperator(headless=headless)
#         self.extractor = PageExtractor(self.operator.page)
        
#         # 初始化 LLM
#         self.llm = ChatOpenAI(
#             base_url=base_url or "https://apihk.unifyllm.top/v1",
#             api_key=api_key or "sk-jsiE3Le9Dh8V7h1UJ202x15uPyIoK909FkaFX8HmAKC0h1ha",
#             model="gemini-2.5-pro",
#             temperature=0  # 使用确定性输出
#         )
        
#         # 创建工具列表
#         self.tools = self._create_tools()
        
#         # 创建 Agent（带记忆）
#         self.checkpointer = InMemorySaver()
#         self.agent = create_agent(
#             model=self.llm,
#             tools=self.tools,
#             checkpointer=self.checkpointer,
#         )
        
#         logger.success("✅ Web Agent 初始化完成")
    
#     def _create_tools(self):
#         """创建工具函数列表"""
        
#         # 保存 self 引用，供工具函数使用
#         operator = self.operator
#         extractor = self.extractor
        
#         @tool
#         def open_website(url: str) -> str:
#             """
#             打开指定的网站
            
#             Args:
#                 url: 网站URL，例如 "https://www.google.com" 或 "https://www.baidu.com"
            
#             Returns:
#                 操作结果
#             """
#             logger.info(f"🌐 打开网站: {url}")
            
#             # 如果用户只说"谷歌"、"百度"等，自动补全URL
#             url_mapping = {
#                 "谷歌": "https://www.google.com",
#                 "google": "https://www.google.com",
#                 "百度": "https://www.baidu.com",
#                 "baidu": "https://www.baidu.com",
#                 "必应": "https://www.bing.com",
#                 "bing": "https://www.bing.com",
#                 "github": "https://github.com",
#                 "pubmed": "https://pmc.ncbi.nlm.nih.gov/",
#             }
            
#             # 检查是否需要补全URL
#             url_lower = url.lower()
#             for key, full_url in url_mapping.items():
#                 if key in url_lower and not url.startswith('http'):
#                     url = full_url
#                     logger.info(f"📝 自动补全URL: {url}")
#                     break
            
#             # 如果还是没有http前缀，添加https://
#             if not url.startswith('http'):
#                 url = 'https://' + url
            
#             success = operator.navigate(url, wait_time=3)
#             if success:
#                 return f"✅ 成功打开网站: {url}"
#             else:
#                 return f"❌ 打开网站失败: {url}"
        
#         @tool
#         def extract_page_elements() -> str:
#             """
#             提取当前页面的所有可交互元素（链接、按钮、输入框等）
            
#             Returns:
#                 提取到的元素列表描述
#             """
#             logger.info("🔍 提取页面元素...")
            
#             elements = extractor.extract_elements(highlight=True, save_to_file=None)
            
#             if not elements:
#                 return "❌ 未找到可交互元素"
            
#             # 生成简洁的元素描述
#             element_desc = f"✅ 找到 {len(elements)} 个可交互元素：\n\n"
            
#             # 按类型分组
#             by_type = {}
#             for elem in elements:
#                 tag = elem['tag']
#                 if tag not in by_type:
#                     by_type[tag] = []
#                 by_type[tag].append(elem)
            
#             # 生成描述
#             for tag, items in by_type.items():
#                 element_desc += f"【{tag.upper()}】 {len(items)} 个\n"
#                 for item in items[:5]:  # 只显示前5个
#                     text = item['text'][:30] if item['text'] else ''
#                     attrs_str = ''
#                     if 'id' in item['attrs']:
#                         attrs_str += f" id={item['attrs']['id']}"
#                     if 'name' in item['attrs']:
#                         attrs_str += f" name={item['attrs']['name']}"
                    
#                     element_desc += f"  [{item['index']}] {text}{attrs_str}\n"
                
#                 if len(items) > 5:
#                     element_desc += f"  ... 还有 {len(items) - 5} 个\n"
#                 element_desc += "\n"
            
#             return element_desc
        
#         @tool
#         def click_element(index: int) -> str:
#             """
#             点击页面上的元素（通过索引号）
            
#             Args:
#                 index: 元素的索引号（从 extract_page_elements 获取）
            
#             Returns:
#                 操作结果
#             """
#             logger.info(f"👆 点击元素 [{index}]...")
            
#             elements = extractor.get_elements()
#             if not elements:
#                 return "❌ 请先调用 extract_page_elements 提取页面元素"
            
#             # 查找对应索引的元素
#             target = None
#             for elem in elements:
#                 if elem['index'] == index:
#                     target = elem
#                     break
            
#             if not target:
#                 return f"❌ 未找到索引为 {index} 的元素"
            
#             # 点击元素
#             success = operator.click_element(target['selector'], wait_before=0.5, wait_after=2)
#             if success:
#                 return f"✅ 成功点击元素 [{index}]: {target['text'][:30]}"
#             else:
#                 return f"❌ 点击元素失败 [{index}]"
        
#         @tool
#         def input_text_to_element(index: int, text: str) -> str:
#             """
#             在输入框中输入文本（通过索引号）
            
#             Args:
#                 index: 输入框的索引号（从 extract_page_elements 获取）
#                 text: 要输入的文本
            
#             Returns:
#                 操作结果
#             """
#             logger.info(f"⌨️  在元素 [{index}] 中输入: {text}")
            
#             elements = extractor.get_elements()
#             if not elements:
#                 return "❌ 请先调用 extract_page_elements 提取页面元素"
            
#             # 查找对应索引的元素
#             target = None
#             for elem in elements:
#                 if elem['index'] == index:
#                     target = elem
#                     break
            
#             if not target:
#                 return f"❌ 未找到索引为 {index} 的元素"
            
#             # 输入文本
#             success = operator.input_text(target['selector'], text, clear=True)
#             if success:
#                 return f"✅ 成功输入文本到 [{index}]"
#             else:
#                 return f"❌ 输入文本失败 [{index}]"
        
#         @tool
#         def get_current_url() -> str:
#             """
#             获取当前页面的URL
            
#             Returns:
#                 当前页面URL
#             """
#             url = operator.get_current_url()
#             return f"当前页面: {url}"
        
#         @tool
#         def go_back() -> str:
#             """
#             返回上一页
            
#             Returns:
#                 操作结果
#             """
#             logger.info("⬅️  返回上一页...")
#             success = operator.go_back(wait_time=2)
#             if success:
#                 return "✅ 已返回上一页"
#             else:
#                 return "❌ 返回失败"
        
#         return [
#             open_website,
#             extract_page_elements,
#             click_element,
#             input_text_to_element,
#             get_current_url,
#             go_back,
#         ]
    
#     def execute(self, instruction: str, thread_id: str = "default"):
#         """
#         执行自然语言指令
        
#         Args:
#             instruction: 自然语言指令，例如 "请帮我打开谷歌"
#             thread_id: 会话ID（用于记忆管理）
        
#         Returns:
#             执行结果
#         """
#         logger.info("=" * 80)
#         logger.info(f"💬 用户指令: {instruction}")
#         logger.info("=" * 80)
        
#         try:
#             config = {"configurable": {"thread_id": thread_id}}
            
#             result = self.agent.invoke(
#                 {"messages": [{"role": "user", "content": instruction}]},
#                 config=config
#             )
            
#             # 提取最后一条AI消息
#             final_message = result['messages'][-1].content
            
#             logger.success("=" * 80)
#             logger.success(f"🤖 Agent 回复: {final_message}")
#             logger.success("=" * 80)
            
#             return final_message
            
#         except Exception as e:
#             logger.error(f"❌ 执行失败: {e}")
#             import traceback
#             traceback.print_exc()
#             return f"执行失败: {e}"
    
#     def close(self):
#         """关闭浏览器"""
#         self.operator.close()


def simple_demo():
    """演示示例 - SDK 模式：直接传入配置参数"""
    logger.info("🚀 Web Agent 演示启动")
    
    # 创建 Agent（直接传入配置参数，或从环境变量读取）
    agent = WebAgent(
        headless=False, 
        api_key=os.getenv("OPENAI_API_KEY") or "sk-jsiE3Le9Dh8V7h1UJ202x15uPyIoK909FkaFX8HmAKC0h1ha", 
        base_url=os.getenv("OPENAI_BASE_URL") or "https://api.tu-zi.com/v1", 
        model="gemini-2.5-pro"
    )
    
    try:
        # 示例1: 打开网站
        logger.info("\n" + "🔹" * 40)
        logger.info("示例 1: 打开谷歌")
        logger.info("🔹" * 40 + "\n")
        agent.execute("请帮我打开谷歌")
        
        # 等待用户观察
        input("\n按 Enter 继续下一个示例...")
        
        # 示例2: 提取页面元素
        logger.info("\n" + "🔹" * 40)
        logger.info("示例 2: 分析页面元素")
        logger.info("🔹" * 40 + "\n")
        agent.execute("帮我看看这个页面有哪些可以点击的元素")
        
        # 等待用户观察
        input("\n按 Enter 继续下一个示例...")
        
        # 示例3: 综合操作（打开百度并搜索）
        logger.info("\n" + "🔹" * 40)
        logger.info("示例 3: 打开百度并搜索")
        logger.info("🔹" * 40 + "\n")
        agent.execute("打开百度")
        agent.execute("帮我看看页面元素")
        agent.execute("在搜索框中输入'人工智能'，然后点击搜索按钮")
        
        input("\n按 Enter 关闭浏览器...")
        
    except KeyboardInterrupt:
        logger.warning("\n⚠️  用户中断")
    finally:
        agent.close()
        logger.info("👋 演示结束")


def sample_demo1():
    agent = WebAgent(headless=False)
    while True:
        instruction = input("请输入指令: ")
        if instruction.lower() in ['exit', 'quit', '退出', '结束']:
            break
        agent.execute(instruction)
        



if __name__ == "__main__":
    

    sample_demo1()

