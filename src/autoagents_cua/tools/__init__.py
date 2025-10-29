"""
Tools for AutoBrowser Agent

提供独立的工具函数，可以自由组合使用
"""

from .web_tool import (
    # 工具函数
    open_website,
    extract_page_elements,
    click_element,
    input_text_to_element,
    get_current_url,
    go_back,
    refresh_page,
    take_screenshot,
    
    # 工具集合
    BASIC_WEB_TOOLS,
    NAVIGATION_TOOLS,
    UTILITY_TOOLS,
    ALL_WEB_TOOLS,
    
    # 辅助函数
    bind_tools_to_context,
    create_tool_with_context,
)

__all__ = [
    # 工具函数
    'open_website',
    'extract_page_elements',
    'click_element',
    'input_text_to_element',
    'get_current_url',
    'go_back',
    'refresh_page',
    'take_screenshot',
    
    # 工具集合
    'BASIC_WEB_TOOLS',
    'NAVIGATION_TOOLS',
    'UTILITY_TOOLS',
    'ALL_WEB_TOOLS',
    
    # 辅助函数
    'bind_tools_to_context',
    'create_tool_with_context',
]
