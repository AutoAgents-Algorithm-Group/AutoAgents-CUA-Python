"""
Prebuilt 模块 - 预构建的特定应用管理器

提供针对特定应用的高层自动化管理器和登录代理。
"""

from .tiktok_manager import TikTokManager
from .login_agent import LoginAgent

__all__ = ['TikTokManager', 'LoginAgent']

