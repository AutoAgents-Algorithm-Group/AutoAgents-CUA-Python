# Mobile 移动端自动化

本目录包含所有与移动端（Android）自动化相关的测试和示例。

## 📁 文件结构

```
mobile/
└── test_tiktok.py              # TikTok 自动化测试
```

## 🎯 功能概述

### TikTok 自动化管理器
**文件**: `test_tiktok.py`

完整的 TikTok 应用自动化解决方案，支持：

#### 核心功能
- 📱 **设备连接**: 支持 USB 和 WiFi ADB 连接
- 🚀 **应用管理**: 启动、停止、重启 TikTok
- 🎯 **元素检测**: 智能识别头像、按钮等元素
- 👆 **手势操作**: 点击、滑动、长按等
- 🔄 **循环操作**: 自动化重复任务
- 📊 **统计分析**: 操作成功率和耗时统计
- ⚠️ **错误处理**: 自动重试和错误恢复

#### 自动化循环
```
循环流程：
1. 检测并点击头像
2. 等待页面加载
3. 点击私信按钮
4. 返回到视频页
5. 再次返回到首页
6. 向上滑动切换视频
```

## 🚀 快速开始

### 前置条件

1. **安装 Android 调试工具**
```bash
# macOS
brew install android-platform-tools

# Ubuntu/Debian
sudo apt-get install android-tools-adb

# Windows
# 从 https://developer.android.com/studio/releases/platform-tools 下载
```

2. **安装 Python 依赖**
```bash
pip install uiautomator2
```

3. **连接 Android 设备**
```bash
# USB 连接
adb devices

# WiFi 连接（需要先 USB 连接一次）
adb tcpip 5555
adb connect <设备IP>:5555
```

### 基础使用

#### 1. 简单的 TikTok 操作

```python
from src.autoagents_cua.prebuilt import TikTokManager

# 创建管理器
manager = TikTokManager(device_address="127.0.0.1:5555")

# 启动 TikTok
manager.start_app()

# 处理启动弹窗
manager.handle_popups()

# 执行单次循环
manager.execute_single_cycle()

# 关闭应用
manager.stop_app()
```

#### 2. 连续自动化循环

```python
from src.autoagents_cua.prebuilt import TikTokManager

manager = TikTokManager()

# 启动并准备
manager.start_app()
manager.handle_popups()

# 运行 10 个循环
stats = manager.run_continuous_cycle(
    cycle_count=10,      # 循环次数
    max_errors=3,        # 最大连续错误数
    delay_range=(2, 5)   # 操作间隔（秒）
)

# 查看统计
manager.print_cycle_stats(stats)
```

#### 3. 高级配置

```python
from src.autoagents_cua.prebuilt import TikTokManager
from src.autoagents_cua.agent import MobileDevice

# 自定义设备配置
device = MobileDevice(device_address="192.168.1.100:5555")

# 创建 TikTok 管理器
manager = TikTokManager(device_address="192.168.1.100:5555")

# 自定义操作参数
manager.execute_single_cycle(
    avatar_wait=3.0,      # 点击头像后等待时间
    message_wait=2.0,     # 点击私信后等待时间
    back_wait=1.5,        # 返回后等待时间
    swipe_ratio=0.5       # 滑动距离比例
)
```

## 🔧 核心类说明

### MobileDevice
**位置**: `src/autoagents_cua/agent/mobile_agent.py`

移动设备基础操作类：

```python
from src.autoagents_cua.agent import MobileDevice

device = MobileDevice("127.0.0.1:5555")

# 基础操作
device.start_app("com.zhiliaoapp.musically")
device.click_element(text="按钮")
device.swipe_up(ratio=0.5)
device.press_back()
device.screenshot(save_path="screen.png")

# 获取设备信息
info = device.get_screen_info()
print(f"屏幕尺寸: {info['width']}x{info['height']}")
```

### TikTokManager
**位置**: `src/autoagents_cua/prebuilt/tiktok_manager.py`

TikTok 专用自动化管理器，继承自 `MobileAgent`。

#### 主要方法

| 方法 | 说明 | 参数 |
|------|------|------|
| `start_app()` | 启动 TikTok | - |
| `stop_app()` | 停止 TikTok | - |
| `handle_popups()` | 处理弹窗 | `max_attempts=3` |
| `detect_avatar()` | 检测头像 | `timeout=5` |
| `execute_single_cycle()` | 执行单次循环 | 多个等待参数 |
| `run_continuous_cycle()` | 连续循环 | `cycle_count`, `max_errors` |

## 📊 统计信息

运行循环后可获得详细统计：

```python
stats = manager.run_continuous_cycle(cycle_count=10)

# 统计信息包含：
print(f"总循环数: {stats['total_cycles']}")
print(f"成功: {stats['successful_cycles']}")
print(f"失败: {stats['failed_cycles']}")
print(f"成功率: {stats['success_rate']:.2%}")
print(f"总耗时: {stats['total_time']:.2f}秒")
print(f"平均耗时: {stats['average_time']:.2f}秒/次")
```

## 🎯 实际应用场景

### 1. 数据收集
- 自动浏览视频收集用户反馈
- 统计特定话题的参与度
- 分析推荐算法模式

### 2. 账号运营
- 自动点赞和评论（需扩展）
- 批量关注/取关
- 定时发布内容

### 3. 测试自动化
- UI 测试
- 性能测试
- 稳定性测试

## ⚠️ 注意事项

### 设备要求
- ✅ Android 5.0 及以上
- ✅ 已启用开发者模式和 USB 调试
- ✅ 已安装 TikTok 应用

### 性能优化
```python
# 减少等待时间提高速度
manager.execute_single_cycle(
    avatar_wait=1.0,
    message_wait=1.0,
    back_wait=0.5
)

# 增加等待时间提高稳定性
manager.execute_single_cycle(
    avatar_wait=5.0,
    message_wait=3.0,
    back_wait=2.0
)
```

### 错误处理
```python
import signal
import sys

def signal_handler(sig, frame):
    """优雅退出"""
    print("\n⚠️ 检测到中断信号，正在停止...")
    manager.stop_app()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

try:
    manager.run_continuous_cycle(cycle_count=100)
except Exception as e:
    print(f"❌ 发生错误: {e}")
finally:
    manager.stop_app()
```

## 🔍 调试技巧

### 1. 截图调试
```python
# 在关键步骤截图
manager.device.screenshot(save_path="debug_1.png")
manager.detect_avatar()
manager.device.screenshot(save_path="debug_2.png")
```

### 2. 查看 UI 层次
```bash
# 使用 uiautomator2 自带工具
python -m uiautomator2 init
# 访问 http://localhost:7912 查看实时界面
```

### 3. 日志分析
```python
from src.autoagents_cua.utils.logging import logger

# 详细日志会自动输出到控制台
# 查看特定阶段的日志
logger.debug("调试信息")
logger.info("普通信息")
logger.warning("警告信息")
logger.error("错误信息")
```

## 📝 自定义扩展

### 创建自定义移动端管理器

```python
from src.autoagents_cua.agent import MobileAgent

class CustomAppManager(MobileAgent):
    """自定义应用管理器"""
    
    APP_PACKAGE = "com.example.app"
    
    def __init__(self, device_address="127.0.0.1:5555"):
        super().__init__(device_address)
    
    def start_app(self):
        """启动应用"""
        self.device.start_app(self.APP_PACKAGE)
    
    def custom_operation(self):
        """自定义操作"""
        # 实现你的逻辑
        self.device.click_element(text="按钮")
        self.device.swipe_up()
```

## 📚 相关文档

- [MobileDevice API 文档](../../src/autoagents_cua/agent/mobile_agent.py)
- [TikTokManager 源码](../../src/autoagents_cua/prebuilt/tiktok_manager.py)
- [uiautomator2 官方文档](https://github.com/openatx/uiautomator2)
- [ADB 命令参考](https://developer.android.com/studio/command-line/adb)

## 🤝 贡献

欢迎提交针对其他应用的自动化方案！

支持的应用类型：
- 社交媒体（微博、小红书、Instagram）
- 电商平台（淘宝、京东、Amazon）
- 内容平台（抖音、快手、YouTube）
- 通讯工具（微信、WhatsApp、Telegram）

