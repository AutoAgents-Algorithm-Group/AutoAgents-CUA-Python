"""
ClarifyNode - 任务澄清节点
"""

from typing import Optional
from langchain_core.messages import HumanMessage, SystemMessage
from loguru import logger
from ..prompts import prompt_loader


class ClarifyNode:
    """
    任务澄清节点
    
    职责：
    - 判断任务描述是否清晰
    - 生成澄清问题
    - 整合用户补充信息
    """
    
    def __init__(
        self,
        llm: Optional[object] = None,
        max_clarify_rounds: int = 1,
        min_query_length: int = 30
    ):
        """
        初始化澄清节点
        
        Args:
            llm: ChatClient 实例（可选）
            max_clarify_rounds: 最大澄清轮次（默认1次，强制澄清）
            min_query_length: 判断查询是否清晰的最小长度
        """
        self.llm_client = llm
        self.max_clarify_rounds = max_clarify_rounds
        self.min_query_length = min_query_length
    
    def __call__(self, state: dict) -> dict:
        """
        执行澄清逻辑
        
        Args:
            state: AgentState 字典
            
        Returns:
            更新后的 state
        """
        log = logger.bind(category="Clarify")
        log.info(f"📝 进入任务澄清节点 (轮次: {state['clarify_count']}/{self.max_clarify_rounds})")
        
        if state['clarify_count'] >= self.max_clarify_rounds:
            log.info(f"✅ 已达最大澄清轮次")
            if not state.get('clarified_input'):
                state['clarified_input'] = state['user_input']
            return state
        
        # 检查是否已有用户澄清回复
        if state.get('user_clarification'):
            # 用户已提供澄清，整合回复
            log.info(f"✅ 收到用户澄清: {state['user_clarification'][:50]}...")
            state['clarified_input'] = self.incorporate_user_response(
                state['user_input'], 
                state['user_clarification']
            )
            state['clarify_count'] += 1
            state['needs_clarification'] = False
            state['clarification_question'] = None
            state['user_clarification'] = None
            log.info(f"✅ 澄清完成，更新后的任务: {state['clarified_input'][:100]}...")
            return state
        
        # 强制进行澄清：生成问题并等待用户输入
        log.info(f"🔄 生成澄清问题...")
        q = self.generate_clarification_question(state['user_input'])
        log.info(f"❓ 澄清问题: {q[:200]}...")
        log.warning(f"⏸️ 等待用户澄清...")
        
        state['needs_clarification'] = True
        state['clarification_question'] = q
        return state
    
    def is_query_clear(self, query: Optional[str]) -> bool:
        """判断查询是否清晰"""
        if not query or len(query.strip()) < 10:
            return False
        
        if not self.llm_client:
            # 简单判断：长度够长就认为清晰
            return len(query.strip()) >= self.min_query_length
        
        # 使用 LLM 判断（从 Markdown 加载提示词）
        prompt = prompt_loader.load("clarify/is_query_clear.md", query=query)
        response = self._call_llm_with_prompt(prompt, temperature=0.0)
        return "CLEAR" in response.upper()
    
    def generate_clarification_question(self, query: str) -> str:
        """生成澄清问题"""
        if not self.llm_client:
            return f"为完成任务，请补充关键约束/范围/交付：{query}"
        
        # 从 Markdown 加载提示词（支持变量插入）
        prompt = prompt_loader.load("clarify/generate_question.md", query=query)
        return self._call_llm_with_prompt(prompt)
    
    def incorporate_user_response(self, query: str, user_resp: str) -> str:
        """整合用户的补充信息"""
        return f"{query} | 澄清补充：{user_resp}"
    
    def _call_llm(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
        """调用 LLM 并返回响应文本（传统方式：system + user）"""
        if not self.llm_client:
            return f"[模拟响应: {user_prompt[:50]}...]"
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            response = self.llm_client.llm.invoke(messages)
            return response.content
        except Exception as e:
            print(f"LLM 调用失败: {e}")
            return f"[LLM调用失败: {str(e)}]"
    
    def _call_llm_with_prompt(self, prompt: str, temperature: float = 0.7) -> str:
        """调用 LLM 并返回响应文本（使用单个完整提示词）"""
        if not self.llm_client:
            return f"[模拟响应: {prompt[:50]}...]"
        
        try:
            messages = [HumanMessage(content=prompt)]
            response = self.llm_client.llm.invoke(messages)
            return response.content
        except Exception as e:
            print(f"LLM 调用失败: {e}")
            return f"[LLM调用失败: {str(e)}]"