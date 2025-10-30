# Prebuilt 预构建解决方案

本目录包含开箱即用的自动化解决方案和实际应用示例。

## 📁 文件结构

```
prebuilt/
├── test_login_agent.py       # 自动登录代理测试
├── test_reddit.py            # Reddit 自动评论示例
└── test_pubmed_demo.py       # PubMed 文献检索示例
```

## 🎯 预构建方案

### 1. LoginAgent - 自动登录
**文件**: `test_login_agent.py`

自动化处理各种网站的登录流程，包括：
- ✅ 自动检测登录表单
- ✅ 智能填写用户名和密码
- ✅ 自动识别和解决验证码
- ✅ 处理双因素认证提示
- ✅ 会话管理

**使用示例**:
```python
from src.autoagents_cua.prebuilt import LoginAgent
from src.autoagents_cua.browser import CaptchaAgent

# 创建验证码识别器
captcha_agent = CaptchaAgent(
    api_key="your-api-key",
    model="gpt-4o"
)

# 创建登录代理
login_agent = LoginAgent(
    url="https://example.com/login",
    captcha_agent=captcha_agent,
    headless=False
)

# 执行登录
success = login_agent.login(
    username="your-username",
    password="your-password",
    auto_handle_captcha=True
)

if success:
    print("✅ 登录成功！")
```

### 2. Reddit 自动评论
**文件**: `test_reddit.py`

完整的 Reddit 自动化工作流示例：
- 🔐 Cookie 登录
- 🔍 搜索特定主题
- 📖 阅读帖子内容
- 🤖 AI 生成评论
- 💬 发表评论
- 🌓 处理 Shadow DOM 元素

**功能亮点**:
- 使用 `WebOperator` 进行页面导航
- 使用 `ShadowDOMParser` 处理 Shadow DOM 按钮
- 集成 OpenAI 生成自然的评论内容
- 完整的错误处理和日志记录

**使用场景**:
- Reddit 营销自动化
- 社区互动机器人
- 内容监控和响应

### 3. PubMed 文献检索
**文件**: `test_pubmed_demo.py`

学术文献自动化检索和整理：
- 📚 搜索学术文献
- 📄 提取文章信息
- 💾 数据结构化存储
- 🔗 管理引用链接

**适用场景**:
- 文献综述自动化
- 学术研究辅助
- 论文信息收集

## 🚀 快速开始

### 运行 LoginAgent 测试

```bash
# 配置环境变量
export OPENAI_API_KEY="your-api-key"

# 运行测试
python playground/prebuilt/test_login_agent.py
```

### 运行 Reddit 示例

```bash
# 1. 更新 Reddit cookies（在文件中）
# 2. 配置 OpenAI API（在文件中）
# 3. 运行脚本
python playground/prebuilt/test_reddit.py
```

### 运行 PubMed 示例

```bash
python playground/prebuilt/test_pubmed_demo.py
```

## 🔧 自定义预构建方案

### 创建自己的预构建方案

```python
from src.autoagents_cua.browser import WebOperator, CaptchaAgent
from src.autoagents_cua.utils.logging import logger

class CustomManager:
    """自定义自动化管理器"""
    
    def __init__(self, headless=False):
        self.web_op = WebOperator(headless=headless)
        self.captcha_agent = CaptchaAgent(
            api_key="your-api-key",
            model="gpt-4o"
        )
    
    def login(self, username, password):
        """登录流程"""
        logger.info("开始登录...")
        self.web_op.navigate("https://example.com/login")
        self.web_op.input_text('css:#username', username)
        self.web_op.input_text('css:#password', password)
        self.web_op.click_element('css:button[type="submit"]')
        logger.success("登录成功")
    
    def perform_task(self):
        """执行主要任务"""
        # 实现你的业务逻辑
        pass
    
    def close(self):
        """清理资源"""
        self.web_op.close()
```

## 📊 示例对比

| 功能 | LoginAgent | Reddit | PubMed |
|------|-----------|--------|---------|
| 自动登录 | ✅ | ✅ | ❌ |
| 验证码处理 | ✅ | ❌ | ❌ |
| Shadow DOM | ❌ | ✅ | ❌ |
| AI 生成内容 | ❌ | ✅ | ❌ |
| 数据提取 | ❌ | ✅ | ✅ |
| Cookie 管理 | ✅ | ✅ | ❌ |

## 💡 最佳实践

### 1. 错误处理
```python
try:
    success = login_agent.login(username, password)
    if not success:
        logger.error("登录失败，请检查凭据")
except Exception as e:
    logger.exception(f"发生错误: {e}")
finally:
    login_agent.close()
```

### 2. 日志记录
```python
from src.autoagents_cua.utils.logging import logger, set_stage
from src.autoagents_cua.models import Stage

# 设置当前阶段
set_stage(Stage.LOGIN)
logger.info("正在执行登录...")

set_stage(Stage.EXTRACTION)
logger.info("正在提取数据...")
```

### 3. 配置管理
```python
# 使用配置文件
import yaml

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

login_agent = LoginAgent(
    url=config['login_url'],
    captcha_agent=captcha_agent,
    **config['browser_options']
)
```

## 🔗 依赖模块

这些预构建方案依赖于：

- `autoagents_cua.browser`: 浏览器操作核心
- `autoagents_cua.prebuilt.LoginAgent`: 登录代理
- `autoagents_cua.utils.logging`: 日志系统
- `openai`: AI 内容生成（可选）

## 📝 贡献你的方案

欢迎提交你的预构建方案！

1. 在 `src/autoagents_cua/prebuilt/` 创建新模块
2. 在 `playground/prebuilt/` 添加测试示例
3. 更新本 README
4. 提交 Pull Request

### 方案要求
- ✅ 完整的文档和注释
- ✅ 清晰的使用示例
- ✅ 错误处理机制
- ✅ 日志记录
- ✅ 实际应用场景

## 📚 相关文档

- [LoginAgent 详细文档](../../src/autoagents_cua/prebuilt/login_agent.py)
- [Browser 模块文档](../../src/autoagents_cua/browser/)
- [创建自定义预构建方案指南](../../docs/custom-prebuilt.md)

