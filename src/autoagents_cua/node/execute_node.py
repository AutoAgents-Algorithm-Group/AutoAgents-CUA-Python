"""
ExecuteNode - 任务执行节点
"""

from typing import List, Dict, Any, Optional, Tuple
from langchain_core.messages import HumanMessage, SystemMessage
from loguru import logger


class ExecuteNode:
    """
    任务执行节点
    
    职责：
    - 选择并调用工具
    - 检测信息增量
    - 判断步骤是否完成
    """
    
    def __init__(
        self,
        llm: Optional[object] = None,
        min_calls_before_complete: int = 2,
        similarity_threshold: float = 0.9,
        max_total_exec_rounds: int = 20
    ):
        """
        初始化执行节点
        
        Args:
            llm: ChatClient 实例（可选）
            min_calls_before_complete: 步骤完成前的最小调用次数
            similarity_threshold: 信息增量检测的相似度阈值
            max_total_exec_rounds: 最大总执行轮次
        """
        self.llm_client = llm
        self.min_calls_before_complete = min_calls_before_complete
        self.similarity_threshold = similarity_threshold
        self.max_total_exec_rounds = max_total_exec_rounds
    
    def __call__(self, state: dict) -> dict:
        """
        执行任务
        
        Args:
            state: AgentState 字典
            
        Returns:
            更新后的 state
        """
        log = logger.bind(category="Execute")
        log.info(f"🔧 进入执行节点 (执行轮次: {state['execution_rounds'] + 1}/{self.max_total_exec_rounds})")
        
        if state['execution_rounds'] >= 40 or state['abort_flag']:  # 使用默认值
            log.warning(f"⚠️ 达到最大轮次或中止标志，停止执行")
            return state
        if state['current_step'] >= len(state['plan']):
            log.success(f"✅ 所有步骤已完成")
            return state
        
        state['execution_rounds'] += 1
        step = state['plan'][state['current_step']]
        hints = state.get('hints_by_step', {}).get(state['current_step'])
        
        log.info(f"📍 当前步骤 {state['current_step'] + 1}/{len(state['plan'])}: {step.get('desc', step)[:80]}...")
        
        # 选择并调用下一工具
        tool_name, tool_input = self.choose_next_tool(step, state['step_tool_results'], hints)
        log.info(f"🔨 调用工具: {tool_name}")
        log.debug(f"   工具输入: {str(tool_input)[:200]}...")
        
        outcome = self.run_tool_for_step(tool_name, tool_input)
        log.info(f"📤 工具执行完成")
        log.debug(f"   工具输出: {str(outcome.get('output', ''))[:200]}...")
        
        state['step_tool_calls'] += 1
        state['step_tool_results'].append(outcome)
        
        # 无进展检测（相似度/信息增量）
        outs = [r.get("output", "") for r in state['step_tool_results'] if isinstance(r.get("output", ""), str)]
        if self.info_gain_ok(outs):
            state['no_progress_streak'] = 0
            log.debug(f"✅ 信息增量正常")
        else:
            state['no_progress_streak'] += 1
            log.warning(f"⚠️ 检测到无进展，连续次数: {state['no_progress_streak']}")
        
        # 完成判据
        log.info(f"🔍 检查步骤是否完成 (已调用工具 {state['step_tool_calls']} 次)...")
        if self.is_step_complete(step, state['step_tool_results']):
            log.success(f"✅ 步骤 {state['current_step'] + 1} 完成！")
            state['results'].append({
                "step": step['desc'],
                "evidence": [r.get("output") for r in state['step_tool_results']]
            })
            state['current_step'] += 1
            state['step_tool_calls'] = 0
            state['step_tool_results'] = []
            state['no_progress_streak'] = 0
            log.info(f"➡️ 进入下一步骤")
            return state
        
        # 未完成：是否需要交由路由决定 SelfCheck / StrategyShift / 继续
        log.info(f"⏭️ 步骤未完成，继续执行或等待反思")
        return state
    
    def choose_next_tool(self, step: dict,
                         partial_results: List[Dict[str, Any]],
                         hints: Optional[Dict[str, Any]] = None) -> Tuple[str, Dict[str, Any]]:
        """选择下一个工具及其参数"""
        hints = hints or {}
        if hints.get("tool_override"):
            return hints["tool_override"], hints.get("params_patch", {})
        
        if "检索" in step['desc']:
            base = {"q": hints.get("query_patch", "example query"), "k": hints.get("k", 5)}
            return hints.get("prefer_tool", "web_search"), base
        if "归纳" in step['desc']:
            chunks = [r.get("output", "") for r in partial_results]
            return hints.get("prefer_tool", "rag_summarize"), {"chunks": chunks}
        return hints.get("prefer_tool", "writer"), {
            "draft": "\n".join([r.get("output", "") for r in partial_results])
        }
    
    def run_tool_for_step(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        运行工具（占位符实现，需要子类化或注入真实工具）
        
        Args:
            tool_name: 工具名称
            tool_input: 工具输入参数
            
        Returns:
            工具执行结果
        """
        # TODO: 替换为你的真实工具调用（检索/爬虫/RAG/代码/浏览器/DeepResearch 等）
        if tool_name == "web_search":
            return {"tool": tool_name, "input": tool_input,
                    "output": "搜索结果片段A; 片段B; 片段C", "final": False}
        if tool_name == "rag_summarize":
            return {"tool": tool_name, "input": tool_input,
                    "output": "归纳要点：1) … 2) … 3) …", "final": False}
        if tool_name == "writer":
            return {"tool": tool_name, "input": tool_input,
                    "output": "可交付总结草稿（含结论与引用）。", "final": True}
        return {"tool": tool_name, "input": tool_input, "output": "占位输出", "final": False}
    
    def info_gain_ok(self, outputs: List[str]) -> bool:
        """检测信息增量是否足够"""
        if len(outputs) < 2:
            return True
        return self._similarity(outputs[-1], outputs[-2]) < self.similarity_threshold
    
    def _similarity(self, a: str, b: str) -> float:
        """计算两个字符串的相似度"""
        sa, sb = set(a.split()), set(b.split())
        return 0.0 if not sa or not sb else len(sa & sb) / len(sa | sb)
    
    def is_step_complete(self, step: dict, partial_results: List[Dict[str, Any]]) -> bool:
        """判断步骤是否完成"""
        if not partial_results:
            return False
        # 工具自声明 final=True
        if partial_results[-1].get("final", False):
            return True
        # 至少 N 次调用，避免"一次即误判完成"
        if len(partial_results) < self.min_calls_before_complete:
            return False
        
        # LLM 评审：根据 acceptance 标准和证据判断是否完成
        if self.llm_client and step.get('acceptance'):
            system_prompt = """你是一个任务评审专家。根据步骤的完成标准和已收集的证据，判断步骤是否已完成。
只返回 "COMPLETE" 或 "INCOMPLETE"，不要有其他内容。"""
            
            evidence_str = "\n".join([f"- {r.get('output', '')[:200]}" for r in partial_results])
            user_prompt = f"""步骤描述：{step['desc']}
完成标准：{step['acceptance']}
已收集证据：
{evidence_str}

请判断该步骤是否已完成："""
            
            response = self._call_llm(system_prompt, user_prompt, temperature=0.0)
            if "COMPLETE" in response.upper():
                return True
        
        # 默认：达到最小调用次数后认为完成
        return True
    
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

