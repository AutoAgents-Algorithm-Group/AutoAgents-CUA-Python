from typing import Optional
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from loguru import logger
from ..node import ClarifyNode, PlanNode, ExecuteNode, ObserveNode, SummaryNode



# -------------------- 状态 --------------------
class AgentState(BaseModel):
    """Agent 状态"""
    # 基本输入
    user_input: str
    clarified_input: Optional[str] = None
    clarify_count: int = 0
    
    # 交互式澄清
    needs_clarification: bool = False  # 是否需要用户澄清
    clarification_question: Optional[str] = None  # 澄清问题
    user_clarification: Optional[str] = None  # 用户的澄清回复

    # 计划与进度
    plan: list = Field(default_factory=list)
    current_step: int = 0

    # 执行与记录
    results: list = Field(default_factory=list)
    execution_rounds: int = 0
    abort_flag: bool = False

    # ——当前 step 的微循环上下文——
    step_tool_calls: int = 0
    step_tool_results: list = Field(default_factory=list)
    no_progress_streak: int = 0

    # 两级反思计数
    self_checks_used: int = 0
    strategy_shifts_used: int = 0

    # 针对每个 step 的"轻度反思"提示（不会改 plan，仅影响工具选择与参数）
    hints_by_step: dict = Field(default_factory=dict)

    # 配置
    max_total_exec_rounds: int = 40

    # 输出
    summary: str = ""


# -------------------- ReActAgent --------------------
class ReActAgent:
    """
    ReAct (Reasoning + Acting) Agent
    
    一个可直接落地的 LangGraph Agent：
    - Clarify → Plan → Execute(子循环) → Observe(SelfCheck/StrategyShift) → Summarize
    - Execute 支持同一 step 内多次工具调用，以"完成判据"为一等公民
    - 反思不依赖显式失败，在"未完成/无进展/预算告警"时也会触发
    - 多重护栏保障终止性
    """
    
    def __init__(
        self,
        clarify_node: Optional[ClarifyNode] = None,
        plan_node: Optional[PlanNode] = None,
        execute_node: Optional[ExecuteNode] = None,
        observe_node: Optional[ObserveNode] = None,
        summary_node: Optional[SummaryNode] = None
    ):
        """
        初始化 ReActAgent
        
        Args:
            clarify_node: ClarifyNode 实例（可选）
            plan_node: PlanNode 实例（可选）
            execute_node: ExecuteNode 实例（可选）
            observe_node: ObserveNode 实例（可选，用于 selfcheck 和 strategyshift）
            summary_node: SummaryNode 实例（可选）
        """
        self.graph = None
        self.checkpointer = MemorySaver()  # 用于支持 interrupt
        
        # 使用提供的节点或创建默认节点
        self.clarify_node = clarify_node or ClarifyNode()
        self.plan_node = plan_node or PlanNode()
        self.execute_node = execute_node or ExecuteNode()
        self.observe_node = observe_node or ObserveNode()
        self.summary_node = summary_node or SummaryNode()
        
        # 从节点中获取全局配置
        self.max_total_exec_rounds = self.execute_node.max_total_exec_rounds
        self.max_clarify_rounds = self.clarify_node.max_clarify_rounds
    
    # ----------- 对外 API -----------
    def invoke(self, user_input: str, thread_id: str = "default") -> AgentState:
        """
        运行 Agent（使用 interrupt 机制支持 human-in-the-loop）
        
        Args:
            user_input: 用户输入的任务描述
            thread_id: 线程 ID，用于标识会话（默认 "default"）
            
        Returns:
            AgentState: Agent 状态（可能处于 interrupt 状态或执行完成状态）
        """
        log = logger.bind(category="Agent")
        log.info("="*70)
        log.info(f"🚀 开始执行任务")
        log.info(f"📝 用户输入: {user_input[:100]}...")
        log.info(f"🧵 Thread ID: {thread_id}")
        log.info("="*70)
        
        if self.graph is None:
            log.info(f"🔧 构建执行图...")
            self.graph = self.build_graph()
        
        init = AgentState(
            user_input=user_input,
            max_total_exec_rounds=self.max_total_exec_rounds
        )
        
        # 配置：递归限制 + thread_id
        config = {
            "recursion_limit": self.max_total_exec_rounds + 10,
            "configurable": {"thread_id": thread_id}
        }
        log.info(f"⚙️ 配置: max_rounds={self.max_total_exec_rounds}, thread_id={thread_id}")
        
        # 使用 invoke 执行（LangGraph 会自动在 interrupt_after 节点处暂停）
        result = self.graph.invoke(init.model_dump(), config=config)
        result_state = AgentState(**result)
        
        # 检查是否需要用户澄清（通过 needs_clarification 标志）
        if result_state.needs_clarification:
            log.warning("⏸️ 任务已暂停（interrupt），等待用户澄清")
            log.info(f"❓ 澄清问题: {result_state.clarification_question}")
            return result_state
        
        log.info("="*70)
        log.success(f"✅ 任务执行完成！")
        log.info("="*70)
        
        return result_state
    
    def continue_with_clarification(self, user_clarification: str, thread_id: str = "default") -> AgentState:
        """
        提供用户澄清并继续执行（使用 interrupt 机制）
        
        Args:
            user_clarification: 用户的澄清回复
            thread_id: 线程 ID，必须与 invoke 时使用的相同
            
        Returns:
            AgentState: 更新后的 Agent 状态
        """
        log = logger.bind(category="Agent")
        log.info("="*70)
        log.info(f"▶️ 继续执行任务")
        log.info(f"💬 用户澄清: {user_clarification[:100]}...")
        log.info(f"🧵 Thread ID: {thread_id}")
        log.info("="*70)
        
        if self.graph is None:
            log.error("❌ Graph 未初始化")
            raise RuntimeError("Graph 未初始化，请先调用 invoke 方法")
        
        # 配置：递归限制 + thread_id
        config = {
            "recursion_limit": self.max_total_exec_rounds + 10,
            "configurable": {"thread_id": thread_id}
        }
        
        # 获取当前保存的状态（包含所有字段）
        current_state = self.graph.get_state(config)
        log.debug(f"当前状态 keys: {list(current_state.values.keys()) if current_state and current_state.values else 'None'}")
        
        # 创建完整的 AgentState（从保存的状态或默认值）
        new_input = AgentState(
            user_input=current_state.values.get('user_input', ""),
            clarified_input=current_state.values.get('clarified_input'),
            clarify_count=0,  # 重置为 0，因为要重新开始
            user_clarification=user_clarification,  # 添加用户澄清
            needs_clarification=False,  # 标记已完成澄清
            max_total_exec_rounds=self.max_total_exec_rounds
        ).model_dump()
        
        log.debug(f"重新执行，传递: user_clarification={user_clarification[:50]}...")
        log.debug(f"new_input keys: {list(new_input.keys())}")
        
        # 重新执行（从头开始，但 Clarify 节点会识别已有 user_clarification）
        result = self.graph.invoke(new_input, config=config)
        result_state = AgentState(**result)
        
        # 检查是否再次需要澄清
        if result_state.needs_clarification:
            log.warning("⏸️ 任务再次暂停（interrupt），等待用户澄清")
            log.info(f"❓ 澄清问题: {result_state.clarification_question}")
            return result_state
        
        log.info("="*70)
        log.success(f"✅ 任务执行完成！")
        log.info("="*70)
        
        return result_state
    
    # ----------- 构图 -----------
    def build_graph(self):
        """构建 LangGraph 图"""
        builder = StateGraph(dict)
        
        # 创建 observe_node 的包装函数以支持不同模式
        def selfcheck_wrapper(state: dict) -> dict:
            original_mode = self.observe_node.mode
            self.observe_node.mode = "self_check"
            result = self.observe_node(state)
            self.observe_node.mode = original_mode
            return result
        
        def strategyshift_wrapper(state: dict) -> dict:
            original_mode = self.observe_node.mode
            self.observe_node.mode = "strategy_shift"
            result = self.observe_node(state)
            self.observe_node.mode = original_mode
            return result
        
        # 添加节点
        builder.add_node("Clarify", self.clarify_node)
        builder.add_node("Plan", self.plan_node)
        builder.add_node("Execute", self.execute_node)
        builder.add_node("SelfCheck", selfcheck_wrapper)
        builder.add_node("StrategyShift", strategyshift_wrapper)
        builder.add_node("Summarize", self.summary_node)
        
        # 添加边
        builder.add_edge(START, "Clarify")
        builder.add_conditional_edges(
            "Clarify",
            self._clarify_router,
            {"again": "Clarify", "plan": "Plan", "wait": END}  # 需要澄清时暂停
        )
        builder.add_edge("Plan", "Execute")
        builder.add_conditional_edges(
            "Execute",
            self._execute_router,
            {
                "done": "Summarize",
                "selfcheck": "SelfCheck",
                "strategyshift": "StrategyShift",
                "loop": "Execute"
            }
        )
        builder.add_edge("SelfCheck", "Execute")
        builder.add_edge("StrategyShift", "Execute")
        builder.add_edge("Summarize", END)
        
        # 编译图，添加 checkpointer
        # 注意：不使用 interrupt_after，而是通过 needs_clarification 标志手动控制
        return builder.compile(checkpointer=self.checkpointer)
    
    # ----------- 路由 -----------
    def _clarify_router(self, state: dict) -> str:
        """Clarify 节点路由"""
        log = logger.bind(category="Router")
        
        # 如果需要等待用户澄清，路由到 END
        if state.get('needs_clarification', False):
            log.warning(f"🔀 Clarify → END (等待用户澄清)")
            return "wait"
        
        # 未达上限且仍不清楚 → again；否则 → plan
        if (state['clarify_count'] < self.max_clarify_rounds and
            not self.clarify_node.is_query_clear(state.get('clarified_input') or state['user_input'])):
            log.info(f"🔀 Clarify → Clarify (继续澄清)")
            return "again"
        log.info(f"🔀 Clarify → Plan (开始规划)")
        return "plan"
    
    def _execute_router(self, state: dict) -> str:
        """Execute 节点路由"""
        log = logger.bind(category="Router")
        # 检查是否完成
        done = (
            state['current_step'] >= len(state.get('plan', [])) or
            state['execution_rounds'] >= self.max_total_exec_rounds or
            state.get('abort_flag', False)
        )
        if done:
            log.info(f"🔀 Execute → Summarize (任务完成)")
            return "done"
        
        # 简化的反思触发逻辑
        # 如果单步调用次数过多或无进展，触发 selfcheck
        if (state.get('step_tool_calls', 0) >= 3 or 
            state.get('no_progress_streak', 0) >= 2):
            if state.get('self_checks_used', 0) < 2:
                log.warning(f"🔀 Execute → SelfCheck (需要轻度反思)")
                return "selfcheck"
            # 如果 selfcheck 用尽，升级到 strategyshift
            elif state.get('strategy_shifts_used', 0) < 1:
                log.warning(f"🔀 Execute → StrategyShift (需要策略调整)")
                return "strategyshift"
        
        # 默认继续循环
        log.info(f"🔀 Execute → Execute (继续执行)")
        return "loop"