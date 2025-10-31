import os
import sys
from tkinter import N
from tracemalloc import start
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from DrissionPage import WebPage
from src.autoagents_cua.browser import CaptchaAgent
from src.autoagents_cua.utils import logger


def test_captcha_agent_full_flow():
    """
    测试 CaptchaAgent 的完整验证码处理流程
    
    CaptchaAgent 现在包含以下方法：
    1. recognize_captcha() - 识别验证码图片
    2. parse_coordinates() - 解析坐标
    3. click_captcha_coordinates() - 点击验证码坐标
    4. solve_captcha() - 完整的验证码处理流程（NEW！）
    """
    
    # 创建 CaptchaAgent（直接传入配置）
    captcha_agent = CaptchaAgent(
        api_key= os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        model=os.getenv("OPENAI_MODEL")
    )
    
    # 创建页面对象
    page = WebPage()
    
    try:
        # 访问登录页面（示例）
        page.get('https://example.com/login')
        
        logger.info("=== 测试 CaptchaAgent 完整流程 ===\n")
        
        # 方式1：使用 solve_captcha 一键处理（推荐）
        logger.info("方式1：使用 solve_captcha 一键处理验证码")
        success = captcha_agent.solve_captcha(
            page=page,
            captcha_selector='t:div@@class=geetest_panel_next',
            save_path='captcha.png',
            timeout=10,
            max_retries=3
        )
        
        if success:
            logger.success("✅ 验证码处理成功！")
        else:
            logger.error("❌ 验证码处理失败")
        
        # 方式2：分步处理（灵活）
        logger.info("\n方式2：分步处理验证码")
        
        # 步骤1：识别验证码
        answer = captcha_agent.recognize_captcha('captcha.png')
        logger.info(f"识别结果: {answer}")
        
        # 步骤2：解析坐标
        coordinates = captcha_agent.parse_coordinates(answer)
        logger.info(f"解析坐标: {coordinates}")
        
        # 步骤3：点击坐标（需要准备 captcha_info）
        # captcha_info = {...}  # 包含位置和尺寸信息
        # success = captcha_agent.click_captcha_coordinates(page, captcha_info, coordinates)
        
        input("\n按回车键关闭浏览器...")
        
    except Exception as e:
        logger.error(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        page.quit()


def test_captcha_agent_with_login():
    """演示在 LoginAgent 中使用 CaptchaAgent - SDK 模式"""
    from src.autoagents_cua.prebuilt import LoginAgent
    
    logger.info("=== 演示 LoginAgent 使用 CaptchaAgent ===\n")
    
    # 创建 CaptchaAgent（直接传入配置）
    captcha_agent = CaptchaAgent(
        
    )
    
    # 创建 LoginAgent（直接传入配置）
    agent = LoginAgent(
        url="https://www.reddit.com/login/",
        captcha_agent=captcha_agent,
        headless=False,
        wait_time=3
    )
    
    try:
        agent.load_page()
        
        # LoginAgent 会自动调用 captcha_agent.solve_captcha()
        success = agent.login(
            username="agentspro0bot",
            password="ubi2future",
            auto_handle_captcha=True  # 内部会调用 captcha_agent.solve_captcha(page)
        )
        
        if success:
            logger.success("✅ 登录成功！")
        else:
            logger.error("❌ 登录失败")
        
        # 也可以手动调用验证码处理
        # captcha_agent.solve_captcha(agent.page)
        
        input("\n按回车键关闭浏览器...")
        
    finally:
        agent.close()


if __name__ == '__main__':
    # 测试 CaptchaAgent 完整流程
    # test_captcha_agent_full_flow()
    
    # 测试与 LoginAgent 的集成
    test_captcha_agent_with_login()

