"""
配置模型 - LLM 客户端和模型配置
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ClientConfig:
    """LLM 客户端配置"""
    base_url: str
    api_key: str
    timeout: Optional[int] = 60
    max_retries: Optional[int] = 3
    
    def __post_init__(self):
        """验证配置"""
        if not self.base_url:
            raise ValueError("base_url 不能为空")
        if not self.api_key:
            raise ValueError("api_key 不能为空")


@dataclass
class ModelConfig:
    """模型配置"""
    name: str
    temperature: float = 0.0
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    
    def __post_init__(self):
        """验证配置"""
        if not self.name:
            raise ValueError("model name 不能为空")
        if not 0 <= self.temperature <= 2:
            raise ValueError("temperature 必须在 0-2 之间")
        if not 0 <= self.top_p <= 1:
            raise ValueError("top_p 必须在 0-1 之间")

