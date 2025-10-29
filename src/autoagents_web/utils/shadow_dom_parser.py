from time import sleep
from .logging import logger


class ShadowDOMParser:  
    def __init__(self, page):

        self.page = page
        logger.info("Shadow DOM 解析器已初始化")
    
    # ========== 私有方法 ==========
    
    def _find_element(self, host_selector, element_selector):
        """
        查找 Shadow DOM 中的元素
        
        Args:
            host_selector: Shadow host 的选择器（例如：'css:faceplate-text-input#login-username'）
            element_selector: Shadow DOM 内部元素的选择器（例如：'css:input[name="username"]'）
        
        Returns:
            找到的元素对象，未找到返回 None
        """
        try:
            # 1. 定位 shadow host
            host = self.page.ele(host_selector, timeout=2)
            if not host:
                logger.warning(f"未找到 Shadow host: {host_selector}")
                return None
            
            # 2. 进入 shadowRoot
            shadow_root = host.shadow_root
            if not shadow_root:
                logger.warning(f"Shadow host 没有 shadow_root: {host_selector}")
                return None
            
            # 3. 在 shadowRoot 中查找元素
            element = shadow_root.ele(element_selector, timeout=2)
            if not element:
                logger.warning(f"在 Shadow DOM 中未找到元素: {element_selector}")
                return None
            
            return element
            
        except Exception as e:
            logger.error(f"查找元素失败: {e}")
            return None
    
    # ========== 公共方法 ==========
    
    def input_text(self, host_selector, element_selector, text, clear=True):
        """
        在 Shadow DOM 的输入框中输入文本
        
        Args:
            host_selector: Shadow host 的选择器
            element_selector: 输入框的选择器
            text: 要输入的文本
            clear: 是否先清空输入框
        
        Returns:
            是否成功
        """
        try:
            element = self._find_element(host_selector, element_selector)
            if not element:
                return False
            
            if clear:
                element.clear()
            
            element.input(text)
            logger.success(f"已在 Shadow DOM 元素中输入: {text}")
            return True
            
        except Exception as e:
            logger.error(f"输入失败: {e}")
            return False
    
    def click_element(self, host_selector, element_selector, wait_after=1):
        """
        点击 Shadow DOM 中的元素
        
        Args:
            host_selector: Shadow host 的选择器
            element_selector: 要点击的元素选择器
            wait_after: 点击后等待时间（秒）
        
        Returns:
            是否成功
        """
        try:
            element = self._find_element(host_selector, element_selector)
            if not element:
                return False
            
            element.click()
            logger.success(f"已点击 Shadow DOM 元素")
            
            if wait_after > 0:
                sleep(wait_after)
            
            return True
            
        except Exception as e:
            logger.error(f"点击失败: {e}")
            return False
    
    def get_element_text(self, host_selector, element_selector):
        """
        获取 Shadow DOM 元素的文本
        
        Args:
            host_selector: Shadow host 选择器
            element_selector: 元素选择器
        
        Returns:
            元素文本，失败返回 None
        """
        try:
            element = self._find_element(host_selector, element_selector)
            if element:
                return element.text
            return None
        except Exception as e:
            logger.error(f"获取元素文本失败: {e}")
            return None