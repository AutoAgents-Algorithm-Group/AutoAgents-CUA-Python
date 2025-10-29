<div align="center">

<img src="https://img.shields.io/badge/-AutoAgents--CUA-000000?style=for-the-badge&labelColor=faf9f6&color=faf9f6&logoColor=000000" alt="AutoAgents-CUA-Python" width="320"/>

<h4>Python SDK for Computer Use Agent</h4>

**English** | [简体中文](README-CN.md)

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

AutoAgents-CUA-Python (Computer Use Agent) is an advanced AI-powered browser automation framework that combines Large Language Models with intelligent web automation capabilities. Built on DrissionPage and powered by state-of-the-art AI models, it transforms complex web automation tasks into simple, reliable operations.

## Table of Contents
- [Table of Contents](#table-of-contents)
- [Why AutoAgents CUA?](#why-autoagents-cua)
  - [Core Capabilities](#core-capabilities)
    - [Intelligent Automation](#intelligent-automation)
    - [High-Performance Architecture](#high-performance-architecture)
    - [Developer Experience](#developer-experience)
  - [What Can AutoAgents CUA Do?](#what-can-autoagents-cua-do)
  - [Technology Foundation](#technology-foundation)
- [Quick Start](#quick-start)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Basic Usage Example](#basic-usage-example)
- [Contributing](#contributing)

## Why AutoAgents CUA?

AutoAgents CUA (Computer Use Agent) is an advanced browser automation platform that combines AI intelligence with robust web automation capabilities. Built on DrissionPage and powered by Large Language Models, AutoAgents CUA transforms complex web automation tasks into simple, natural language-driven operations.

### Core Capabilities

#### Intelligent Automation
- **AI-Powered CAPTCHA Solving**: Automatically recognizes and solves image-based CAPTCHAs with 90%+ accuracy
- **Smart Form Detection**: Auto-detects and fills login forms without manual configuration
- **Adaptive Retry Logic**: Intelligently retries failed operations with exponential backoff
- **Natural Language Processing**: Describe what you want to automate in plain language

#### High-Performance Architecture
- **10-50x Faster Element Extraction**: JavaScript-based batch extraction vs traditional methods
- **Shadow DOM Support**: Full support for modern web components and Shadow DOM
- **Optimized Network Usage**: Minimize browser-server communication overhead
- **Production-Ready Logging**: Comprehensive stage-based logging for debugging and monitoring

#### Developer Experience
- **Zero Configuration**: Get started immediately with sensible defaults
- **YAML Configuration**: Flexible configuration management for complex scenarios
- **Modular Design**: Use individual components or the complete automation suite
- **Extensive Examples**: Ready-to-use examples in the playground directory

### What Can AutoAgents CUA Do?

- **Natural Language Automation**: Control browsers using natural language commands
- **Automated Login**: Handle complex login flows including 2FA and CAPTCHAs
- **Data Extraction**: Extract structured data from dynamic web pages
- **Form Automation**: Fill and submit forms across multiple pages
- **Session Management**: Maintain authenticated sessions across operations
- **Workflow Automation**: Chain multiple operations into complex workflows

### Technology Foundation

- **DrissionPage 4.0+**: Modern browser automation framework
- **AI Models**: Advanced vision models for CAPTCHA recognition
- **Python 3.11+**: Built on the latest Python features
- **Loguru**: Professional-grade logging system

## Quick Start

### Prerequisites
- Python 3.11+
- Chrome Browser
- Node.js 18+ (optional, for frontend features)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-org/AutoAgents-CUA-Python.git
cd AutoAgents-CUA-Python

# 2. Install dependencies
pip install -e .

# 3. Set up environment variables
export OPENAI_API_KEY="your-api-key"
export OPENAI_BASE_URL="https://api.openai.com/v1"
export OPENAI_MODEL="gpt-4o"
```

### Basic Usage Example

```python
from autoagents_cua.client import ChatClient
from autoagents_cua.models import ClientConfig, ModelConfig
from autoagents_cua.computer import Browser
from autoagents_cua.agent import BrowserAgent
from autoagents_cua.tools import ALL_WEB_TOOLS

# 1. Create LLM client
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

# 2. Create Browser
browser = Browser(
    headless=False,
    window_size={'width': 1000, 'height': 700}
)

# 3. Create BrowserAgent
agent = BrowserAgent(
    browser=browser,
    llm=llm,
    tools=ALL_WEB_TOOLS
)

# 4. Execute tasks with natural language
agent.invoke("Please open Google and search for 'Python automation'")
agent.invoke("Click on the first search result")
agent.invoke("Extract the main content from this page")

# 5. Clean up
agent.close()
```

For more examples, see the `playground/` directory.


## Contributing

We welcome contributions from the community!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request