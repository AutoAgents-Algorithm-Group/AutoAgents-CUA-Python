"""
BrowserAgent 高级使用测试

演示如何自定义配置和使用多个 BrowserAgent 实例
"""

import os
import sys

# 添加项目路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.autoagents_cua.client import ChatClient
from src.autoagents_cua.models import ClientConfig, ModelConfig
from src.autoagents_cua.tools import (
    ALL_WEB_TOOLS,
    BASIC_WEB_TOOLS, 
    open_website, 
    click_element,
    extract_page_elements
)
from src.autoagents_cua.agent import BrowserAgent
from src.autoagents_cua.computer import Browser
from src.autoagents_cua.utils import logger


def example1_custom_llm_config():
    """示例1：自定义 LLM 配置"""
    logger.info("=" * 80)
    logger.info("示例1：使用自定义 LLM 配置")
    logger.info("=" * 80)
    
    # 创建高温度的配置（更有创造性的回复）
    llm_creative = ChatClient(
        client_config=ClientConfig(
            base_url="https://api.openai.com/v1",
            api_key=os.getenv("OPENAI_API_KEY"),
            timeout=30
        ),
        model_config=ModelConfig(
            name="gpt-4o",
            temperature=0.7,  # 更高的温度
            max_tokens=1000
        )
    )
    
    # 创建低温度的配置（更确定性的回复）
    llm_deterministic = ChatClient(
        client_config=ClientConfig(
            base_url="https://api.openai.com/v1",
            api_key=os.getenv("OPENAI_API_KEY")
        ),
        model_config=ModelConfig(
            name="gpt-4o",
            temperature=0.0,  # 确定性输出
            max_tokens=1000
        )
    )
    
    # 创建 Browser
    browser = Browser(headless=False)
    
    # 使用确定性配置创建 agent
    agent = BrowserAgent(browser=browser, llm=llm_deterministic)
    
    logger.info("✅ 使用低温度模型，输出更确定")
    return agent


def example2_custom_browser():
    """示例2：自定义 Browser 配置"""
    logger.info("=" * 80)
    logger.info("示例2：使用自定义 Browser 配置")
    logger.info("=" * 80)
    
    # 创建自定义的 Browser（例如设置浏览器指纹和窗口大小）
    browser = Browser(
        headless=False,
        window_size={'width': 1200, 'height': 800},
        fingerprint_config='mac_chrome'  # 使用 Mac Chrome 指纹
    )
    
    # 创建 LLM 客户端
    llm = ChatClient(
        client_config=ClientConfig(
            base_url="https://api.openai.com/v1",
            api_key=os.getenv("OPENAI_API_KEY")
        ),
        model_config=ModelConfig(name="gpt-4o")
    )
    
    # 使用自定义 browser 创建 agent
    agent = BrowserAgent(browser=browser, llm=llm)
    
    logger.info("✅ 使用自定义 Browser（带浏览器指纹）")
    return agent


def example3_multiple_agents():
    """示例3：使用多个 Agent 实例"""
    logger.info("=" * 80)
    logger.info("示例3：同时使用多个 BrowserAgent")
    logger.info("=" * 80)
    
    # 共享的 LLM 配置
    shared_llm = ChatClient(
        client_config=ClientConfig(
            base_url="https://api.openai.com/v1",
            api_key=os.getenv("OPENAI_API_KEY")
        ),
        model_config=ModelConfig(name="gpt-4o")
    )
    
    # 创建两个独立的 Browser
    browser1 = Browser(headless=False, window_size={'width': 800, 'height': 600})
    browser2 = Browser(headless=False, window_size={'width': 800, 'height': 600})
    
    # 创建两个独立的 agent（使用相同的 LLM，但不同的浏览器）
    agent1 = BrowserAgent(browser=browser1, llm=shared_llm)
    agent2 = BrowserAgent(browser=browser2, llm=shared_llm)
    
    logger.info("✅ 创建了两个独立的 BrowserAgent 实例")
    
    # 可以并行使用它们
    # agent1.invoke("打开谷歌")
    # agent2.invoke("打开百度")
    
    return agent1, agent2


def example4_token_tracking():
    """示例4：Token 追踪和成本估算"""
    logger.info("=" * 80)
    logger.info("示例4：Token 追踪和成本估算")
    logger.info("=" * 80)
    
    # 创建启用 token 追踪的客户端
    llm = ChatClient(
        client_config=ClientConfig(
            base_url="https://api.openai.com/v1",
            api_key=os.getenv("OPENAI_API_KEY")
        ),
        model_config=ModelConfig(name="gpt-4o"),
        enable_token_tracking=True  # 显式启用 token 追踪
    )
    
    browser = Browser(headless=False)
    agent = BrowserAgent(browser=browser, llm=llm)
    
    # 执行操作
    agent.invoke("打开谷歌")
    
    # 查看 token 使用情况
    usage = agent.get_latest_token_usage()
    logger.info(f"\n📊 Token 使用情况:")
    logger.info(f"   总Token: {usage['total_tokens']}")
    logger.info(f"   Prompt Token: {usage['prompt_tokens']}")
    logger.info(f"   Completion Token: {usage['completion_tokens']}")
    
    # 估算成本（假设 GPT-4 价格）
    # 注意：实际价格可能不同，请查看最新定价
    prompt_cost = usage['prompt_tokens'] * 0.00003  # $0.03 / 1K tokens
    completion_cost = usage['completion_tokens'] * 0.00006  # $0.06 / 1K tokens
    total_cost = prompt_cost + completion_cost
    
    logger.info(f"\n💰 估算成本:")
    logger.info(f"   Prompt 成本: ${prompt_cost:.6f}")
    logger.info(f"   Completion 成本: ${completion_cost:.6f}")
    logger.info(f"   总成本: ${total_cost:.6f}")
    
    return agent


def main():
    """主函数"""
    logger.info("🚀 BrowserAgent 高级示例")
    
    # 选择要运行的示例
    print("\n请选择示例:")
    print("1. 自定义 LLM 配置")
    print("2. 自定义 Browser 配置")
    print("3. 多个 Agent 实例")
    print("4. Token 追踪和成本估算")
    
    choice = input("\n请输入选项 (1-4): ").strip()
    
    try:
        if choice == "1":
            agent = example1_custom_llm_config()
            agent.invoke("打开谷歌")
            input("\n按 Enter 关闭...")
            agent.close()
            
        elif choice == "2":
            agent = example2_custom_browser()
            agent.invoke("打开谷歌")
            input("\n按 Enter 关闭...")
            agent.close()
            
        elif choice == "3":
            agent1, agent2 = example3_multiple_agents()
            logger.info("\n提示：现在可以分别控制两个浏览器")
            input("\n按 Enter 关闭...")
            agent1.close()
            agent2.close()
            
        elif choice == "4":
            agent = example4_token_tracking()
            input("\n按 Enter 关闭...")
            agent.close()
            
        else:
            logger.error("无效的选项")
            
    except Exception as e:
        logger.error(f"发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

