import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.autoagents_cua.prebuilt.react_agent import ReActAgent
from src.autoagents_cua.node import ClarifyNode, PlanNode, ExecuteNode, ObserveNode, SummaryNode
from src.autoagents_cua.client.chat_client import ChatClient
from src.autoagents_cua.models.config import ClientConfig, ModelConfig


def main():    
    chat_client = ChatClient(
        client_config=ClientConfig(
            base_url="https://apihk.unifyllm.top/v1",
            api_key="sk-jsiE3Le9Dh8V7h1UJ202x15uPyIoK909FkaFX8HmAKC0h1ha"
        ),
        model_config=ModelConfig(
            name="gemini-2.5-pro",
            temperature=0.7
        )
    )
    
    # 创建 Agent - 直接传参数
    agent = ReActAgent(
        clarify_node=ClarifyNode(
            llm=chat_client,
            max_clarify_rounds=1  # 强制澄清1次
        ),
        plan_node=PlanNode(
            llm=chat_client
        ),
        execute_node=ExecuteNode(
            llm=chat_client,
            min_calls_before_complete=2,
            max_total_exec_rounds=15
        ),
        observe_node=ObserveNode(
            llm=chat_client,
            mode="self_check"
        ),
        summary_node=SummaryNode(
            llm=chat_client
        )
    )
    
    print("\n✅ Agent 创建完成")
    
    # 运行任务（使用 interrupt 机制）
    try:
        print("\n⏳ 开始执行任务...\n")
        
        # 生成唯一的 thread_id
        import uuid
        thread_id = str(uuid.uuid4())
        
        # 第一次调用：执行到澄清节点后会自动 interrupt
        state = agent.invoke(
            "做一份关于近三年AIGC投融资趋势的小型研究报告（包含主要轮次、金额、地域、代表机构与项目）",
            thread_id=thread_id
        )
        
        # 检查是否需要澄清（LangGraph 在 Clarify 节点后自动 interrupt）
        if state.needs_clarification:
            print("\n" + "="*70)
            print("⏸️ 任务已中断（Human-in-the-loop）")
            print("="*70)
            print("❓ 澄清问题:")
            print(state.clarification_question)
            print("="*70)
            
            # 获取用户输入
            print("\n💬 请提供澄清信息:")
            user_response = input("> ")
            
            # 继续执行（使用相同的 thread_id）
            print("\n⏳ 继续执行任务...\n")
            state = agent.continue_with_clarification(user_response, thread_id=thread_id)
        
        # 输出结果
        print("\n" + "="*70)
        print("📊 执行结果:")
        print("="*70)
        print(state.summary)
        print(f"\n完成步骤: {state.current_step}/{len(state.plan)}")
        print(f"执行轮次: {state.execution_rounds}")
        print("="*70)
        print("✅ 执行完成!")
        
    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
