import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from src.utils.agent.autobrowser_agent import WebAgent
from src.utils.logging import logger



def main():
    """主函数 - 交互式 Web Agent 测试"""
    
    # 创建 WebAgent 实例（配置从 config.yaml 加载）
    try:
        agent = WebAgent(headless=False)
        logger.success("✅ Web Agent 初始化成功\n")
    except Exception as e:
        logger.error(f"❌ Web Agent 初始化失败: {e}")
        return
    
    # 统计总的 token 使用
    total_stats = {
        'total_tokens': 0,
        'prompt_tokens': 0,
        'completion_tokens': 0,
        'total_time': 0,
        'request_count': 0
    }
    
    try:
        while True:
            # 获取用户输入
            print("\n" + "─" * 80)
            instruction = input("💬 请输入指令: ").strip()
            
            # 检查退出命令
            if instruction.lower() in ['exit', 'quit', '退出', '结束', 'q']:
                logger.info("👋 准备退出...")
                break
            
            # 忽略空输入
            if not instruction:
                logger.warning("⚠️  请输入有效指令")
                continue
            
            # 执行指令并获取 token 统计
            try:
                result = agent.execute(instruction, return_tokens=True)
                
                # 更新统计
                if isinstance(result, dict):
                    token_usage = result.get('token_usage', {})
                    time_usage = result.get('time_usage', {})
                    
                    total_stats['total_tokens'] += token_usage.get('total_tokens', 0)
                    total_stats['prompt_tokens'] += token_usage.get('prompt_tokens', 0)
                    total_stats['completion_tokens'] += token_usage.get('completion_tokens', 0)
                    total_stats['total_time'] += time_usage.get('total', 0)
                    total_stats['request_count'] += 1
                    
                    # 显示本次统计
                    print("\n" + "📊" * 40)
                    logger.info("📊 本次执行统计：")
                    logger.info(f"   Token 使用: {token_usage.get('total_tokens', 0)} tokens")
                    logger.info(f"     - Prompt: {token_usage.get('prompt_tokens', 0)}")
                    logger.info(f"     - Completion: {token_usage.get('completion_tokens', 0)}")
                    logger.info(f"   执行时间: {time_usage.get('total', 0):.2f}s")
                    logger.info(f"     - LLM调用: {time_usage.get('llm_invoke', 0):.2f}s")
                    logger.info(f"     - 工具调用: {time_usage.get('tool_call', 0):.2f}s")
                    logger.info(f"     - 页面提取: {time_usage.get('page_extraction', 0):.2f}s")
                    
                    # 显示累计统计
                    print("\n" + "📈" * 40)
                    logger.info("📈 累计统计：")
                    logger.info(f"   总请求数: {total_stats['request_count']}")
                    logger.info(f"   总 Token: {total_stats['total_tokens']} tokens")
                    logger.info(f"     - Prompt: {total_stats['prompt_tokens']}")
                    logger.info(f"     - Completion: {total_stats['completion_tokens']}")
                    logger.info(f"   总耗时: {total_stats['total_time']:.2f}s")
                    if total_stats['request_count'] > 0:
                        avg_tokens = total_stats['total_tokens'] / total_stats['request_count']
                        avg_time = total_stats['total_time'] / total_stats['request_count']
                        logger.info(f"   平均每次: {avg_tokens:.0f} tokens, {avg_time:.2f}s")
                    
            except KeyboardInterrupt:
                logger.warning("\n⚠️  操作被用户中断")
                continue
            except Exception as e:
                logger.error(f"❌ 执行失败: {e}")
                import traceback
                traceback.print_exc()
                continue
    
    except KeyboardInterrupt:
        logger.warning("\n\n⚠️  程序被用户中断")
    finally:
        # 关闭浏览器
        logger.info("\n🔄 正在关闭浏览器...")
        agent.close()
        
        # 显示最终统计
        print("\n" + "=" * 80)
        logger.info("📊 最终统计报告：")
        logger.info(f"   总请求数: {total_stats['request_count']}")
        logger.info(f"   总 Token: {total_stats['total_tokens']} tokens")
        logger.info(f"   总耗时: {total_stats['total_time']:.2f}s")
        logger.info("=" * 80)
        logger.success("👋 Web Agent 测试结束")


if __name__ == "__main__":
    main()