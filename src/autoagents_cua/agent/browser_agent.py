from ..computer import Browser
from ..utils.logging import logger
from ..tools import bind_tools_to_context, ALL_WEB_TOOLS
from ..client import ChatClient

from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from typing import List, Callable, Optional
import time
from collections import defaultdict


class TimeTracker:
    """时间追踪类，用于记录各个阶段的耗时"""
    
    def __init__(self):
        self.start_times = {}
        self.durations = defaultdict(float)
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


class BrowserAgent:
    """
    Browser Agent - 结合 LLM 的智能网页操作
    
    通过依赖注入的方式接收 Browser 和 LLM 客户端，
    使得 Agent 更加灵活和可测试。
    """
    
    def __init__(
        self,
        browser: Browser,
        llm: ChatClient,
        tools: Optional[List[Callable]] = None,
    ):
        """
        初始化 Browser Agent
        
        Args:
            browser: Browser 实例（必需）
            llm: ChatClient 实例（必需）
            tools: 工具函数列表，默认使用 ALL_WEB_TOOLS
        
        示例:
            # 方式1：使用所有工具
            browser = Browser(headless=False)
            agent = BrowserAgent(browser=browser, llm=llm)
            
            # 方式2：自定义工具
            from autoagents_cua.tools import open_website, click_element
            agent = BrowserAgent(
                browser=browser,
                llm=llm, 
                tools=[open_website, click_element]
            )
            
            # 方式3：使用预定义工具集
            from autoagents_cua.tools import BASIC_WEB_TOOLS
            agent = BrowserAgent(
                browser=browser,
                llm=llm, 
                tools=BASIC_WEB_TOOLS
            )
        """
        self.llm_client = llm
        self.browser = browser
        self.operator = browser.operator
        self.extractor = browser.extractor
        
        # 设置工具列表（默认使用所有工具）
        if tools is None:
            tools = ALL_WEB_TOOLS
        
        # 绑定工具到上下文（operator, extractor, time_tracker）
        self.bound_tools = bind_tools_to_context(
            tools=tools,
            operator=self.operator,
            extractor=self.extractor,
            time_tracker_ref=self
        )
        
        # 创建 Agent（带记忆）
        self.checkpointer = InMemorySaver()
        self.agent = create_agent(
            model=self.llm_client.llm,
            tools=self.bound_tools,
            checkpointer=self.checkpointer,
        )
        self.graph = self.agent.get_graph()
        
        # 初始化截图追踪
        self.recent_screenshot = None
        
        logger.success(f"✅ Browser Agent 初始化完成 - 工具数量: {len(self.bound_tools)}")
    
    def invoke(self, instruction: str, thread_id: str = "default", return_tokens=False):
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
        self.llm_client.reset_token_usage()
        
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
                result = self.agent.invoke(
                    {"messages": [{"role": "user", "content": user_message_content}]},
                    config=config,
                    recursion_limit=40
                )
            finally:
                # 记录LLM调用结束（无论是否成功）
                llm_time = time_tracker.end("llm_invoke")
                logger.debug(f"⏱️  LLM invoke耗时: {llm_time:.2f}s")
            
            # 提取最后一条AI消息
            final_message = result['messages'][-1].content
            
            # 从 ChatClient 获取token使用情况
            token_usage = self.llm_client.get_token_usage()
            
            # 如果没有捕获到token信息，尝试从result中提取
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
            token_usage = self.llm_client.get_token_usage()
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
        return self.llm_client.get_token_usage()
    
    def close(self):
        """关闭浏览器"""
        self.browser.close()

