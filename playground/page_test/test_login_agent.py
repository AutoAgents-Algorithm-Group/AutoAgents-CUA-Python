import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.autoagents_cua.utils import LoginAgent, CaptchaAgent, ConfigLoader, logger


def main():
    
    loader = ConfigLoader()
    captcha_config = loader.get_captcha_agent_config()
    login_config = loader.get_login_agent_config()
    
    # 创建 CaptchaAgent（从配置文件读取）
    captcha_agent = CaptchaAgent(
        api_key=captcha_config['api_key'],
        base_url=captcha_config['base_url'],
        model=captcha_config['model']
    )
    
    # 创建 LoginAgent（从配置文件读取）
    agent = LoginAgent(
        url=login_config['url'],
        captcha_agent=captcha_agent,
        headless=login_config['headless'],
        wait_time=login_config['wait_time']
    )
    

    # 方式1：直接调用 login()，内部自动加载页面（推荐）
    # login() 方法现在会自动调用 web_operator.navigate() 来加载页面
    success = agent.login(
        username=login_config['username'],
        password=login_config['password'],
        username_selector=login_config['username_selector'],
        password_selector=login_config['password_selector'],
        button_selector=login_config['button_selector'],
        auto_handle_captcha=login_config['auto_handle_captcha']
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