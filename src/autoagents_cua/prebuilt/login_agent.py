"""
Login Agent - 


"""

from ..utils.logging import logger, set_stage
from ..models import Stage
from ..browser import PageExtractor, ShadowDOMParser, WebOperator


class LoginAgent:
    """ - """
    
    def __init__(self, url, captcha_agent, headless=False, wait_time=3):
        """
        
        
        Args:
            url: URL
            captcha_agent: CaptchaAgent 
            headless: 
            wait_time: 
        """
        self.url = url
        self.wait_time = wait_time
        
        # WebOperator DrissionPage
        self.web_operator = WebOperator(headless=headless)
        
        # WebOperator page 
        self.page = self.web_operator.page
        
        # 
        self.page_extractor = PageExtractor(self.page)
        
        # 
        self.captcha_agent = captcha_agent
        
        # Shadow DOM 
        self.shadow_parser = ShadowDOMParser(self.page)
    
    def load_page(self):
        """ WebOperator"""
        return self.web_operator.navigate(self.url, self.wait_time)
    
    def close(self):
        """ WebOperator"""
        self.web_operator.close()

    def login(
        self, 
        username,  # 
        password,  # 
        username_selector=None,  # 
        password_selector=None,  # 
        button_selector=None,  # 
        auto_handle_captcha=True  # 
    ):
        log = set_stage(Stage.LOGIN)
        try:
            log.info("")
            
            page_log = set_stage(Stage.PAGE_LOAD)
            success = self.web_operator.navigate(self.url, self.wait_time)
            if not success:
                log.error("")
                return False
            
            # 
            if not (username_selector and password_selector and button_selector):
                element_log = set_stage(Stage.ELEMENT)
                element_log.info("...")
                self.page_extractor.extract_elements()
                
                input_elements = self.page_extractor.get_elements_by_tag('input')
                button_elements = self.page_extractor.get_elements_by_tag('button')
                
                if len(input_elements) < 2:
                    element_log.warning("")
                    return False
                
                if not button_elements:
                    element_log.warning("")
                    return False
                
                username_selector = username_selector or input_elements[0]['selector']
                password_selector = password_selector or input_elements[1]['selector']
                button_selector = button_selector or button_elements[0]['selector']
                
                element_log.success(f": {username_selector}")
                element_log.success(f": {password_selector}")
                element_log.success(f": {button_selector}")
            
            # 
            log.info("...")
            self.web_operator.input_text(username_selector, username)
            self.web_operator.input_text(password_selector, password)
            
            # 
            log.info("...")
            result = self.web_operator.click_element(button_selector)
            
            if not result:
                log.warning("")
                return False
            
            log.success("")
            
            # CaptchaAgent
            if auto_handle_captcha:
                captcha_success = self.captcha_agent.solve_captcha(self.page)
                return captcha_success
            
            return True
        
        except Exception as e:
            log.error(f": {e}")
            log.exception("")
            return False

