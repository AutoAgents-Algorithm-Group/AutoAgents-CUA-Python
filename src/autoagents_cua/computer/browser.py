"""
Browser - 浏览器配置和管理类
"""

from typing import Optional, Dict, Any
from ..utils.web_operator import WebOperator
from ..utils.page_extractor import PageExtractor
from ..utils.logging import logger


class Browser:
    """
    浏览器类 - 封装浏览器配置和操作
    
    使用示例:
        # 基本用法
        browser = Browser(headless=False)
        
        # 自定义窗口大小
        browser = Browser(
            headless=False,
            window_size={'width': 1000, 'height': 700}
        )
        
        # 使用指纹
        browser = Browser(
            headless=False,
            fingerprint_config='mac_chrome'
        )
    """
    
    def __init__(
        self,
        headless: bool = False,
        window_size: Optional[Dict[str, int]] = None,
        fingerprint_config: Optional[Any] = None,
        user_data_dir: Optional[str] = None,
    ):
        """
        初始化浏览器
        
        Args:
            headless: 是否无头模式
            window_size: 窗口大小，格式 {'width': 1000, 'height': 700}
            fingerprint_config: 指纹配置
            user_data_dir: 用户数据目录
        """
        self.headless = headless
        self.window_size = window_size or {'width': 1280, 'height': 720}
        self.fingerprint_config = fingerprint_config
        self.user_data_dir = user_data_dir
        
        # 创建 WebOperator
        self.operator = WebOperator(
            headless=headless,
            fingerprint_config=fingerprint_config,
            user_data_dir=user_data_dir
        )
        
        # 设置窗口大小
        if window_size and not headless:
            try:
                self.operator.page.set.window.size(
                    window_size['width'], 
                    window_size['height']
                )
            except Exception as e:
                logger.warning(f"设置窗口大小失败: {e}")
        
        # 创建 PageExtractor
        self.extractor = PageExtractor(self.operator.page)
        
        logger.success(f"✅ Browser 初始化完成 - {'无头' if headless else '有头'}模式, 窗口大小: {self.window_size['width']}x{self.window_size['height']}")
    
    @property
    def page(self):
        """获取 page 对象"""
        return self.operator.page
    
    def close(self):
        """关闭浏览器"""
        self.operator.close()
        logger.info("🔒 浏览器已关闭")
    
    def __enter__(self):
        """支持 with 语句"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """支持 with 语句"""
        self.close()
    
    def __repr__(self):
        return f"Browser(headless={self.headless}, window_size={self.window_size})"

