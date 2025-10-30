# Mobile 端测试

此目录包含针对移动设备的自动化测试脚本。

## 架构说明

### 基础层：MobileDevice (`src/autoagents_cua/agent/mobile_agent.py`)
提供移动设备的基础操作封装，类似于 `Browser` 类对浏览器的封装。

主要功能：
- 设备连接和管理
- 基础操作：点击、滑动、按键等
- 元素查找和交互
- 截图和界面检测

使用示例：
```python
from autoagents_cua.agent.mobile_agent import MobileDevice

# 连接设备
device = MobileDevice("127.0.0.1:5555")

# 启动应用
device.start_app("com.example.app")

# 点击元素
device.click_element(text="按钮")

# 滑动
device.swipe_up(ratio=0.5)
```

### 应用层：TikTokManager (`src/autoagents_cua/prebuilt/tiktok_manager.py`)
基于 `MobileDevice` 的高层封装，提供 TikTok 特定的自动化操作。

主要功能：
- TikTok 应用管理
- 视频浏览和切换
- 直播间检测和跳过
- 用户交互（点赞、评论、私信等）
- 循环操作自动化

使用示例：
```python
from autoagents_cua.prebuilt.tiktok_manager import TikTokManager

# 创建管理器
manager = TikTokManager()

# 启动应用
manager.start_app()

# 处理弹窗
manager.handle_popups()

# 滚动浏览视频
manager.scroll_to_next_video(force_level="strong")

# 运行循环操作
manager.run_continuous_cycle(cycle_count=10)
```

## 测试文件

### test_cycle_operations.py
测试 TikTok 的循环操作功能。

**循环流程：**
1. 检测是否为直播间（如果是则跳过）
2. 点击创作者头像
3. 点击私信按钮
4. 第一次返回（聊天页面 → 个人主页）
5. 第二次返回（个人主页 → 视频页面）
6. 向下滚轮切换视频

**使用方法：**
```bash
# 无限循环（按 Ctrl+C 停止）
python test_cycle_operations.py

# 指定循环次数
python test_cycle_operations.py 10
```

**参数说明：**
- `cycle_count`: 循环次数，不指定或 ≤ 0 表示无限循环
- 程序会自动检测并跳过直播间
- 连续3次失败后自动停止

## 开发指南

### 创建新的应用管理器

如果要为其他应用创建管理器，建议按照以下步骤：

1. **在 `src/autoagents_cua/prebuilt/` 创建新的管理器类**
   ```python
   from ..agent.mobile_agent import MobileDevice
   
   class MyAppManager:
       def __init__(self, device_address: str = "127.0.0.1:5555"):
           self.device = MobileDevice(device_address)
       
       # 实现应用特定的功能
   ```

2. **在 `src/autoagents_cua/prebuilt/__init__.py` 中导出**
   ```python
   from .my_app_manager import MyAppManager
   __all__ = ['TikTokManager', 'MyAppManager']
   ```

3. **在 `playground/mobile/` 创建测试文件**
   ```python
   from autoagents_cua.prebuilt.my_app_manager import MyAppManager
   # 编写测试代码
   ```

### 最佳实践

1. **基础操作使用 MobileDevice**：所有通用的移动设备操作应该使用 `MobileDevice` 类
2. **应用特定逻辑放在 prebuilt**：针对特定应用的高层逻辑放在 `prebuilt` 目录下的管理器中
3. **测试文件放在 playground/mobile**：所有测试脚本放在 `playground/mobile/` 目录下
4. **使用日志记录**：使用 `from ..utils.logging import logger` 进行日志记录
5. **错误处理**：所有操作都应该有适当的错误处理和返回值检查

## 设备要求

- Android 设备或模拟器
- 已安装 ADB（Android Debug Bridge）
- 设备已开启 USB 调试
- 已安装 uiautomator2：`pip install uiautomator2`

## 常见问题

**Q: 设备连接失败怎么办？**
A: 确保：
- ADB 服务已启动：`adb start-server`
- 设备已连接：`adb devices`
- 设备地址正确（默认：`127.0.0.1:5555`）

**Q: 找不到元素怎么办？**
A: 可以使用 `uiautomator2` 的调试工具：
```python
# 打印当前页面的所有元素
device.device.dump_hierarchy()

# 使用 weditor 可视化调试
# pip install weditor
# weditor
```

**Q: 如何调整操作速度？**
A: 在操作之间添加 `time.sleep()` 来调整等待时间，或修改滑动的 `duration` 参数。

