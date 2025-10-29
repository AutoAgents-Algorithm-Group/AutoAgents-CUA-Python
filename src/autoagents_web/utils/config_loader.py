"""
配置加载器 - 从 config.yaml 读取配置
"""

import os
import yaml
from typing import Dict, Any, Optional


class ConfigLoader:
    """配置加载器"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置加载器
        
        Args:
            config_path: 配置文件路径，默认为项目根目录的 config.yaml
        """
        if config_path is None:
            # 默认使用项目根目录的 config.yaml
            # 从 src/autoagents_web/utils/config_loader.py 向上 4 层到项目根目录
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            config_path = os.path.join(project_root, 'config.yaml')
            
        
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        加载配置文件
        
        Returns:
            配置字典
        """
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            if config is None:
                config = {}
            
            return config
        except Exception as e:
            raise RuntimeError(f"加载配置文件失败: {e}")
    
    def get_captcha_agent_config(self) -> Dict[str, Any]:
        """
        获取 CaptchaAgent 配置
        
        Returns:
            配置字典，包含 api_key, base_url, model
        """
        captcha_config = self.config.get('captcha_agent', {})
        
        # 支持环境变量覆盖
        return {
            'api_key': os.getenv('CAPTCHA_API_KEY') or captcha_config.get('api_key'),
            'base_url': os.getenv('CAPTCHA_BASE_URL') or captcha_config.get('base_url', 'https://api.openai.com/v1'),
            'model': os.getenv('CAPTCHA_MODEL') or captcha_config.get('model', 'gpt-4o')
        }
    
    def get_autobrowser_agent_config(self) -> Dict[str, Any]:
        """
        获取 AutoBrowserAgent 配置
        
        Returns:
            配置字典，包含 api_key, base_url, model
        """
        autobrowser_config = self.config.get('autobrowser_agent', {})
        
        # 支持环境变量覆盖
        return {
            'api_key': os.getenv('AUTOBROWSER_AGENT_API_KEY') or autobrowser_config.get('api_key'),
            'base_url': os.getenv('AUTOBROWSER_AGENT_API_BASEURL') or autobrowser_config.get('base_url', 'https://api.openai.com/v1'),
            'model': os.getenv('AUTOBROWSER_AGENT_MODEL') or autobrowser_config.get('model', 'gpt-4o')
        }
    
    def get_login_agent_config(self) -> Dict[str, Any]:
        """
        获取 LoginAgent 配置
        
        Returns:
            配置字典，包含 init 和 login 两部分
        """
        login_config = self.config.get('login_agent', {})
        
        # 获取初始化配置
        init_config = login_config.get('init', {})
        login_params = login_config.get('login', {})
        
        return {
            # 初始化参数
            'url': init_config.get('url', ''),
            'headless': init_config.get('headless', False),
            'wait_time': init_config.get('wait_time', 3),
            # 登录参数
            'username': login_params.get('username', ''),
            'password': login_params.get('password', ''),
            'username_selector': login_params.get('username_selector'),
            'password_selector': login_params.get('password_selector'),
            'button_selector': login_params.get('button_selector'),
            'auto_handle_captcha': login_params.get('auto_handle_captcha', True)
        }
    
    def get_login_agent_init_config(self) -> Dict[str, Any]:
        """
        获取 LoginAgent 初始化配置
        
        Returns:
            初始化配置字典
        """
        login_config = self.config.get('login_agent', {})
        init_config = login_config.get('init', {})
        
        return {
            'url': init_config.get('url', ''),
            'headless': init_config.get('headless', False),
            'wait_time': init_config.get('wait_time', 3)
        }
    
    def get_login_agent_login_config(self) -> Dict[str, Any]:
        """
        获取 LoginAgent 登录配置
        
        Returns:
            登录配置字典
        """
        login_config = self.config.get('login_agent', {})
        login_params = login_config.get('login', {})
        
        return {
            'username': login_params.get('username', ''),
            'password': login_params.get('password', ''),
            'username_selector': login_params.get('username_selector'),
            'password_selector': login_params.get('password_selector'),
            'button_selector': login_params.get('button_selector'),
            'auto_handle_captcha': login_params.get('auto_handle_captcha', True)
        }
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        获取指定配置项
        
        Args:
            key: 配置键，支持点号分隔的嵌套键（如 'captcha_agent.model'）
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def reload(self):
        """重新加载配置文件"""
        self.config = self._load_config()
    
    def __repr__(self):
        return f"ConfigLoader(config_path='{self.config_path}')"


# 便捷函数

def load_config(config_path: Optional[str] = None) -> ConfigLoader:
    """
    快速创建配置加载器
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        ConfigLoader 实例
    """
    return ConfigLoader(config_path)


def get_captcha_agent_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    快速获取 CaptchaAgent 配置
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        配置字典
    """
    loader = ConfigLoader(config_path)
    return loader.get_captcha_agent_config()


def get_autobrowser_agent_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    快速获取 AutoBrowserAgent 配置
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        配置字典
    """
    loader = ConfigLoader(config_path)
    return loader.get_autobrowser_agent_config()


def get_login_agent_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    快速获取 LoginAgent 配置
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        配置字典
    """
    loader = ConfigLoader(config_path)
    return loader.get_login_agent_config()