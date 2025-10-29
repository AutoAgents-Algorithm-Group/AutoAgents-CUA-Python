"""
BrowserAgent 简单使用测试 - 新架构

演示如何使用新的依赖注入架构实例化 BrowserAgent
"""

import os
import sys

# 添加项目路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.autoagents_cua.client import ChatClient
from src.autoagents_cua.models import ClientConfig, ModelConfig
from src.autoagents_cua.tools import ALL_WEB_TOOLS, open_website, click_element
from src.autoagents_cua.agent import BrowserAgent
from src.autoagents_cua.computer import Browser
from src.autoagents_cua.utils import logger


def main():
    """主函数 - 演示新架构的使用方式"""
    
    logger.info("🚀 BrowserAgent 新架构测试")
    logger.info("=" * 80)
    
    # 步骤1：创建 LLM 客户端配置
    client_config = ClientConfig(
        base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        api_key=os.getenv("OPENAI_API_KEY", "your-api-key-here"),
        timeout=60,
        max_retries=3
    )
    
    # 步骤2：创建模型配置
    model_config = ModelConfig(
        name=os.getenv("OPENAI_MODEL", "gpt-4o"),
        temperature=0.0,
        max_tokens=2000
    )
    
    # 步骤3：创建 ChatClient
    llm = ChatClient(
        client_config=client_config,
        model_config=model_config,
        enable_token_tracking=True
    )
    
    logger.info(f"✅ LLM 客户端创建成功: {llm}")
    
    # 步骤4：创建 Browser
    browser = Browser(
        headless=False,  # 显示浏览器窗口
        window_size={'width': 1000, 'height': 700}  # 设置窗口大小
    )
    
    # 步骤5：创建 BrowserAgent
    # 方式1：使用所有工具（默认）
    agent = BrowserAgent(browser=browser, llm=llm)
    
    # 方式2：使用所有工具（显式）
    # agent = BrowserAgent(browser=browser, llm=llm, tools=ALL_WEB_TOOLS)
    
    # 方式3：只使用部分工具
    # agent = BrowserAgent(browser=browser, llm=llm, tools=[open_website, click_element])
    
    logger.info("=" * 80)
    logger.info("BrowserAgent 已准备就绪！")
    logger.info("=" * 80)
    
    try:
        # 示例1: 打开网站
        logger.info("\n示例 1: 打开谷歌")
        logger.info("-" * 80)
        result = agent.invoke("请帮我打开谷歌")
        
        input("\n按 Enter 继续下一个示例...")
        
        # 示例2: 提取页面元素
        logger.info("\n示例 2: 分析页面元素")
        logger.info("-" * 80)
        result = agent.invoke("帮我看看这个页面有哪些可以点击的元素")
        
        input("\n按 Enter 继续下一个示例...")
        
        # 示例3: 搜索
        logger.info("\n示例 3: 在搜索框中输入内容")
        logger.info("-" * 80)
        result = agent.invoke("在搜索框中输入 'Python'")
        
        # 查看 token 使用情况
        logger.info("\n" + "=" * 80)
        logger.info("📊 总体 Token 使用情况:")
        token_usage = agent.get_latest_token_usage()
        logger.info(f"   总Token: {token_usage['total_tokens']}")
        logger.info(f"   Prompt Token: {token_usage['prompt_tokens']}")
        logger.info(f"   Completion Token: {token_usage['completion_tokens']}")
        logger.info("=" * 80)
        
        input("\n按 Enter 关闭浏览器...")
        
    except KeyboardInterrupt:
        logger.warning("\n⚠️  用户中断")
    except Exception as e:
        logger.error(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        agent.close()
        logger.info("👋 测试结束")


if __name__ == "__main__":
    main()

