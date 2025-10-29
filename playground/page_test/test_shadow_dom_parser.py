import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.autoagents_web.utils import logger, ConfigLoader, LoginAgent, CaptchaAgent
from time import time



def main():
    start_time = time()

    loader = ConfigLoader()
    captcha_config = loader.get_captcha_agent_config()
    login_config = loader.get_login_agent_config()
    
    # 创建 CaptchaAgent
    captcha_agent = CaptchaAgent(
        api_key=captcha_config['api_key'],
        base_url=captcha_config['base_url'],
        model=captcha_config['model']
    )
    
    # 创建 LoginAgent
    agent = LoginAgent(
        url=login_config['url'],
        captcha_agent=captcha_agent,
        headless=login_config['headless'],
        wait_time=login_config['wait_time']
    )
    
    try:
        agent.load_page()
        
        # 如果需要处理 Shadow DOM，可以使用 agent.shadow_parser
        # 例如：
        agent.shadow_parser.input_text(
            host_selector='css:faceplate-text-input#login-username',
            element_selector='css:input[name="username"]',
            text=login_config['username']
        )
        
        agent.shadow_parser.input_text(
            host_selector='css:faceplate-text-input#login-password',
            element_selector='css:input[name="password"]',
            text=login_config['password']
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