# Web 操作 Agent 🤖

基于 LangChain + LangGraph 的智能网页自动化 Agent，支持自然语言指令控制浏览器。

## ✨ 功能特性

- 🌐 **自然语言控制**：用自然语言指令操作浏览器
- 🔍 **智能元素识别**：自动提取和识别页面可交互元素
- 🧠 **上下文记忆**：支持多轮对话，记住之前的操作
- 🛠️ **丰富工具集**：打开网页、点击、输入、返回等操作

## 🚀 快速开始

### 1. 安装依赖

```bash
cd /Users/yhl/project/Mikeno/backend
pip install -r requirements.txt
```

### 2. 运行演示

```bash
python playground/agent_test/agent_simple_demo.py
```

## 💡 使用示例

### 示例 1: 打开网站

```python
from agent_simple_demo import WebAgent

agent = WebAgent(headless=False)

# 自然语言指令
agent.execute("请帮我打开谷歌")
agent.execute("打开百度")
agent.execute("打开 https://github.com")

agent.close()
```

### 示例 2: 页面元素提取

```python
agent.execute("帮我看看这个页面有哪些可以点击的元素")
```

**Agent 会返回：**
```
✅ 找到 40 个可交互元素：

【A】 15 个
  [1] Skip to main content
  [2] Google
  [3] Gmail
  ...

【BUTTON】 3 个
  [4] 搜索 name=btnK
  [5] 手气不错 name=btnI
  ...

【INPUT】 2 个
  [6] name=q
  ...
```

### 示例 3: 综合操作

```python
# 打开百度并搜索
agent.execute("打开百度")
agent.execute("帮我看看页面元素")
agent.execute("在搜索框中输入'人工智能'，然后点击搜索按钮")
```

### 示例 4: 多轮对话

```python
# Agent 会记住上下文
agent.execute("打开谷歌")
agent.execute("分析一下页面元素")  # 知道是当前页面
agent.execute("返回上一页")  # 知道要返回
```

## 🛠️ 可用工具

### 1. `open_website(url: str)`
打开指定的网站

**支持简写：**
- "谷歌" → https://www.google.com
- "百度" → https://www.baidu.com  
- "github" → https://github.com
- "pubmed" → https://pmc.ncbi.nlm.nih.gov/

**示例：**
```python
agent.execute("打开谷歌")
agent.execute("打开 https://www.example.com")
```

### 2. `extract_page_elements()`
提取当前页面的所有可交互元素

**返回：**
- 元素索引号 `[1]`, `[2]`, ...
- 元素类型（链接、按钮、输入框等）
- 元素文本和属性

**示例：**
```python
agent.execute("帮我分析一下页面元素")
agent.execute("这个页面有哪些按钮？")
```

### 3. `click_element(index: int)`
点击页面上的元素（通过索引号）

**示例：**
```python
agent.execute("点击第3个元素")
agent.execute("点击搜索按钮")  # Agent会先提取元素，找到搜索按钮，然后点击
```

### 4. `input_text_to_element(index: int, text: str)`
在输入框中输入文本

**示例：**
```python
agent.execute("在第6个元素中输入'hello world'")
agent.execute("在搜索框中输入'Python'")  # Agent会智能识别搜索框
```

### 5. `get_current_url()`
获取当前页面URL

**示例：**
```python
agent.execute("现在在哪个页面？")
agent.execute("当前URL是什么？")
```

### 6. `go_back()`
返回上一页

**示例：**
```python
agent.execute("返回上一页")
agent.execute("退回去")
```

## 🧪 高级用法

### 自定义 LLM 配置

```python
agent = WebAgent(
    headless=False,  # 是否无头模式
    api_key="your-api-key",
    base_url="https://your-api-endpoint.com/v1"
)
```

### 会话管理

```python
# 使用不同的 thread_id 管理不同会话
agent.execute("打开谷歌", thread_id="session_1")
agent.execute("打开百度", thread_id="session_2")

# 返回 session_1 继续操作
agent.execute("分析页面", thread_id="session_1")  # 仍在谷歌页面
```

### 添加自定义工具

```python
from langchain_core.tools import tool

@tool
def search_google(query: str) -> str:
    """在谷歌搜索"""
    # 实现搜索逻辑
    return f"搜索: {query}"

# 添加到 Agent
agent.tools.append(search_google)
```

## 📋 实际应用场景

### 1. 网页测试自动化
```python
agent.execute("打开我们的产品页面 https://example.com/product")
agent.execute("检查页面上是否有'立即购买'按钮")
agent.execute("点击购买按钮")
agent.execute("填写表单并提交")
```

### 2. 数据采集
```python
agent.execute("打开 PubMed")
agent.execute("搜索 'machine learning in medicine'")
agent.execute("提取搜索结果的标题和链接")
```

### 3. 网页监控
```python
agent.execute("打开目标网站")
agent.execute("检查是否有'新产品'标签")
agent.execute("如果有，点击并获取详情")
```

## ⚙️ 配置说明

### API Key 配置

1. **使用环境变量：**
```bash
export OPENAI_API_KEY="your-api-key"
export OPENAI_BASE_URL="https://your-endpoint.com/v1"
```

2. **代码中配置：**
```python
agent = WebAgent(
    api_key="your-api-key",
    base_url="https://your-endpoint.com/v1"
)
```

## 🔧 故障排查

### 问题 1: 无法找到元素

**原因：** 页面元素未提取或索引错误

**解决：**
```python
# 先提取元素
agent.execute("分析页面元素")
# 然后根据返回的索引号操作
agent.execute("点击第5个元素")
```

### 问题 2: Agent 不理解指令

**原因：** 指令太模糊

**解决：** 使用更明确的指令
```python
# ❌ 模糊
agent.execute("搜索")

# ✅ 明确
agent.execute("在搜索框中输入'Python'，然后点击搜索按钮")
```

### 问题 3: 页面加载慢导致元素未找到

**解决：** 分步操作，给页面加载时间
```python
agent.execute("打开网站")
# 等待几秒
agent.execute("分析页面元素")
```

## 📝 开发计划

- [ ] 支持更多操作类型（下拉框、拖拽等）
- [ ] 添加截图功能
- [ ] 支持多页面/多标签页管理
- [ ] 添加元素智能匹配（通过文本/属性自动查找）
- [ ] 支持自定义工作流保存和重放

## 🤝 贡献

欢迎提 Issue 和 PR！

## 📄 许可证

MIT License

