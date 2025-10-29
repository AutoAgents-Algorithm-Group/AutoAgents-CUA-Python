"""
聊天客户端 - 封装 LLM 调用
"""

from typing import Optional, Any
from langchain_openai import ChatOpenAI
from langchain_core.callbacks import BaseCallbackHandler, CallbackManager
from ..models.config import ClientConfig, ModelConfig
from ..utils.logging import logger


class TokenUsageCallback(BaseCallbackHandler):
    """Token使用情况追踪回调类"""
    
    def __init__(self):
        super().__init__()
        self.total_tokens = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0
    
    def reset(self):
        """重置统计"""
        self.total_tokens = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0
    
    def on_llm_end(self, response: Any, **kwargs: Any) -> None:
        """LLM调用结束时的回调"""
        try:
            # 从 llm_output 中提取 token usage（LangChain/OpenAI 标准位置）
            if hasattr(response, 'llm_output') and response.llm_output:
                llm_output = response.llm_output
                if isinstance(llm_output, dict) and 'token_usage' in llm_output:
                    usage = llm_output['token_usage']
                    if isinstance(usage, dict):
                        self.total_tokens += usage.get('total_tokens', 0)
                        self.prompt_tokens += usage.get('prompt_tokens', 0)
                        self.completion_tokens += usage.get('completion_tokens', 0)
                        logger.debug(f"✅ 累积token: 本次 {usage.get('total_tokens', 0)} | 累计 {self.total_tokens} total tokens")
                        return
            
            logger.debug("⚠️  未找到 token_usage 信息")
                
        except Exception as e:
            logger.debug(f"⚠️  提取token信息时出错: {e}")
            import traceback
            logger.debug(traceback.format_exc())
    
    def get_summary(self):
        """获取token使用摘要"""
        return {
            'total_tokens': self.total_tokens,
            'prompt_tokens': self.prompt_tokens,
            'completion_tokens': self.completion_tokens
        }


class ChatClient:
    """
    聊天客户端 - 封装 LLM 调用逻辑
    
    使用示例：
        client_config = ClientConfig(
            base_url="https://api.openai.com/v1",
            api_key="sk-xxx"
        )
        model_config = ModelConfig(
            name="gpt-4o",
            temperature=0.0
        )
        
        llm = ChatClient(
            client_config=client_config,
            model_config=model_config
        )
    """
    
    def __init__(
        self, 
        client_config: ClientConfig,
        model_config: ModelConfig,
        enable_token_tracking: bool = True
    ):
        """
        初始化聊天客户端
        
        Args:
            client_config: 客户端配置
            model_config: 模型配置
            enable_token_tracking: 是否启用 token 追踪
        """
        self.client_config = client_config
        self.model_config = model_config
        self.enable_token_tracking = enable_token_tracking
        
        # 初始化 token 追踪
        self.token_callback = None
        if enable_token_tracking:
            self.token_callback = TokenUsageCallback()
            self.callback_manager = CallbackManager([self.token_callback])
        else:
            self.callback_manager = None
        
        # 创建 LLM 实例
        self._llm = self._create_llm()
        
        logger.success(f"✅ ChatClient 初始化完成 - 模型: {model_config.name}")
    
    def _create_llm(self) -> ChatOpenAI:
        """创建 LangChain LLM 实例"""
        kwargs = {
            'base_url': self.client_config.base_url,
            'api_key': self.client_config.api_key,
            'model': self.model_config.name,
            'temperature': self.model_config.temperature,
            'model_kwargs': {
                'top_p': self.model_config.top_p,
                'frequency_penalty': self.model_config.frequency_penalty,
                'presence_penalty': self.model_config.presence_penalty,
            },
            'timeout': self.client_config.timeout,
            'max_retries': self.client_config.max_retries,
        }
        
        # 添加 max_tokens（如果设置）
        if self.model_config.max_tokens is not None:
            kwargs['max_tokens'] = self.model_config.max_tokens
        
        # 添加回调（如果启用）
        if self.callback_manager:
            kwargs['callbacks'] = self.callback_manager
        
        return ChatOpenAI(**kwargs)
    
    @property
    def llm(self) -> ChatOpenAI:
        """获取 LLM 实例"""
        return self._llm
    
    def get_token_usage(self) -> dict:
        """
        获取 token 使用情况
        
        Returns:
            包含 total_tokens, prompt_tokens, completion_tokens 的字典
        """
        if self.token_callback:
            return self.token_callback.get_summary()
        return {
            'total_tokens': 0,
            'prompt_tokens': 0,
            'completion_tokens': 0
        }
    
    def reset_token_usage(self):
        """重置 token 使用统计"""
        if self.token_callback:
            self.token_callback.reset()
    
    def __repr__(self):
        return f"ChatClient(model={self.model_config.name}, base_url={self.client_config.base_url})"

