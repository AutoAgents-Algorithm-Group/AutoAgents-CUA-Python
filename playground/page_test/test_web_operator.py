"""
测试 WebOperator - 网页操作器
"""
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.autoagents_web.utils import WebOperator, logger


def test_web_operator():
    """测试 WebOperator 的基本功能"""
    
    # 创建 WebOperator（自动创建和管理 DrissionPage）
    web_operator = WebOperator(headless=False)
    
    try:
        # 使用 WebOperator 导航到测试页面
        web_operator.navigate('https://www.baidu.com', wait_time=3)
        
        logger.info("=== 测试 WebOperator 功能 ===")
        
        # 测试输入文本
        logger.info("\n1. 测试输入文本")
        web_operator.input_text('#kw', 'DrissionPage', clear=True)
        
        # 测试点击元素
        logger.info("\n2. 测试点击元素")
        web_operator.click_element('#su', wait_before=1, wait_after=2)
        
        # 测试获取元素文本
        logger.info("\n3. 测试获取元素文本")
        # 等待结果加载
        from time import sleep
        sleep(2)
        
        # 测试检查元素是否可见
        logger.info("\n4. 测试检查元素是否可见")
        is_visible = web_operator.is_element_visible('#kw')
        logger.info(f"搜索框是否可见: {is_visible}")
        
        # 测试等待元素
        logger.info("\n5. 测试等待元素")
        web_operator.wait_for_element('#kw', timeout=5)
        
        logger.success("\n✅ WebOperator 测试完成！")
        
        input("\n按回车键关闭浏览器...")
        
    except Exception as e:
        logger.error(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        web_operator.close()


def test_web_operator_with_login_agent():
    """演示 LoginAgent 如何使用 WebOperator"""
    from src.autoagents_web.utils import LoginAgent, CaptchaAgent, ConfigLoader
    
    logger.info("=== 演示 LoginAgent 使用 WebOperator ===\n")
    
    loader = ConfigLoader()
    captcha_config = loader.get_captcha_agent_config()
    login_config = loader.get_login_agent_config()
    
    # 创建 CaptchaAgent
    captcha_agent = CaptchaAgent(
        api_key=captcha_config['api_key'],
        base_url=captcha_config['base_url'],
        model=captcha_config['model']
    )
    
    # 创建 LoginAgent（内部会自动创建 WebOperator）
    agent = LoginAgent(
        url=login_config['url'],
        captcha_agent=captcha_agent,
        headless=False,
        wait_time=3
    )
    
    try:
        agent.load_page()
        
        # 通过 LoginAgent 的 web_operator 进行操作
        logger.info("使用 LoginAgent.web_operator 进行网页操作:")
        
        # 示例：直接使用 web_operator 进行自定义操作
        # agent.web_operator.input_text(selector, text)
        # agent.web_operator.click_element(selector)
        # agent.web_operator.get_element_text(selector)
        
        logger.success("✅ LoginAgent 集成 WebOperator 成功！")
        
        input("\n按回车键关闭浏览器...")
        
    finally:
        agent.close()


def test_web_operator_standalone():
    """测试 WebOperator 的独立使用（推荐）"""
    
    logger.info("=== 测试 WebOperator 独立使用 ===")
    
    # 创建 WebOperator（内部自动创建和管理 DrissionPage）
    web_operator = WebOperator(headless=False)
    
    try:
        # 导航到页面
        logger.info("\n1. 测试页面导航")
        web_operator.navigate('https://www.baidu.com', wait_time=3)
        
        # 输入文本
        logger.info("\n2. 测试输入文本")
        web_operator.input_text('#kw', 'DrissionPage', clear=True)
        
        # 点击元素
        logger.info("\n3. 测试点击元素")
        web_operator.click_element('#su', wait_before=1, wait_after=2)
        
        # 获取当前 URL
        logger.info("\n4. 测试获取 URL")
        current_url = web_operator.get_current_url()
        
        # 检查元素是否可见
        logger.info("\n5. 测试检查元素可见性")
        is_visible = web_operator.is_element_visible('#kw')
        logger.info(f"搜索框是否可见: {is_visible}")
        
        # 刷新页面
        logger.info("\n6. 测试刷新页面")
        web_operator.refresh_page(wait_time=2)
        
        logger.success("\n✅ WebOperator 独立测试完成！")
        
        input("\n按回车键关闭浏览器...")
        
    except Exception as e:
        logger.error(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # WebOperator 会自动关闭它创建的浏览器
        web_operator.close()


if __name__ == '__main__':
    # 测试 WebOperator 基本功能
    # test_web_operator()
    
    # 测试 WebOperator 独立使用（推荐）
    test_web_operator_standalone()
    
    # 测试与 LoginAgent 集成
    # test_web_operator_with_login_agent()

