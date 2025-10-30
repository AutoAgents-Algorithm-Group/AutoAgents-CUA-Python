"""
Mobile Agent - 移动端基础操作封装

提供与 uiautomator2 设备的基础交互功能，类似于 Browser 类对浏览器的封装。
"""

import uiautomator2 as u2
import time
import hashlib
from typing import Optional, Dict, List, Tuple
from PIL import Image

from ..utils.logging import logger


class MobileDevice:
    """移动设备基础操作类"""
    
    def __init__(self, device_address: str = "127.0.0.1:5555"):
        """
        初始化移动设备连接
        
        Args:
            device_address: 设备地址，默认为本地模拟器
        """
        self.device_address = device_address
        self.device: Optional[u2.Device] = None
        self.screen_width = 0
        self.screen_height = 0
        self.is_connected = False
        
        # 连接设备
        self._connect()
    
    def _connect(self) -> bool:
        """连接到设备"""
        try:
            logger.info(f"正在连接设备: {self.device_address}")
            self.device = u2.connect(self.device_address)
            
            # 获取设备信息
            device_info = self.device.info
            self.screen_width = device_info['displayWidth']
            self.screen_height = device_info['displayHeight']
            
            logger.info(
                f"设备连接成功: {device_info.get('deviceName', 'Unknown')}, "
                f"屏幕尺寸: {self.screen_width} x {self.screen_height}"
            )
            
            self.is_connected = True
            return True
            
        except Exception as e:
            logger.error(f"设备连接失败: {e}")
            self.is_connected = False
            return False
    
    def reconnect(self) -> bool:
        """重新连接设备"""
        logger.info("尝试重新连接设备...")
        return self._connect()
    
    def start_app(self, package_name: str, wait_time: float = 3.0) -> bool:
        """
        启动应用
        
        Args:
            package_name: 应用包名
            wait_time: 启动后等待时间（秒）
        """
        try:
            logger.info(f"启动应用: {package_name}")
            self.device.app_start(package_name)
            time.sleep(wait_time)
            logger.info("应用启动成功")
            return True
        except Exception as e:
            logger.error(f"启动应用失败: {e}")
            return False
    
    def stop_app(self, package_name: str) -> bool:
        """
        停止应用
        
        Args:
            package_name: 应用包名
        """
        try:
            logger.info(f"停止应用: {package_name}")
            self.device.app_stop(package_name)
            return True
        except Exception as e:
            logger.error(f"停止应用失败: {e}")
            return False
    
    def click(self, x: int, y: int) -> bool:
        """
        点击坐标位置
        
        Args:
            x: X坐标
            y: Y坐标
        """
        try:
            self.device.click(x, y)
            logger.debug(f"点击坐标: ({x}, {y})")
            return True
        except Exception as e:
            logger.error(f"点击失败: {e}")
            return False
    
    def swipe(
        self, 
        start_x: int, 
        start_y: int, 
        end_x: int, 
        end_y: int, 
        duration: float = 0.5
    ) -> bool:
        """
        滑动操作
        
        Args:
            start_x: 起始X坐标
            start_y: 起始Y坐标
            end_x: 结束X坐标
            end_y: 结束Y坐标
            duration: 滑动持续时间（秒）
        """
        try:
            self.device.swipe(start_x, start_y, end_x, end_y, duration=duration)
            logger.debug(f"滑动: ({start_x}, {start_y}) → ({end_x}, {end_y})")
            return True
        except Exception as e:
            logger.error(f"滑动失败: {e}")
            return False
    
    def swipe_up(self, ratio: float = 0.5, duration: float = 0.5) -> bool:
        """
        向上滑动
        
        Args:
            ratio: 滑动距离占屏幕高度的比例
            duration: 滑动持续时间（秒）
        """
        center_x = self.screen_width // 2
        start_y = int(self.screen_height * (0.5 + ratio / 2))
        end_y = int(self.screen_height * (0.5 - ratio / 2))
        return self.swipe(center_x, start_y, center_x, end_y, duration)
    
    def swipe_down(self, ratio: float = 0.5, duration: float = 0.5) -> bool:
        """
        向下滑动
        
        Args:
            ratio: 滑动距离占屏幕高度的比例
            duration: 滑动持续时间（秒）
        """
        center_x = self.screen_width // 2
        start_y = int(self.screen_height * (0.5 - ratio / 2))
        end_y = int(self.screen_height * (0.5 + ratio / 2))
        return self.swipe(center_x, start_y, center_x, end_y, duration)
    
    def swipe_left(self, ratio: float = 0.5, duration: float = 0.5) -> bool:
        """
        向左滑动
        
        Args:
            ratio: 滑动距离占屏幕宽度的比例
            duration: 滑动持续时间（秒）
        """
        center_y = self.screen_height // 2
        start_x = int(self.screen_width * (0.5 + ratio / 2))
        end_x = int(self.screen_width * (0.5 - ratio / 2))
        return self.swipe(start_x, center_y, end_x, center_y, duration)
    
    def swipe_right(self, ratio: float = 0.5, duration: float = 0.5) -> bool:
        """
        向右滑动
        
        Args:
            ratio: 滑动距离占屏幕宽度的比例
            duration: 滑动持续时间（秒）
        """
        center_y = self.screen_height // 2
        start_x = int(self.screen_width * (0.5 - ratio / 2))
        end_x = int(self.screen_width * (0.5 + ratio / 2))
        return self.swipe(start_x, center_y, end_x, center_y, duration)
    
    def press_back(self) -> bool:
        """按返回键"""
        try:
            self.device.press("back")
            logger.debug("按下返回键")
            return True
        except Exception as e:
            logger.error(f"按返回键失败: {e}")
            return False
    
    def press_home(self) -> bool:
        """按Home键"""
        try:
            self.device.press("home")
            logger.debug("按下Home键")
            return True
        except Exception as e:
            logger.error(f"按Home键失败: {e}")
            return False
    
    def screenshot(self, save_path: Optional[str] = None) -> Optional[Image.Image]:
        """
        截图
        
        Args:
            save_path: 保存路径，如果不指定则不保存
            
        Returns:
            PIL Image 对象
        """
        try:
            img = self.device.screenshot()
            if save_path:
                img.save(save_path)
                logger.info(f"截图已保存: {save_path}")
            return img
        except Exception as e:
            logger.error(f"截图失败: {e}")
            return None
    
    def get_screenshot_hash(self) -> Optional[str]:
        """
        获取当前屏幕截图的哈希值，用于检测界面变化
        
        Returns:
            截图的MD5哈希值（前8位）
        """
        try:
            img = self.screenshot()
            if img:
                return hashlib.md5(img.tobytes()).hexdigest()[:8]
        except Exception as e:
            logger.error(f"获取截图哈希失败: {e}")
        return None
    
    def find_element(
        self, 
        text: Optional[str] = None,
        text_contains: Optional[str] = None,
        resource_id: Optional[str] = None,
        class_name: Optional[str] = None,
        description: Optional[str] = None,
        timeout: float = 10.0
    ) -> Optional[u2.UiObject]:
        """
        查找元素
        
        Args:
            text: 精确文本匹配
            text_contains: 文本包含匹配
            resource_id: 资源ID
            class_name: 类名
            description: 描述
            timeout: 超时时间（秒）
            
        Returns:
            找到的元素对象，未找到返回None
        """
        try:
            selector = {}
            if text:
                selector['text'] = text
            elif text_contains:
                selector['textContains'] = text_contains
            if resource_id:
                selector['resourceId'] = resource_id
            if class_name:
                selector['className'] = class_name
            if description:
                selector['description'] = description
            
            element = self.device(**selector)
            if element.exists(timeout=timeout):
                return element
        except Exception as e:
            logger.error(f"查找元素失败: {e}")
        return None
    
    def click_element(
        self,
        text: Optional[str] = None,
        text_contains: Optional[str] = None,
        resource_id: Optional[str] = None,
        class_name: Optional[str] = None,
        timeout: float = 10.0
    ) -> bool:
        """
        查找并点击元素
        
        Args:
            text: 精确文本匹配
            text_contains: 文本包含匹配
            resource_id: 资源ID
            class_name: 类名
            timeout: 超时时间（秒）
        """
        element = self.find_element(
            text=text,
            text_contains=text_contains,
            resource_id=resource_id,
            class_name=class_name,
            timeout=timeout
        )
        if element:
            try:
                element.click()
                logger.debug(f"点击元素成功: text={text}, resource_id={resource_id}")
                return True
            except Exception as e:
                logger.error(f"点击元素失败: {e}")
        return False
    
    def get_text(
        self,
        text: Optional[str] = None,
        text_contains: Optional[str] = None,
        resource_id: Optional[str] = None,
        class_name: Optional[str] = None,
        timeout: float = 10.0
    ) -> Optional[str]:
        """
        获取元素文本
        
        Args:
            text: 精确文本匹配
            text_contains: 文本包含匹配
            resource_id: 资源ID
            class_name: 类名
            timeout: 超时时间（秒）
            
        Returns:
            元素文本，未找到返回None
        """
        element = self.find_element(
            text=text,
            text_contains=text_contains,
            resource_id=resource_id,
            class_name=class_name,
            timeout=timeout
        )
        if element:
            try:
                return element.get_text()
            except Exception as e:
                logger.error(f"获取文本失败: {e}")
        return None
    
    def wait_for_element(
        self,
        text: Optional[str] = None,
        text_contains: Optional[str] = None,
        resource_id: Optional[str] = None,
        timeout: float = 10.0
    ) -> bool:
        """
        等待元素出现
        
        Args:
            text: 精确文本匹配
            text_contains: 文本包含匹配
            resource_id: 资源ID
            timeout: 超时时间（秒）
        """
        element = self.find_element(
            text=text,
            text_contains=text_contains,
            resource_id=resource_id,
            timeout=timeout
        )
        return element is not None
    
    def get_current_activity(self) -> Optional[str]:
        """获取当前Activity"""
        try:
            info = self.device.app_current()
            return info.get('activity')
        except Exception as e:
            logger.error(f"获取当前Activity失败: {e}")
            return None
    
    def get_current_package(self) -> Optional[str]:
        """获取当前应用包名"""
        try:
            info = self.device.app_current()
            return info.get('package')
        except Exception as e:
            logger.error(f"获取当前包名失败: {e}")
            return None
    
    def is_app_running(self, package_name: str) -> bool:
        """
        检查应用是否在运行
        
        Args:
            package_name: 应用包名
        """
        try:
            return self.device.app_wait(package_name, front=True, timeout=1)
        except:
            return False


class MobileAgent:
    """
    Mobile Agent - 移动端智能操作代理
    
    提供对移动设备的高级操作封装，类似于 BrowserAgent
    """
    
    def __init__(self, device: MobileDevice):
        """
        初始化 Mobile Agent
        
        Args:
            device: MobileDevice 实例
        """
        self.device = device
    
    def execute_task(self, task_description: str) -> Dict:
        """
        执行任务（预留接口，可以后续集成LLM）
        
        Args:
            task_description: 任务描述
            
        Returns:
            执行结果字典
        """
        # TODO: 集成 LLM 进行智能任务执行
        raise NotImplementedError("该功能尚未实现，请使用 MobileDevice 的基础操作方法")

