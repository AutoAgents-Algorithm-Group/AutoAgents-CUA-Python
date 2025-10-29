<div align="center">

<img src="https://img.shields.io/badge/-Mikeno-000000?style=for-the-badge&labelColor=faf9f6&color=faf9f6&logoColor=000000" alt="Mikeno" width="280"/>

<h4>AI-Powered Intelligent Browser Automation Platform</h4>

**English** | [简体中文](README-CN.md)

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="media/dark_license.svg" />
  <img alt="License AGPL-3.0" src="media/light_license.svg" />
</picture>

</div>

Named after Mount Mikeno in the Virunga Mountains, one of the most challenging peaks to climb, this platform represents the pinnacle of browser automation technology - powerful, intelligent, and capable of conquering the most complex web automation challenges.

## Table of Contents
- [Table of Contents](#table-of-contents)
- [Why Mikeno?](#why-mikeno)
  - [Core Capabilities](#core-capabilities)
    - [Intelligent Automation](#intelligent-automation)
    - [High-Performance Architecture](#high-performance-architecture)
    - [Developer Experience](#developer-experience)
  - [What Can Mikeno Do?](#what-can-mikeno-do)
  - [Technology Foundation](#technology-foundation)
- [Quick Start](#quick-start)
  - [Prerequisites](#prerequisites)
  - [Automated Setup with setup.sh (Recommended)](#automated-setup-with-setupsh-recommended)
  - [Manual Setup (Alternative)](#manual-setup-alternative)
  - [Basic Usage Example (SDK Mode)](#basic-usage-example-sdk-mode)
- [Deployment](#deployment)
  - [Docker Deployment (Recommended)](#docker-deployment-recommended)
  - [Environment Configuration](#environment-configuration)
  - [Production Deployment](#production-deployment)
  - [Troubleshooting](#troubleshooting)
- [Project Structure](#project-structure)
- [Core Components](#core-components)
  - [LoginAgent](#loginagent)
  - [CaptchaAgent](#captchaagent)
  - [WebOperator](#weboperator)
  - [PageExtractor](#pageextractor)
  - [ShadowDOMParser](#shadowdomparser)
- [Performance Metrics](#performance-metrics)
- [Contributing](#contributing)
  - [Development Guidelines](#development-guidelines)
- [Security Notice](#security-notice)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Why Mikeno?

Mikeno is an advanced browser automation platform that combines AI intelligence with robust web automation capabilities. Built on DrissionPage and powered by AI models, Mikeno transforms complex web automation tasks into simple, reliable operations.

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

### What Can Mikeno Do?

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

### Automated Setup with setup.sh (Recommended)

The easiest way to get Mikeno running:

```bash
# 1. Clone the repository
git clone https://github.com/your-org/Mikeno.git
cd Mikeno

# 2. Make setup script executable and run it
chmod +x setup.sh
./setup.sh

# 3. Configure your API keys
# Edit backend/config.yaml with your API credentials

# 4. Run example automation
cd backend
python playground/test_login_agent.py
```

### Manual Setup (Alternative)

```bash
# Clone and navigate
git clone https://github.com/your-org/Mikeno.git
cd Mikeno

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Configure API keys
cp config.yaml.example config.yaml
# Edit config.yaml with your credentials

# Run tests
python playground/test_login_agent.py
```

### Basic Usage Example (SDK Mode)

```python
from src.autoagents_cua.utils import LoginAgent, CaptchaAgent

# Initialize CaptchaAgent (pass config directly)
captcha_agent = CaptchaAgent(
    api_key="your-api-key",
    base_url="https://api.openai.com/v1",
    model="gpt-4o"
)

# Initialize LoginAgent (pass config directly)
login_agent = LoginAgent(
    url="https://example.com/login",
    captcha_agent=captcha_agent,
    headless=False,
    wait_time=3
)

# Execute automated login
success = login_agent.login(
    username='your_username',
    password='your_password',
    username_selector='xpath://input[@name="username"]',
    password_selector='xpath://input[@name="password"]',
    button_selector='xpath://button[@type="submit"]',
    auto_handle_captcha=True
)

if success:
    print("Login successful!")
    
login_agent.close()
```

For more examples, see [SDK_USAGE.md](SDK_USAGE.md).

## Deployment

### Docker Deployment (Recommended)

```bash
cd Mikeno
docker compose -f docker/docker-compose.yml up -d
```

### Environment Configuration

Create `backend/config.yaml`:

```yaml
# CAPTCHA Recognition Configuration
captcha_agent:
  api_key: "your-api-key"
  base_url: "https://api.example.com/v1"
  model: "gemini-2.5-pro"

# Login Automation Configuration
login_agent:
  url: "https://example.com/login"
  username: "your_username"
  password: "your_password"
  headless: false
  wait_time: 3
  auto_handle_captcha: true
```

### Production Deployment

```bash
# Build production image
docker build -t mikeno-prod -f docker/Dockerfile .

# Run with production settings
docker run -d \
  --name mikeno \
  -v $(pwd)/backend/config.yaml:/app/config.yaml \
  -v $(pwd)/backend/logs:/app/logs \
  mikeno-prod
```

### Troubleshooting

```bash
# View application logs
docker compose -f docker/docker-compose.yml logs -f app

# Check container status
docker compose -f docker/docker-compose.yml ps

# Restart services
docker compose -f docker/docker-compose.yml restart

# Stop and clean up
docker compose -f docker/docker-compose.yml down
docker rmi mikeno-app
```

## Project Structure

```
Mikeno/
├── backend/
│   ├── src/
│   │   ├── models/
│   │   │   ├── captcha.py              # CAPTCHA data models
│   │   │   └── stage.py                # Logging stage definitions
│   │   ├── services/
│   │   │   └── reddit/                 # Platform-specific services
│   │   └── utils/
│   │       ├── agent/
│   │       │   └── login_agent.py      # Login automation agent
│   │       ├── captcha_solver/
│   │       │   ├── common.py           # Generic CAPTCHA solver
│   │       │   └── google.py           # Google reCAPTCHA solver
│   │       ├── config_loader.py        # Configuration management
│   │       ├── image_converter.py      # Image processing utilities
│   │       ├── logging.py              # Logging system
│   │       ├── page_extractor.py       # High-performance element extraction
│   │       ├── shadow_dom_parser.py    # Shadow DOM handling
│   │       └── web_operator.py         # Core browser operations
│   ├── playground/
│   │   ├── test_login_agent.py         # Login automation examples
│   │   ├── test_captcha_agent.py       # CAPTCHA solving examples
│   │   ├── test_page_extractor.py      # Element extraction examples
│   │   ├── test_web_operator.py        # Browser operation examples
│   │   └── utils/captcha/
│   │       └── test_google.py          # Google reCAPTCHA examples
│   ├── config.yaml                     # Main configuration file
│   ├── requirements.txt                # Python dependencies
│   └── logs/                           # Application logs
├── docker/
│   └── docker-compose.yml              # Docker orchestration
└── README.md

```

## Core Components

### LoginAgent
Intelligent login automation with auto-detection and CAPTCHA handling.

### CaptchaAgent
AI-powered CAPTCHA recognition supporting multiple CAPTCHA types.

### WebOperator
Low-level browser control with comprehensive element interaction methods.

### PageExtractor
High-performance element extraction with 10-50x speed improvement.

### ShadowDOMParser
Complete support for Shadow DOM and web components.

## Performance Metrics

| Operation | Traditional Method | Mikeno | Improvement |
|-----------|-------------------|---------|-------------|
| Element Extraction (100+ elements) | 5-10 seconds | 0.3-0.8 seconds | 10-50x faster |
| CAPTCHA Recognition | Manual / 30+ seconds | 2-5 seconds | Fully automated |
| Login Automation | Manual / 60+ seconds | 5-10 seconds | 6-12x faster |

## Contributing

We welcome contributions from the community!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR

## Security Notice

**Important**: This tool is designed for legitimate automation purposes only.

- Respect website terms of service
- Do not abuse rate limits
- Protect your API credentials
- Use test accounts for development
- Never commit credentials to version control

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0) - see the [LICENSE](LICENSE) file for details.

**Important**: Under AGPL-3.0, if you modify this software and run it on a server where users can interact with it, you must make your modified source code available to those users.

## Acknowledgments

- Built on [DrissionPage](https://github.com/g1879/DrissionPage) - Modern browser automation framework
- Powered by advanced AI vision models for intelligent automation
- Inspired by the majestic Mount Mikeno - standing tall and conquering challenges

