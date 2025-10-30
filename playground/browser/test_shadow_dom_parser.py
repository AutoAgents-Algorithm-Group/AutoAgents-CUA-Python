import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.autoagents_cua.prebuilt import LoginAgent
from src.autoagents_cua.browser import CaptchaAgent
from src.autoagents_cua.utils import logger
from time import time


def main():
    """
    Shadow DOM 解析器测试 - SDK 模式
    
    在实例化时直接传入配置参数
    """
    start_time = time()

    # 创建 CaptchaAgent（直接传入配置）
    captcha_agent = CaptchaAgent(
        api_key="sk-jsiE3Le9Dh8V7h1UJ202x15uPyIoK909FkaFX8HmAKC0h1ha",
        base_url="https://api.tu-zi.com/v1",
        model="gemini-2.5-pro"
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
        
        # 如果需要处理 Shadow DOM，可以使用 agent.shadow_parser
        # 例如：
        agent.shadow_parser.input_text(
            host_selector='css:faceplate-text-input#login-username',
            element_selector='css:input[name="username"]',
            text="agentspro0bot"
        )
        
        agent.shadow_parser.input_text(
            host_selector='css:faceplate-text-input#login-password',
            element_selector='css:input[name="password"]',
            text="ubi2future"
        )
        
        # 使用 web_operator 点击登录按钮（XPath 定位）
        agent.web_operator.click_element(
            'x://*[@id="login"]/auth-flow-modal/div[2]/faceplate-tracker[1]/button'
        )

        # agent.web_operator.navigate("https://www.reddit.com/")
        
        logger.success(f"登录流程完成，耗时 {time() - start_time} 秒")
        
        input("\n按回车键关闭浏览器...")
        
    except Exception as e:
        logger.error(f"示例失败: {e}")
    finally:
        agent.close()


if __name__ == "__main__":
    main()