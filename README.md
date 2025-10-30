<div align="center">

<img src="https://img.shields.io/badge/-AutoAgents--CUA-000000?style=for-the-badge&labelColor=faf9f6&color=faf9f6&logoColor=000000" alt="AutoAgents-CUA-Python" width="320"/>

<h4>Python SDK for Computer Use Agent</h4>

**English** | [简体中文](README-CN.md)

<a href="https://pypi.org/project/autoagents-cua">
  <img alt="PyPI version" src="https://img.shields.io/pypi/v/autoagents-cua.svg?style=for-the-badge" />
</a>
<a href="LICENSE">
  <img alt="License MIT" src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" />
</a>

</div>

AutoAgents-CUA-Python (Computer Use Agent) is an advanced AI-powered automation framework that combines Large Language Models with intelligent browser and mobile automation capabilities. Built on DrissionPage and uiautomator2, it transforms complex automation tasks into simple, reliable operations.

## Table of Contents
- [Table of Contents](#table-of-contents)
- [Why AutoAgents CUA?](#why-autoagents-cua)
  - [Core Capabilities](#core-capabilities)
    - [Intelligent Automation](#intelligent-automation)
    - [High-Performance Architecture](#high-performance-architecture)
    - [Developer Experience](#developer-experience)
  - [What Can AutoAgents CUA Do?](#what-can-autoagents-cua-do)
  - [Technology Foundation](#technology-foundation)
- [Project Architecture](#project-architecture)
  - [Module Structure](#module-structure)
  - [Layered Design](#layered-design)
- [Quick Start](#quick-start)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Basic Usage Examples](#basic-usage-examples)
    - [Browser Automation](#browser-automation)
    - [Automated Login with CAPTCHA](#automated-login-with-captcha)
    - [Mobile Automation (TikTok)](#mobile-automation-tiktok)
- [Advanced Features](#advanced-features)
  - [Browser Fingerprinting](#browser-fingerprinting)
  - [CAPTCHA Solving](#captcha-solving)
  - [Mobile Device Control](#mobile-device-control)
- [Contributing](#contributing)

## Why AutoAgents CUA?

AutoAgents CUA (Computer Use Agent) is an advanced automation platform that combines AI intelligence with robust browser and mobile automation capabilities. Built on DrissionPage and uiautomator2, powered by Large Language Models, AutoAgents CUA transforms complex automation tasks into simple, natural language-driven operations.

### Core Capabilities

#### Intelligent Automation
- **AI-Powered CAPTCHA Solving**: Automatically recognizes and solves image-based CAPTCHAs with 90%+ accuracy
- **Smart Form Detection**: Auto-detects and fills login forms without manual configuration
- **Adaptive Retry Logic**: Intelligently retries failed operations with exponential backoff
- **Natural Language Processing**: Describe what you want to automate in plain language
- **Mobile App Automation**: Control Android apps with intelligent gesture recognition

#### High-Performance Architecture
- **10-50x Faster Element Extraction**: JavaScript-based batch extraction vs traditional methods
- **Shadow DOM Support**: Full support for modern web components and Shadow DOM
- **Optimized Network Usage**: Minimize browser-server communication overhead
- **Production-Ready Logging**: Comprehensive stage-based logging for debugging and monitoring
- **Modular Design**: Clean separation of concerns with independent, reusable modules

#### Developer Experience
- **Zero Configuration**: Get started immediately with sensible defaults
- **Modular Architecture**: Use individual components or the complete automation suite
- **Type Hints**: Full type annotation support for better IDE integration
- **Extensive Examples**: Ready-to-use examples in the playground directory
- **Backward Compatible**: Old import paths still work for smooth migration

### What Can AutoAgents CUA Do?

**Web Automation:**
- Natural language browser control using AI
- Automated login with 2FA and CAPTCHA handling
- Data extraction from dynamic web pages
- Form automation across multiple pages
- Session management and workflow automation

**Mobile Automation:**
- Android app control and automation
- TikTok video interaction automation
- Element detection and gesture simulation
- Screenshot analysis and comparison

**Prebuilt Solutions:**
- LoginAgent for automatic web login
- TikTokManager for TikTok automation
- Extensible for custom applications

### Technology Foundation

- **DrissionPage 4.0+**: Modern browser automation framework
- **uiautomator2**: Android automation framework
- **AI Models**: Advanced vision models for CAPTCHA recognition
- **Python 3.11+**: Built on the latest Python features
- **Loguru**: Professional-grade logging system

## Project Architecture

### Module Structure

```
autoagents_cua/
├── browser/              # Browser automation core
│   ├── Browser           # Browser management
│   ├── WebOperator       # Web page operations
│   ├── PageExtractor     # Element extraction
│   ├── ShadowDOMParser   # Shadow DOM parsing
│   ├── CaptchaAgent      # CAPTCHA solving
│   └── BrowserFingerprint # Anti-detection fingerprinting
│
├── agent/                # Intelligent agents
│   ├── BrowserAgent      # AI-powered browser agent
│   ├── MobileDevice      # Mobile device control
│   └── MobileAgent       # AI-powered mobile agent
│
├── prebuilt/             # Ready-to-use managers
│   ├── LoginAgent        # Automated web login
│   └── TikTokManager     # TikTok automation
│
├── client/               # LLM client
│   └── ChatClient        # AI model integration
│
├── tools/                # Tool functions
└── utils/                # Utilities
```

### Layered Design

```
┌─────────────────────────────────────────────────┐
│         Prebuilt Layer (LoginAgent, TikTok)     │
│              Ready-to-use Solutions             │
└─────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────┐
│      Agent Layer (BrowserAgent, MobileAgent)    │
│           AI-Powered Intelligent Agents         │
└─────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────┐
│    Browser/Mobile Layer (Core Functionality)    │
│     Browser Operations & Mobile Control         │
└─────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────┐
│         Utils Layer (Logging, Tools)            │
│            Infrastructure & Utilities           │
└─────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites
- Python 3.11+
- Chrome Browser (for web automation)
- Android Device/Emulator with ADB (for mobile automation)
- Node.js 18+ (optional, for frontend features)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-org/AutoAgents-CUA-Python.git
cd AutoAgents-CUA-Python

# 2. Install dependencies
pip install -e .
```

### Basic Usage Examples

#### Browser Automation

```python
from autoagents_cua import Browser, BrowserAgent
from autoagents_cua.client import ChatClient
from autoagents_cua.models import ClientConfig, ModelConfig

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

# 2. Create Browser with fingerprinting
browser = Browser(
    headless=False,
    use_fingerprint=True,  # Anti-detection
    window_size={'width': 1000, 'height': 700}
)

# 3. Create BrowserAgent
agent = BrowserAgent(browser=browser, llm=llm)

# 4. Execute tasks with natural language
agent.invoke("Please open Google and search for 'Python automation'")
agent.invoke("Click on the first search result")
agent.invoke("Extract the main content from this page")

# 5. Clean up
agent.close()
```

#### Automated Login with CAPTCHA

```python
from autoagents_cua.prebuilt import LoginAgent
from autoagents_cua.browser import CaptchaAgent

# 1. Create CAPTCHA solver
captcha_agent = CaptchaAgent(
    api_key="your-api-key",
    base_url="https://api.openai.com/v1",
    model="gpt-4o"
)

# 2. Create LoginAgent
login_agent = LoginAgent(
    url="https://example.com/login",
    captcha_agent=captcha_agent,
    headless=False
)

# 3. Automatic login with CAPTCHA handling
success = login_agent.login(
    username="your-username",
    password="your-password",
    auto_handle_captcha=True  # Automatically solve CAPTCHAs
)

if success:
    print("✅ Login successful!")
```

#### Mobile Automation (TikTok)

```python
from autoagents_cua.prebuilt import TikTokManager

# 1. Create TikTok manager
manager = TikTokManager(device_address="127.0.0.1:5555")

# 2. Start app and handle popups
manager.start_app()
manager.handle_popups()

# 3. Run automated cycle
# Cycle: click avatar → message → back → back → scroll
manager.run_continuous_cycle(
    cycle_count=10,  # Run 10 cycles
    max_errors=3     # Stop after 3 consecutive errors
)

# View statistics
manager.print_cycle_stats(stats)
```

## Advanced Features

### Browser Fingerprinting

```python
from autoagents_cua.browser import Browser, BrowserFingerprint

# Generate random fingerprint
fingerprint = BrowserFingerprint.generate_random_fingerprint()

# Create browser with custom fingerprint
browser = Browser(
    headless=False,
    use_fingerprint=True,
    fingerprint_preset='windows_chrome'  # or custom fingerprint
)
```

### CAPTCHA Solving

```python
from autoagents_cua.browser import CaptchaAgent

# Create CAPTCHA agent
agent = CaptchaAgent(
    api_key="your-api-key",
    model="gpt-4o"
)

# Solve CAPTCHA on a page
success = agent.solve_captcha(
    page=page,
    captcha_selector='css:.captcha-container',
    max_retries=3
)
```

### Mobile Device Control

```python
from autoagents_cua.agent import MobileDevice

# Connect to device
device = MobileDevice("127.0.0.1:5555")

# Basic operations
device.start_app("com.example.app")
device.click_element(text="Button")
device.swipe_up(ratio=0.5)
device.screenshot(save_path="screenshot.png")
```

For more examples, see the `playground/` directory:
- `playground/agent/` - BrowserAgent examples
- `playground/mobile/` - Mobile automation examples
- `playground/page_test/` - Web automation examples

## Contributing

We welcome contributions from the community!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
