"""
日志配置模块 - 使用 loguru
"""

import sys
from pathlib import Path
from loguru import logger as _logger
from ..models import Stage


class Logger:
    """
    日志管理器
    
    封装 loguru 的日志功能，提供统一的日志接口
    """
    
    def __init__(self):
        """初始化日志管理器"""
        # 移除默认的 handler
        _logger.remove()
        
        # 获取项目根目录
        self.project_root = Path(__file__).parent.parent.parent
        self.log_dir = self.project_root / "logs"
        self.log_dir.mkdir(exist_ok=True)
        
        # 配置默认的 extra 值
        _logger.configure(extra={"stage": Stage.SYSTEM})
        
        # 配置日志格式
        self._setup_handlers()
        
        # 导出 logger 实例
        self.logger = _logger
    
    def _setup_handlers(self):
        """设置日志处理器"""
        # 日志格式
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{extra[stage]}</cyan> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )
        
        # 简化的控制台格式
        console_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <7}</level> | "
            "<cyan>{extra[stage]}</cyan> | "
            "<level>{message}</level>"
        )
        
        # 添加控制台输出 (INFO 及以上级别)
        _logger.add(
            sys.stdout,
            format=console_format,
            level="INFO",
            colorize=True,
            backtrace=True,
            diagnose=True
        )
        
        # 添加日志文件 (DEBUG 及以上级别)
        # 每次运行创建新的日志文件（使用时间戳到秒）
        _logger.add(
            self.log_dir / "{time:YYYY-MM-DD_HH-mm-ss}.log",
            format=log_format,
            level="DEBUG",
            rotation=None,  # 不轮转，每次运行新建文件
            retention="7 days",  # 保留 7 天
            encoding="utf-8",
            backtrace=True,
            diagnose=True
        )
    
    def get_logger(self, name: str = None):
        """
        获取 logger 实例
        
        Args:
            name: logger 名称，通常使用 __name__
            
        Returns:
            logger 实例
        """
        if name:
            return self.logger.bind(name=name)
        return self.logger
    
    def set_stage(self, stage: str):
        """
        设置当前日志阶段
        
        Args:
            stage: 阶段名称，如 Stage.LOGIN, Stage.CAPTCHA 等
            
        Returns:
            绑定了阶段信息的 logger
            
        Example:
            >>> logger_manager = Logger()
            >>> log = logger_manager.set_stage(Stage.LOGIN)
            >>> log.info("开始登录流程")
            # 输出: 17:30:00 | INFO    | 登录操作 | 开始登录流程
        """
        return self.logger.bind(stage=stage)


# 创建全局日志管理器实例
logger_manager = Logger()

# 导出常用的实例和方法
logger = logger_manager.logger
get_logger = logger_manager.get_logger
set_stage = logger_manager.set_stage


# 使用示例
if __name__ == '__main__':
    # 基本使用（默认系统级别阶段）
    logger.debug("这是一条 DEBUG 消息")
    logger.info("这是一条 INFO 消息")
    logger.success("这是一条 SUCCESS 消息")
    logger.warning("这是一条 WARNING 消息")
    logger.error("这是一条 ERROR 消息")
    
    print("\n" + "=" * 80)
    print("使用阶段标记")
    print("=" * 80 + "\n")
    
    # 使用阶段标记
    init_log = set_stage(Stage.INIT)
    init_log.info("系统初始化开始")
    init_log.success("配置加载完成")
    
    login_log = set_stage(Stage.LOGIN)
    login_log.info("开始登录流程")
    login_log.success("用户 admin 登录成功")
    
    captcha_log = set_stage(Stage.CAPTCHA)
    captcha_log.info("检测到验证码")
    captcha_log.success("验证码识别完成")
    
    # 使用 with 上下文（推荐）
    print("\n使用上下文管理器：\n")
    with logger.contextualize(stage=Stage.PAGE_LOAD):
        logger.info("正在加载页面...")
        logger.success("页面加载完成")
    
    # 异常日志
    try:
        1 / 0
    except Exception as e:
        error_log = set_stage(Stage.ERROR)
        error_log.exception("发生异常")

