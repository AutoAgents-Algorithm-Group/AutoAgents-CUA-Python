from ..utils.logging import logger, set_stage
from ..models import Stage
from ..utils.page_extractor import PageExtractor
from ..utils.shadow_dom_parser import ShadowDOMParser
from ..utils.web_operator import WebOperator


class LoginAgent:
    """登录代理 - 提供完整的登录和验证码处理功能"""
    
    def __init__(self, url, captcha_agent, headless=False, wait_time=3):
        """
        初始化登录代理
        
        Args:
            url: 要访问的网页URL
            captcha_agent: CaptchaAgent 实例（必传）
            headless: 是否使用无头模式
            wait_time: 页面加载等待时间（秒）
        """
        self.url = url
        self.wait_time = wait_time
        
        # 创建网页操作器（WebOperator 负责创建和管理 DrissionPage）
        self.web_operator = WebOperator(headless=headless)
        
        # 从 WebOperator 获取 page 对象
        self.page = self.web_operator.page
        
        # 创建页面元素提取器
        self.page_extractor = PageExtractor(self.page)
        
        # 设置验证码代理（必传参数）
        self.captcha_agent = captcha_agent
        
        # 创建 Shadow DOM 解析器
        self.shadow_parser = ShadowDOMParser(self.page)
    
    def load_page(self):
        """加载网页（委托给 WebOperator）"""
        return self.web_operator.navigate(self.url, self.wait_time)
    
    def close(self):
        """关闭浏览器（委托给 WebOperator）"""
        self.web_operator.close()

    def login(
            self, 
            username,  # 用户名
            password,  # 密码
            username_selector=None,  # 用户名输入框定位器
            password_selector=None,  # 密码输入框定位器     
            button_selector=None,  # 登录按钮定位器
            auto_handle_captcha=True):  # 是否自动处理验证码

        log = set_stage(Stage.LOGIN)
        try:
            log.info("开始登录流程")
            
            page_log = set_stage(Stage.PAGE_LOAD)
            success = self.web_operator.navigate(self.url, self.wait_time)
            if not success:
                log.error("页面加载失败")
                return False
            
            # 如果没有提供定位器，自动提取
            if not (username_selector and password_selector and button_selector):
                element_log = set_stage(Stage.ELEMENT)
                element_log.info("自动提取页面元素...")
                self.page_extractor.extract_elements()
                
                input_elements = self.page_extractor.get_elements_by_tag('input')
                button_elements = self.page_extractor.get_elements_by_tag('button')
                
                if len(input_elements) < 2:
                    element_log.warning("未找到足够的输入框")
                    return False
                
                if not button_elements:
                    element_log.warning("未找到按钮元素")
                    return False
                
                username_selector = username_selector or input_elements[0]['selector']
                password_selector = password_selector or input_elements[1]['selector']
                button_selector = button_selector or button_elements[0]['selector']
                
                element_log.success(f"用户名输入框: {username_selector}")
                element_log.success(f"密码输入框: {password_selector}")
                element_log.success(f"登录按钮: {button_selector}")
            
            # 输入用户名和密码
            log.info("输入登录信息...")
            self.web_operator.input_text(username_selector, username)
            self.web_operator.input_text(password_selector, password)
            
            # 点击登录按钮
            log.info("点击登录按钮...")
            result = self.web_operator.click_element(button_selector)
            
            if not result:
                log.warning("登录按钮点击失败")
                return False
            
            log.success("登录按钮点击成功")
            
            # 自动处理验证码（委托给 CaptchaAgent）
            if auto_handle_captcha:
                captcha_success = self.captcha_agent.solve_captcha(self.page)
                return captcha_success
            
            return True
            
        except Exception as e:
            log.error(f"登录失败: {e}")
            log.exception("登录异常详情")
            return False


