"""
测试截图工具功能

演示如何使用新的 take_screenshot 工具来辅助页面操作
"""
import os
import sys

# 添加项目路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.autoagents_web.utils.agent import WebAgent
from src.autoagents_web.utils.logging import logger
from dotenv import load_dotenv


def test_screenshot_tool():
    """测试截图工具"""
    logger.info("🚀 启动截图工具测试")
    
    # 加载环境变量
    load_dotenv()
    
    # 创建 Agent
    agent = WebAgent(headless=False)
    
    try:
        # 1. 打开网页并截图
        logger.info("\n" + "=" * 80)
        logger.info("步骤 1: 打开百度并截图")
        logger.info("=" * 80 + "\n")
        agent.execute("打开百度")
        agent.execute("截图")  # Agent 会自动调用 take_screenshot 工具
        
        # 等待查看结果
        input("\n按 Enter 继续下一步（截图已保存在 media 文件夹）...")
        
        # 2. 截图后查询页面元素
        logger.info("\n" + "=" * 80)
        logger.info("步骤 2: 查询页面可操作元素")
        logger.info("=" * 80 + "\n")
        # 由于有截图，Agent 在执行操作时会参考截图
        agent.execute("帮我看看这个页面有哪些可点击的元素")
        
        input("\n按 Enter 继续下一步...")
        
        # 3. 在搜索框输入并截图
        logger.info("\n" + "=" * 80)
        logger.info("步骤 3: 输入搜索词并截图查看状态")
        logger.info("=" * 80 + "\n")
        agent.execute("在搜索框输入'Python'")
        agent.execute("截图")  # 再次截图查看输入后的状态
        
        input("\n按 Enter 继续下一步...")
        
        # 4. 通过截图辅助判断元素
        logger.info("\n" + "=" * 80)
        logger.info("步骤 4: 通过截图查看页面状态")
        logger.info("=" * 80 + "\n")
        agent.execute("页面当前截图在哪里？我可以查看截图来了解页面状态")
        
        logger.info("\n✅ 截图工具测试完成！")
        logger.info("📁 截图文件保存在: media 文件夹下")
        
    except KeyboardInterrupt:
        logger.warning("\n⚠️  用户中断")
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        agent.close()
        logger.info("👋 测试结束")


def simple_screenshot_demo():
    """简单的截图演示"""
    logger.info("🚀 简单截图演示")
    
    load_dotenv()
    agent = WebAgent(headless=False)
    
    try:
        # 打开页面
        agent.execute("打开谷歌")
        
        # 截图
        logger.info("\n📸 执行截图...")
        result = agent.execute("截图")
        logger.success(f"截图结果: {result}")
        
        # 查看截图路径
        if hasattr(agent, 'recent_screenshot'):
            screenshot_path = agent.recent_screenshot
            if screenshot_path and os.path.exists(screenshot_path):
                logger.success(f"✅ 截图已保存: {screenshot_path}")
            else:
                logger.warning("❌ 未找到截图文件")
        else:
            logger.warning("❌ 未找到截图路径")
        
        logger.info("\n 解析图片内容...")

        result = agent.execute("解析图片内容")
        logger.success(f"解析图片内容结果: {result}")

        input("\n按 Enter 关闭浏览器...")
        
    except Exception as e:
        logger.error(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        agent.close()


if __name__ == "__main__":
    # 简单演示
    # simple_screenshot_demo()
    # 加载环境变量
    load_dotenv()
    # 完整测试（取消注释以运行）
    # test_screenshot_tool()
    agent = WebAgent(headless=False)

    # 打开网页
    agent.execute("打开百度")

    # 截图
    agent.execute("截图")

    
