<div align="center">

<img src="https://img.shields.io/badge/-AutoAgents--CUA-000000?style=for-the-badge&labelColor=faf9f6&color=faf9f6&logoColor=000000" alt="AutoAgents-CUA-Python" width="320"/>

<h4>计算机使用代理 Python SDK</h4>

[English](README.md) | **简体中文**

<a href="https://pypi.org/project/autoagents-cua">
  <img alt="PyPI version" src="https://img.shields.io/pypi/v/autoagents-cua.svg?style=for-the-badge" />
</a>
<a href="LICENSE">
  <img alt="License MIT" src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" />
</a>

</div>

AutoAgents-CUA-Python（计算机使用代理）是一个先进的 AI 驱动自动化框架，将大语言模型与智能浏览器和移动端自动化能力相结合。基于 DrissionPage 和 uiautomator2 构建，将复杂的自动化任务转化为简单、可靠的操作。

## 目录
- [目录](#目录)
- [为什么选择 AutoAgents CUA？](#为什么选择-autoagents-cua)
  - [核心能力](#核心能力)
    - [智能自动化](#智能自动化)
    - [高性能架构](#高性能架构)
    - [开发者体验](#开发者体验)
  - [AutoAgents CUA 能做什么？](#autoagents-cua-能做什么)
  - [技术基础](#技术基础)
- [项目架构](#项目架构)
  - [模块结构](#模块结构)
  - [分层设计](#分层设计)
- [快速开始](#快速开始)
  - [前提条件](#前提条件)
  - [安装](#安装)
  - [基本使用示例](#基本使用示例)
    - [浏览器自动化](#浏览器自动化)
    - [自动登录与验证码](#自动登录与验证码)
    - [移动端自动化（TikTok）](#移动端自动化tiktok)
- [高级功能](#高级功能)
  - [浏览器指纹](#浏览器指纹)
  - [验证码识别](#验证码识别)
  - [移动设备控制](#移动设备控制)
- [贡献](#贡献)

## 为什么选择 AutoAgents CUA？

AutoAgents CUA（计算机使用代理）是一个先进的自动化平台，将 AI 智能与强大的浏览器和移动端自动化能力相结合。基于 DrissionPage 和 uiautomator2 构建，由大语言模型驱动，AutoAgents CUA 将复杂的自动化任务转化为简单的自然语言驱动操作。

### 核心能力

#### 智能自动化
- **AI 验证码识别**：自动识别和解决图像验证码，准确率超过 90%
- **智能表单检测**：无需手动配置即可自动检测和填写登录表单
- **自适应重试逻辑**：智能重试失败操作，采用指数退避策略
- **自然语言处理**：用简单语言描述您想要自动化的内容
- **移动应用自动化**：通过智能手势识别控制 Android 应用

#### 高性能架构
- **10-50 倍速度提升**：基于 JavaScript 的批量提取 vs 传统方法
- **Shadow DOM 支持**：完全支持现代 Web 组件和 Shadow DOM
- **优化网络使用**：最小化浏览器-服务器通信开销
- **生产就绪日志**：全面的分阶段日志系统，便于调试和监控
- **模块化设计**：清晰的关注点分离，独立可复用的模块

#### 开发者体验
- **零配置**：使用合理的默认设置立即开始
- **模块化架构**：使用单个组件或完整的自动化套件
- **类型提示**：完整的类型注解支持，更好的 IDE 集成
- **丰富示例**：playground 目录中的即用示例
- **向后兼容**：旧的导入路径仍然有效，平滑迁移

### AutoAgents CUA 能做什么？

**网页自动化：**
- 使用 AI 进行自然语言浏览器控制
- 处理双因素认证和验证码的自动登录
- 从动态网页中提取数据
- 跨多个页面的表单自动化
- 会话管理和工作流自动化

**移动端自动化：**
- Android 应用控制和自动化
- TikTok 视频交互自动化
- 元素检测和手势模拟
- 截图分析和对比

**预构建解决方案：**
- LoginAgent 用于自动网页登录
- TikTokManager 用于 TikTok 自动化
- 可扩展的自定义应用

### 技术基础

- **DrissionPage 4.0+**：现代浏览器自动化框架
- **uiautomator2**：Android 自动化框架
- **AI 模型**：用于验证码识别的先进视觉模型
- **Python 3.11+**：基于最新 Python 特性构建
- **Loguru**：专业级日志系统

## 项目架构

### 模块结构

```
autoagents_cua/
├── browser/              # 浏览器自动化核心
│   ├── Browser           # 浏览器管理
│   ├── WebOperator       # 网页操作
│   ├── PageExtractor     # 元素提取
│   ├── ShadowDOMParser   # Shadow DOM 解析
│   ├── CaptchaAgent      # 验证码识别
│   └── BrowserFingerprint # 反检测指纹
│
├── agent/                # 智能代理
│   ├── BrowserAgent      # AI 驱动的浏览器代理
│   ├── MobileDevice      # 移动设备控制
│   └── MobileAgent       # AI 驱动的移动代理
│
├── prebuilt/             # 开箱即用的管理器
│   ├── LoginAgent        # 自动网页登录
│   └── TikTokManager     # TikTok 自动化
│
├── client/               # LLM 客户端
│   └── ChatClient        # AI 模型集成
│
├── tools/                # 工具函数
└── utils/                # 实用工具
```

### 分层设计

```
┌─────────────────────────────────────────────────┐
│       Prebuilt 层 (LoginAgent, TikTok)          │
│              开箱即用的解决方案                  │
└─────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────┐
│    Agent 层 (BrowserAgent, MobileAgent)         │
│           AI 驱动的智能代理                      │
└─────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────┐
│    Browser/Mobile 层 (核心功能)                 │
│     浏览器操作 & 移动端控制                      │
└─────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────┐
│         Utils 层 (日志、工具)                    │
│            基础设施 & 实用工具                   │
└─────────────────────────────────────────────────┘
```

## 快速开始

### 前提条件
- Python 3.11+
- Chrome 浏览器（用于网页自动化）
- 带 ADB 的 Android 设备/模拟器（用于移动端自动化）
- Node.js 18+（可选，用于前端功能）

### 安装

```bash
# 1. 克隆仓库
git clone https://github.com/your-org/AutoAgents-CUA-Python.git
cd AutoAgents-CUA-Python

# 2. 安装依赖
pip install -e .
```

### 基本使用示例

#### 浏览器自动化

```python
from autoagents_cua import Browser, BrowserAgent
from autoagents_cua.client import ChatClient
from autoagents_cua.models import ClientConfig, ModelConfig

# 1. 创建 LLM 客户端
llm = ChatClient(
    client_config=ClientConfig(
        base_url="https://api.openai.com/v1",
        api_key="your-api-key"
    ),
    model_config=ModelConfig(
        name="gpt-4o",
        temperature=0.0
    )
)

# 2. 创建带指纹的浏览器
browser = Browser(
    headless=False,
    use_fingerprint=True,  # 反检测
    window_size={'width': 1000, 'height': 700}
)

# 3. 创建 BrowserAgent
agent = BrowserAgent(browser=browser, llm=llm)

# 4. 使用自然语言执行任务
agent.invoke("请帮我打开谷歌并搜索 'Python 自动化'")
agent.invoke("点击第一个搜索结果")
agent.invoke("提取这个页面的主要内容")

# 5. 清理
agent.close()
```

#### 自动登录与验证码

```python
from autoagents_cua.prebuilt import LoginAgent
from autoagents_cua.browser import CaptchaAgent

# 1. 创建验证码识别器
captcha_agent = CaptchaAgent(
    api_key="your-api-key",
    base_url="https://api.openai.com/v1",
    model="gpt-4o"
)

# 2. 创建 LoginAgent
login_agent = LoginAgent(
    url="https://example.com/login",
    captcha_agent=captcha_agent,
    headless=False
)

# 3. 自动登录并处理验证码
success = login_agent.login(
    username="your-username",
    password="your-password",
    auto_handle_captcha=True  # 自动解决验证码
)

if success:
    print("✅ 登录成功！")
```

#### 移动端自动化（TikTok）

```python
from autoagents_cua.prebuilt import TikTokManager

# 1. 创建 TikTok 管理器
manager = TikTokManager(device_address="127.0.0.1:5555")

# 2. 启动应用并处理弹窗
manager.start_app()
manager.handle_popups()

# 3. 运行自动化循环
# 循环：点击头像 → 私信 → 返回 → 返回 → 滚动
manager.run_continuous_cycle(
    cycle_count=10,  # 运行 10 个循环
    max_errors=3     # 连续 3 次错误后停止
)

# 查看统计
manager.print_cycle_stats(stats)
```

## 高级功能

### 浏览器指纹

```python
from autoagents_cua.browser import Browser, BrowserFingerprint

# 生成随机指纹
fingerprint = BrowserFingerprint.generate_random_fingerprint()

# 创建带自定义指纹的浏览器
browser = Browser(
    headless=False,
    use_fingerprint=True,
    fingerprint_preset='windows_chrome'  # 或自定义指纹
)
```

### 验证码识别

```python
from autoagents_cua.browser import CaptchaAgent

# 创建验证码代理
agent = CaptchaAgent(
    api_key="your-api-key",
    model="gpt-4o"
)

# 在页面上解决验证码
success = agent.solve_captcha(
    page=page,
    captcha_selector='css:.captcha-container',
    max_retries=3
)
```

### 移动设备控制

```python
from autoagents_cua.agent import MobileDevice

# 连接设备
device = MobileDevice("127.0.0.1:5555")

# 基础操作
device.start_app("com.example.app")
device.click_element(text="按钮")
device.swipe_up(ratio=0.5)
device.screenshot(save_path="screenshot.png")
```

更多示例请查看 `playground/` 目录：
- `playground/agent/` - BrowserAgent 示例
- `playground/mobile/` - 移动端自动化示例
- `playground/page_test/` - 网页自动化示例

## 贡献

我们欢迎社区贡献！

1. Fork 仓库
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。
