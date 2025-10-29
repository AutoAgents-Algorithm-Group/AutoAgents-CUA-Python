"""
AutoAgents CUA - Computer Use Agent for AutoAgents
"""

__version__ = "0.1.0"

# 导出常用的类和函数
from .utils import WebOperator, PageExtractor
from .computer import Browser
from .agent import BrowserAgent, LoginAgent, TimeTracker
from .client import ChatClient
from .models import ClientConfig, ModelConfig

__all__ = [
    'WebOperator', 
    'PageExtractor', 
    'Browser',
    'BrowserAgent',
    'LoginAgent',
    'TimeTracker',
    'ChatClient',
    'ClientConfig',
    'ModelConfig',
    '__version__'
]

