from time import sleep
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.autoagents_cua.prebuilt import LoginAgent
from src.autoagents_cua.browser import CaptchaAgent
from src.autoagents_cua.utils import logger


def main():
    """
    LoginAgent 使用示例 - SDK 模式
    
    在实例化时直接传入配置参数，不需要配置文件
    """
    
    # 创建 CaptchaAgent（直接传入配置）
    captcha_agent = CaptchaAgent(
        api_key= os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        model=os.getenv("OPENAI_MODEL")
    )
    
    # 创建 LoginAgent（直接传入配置）
    agent = LoginAgent(
        url="https://www.reddit.com/login/",
        captcha_agent=captcha_agent,
        headless=False,
        wait_time=3
    )
    
    # 方式1：直接调用 login()，内部自动加载页面（推荐）
    # login() 方法现在会自动调用 web_operator.navigate() 来加载页面
    success = agent.login(
        username="agentspro0bot",
        password="ubi2future",
        username_selector='xpath://input[@name="username"]',
        password_selector='xpath://input[@name="password"]',
        button_selector='xpath://button[contains(@class, "login")]',
        auto_handle_captcha=True
    )
    
    # 方式2：如果需要手动控制页面加载，可以：
    # agent.load_page()  # 先手动加载
    # success = agent.login(..., load_page=False)  # 然后登录时跳过加载
    
    if success:
        logger.success("🎉 登录成功！")
    else:
        logger.error("❌ 登录失败")
    
    input("\n按回车键关闭浏览器...")



if __name__ == '__main__':
    main()