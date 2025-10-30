from .image_converter import encode_image
from .logging import logger, get_logger, set_stage, logger_manager, Logger
from ..models import Stage

# 向后兼容 - 从 browser 模块导入
from ..browser import (
    PageExtractor,
    ShadowDOMParser,
    WebOperator,
    CaptchaAgent,
    GoogleRecaptchaSolver,
)

__all__ = [
    'encode_image', 
    'logger', 
    'get_logger', 
    'set_stage', 
    'logger_manager',
    'Logger',
    'Stage', 
    'PageExtractor', 
    'ShadowDOMParser', 
    'WebOperator',
    'CaptchaAgent',
    'GoogleRecaptchaSolver',
]