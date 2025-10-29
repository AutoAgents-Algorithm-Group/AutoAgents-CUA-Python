import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from DrissionPage import WebPage
from src.autoagents_web.utils import CaptchaAgent, ConfigLoader, logger
from time import sleep


class GoogleReCaptchaHandler:
    """Google reCAPTCHA 处理器 - 使用传参方式"""
    
    def fill_form(self, page, config):
        """填写表单"""
        try:
            logger.info("填写表单...")
            # 根据实际页面需求填写表单
            # 这里只是示例，您可以根据实际页面调整
            return True
        except Exception as e:
            logger.error(f"表单填写失败: {e}")
            return False
    
    def solve_recaptcha(self, page, captcha_agent, config):
        """处理 reCAPTCHA"""
        try:
            logger.info("调用 CaptchaAgent.solve_recaptcha 自动处理 reCAPTCHA...")
            # 设置 page 对象到 captcha_agent
            captcha_agent.page = page
            success = captcha_agent.solve_recaptcha(
                max_retries=config.get('max_retries', 5)
            )
            return success
        except Exception as e:
            logger.error(f"reCAPTCHA 处理失败: {e}")
            return False
    
    def submit_form(self, page, config):
        """提交表单"""
        try:
            logger.info("尝试提交表单...")
            submit_btn = page.ele('css:button[type="submit"],css:input[type="submit"]', timeout=3)
            if submit_btn:
                submit_btn.click()
                logger.success("已点击提交按钮")
                return True
            else:
                logger.error("未找到提交按钮")
                return False
        except Exception as e:
            logger.error(f"表单提交失败: {e}")
            return False

def main():
    """主函数"""
    logger.info("="*80)
    logger.info("Google reCAPTCHA v2 自动化测试")
    logger.info("="*80)
    
    # 加载配置
    loader = ConfigLoader()
    captcha_config = loader.get_captcha_agent_config()
    
    # Google reCAPTCHA 测试配置
    recaptcha_config = {
        'url': 'https://www.google.com/recaptcha/api2/demo',
        'captcha_selector': 'css:.g-recaptcha',
        'timeout': 10,
        'max_retries': 5
    }
    
    # 创建 CaptchaAgent
    captcha_agent = CaptchaAgent(
        api_key=captcha_config['api_key'],
        base_url=captcha_config['base_url'],
        model=captcha_config['model']
    )
    
    # 创建浏览器页面
    page = WebPage()
    
    try:
        # 加载页面
        logger.info(f"\n正在加载页面: {recaptcha_config['url']}")
        page.get(recaptcha_config['url'])
        sleep(3)
        logger.success("页面加载完成！\n")
        
        # 创建处理器
        handler = GoogleReCaptchaHandler()
        
        # 1. 填写表单
        if not handler.fill_form(page, recaptcha_config):
            logger.error("❌ 表单填写失败")
            return
        
        sleep(1)
        
        # 2. 处理 reCAPTCHA
        if not handler.solve_recaptcha(page, captcha_agent, recaptcha_config):
            logger.error("❌ reCAPTCHA 验证失败")
            return
        
        sleep(2)
        
        # 3. 提交表单
        if handler.submit_form(page, recaptcha_config):
            logger.success("\n" + "="*80)
            logger.success("🎉 完整流程执行成功！")
            logger.success("="*80)
        else:
            logger.error("❌ 表单提交失败")
        
        input("\n按回车键关闭浏览器...")
        
    except Exception as e:
        logger.error(f"执行失败: {e}")
        logger.exception("异常详情")
        
    finally:
        page.quit()
        logger.info("\n浏览器已关闭")


if __name__ == '__main__':
    main()