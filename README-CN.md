<div align="center">

<img src="https://img.shields.io/badge/-Mikeno-000000?style=for-the-badge&labelColor=faf9f6&color=faf9f6&logoColor=000000" alt="Mikeno" width="280"/>

<h4>AI 驱动的智能浏览器自动化平台</h4>

[English](README.md) | **简体中文**

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="media/dark_license.svg" />
  <img alt="License AGPL-3.0" src="media/light_license.svg" />
</picture>

</div>

以维龙加山脉中最具挑战性的米凯诺峰命名，这个平台代表了浏览器自动化技术的巅峰 - 强大、智能，能够征服最复杂的网页自动化挑战。

## 目录
- [目录](#目录)
- [为什么选择 Mikeno？](#为什么选择-mikeno)
  - [核心能力](#核心能力)
    - [智能自动化](#智能自动化)
    - [高性能架构](#高性能架构)
    - [开发者体验](#开发者体验)
  - [Mikeno 能做什么？](#mikeno-能做什么)
  - [技术基础](#技术基础)
- [快速开始](#快速开始)
  - [前提条件](#前提条件)
  - [使用 setup.sh 自动安装（推荐）](#使用-setupsh-自动安装推荐)
  - [手动安装（备选方案）](#手动安装备选方案)
  - [基本使用示例（SDK 模式）](#基本使用示例sdk-模式)
- [部署](#部署)
  - [Docker 部署（推荐）](#docker-部署推荐)
  - [环境配置](#环境配置)
  - [生产部署](#生产部署)
  - [故障排除](#故障排除)
- [项目结构](#项目结构)
- [核心组件](#核心组件)
  - [LoginAgent](#loginagent)
  - [CaptchaAgent](#captchaagent)
  - [WebOperator](#weboperator)
  - [PageExtractor](#pageextractor)
  - [ShadowDOMParser](#shadowdomparser)
- [性能指标](#性能指标)
- [贡献](#贡献)
  - [开发指南](#开发指南)
- [安全提示](#安全提示)
- [许可证](#许可证)
- [致谢](#致谢)

## 为什么选择 Mikeno？

Mikeno 是一个先进的浏览器自动化平台，将 AI 智能与强大的网页自动化能力相结合。基于 DrissionPage 构建，由 AI 模型驱动，Mikeno 将复杂的网页自动化任务转化为简单、可靠的操作。

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

### Mikeno 能做什么？

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

### 使用 setup.sh 自动安装（推荐）

最简单的 Mikeno 启动方式：

```bash
# 1. 克隆仓库
git clone https://github.com/your-org/Mikeno.git
cd Mikeno

# 2. 使脚本可执行并运行
chmod +x setup.sh
./setup.sh

# 3. 配置您的 API 密钥
# 编辑 backend/config.yaml 添加您的 API 凭据

# 4. 运行示例自动化
cd backend
python playground/test_login_agent.py
```

### 手动安装（备选方案）

```bash
# 克隆并进入目录
git clone https://github.com/your-org/Mikeno.git
cd Mikeno

# 安装后端依赖
cd backend
pip install -r requirements.txt

# 配置 API 密钥
cp config.yaml.example config.yaml
# 编辑 config.yaml 添加您的凭据

# 运行测试
python playground/test_login_agent.py
```

### 基本使用示例（SDK 模式）

```python
from src.autoagents_cua.utils import LoginAgent, CaptchaAgent

# 初始化 CaptchaAgent（直接传入配置）
captcha_agent = CaptchaAgent(
    api_key="your-api-key",
    base_url="https://api.openai.com/v1",
    model="gpt-4o"
)

# 初始化 LoginAgent（直接传入配置）
login_agent = LoginAgent(
    url="https://example.com/login",
    captcha_agent=captcha_agent,
    headless=False,
    wait_time=3
)

# 执行自动登录
success = login_agent.login(
    username='your_username',
    password='your_password',
    username_selector='xpath://input[@name="username"]',
    password_selector='xpath://input[@name="password"]',
    button_selector='xpath://button[@type="submit"]',
    auto_handle_captcha=True
)

if success:
    print("登录成功！")
    
login_agent.close()
```

更多示例请查看 [SDK_USAGE.md](SDK_USAGE.md)

## 部署

### Docker 部署（推荐）

```bash
cd Mikeno
docker compose -f docker/docker-compose.yml up -d
```

### 环境配置

创建 `backend/config.yaml`：

```yaml
# 验证码识别配置
captcha_agent:
  api_key: "your-api-key"
  base_url: "https://api.example.com/v1"
  model: "gemini-2.5-pro"

# 登录自动化配置
login_agent:
  url: "https://example.com/login"
  username: "your_username"
  password: "your_password"
  headless: false
  wait_time: 3
  auto_handle_captcha: true
```

### 生产部署

```bash
# 构建生产镜像
docker build -t mikeno-prod -f docker/Dockerfile .

# 使用生产设置运行
docker run -d \
  --name mikeno \
  -v $(pwd)/backend/config.yaml:/app/config.yaml \
  -v $(pwd)/backend/logs:/app/logs \
  mikeno-prod
```

### 故障排除

```bash
# 查看应用程序日志
docker compose -f docker/docker-compose.yml logs -f app

# 检查容器状态
docker compose -f docker/docker-compose.yml ps

# 重启服务
docker compose -f docker/docker-compose.yml restart

# 停止并清理
docker compose -f docker/docker-compose.yml down
docker rmi mikeno-app
```

## 项目结构

```
Mikeno/
├── backend/
│   ├── src/
│   │   ├── models/
│   │   │   ├── captcha.py              # 验证码数据模型
│   │   │   └── stage.py                # 日志阶段定义
│   │   ├── services/
│   │   │   └── reddit/                 # 平台特定服务
│   │   └── utils/
│   │       ├── agent/
│   │       │   └── login_agent.py      # 登录自动化代理
│   │       ├── captcha_solver/
│   │       │   ├── common.py           # 通用验证码识别器
│   │       │   └── google.py           # Google reCAPTCHA 识别器
│   │       ├── config_loader.py        # 配置管理
│   │       ├── image_converter.py      # 图像处理工具
│   │       ├── logging.py              # 日志系统
│   │       ├── page_extractor.py       # 高性能元素提取
│   │       ├── shadow_dom_parser.py    # Shadow DOM 处理
│   │       └── web_operator.py         # 核心浏览器操作
│   ├── playground/
│   │   ├── test_login_agent.py         # 登录自动化示例
│   │   ├── test_captcha_agent.py       # 验证码识别示例
│   │   ├── test_page_extractor.py      # 元素提取示例
│   │   ├── test_web_operator.py        # 浏览器操作示例
│   │   └── utils/captcha/
│   │       └── test_google.py          # Google reCAPTCHA 示例
│   ├── config.yaml                     # 主配置文件
│   ├── requirements.txt                # Python 依赖
│   └── logs/                           # 应用程序日志
├── docker/
│   └── docker-compose.yml              # Docker 编排
└── README.md
```

## 核心组件

### LoginAgent
智能登录自动化，支持自动检测和验证码处理。

### CaptchaAgent
AI 驱动的验证码识别，支持多种验证码类型。

### WebOperator
底层浏览器控制，提供全面的元素交互方法。

### PageExtractor
高性能元素提取，速度提升 10-50 倍。

### ShadowDOMParser
完全支持 Shadow DOM 和 Web 组件。

## 性能指标

| 操作 | 传统方法 | Mikeno | 提升 |
|------|---------|--------|------|
| 元素提取（100+ 个元素） | 5-10 秒 | 0.3-0.8 秒 | 10-50 倍更快 |
| 验证码识别 | 手动 / 30+ 秒 | 2-5 秒 | 完全自动化 |
| 登录自动化 | 手动 / 60+ 秒 | 5-10 秒 | 6-12 倍更快 |

## 贡献

我们欢迎社区贡献！

1. Fork 仓库
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 Pull Request

### 开发指南

- 遵循 PEP 8 代码风格指南
- 为新功能添加测试
- 根据需要更新文档
- 提交 PR 前确保所有测试通过

## 安全提示

**重要**：此工具仅设计用于合法的自动化目的。

- 尊重网站服务条款
- 不要滥用速率限制
- 保护您的 API 凭据
- 使用测试账户进行开发
- 切勿将凭据提交到版本控制

## 许可证

本项目采用 GNU Affero 通用公共许可证 v3.0 (AGPL-3.0) - 详见 [LICENSE](LICENSE) 文件。

**重要说明**：根据 AGPL-3.0，如果您修改此软件并在服务器上运行以供用户交互使用，您必须向这些用户提供修改后的源代码。

## 致谢

- 基于 [DrissionPage](https://github.com/g1879/DrissionPage) 构建 - 现代浏览器自动化框架
- 由先进的 AI 视觉模型驱动智能自动化
- 灵感来自雄伟的米凯诺峰 - 屹立不倒，征服挑战


