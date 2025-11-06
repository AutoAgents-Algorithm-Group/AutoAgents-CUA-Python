"""
提示词管理模块

支持从 Markdown 文件加载提示词，并进行变量插入
"""

from pathlib import Path
from typing import Dict, Any


class PromptLoader:
    """提示词加载器"""
    
    def __init__(self):
        """初始化加载器"""
        self.prompts_dir = Path(__file__).parent
        self._cache = {}
    
    def load(self, prompt_path: str, **variables) -> str:
        """
        加载提示词并填充变量
        
        Args:
            prompt_path: 提示词文件路径（相对于 prompts 目录），如 "clarify/generate_question.md"
            **variables: 要插入的变量，如 query="用户任务"
            
        Returns:
            填充变量后的提示词
            
        Example:
            >>> loader = PromptLoader()
            >>> prompt = loader.load("clarify/generate_question.md", query="做报告")
        """
        # 构造完整路径
        full_path = self.prompts_dir / prompt_path
        
        # 检查文件是否存在
        if not full_path.exists():
            raise FileNotFoundError(f"提示词文件不存在: {full_path}")
        
        # 从缓存或文件读取
        if prompt_path not in self._cache:
            with open(full_path, 'r', encoding='utf-8') as f:
                template = f.read()
            self._cache[prompt_path] = template
        else:
            template = self._cache[prompt_path]
        
        # 填充变量（使用 .format() 方法）
        try:
            return template.format(**variables)
        except KeyError as e:
            raise ValueError(f"提示词模板缺少变量: {e}")
    
    def clear_cache(self):
        """清除缓存（用于开发时重新加载提示词）"""
        self._cache.clear()


# 创建全局加载器实例
prompt_loader = PromptLoader()


# 导出
__all__ = ['PromptLoader', 'prompt_loader']


