"""
ObserveNode - 任务观察与反思节点
"""

from typing import List, Dict, Any, Optional
from langchain_core.messages import HumanMessage, SystemMessage
from loguru import logger
import json


class ObserveNode:
    """
    任务观察与反思节点
    
    职责：
    - SelfCheck: 轻度反思，提供改进建议
    - StrategyShift: 深度反思，进行策略重构
    """
    
    def __init__(
        self,
        llm: Optional[object] = None,
        mode: str = "self_check"
    ):
        """
        初始化观察节点
        
        Args:
            llm: ChatClient 实例（可选）
            mode: "self_check" 或 "strategy_shift"
        """
        self.llm_client = llm
        self.mode = mode
    
    def __call__(self, state: dict) -> dict:
        """
        执行观察与反思
        
        Args:
            state: AgentState 字典
            
        Returns:
            更新后的 state
        """
        log = logger.bind(category="Observe")
        log.info(f"🧠 进入观察反思节点 (模式: {self.mode})")
        
        if self.mode == "self_check":
            log.info(f"🔍 执行轻度反思 (SelfCheck)")
            return self.self_check(state)
        elif self.mode == "strategy_shift":
            log.warning(f"🔄 执行策略调整 (StrategyShift)")
            return self.strategy_shift(state)
        else:
            raise ValueError(f"未知的观察模式: {self.mode}")
    
    def self_check(self, state: dict) -> dict:
        """
        自我检查：轻度反思，提供改进建议
        
        Args:
            state: AgentState 字典
            
        Returns:
            更新后的 state
        """
        log = logger.bind(category="SelfCheck")
        state['self_checks_used'] = state.get('self_checks_used', 0) + 1
        log.info(f"💡 执行自我检查 (第 {state['self_checks_used']} 次)")
        
        if state['current_step'] >= len(state['plan']):
            log.warning(f"⚠️ 当前步骤超出计划范围，跳过")
            return state
        
        step = state['plan'][state['current_step']]
        log.info(f"🔍 分析步骤: {step.get('desc', step)[:80]}...")
        
        patch = self.model_self_check(step, state['step_tool_results'])
        log.info(f"📝 生成改进建议")
        
        self.apply_self_patch(state, patch.get("hints_patch", {}))
        log.success(f"✅ 已应用改进建议")
        
        return state
    
    def strategy_shift(self, state: dict) -> dict:
        """
        策略转换：深度反思，进行策略重构
        
        Args:
            state: AgentState 字典
            
        Returns:
            更新后的 state
        """
        log = logger.bind(category="Strategy")
        state['strategy_shifts_used'] = state.get('strategy_shifts_used', 0) + 1
        log.warning(f"🔄 执行策略调整 (第 {state['strategy_shifts_used']} 次)")
        
        if state['current_step'] >= len(state['plan']):
            log.warning(f"⚠️ 当前步骤超出计划范围，跳过")
            return state
        
        step = state['plan'][state['current_step']]
        budget_ratio = (state['execution_rounds'] / float(state.get('max_total_exec_rounds', 40)))
        log.info(f"📊 预算使用率: {budget_ratio:.1%}")
        log.info(f"🎯 重新评估步骤: {step.get('desc', step)[:80]}...")
        
        patch = self.model_strategy_shift(step, state['step_tool_results'], state['plan'], budget_ratio)
        log.info(f"📝 生成策略调整方案")
        
        self.apply_strategy_shift(state, patch.get("patch", {}))
        log.success(f"✅ 策略调整已应用")
        
        return state
    
    def model_self_check(self, step: dict, partial_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """使用 LLM 进行自我检查，分析当前进展并提供改进建议"""
        if not self.llm_client:
            # 默认回退
            return {
                "insight": f"SelfCheck: 『{step['desc']}』信息增量不足，尝试换关键词/扩大检索。",
                "hints_patch": {"prefer_tool": "web_search", "query_patch": "更聚焦的关键词", "k": 8}
            }
        
        system_prompt = """你是一个任务执行反思专家。分析当前步骤的执行情况，提供改进建议。

请以 JSON 格式返回分析结果：
{
    "insight": "对当前执行情况的分析和反思",
    "hints_patch": {
        "prefer_tool": "建议使用的工具名称",
        "query_patch": "改进的查询关键词（如适用）",
        "k": 建议的结果数量（如适用）
    }
}

只返回 JSON，不要有其他内容。"""
        
        evidence_str = "\n".join([
            f"工具: {r.get('tool', 'unknown')}, 输出: {r.get('output', '')[:150]}..."
            for r in partial_results
        ])
        
        user_prompt = f"""步骤描述：{step['desc']}
完成标准：{step.get('acceptance', 'N/A')}
已执行的工具调用（{len(partial_results)}次）：
{evidence_str}

问题：当前执行似乎陷入困境或信息增量不足，请分析原因并提供改进建议。"""
        
        response = self._call_llm(system_prompt, user_prompt)
        
        try:
            # 提取 JSON
            json_str = response.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()
            
            return json.loads(json_str)
        except Exception as e:
            print(f"解析 SelfCheck 响应失败: {e}")
            return {
                "insight": f"SelfCheck 分析：{response[:100]}",
                "hints_patch": {"prefer_tool": "web_search"}
            }
    
    def model_strategy_shift(self, step: dict,
                             partial_results: List[Dict[str, Any]],
                             plan: List[dict],
                             budget_ratio: float) -> Dict[str, Any]:
        """使用 LLM 进行策略转换，提供更激进的改进方案"""
        if not self.llm_client:
            # 默认回退
            return {
                "insight": f"StrategyShift: 『{step['desc']}』久攻不下，改为'先生成数据源清单再检索'。",
                "patch": {"insert_before": f"（修正）为『{step['desc']}』生成≥5条数据源/关键词清单",
                          "prefer_tool": "source_planner"}
            }
        
        system_prompt = """你是一个策略转换专家。当前步骤执行遇到严重困难，需要更激进的策略调整。

可选的策略包括：
1. 插入新的准备步骤（如先生成数据源清单、关键词列表等）
2. 完全改变工具选择策略
3. 调整执行方式或参数

请以 JSON 格式返回策略调整方案：
{
    "insight": "对问题的深度分析和策略转换建议",
    "patch": {
        "insert_before": "要插入的新步骤描述（可选，如果需要插入新步骤）",
        "prefer_tool": "建议使用的工具名称（可选）"
    }
}

只返回 JSON，不要有其他内容。"""
        
        evidence_str = "\n".join([
            f"工具: {r.get('tool', 'unknown')}, 输出: {r.get('output', '')[:150]}..."
            for r in partial_results
        ])
        
        plan_str = "\n".join([f"{i+1}. {s['desc']}" for i, s in enumerate(plan)])
        
        user_prompt = f"""当前步骤：{step['desc']}
完成标准：{step.get('acceptance', 'N/A')}
整体计划：
{plan_str}

已尝试执行（{len(partial_results)}次，预算使用{budget_ratio:.1%}）：
{evidence_str}

问题：该步骤久攻不下，需要策略转换。请提供深度分析和激进的改进方案。"""
        
        response = self._call_llm(system_prompt, user_prompt)
        
        try:
            # 提取 JSON
            json_str = response.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()
            
            return json.loads(json_str)
        except Exception as e:
            print(f"解析 StrategyShift 响应失败: {e}")
            return {
                "insight": f"StrategyShift 分析：{response[:100]}",
                "patch": {"prefer_tool": "web_search"}
            }
    
    def apply_self_patch(self, state: dict, hints_patch: Dict[str, Any]) -> None:
        """应用自我检查的改进建议"""
        idx = state['current_step']
        hints = state.get('hints_by_step', {}).get(idx, {}).copy()
        hints.update(hints_patch or {})
        if 'hints_by_step' not in state:
            state['hints_by_step'] = {}
        state['hints_by_step'][idx] = hints
        state['no_progress_streak'] = 0  # "局部降温"
    
    def apply_strategy_shift(self, state: dict, patch: Dict[str, Any]) -> None:
        """应用策略转换的改进方案"""
        if "insert_before" in patch:
            fix_step = {
                "desc": patch["insert_before"],
                "acceptance": "列出≥5条高质量数据源/关键词"
            }
            state['plan'].insert(state['current_step'], fix_step)
        
        if 'hints_by_step' not in state:
            state['hints_by_step'] = {}
        
        hints = state['hints_by_step'].get(state['current_step'], {}).copy()
        if "prefer_tool" in patch:
            hints["tool_override"] = patch["prefer_tool"]
        state['hints_by_step'][state['current_step']] = hints
        state['step_tool_calls'] = 0
        state['step_tool_results'] = []
        state['no_progress_streak'] = 0
    
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

