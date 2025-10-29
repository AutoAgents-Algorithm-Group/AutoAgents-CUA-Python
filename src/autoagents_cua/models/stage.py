"""
日志阶段常量模型
"""


class Stage:
    """日志阶段常量"""
    SYSTEM = "系统级别"         # 系统级别
    INIT = "初始化中"           # 初始化阶段
    PAGE_LOAD = "页面加载"      # 页面加载
    ELEMENT = "元素提取"        # 元素提取
    LOGIN = "登录操作"          # 登录操作
    CAPTCHA = "验证处理"        # 验证码处理
    VALIDATION = "数据校验"     # 数据校验
    CLEANUP = "资源清理"        # 资源清理
    ERROR = "错误处理"          # 错误处理

