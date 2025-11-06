"""
PlanNode - 任务规划节点
"""

from typing import List, Optional
from langchain_core.messages import HumanMessage, SystemMessage
from loguru import logger
import json


class PlanNode:
    """
    任务规划节点
    
    职责：
    - 将任务分解为可执行步骤
    - 为每个步骤定义完成标准
    """
    
    def __init__(
        self,
        llm: Optional[object] = None,
        default_steps: int = 3
    ):
        """
        初始化规划节点
        
        Args:
            llm: ChatClient 实例（可选）
            default_steps: 默认生成的步骤数
        """
        self.llm_client = llm
        self.default_steps = default_steps
    
    def __call__(self, state: dict) -> dict:
        """
        执行规划逻辑
        
        Args:
            state: AgentState 字典
            
        Returns:
            更新后的 state
        """
        log = logger.bind(category="Plan")
        log.info(f"📋 进入任务规划节点")
        log.debug(f"收到的 state keys: {list(state.keys())}")
        log.debug(f"state 中是否已有 plan: {'plan' in state}")
        
        goal = state.get('clarified_input') or state['user_input']
        log.info(f"🎯 目标任务: {goal[:100]}...")
        
        generated_plan = self.generate_plan(goal)
        log.debug(f"生成的计划: {generated_plan}")
        
        state['plan'] = generated_plan
        log.success(f"✅ 生成计划，共 {len(state['plan'])} 个步骤:")
        for i, step in enumerate(state['plan'], 1):
            log.info(f"   步骤{i}: {step.get('desc', step)[:80]}...")
        
        state['current_step'] = 0
        state['step_tool_calls'] = 0
        state['step_tool_results'] = []
        state['no_progress_streak'] = 0
        state['hints_by_step'] = {}
        return state
    
    def generate_plan(self, clarified: str) -> List[dict]:
        """生成执行计划"""
        if not self.llm_client:
            # 默认计划
            return [
                {"desc": f"检索/收集：{clarified}", "acceptance": "至少3个独立可靠来源"},
                {"desc": "归纳整合成结构化要点", "acceptance": "覆盖主要问题的要点清单"},
                {"desc": "撰写面向用户的可交付总结", "acceptance": "可读/有引用/有结论"}
            ]
        
        system_prompt = """你是一个任务规划专家。根据用户的任务目标，生成一个详细的执行计划。

计划应该包含 3-5 个步骤，每个步骤都要有：
1. desc: 步骤的具体描述
2. acceptance: 该步骤的完成标准

请以 JSON 格式返回，格式如下：
[
    {"desc": "步骤1描述", "acceptance": "完成标准1"},
    {"desc": "步骤2描述", "acceptance": "完成标准2"},
    ...
]

只返回 JSON 数组，不要有其他内容。"""
        
        user_prompt = f"任务目标：{clarified}"
        response = self._call_llm(system_prompt, user_prompt)
        
        try:
            # 提取 JSON（可能包裹在 markdown 代码块中）
            json_str = response.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()
            
            plan_data = json.loads(json_str)
            return plan_data
        except Exception as e:
            print(f"解析计划失败: {e}，使用默认计划")
            return [
                {"desc": f"检索/收集相关信息：{clarified}", "acceptance": "至少3个独立可靠来源"},
                {"desc": "归纳整合成结构化要点", "acceptance": "覆盖主要问题的要点清单"},
                {"desc": "撰写面向用户的可交付总结", "acceptance": "可读/有引用/有结论"}
            ]
    
    def _call_llm(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
        """调用 LLM 并返回响应文本"""
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

