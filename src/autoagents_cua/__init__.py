"""
AutoAgents CUA - Computer Use Agent for AutoAgents
"""

__version__ = "0.1.0"

# 导出常用的类和函数
from .browser import (
    Browser,
    BrowserFingerprint,
    WebOperator,
    PageExtractor,
    ShadowDOMParser,
    CaptchaAgent,
    GoogleRecaptchaSolver,
)
from .agent import BrowserAgent, TimeTracker, MobileDevice, MobileAgent
from .prebuilt import LoginAgent, TikTokManager
from .client import ChatClient
from .models import ClientConfig, ModelConfig

__all__ = [
    # Browser 相关
    'Browser',
    'BrowserFingerprint',
    'WebOperator', 
    'PageExtractor',
    'ShadowDOMParser',
    'CaptchaAgent',
    'GoogleRecaptchaSolver',
    # Agent 相关
    'BrowserAgent',
    'TimeTracker',
    'MobileDevice',
    'MobileAgent',
    # Prebuilt
    'LoginAgent',
    'TikTokManager',
    # 客户端和配置
    'ChatClient',
    'ClientConfig',
    'ModelConfig',
    # 版本
    '__version__'
]