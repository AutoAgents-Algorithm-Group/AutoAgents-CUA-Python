<div align="center">

<img src="https://img.shields.io/badge/-AutoAgents--CUA-000000?style=for-the-badge&labelColor=faf9f6&color=faf9f6&logoColor=000000" alt="AutoAgents-CUA-Python" width="320"/>

<h4>计算机使用代理 Python SDK</h4>

[English](README.md) | **简体中文**

<a href="https://pypi.org/project/autoagents-cua">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://img.shields.io/pypi/v/autoagents-cua.svg?style=for-the-badge" />
    <img alt="PyPI version" src="https://img.shields.io/pypi/v/autoagents-cua.svg?style=for-the-badge" />
  </picture>
</a>
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="media/dark_license.svg" />
  <img alt="License MIT" src="media/light_license.svg" />
</picture>

</div>

AutoAgents-CUA-Python（计算机使用代理）是一个先进的 AI 驱动浏览器自动化框架，将大语言模型与智能网页自动化能力相结合。基于 DrissionPage 构建，由最先进的 AI 模型驱动，将复杂的网页自动化任务转化为简单、可靠的操作。

## 目录
- [目录](#目录)
- [为什么选择 AutoAgents CUA？](#为什么选择-autoagents-cua)
  - [核心能力](#核心能力)
    - [智能自动化](#智能自动化)
    - [高性能架构](#高性能架构)
    - [开发者体验](#开发者体验)
  - [AutoAgents CUA 能做什么？](#autoagents-cua-能做什么)
  - [技术基础](#技术基础)
- [快速开始](#快速开始)
  - [前提条件](#前提条件)
  - [安装](#安装)
  - [基本使用示例](#基本使用示例)
- [贡献](#贡献)

## 为什么选择 AutoAgents CUA？

AutoAgents CUA（计算机使用代理）是一个先进的浏览器自动化平台，将 AI 智能与强大的网页自动化能力相结合。基于 DrissionPage 构建，由大语言模型驱动，AutoAgents CUA 将复杂的网页自动化任务转化为简单的自然语言驱动操作。

### 核心能力

#### 智能自动化
- **AI 验证码识别**：自动识别和解决图像验证码，准确率超过 90%
- **智能表单检测**：无需手动配置即可自动检测和填写登录表单
- **自适应重试逻辑**：智能重试失败操作，采用指数退避策略
- **自然语言处理**：用简单语言描述您想要自动化的内容

#### 高性能架构
- **10-50 倍速度提升**：基于 JavaScript 的批量提取 vs 传统方法
- **Shadow DOM 支持**：完全支持现代 Web 组件和 Shadow DOM
- **优化网络使用**：最小化浏览器-服务器通信开销
- **生产就绪日志**：全面的分阶段日志系统，便于调试和监控

#### 开发者体验
- **零配置**：使用合理的默认设置立即开始
- **YAML 配置**：针对复杂场景的灵活配置管理
- **模块化设计**：使用单个组件或完整的自动化套件
- **丰富示例**：playground 目录中的即用示例

### AutoAgents CUA 能做什么？

- **自然语言自动化**：使用自然语言命令控制浏览器
- **自动登录**：处理包括双因素认证和验证码在内的复杂登录流程
- **数据提取**：从动态网页中提取结构化数据
- **表单自动化**：跨多个页面填写和提交表单
- **会话管理**：在操作过程中维护认证会话
- **工作流自动化**：将多个操作链接成复杂的工作流

### 技术基础

- **DrissionPage 4.0+**：现代浏览器自动化框架
- **AI 模型**：用于验证码识别的先进视觉模型
- **Python 3.11+**：基于最新 Python 特性构建
- **Loguru**：专业级日志系统

## 快速开始

### 前提条件
- Python 3.11+
- Chrome 浏览器
- Node.js 18+（可选，用于前端功能）

### 安装

```bash
# 1. 克隆仓库
git clone https://github.com/your-org/AutoAgents-CUA-Python.git
cd AutoAgents-CUA-Python

# 2. 安装依赖
pip install -e .

# 3. 设置环境变量
export OPENAI_API_KEY="your-api-key"
export OPENAI_BASE_URL="https://api.openai.com/v1"
export OPENAI_MODEL="gpt-4o"
```

### 基本使用示例

```python
from autoagents_cua.client import ChatClient
from autoagents_cua.models import ClientConfig, ModelConfig
from autoagents_cua.computer import Browser
from autoagents_cua.agent import BrowserAgent
from autoagents_cua.tools import ALL_WEB_TOOLS

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

# 2. 创建 Browser
browser = Browser(
    headless=False,
    window_size={'width': 1000, 'height': 700}
)

# 3. 创建 BrowserAgent
agent = BrowserAgent(
    browser=browser,
    llm=llm,
    tools=ALL_WEB_TOOLS
)

# 4. 使用自然语言执行任务
agent.invoke("请帮我打开谷歌并搜索 'Python 自动化'")
agent.invoke("点击第一个搜索结果")
agent.invoke("提取这个页面的主要内容")

# 5. 清理
agent.close()
```

更多示例请查看 `playground/` 目录。


## 贡献

我们欢迎社区贡献！

1. Fork 仓库
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 Pull Request