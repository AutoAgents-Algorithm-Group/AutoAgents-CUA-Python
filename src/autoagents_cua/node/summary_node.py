"""
SummaryNode - 任务总结节点
"""

from typing import Optional
from loguru import logger


class SummaryNode:
    """
    任务总结节点
    
    职责：
    - 汇总各步骤的执行结果
    - 生成结构化的执行报告
    """
    
    def __init__(
        self,
        llm: Optional[object] = None,
        use_llm_summary: bool = False
    ):
        """
        初始化总结节点
        
        Args:
            llm: ChatClient 实例（可选）
            use_llm_summary: 是否使用 LLM 生成智能总结
        """
        self.llm_client = llm
        self.use_llm_summary = use_llm_summary
    
    def __call__(self, state: dict) -> dict:
        """
        生成执行总结
        
        Args:
            state: AgentState 字典
            
        Returns:
            更新后的 state
        """
        log = logger.bind(category="Summary")
        log.info(f"📄 进入总结节点")
        log.info(f"📊 统计执行情况:")
        log.info(f"   - 完成步骤: {state['current_step']}/{len(state.get('plan', []))}")
        log.info(f"   - 执行轮次: {state['execution_rounds']}")
        log.info(f"   - 自我检查次数: {state.get('self_checks_used', 0)}")
        log.info(f"   - 策略调整次数: {state.get('strategy_shifts_used', 0)}")
        
        lines = []
        for i, r in enumerate(state.get('results', []), 1):
            lines.append(f"{i}. [{r['step']}]")
            for j, ev in enumerate(r.get("evidence", []), 1):
                lines.append(f"   - 证据{j}: {ev}")
        
        if state['current_step'] < len(state.get('plan', [])):
            remain = len(state['plan']) - state['current_step']
            log.warning(f"⚠️ 尚有 {remain} 个步骤未完成，提前退出")
            lines.append(f"\n（提示）尚有 {remain} 个步骤未完成，已提前收敛退出。")
        else:
            log.success(f"✅ 所有步骤已完成！")
        
        state['summary'] = "执行总结：\n" + "\n".join(lines)
        log.success(f"✅ 总结生成完成")
        return state
