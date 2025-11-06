# 提示词管理系统

使用 Markdown 文件管理提示词，支持变量插入和缓存机制。

## 📁 目录结构

```
prompts/
├── __init__.py              # PromptLoader 实现
├── README.md                # 本文档
├── clarify/                 # 澄清节点的提示词
│   ├── is_query_clear.md
│   └── generate_question.md
├── plan/                    # 规划节点的提示词（未来）
├── execute/                 # 执行节点的提示词（未来）
└── ...
```

## 🚀 快速开始

### 1. 基本使用

```python
from src.autoagents_cua.prompts import prompt_loader

# 加载提示词并插入变量
prompt = prompt_loader.load(
    "clarify/generate_question.md",
    query="做一份AIGC投融资报告"
)

# 发送给 LLM
response = llm.invoke(prompt)
```

### 2. 多个变量

```python
prompt = prompt_loader.load(
    "custom/template.md",
    user="张三",
    task="完成需求文档",
    priority="高",
    deadline="2024-12-31"
)
```

### 3. 清除缓存（开发时）

```python
# 修改 Markdown 文件后，清除缓存以重新加载
prompt_loader.clear_cache()
```

## 📝 创建新的提示词

### 格式规范

在 Markdown 文件中使用 `{变量名}` 作为占位符：

```markdown
# 任务描述

用户: {user}
任务: {task}
优先级: {priority}

---

{user}，您的任务「{task}」已记录，优先级为 {priority}。

请提供以下信息...
```

### 变量命名规范

- 使用小写字母和下划线：`user_name`、`task_description`
- 见名知意：`query` 而不是 `q`
- 常用变量：
  - `query`: 用户输入的任务
  - `user`: 用户名
  - `context`: 上下文信息
  - `examples`: 示例
  - `format`: 格式要求

### 组织结构

按节点/功能组织提示词文件：

```
prompts/
├── clarify/          # 澄清相关
│   ├── is_query_clear.md
│   └── generate_question.md
├── plan/             # 规划相关
│   ├── generate_plan.md
│   └── refine_plan.md
├── execute/          # 执行相关
│   ├── choose_tool.md
│   └── check_complete.md
└── observe/          # 反思相关
    ├── self_check.md
    └── strategy_shift.md
```

## 🎯 最佳实践

### 1. 提示词结构

推荐使用清晰的 Markdown 结构：

```markdown
# 角色定义
你是一个...专家

## 任务目标
请根据...

## 格式要求
1. 第一点
2. 第二点

## 示例
```示例内容```

## 注意事项
- 注意点1
- 注意点2

---

## 用户输入
{query}

---

## 请开始
```

### 2. 变量使用

✅ **推荐**：
```markdown
**任务：**{query}

**要求：**
- 深度：{depth}
- 范围：{scope}
```

❌ **不推荐**：
```markdown
任务：{query}要求：{depth}{scope}
```

### 3. 文件命名

- 使用小写字母和下划线
- 描述性命名：`generate_question.md` 而不是 `gq.md`
- 按功能分组：`clarify/xxx.md`、`plan/xxx.md`

### 4. 版本控制

提示词文件纳入 Git 管理：
- 记录每次修改的原因（git commit message）
- 重大改动前备份旧版本
- 在注释中记录版本历史

```markdown
<!--
Version: 2.0
Last Updated: 2024-01-01
Changes: 改进了问题结构，增加了示例
-->

你是一个任务澄清专家...
```

## 🔧 高级用法

### 1. 条件变量

使用 Python 预处理条件逻辑：

```python
# 在代码中处理条件
if user_type == "expert":
    detail_level = "高级"
else:
    detail_level = "基础"

prompt = prompt_loader.load(
    "custom/template.md",
    detail_level=detail_level
)
```

### 2. 嵌套变量

先加载子模板，再插入主模板：

```python
examples = prompt_loader.load("common/examples.md", domain="AIGC")
prompt = prompt_loader.load(
    "main/template.md",
    query="任务描述",
    examples=examples
)
```

### 3. 动态提示词选择

根据场景选择不同的提示词：

```python
if task_complexity == "high":
    prompt_path = "clarify/generate_question_detailed.md"
else:
    prompt_path = "clarify/generate_question_simple.md"

prompt = prompt_loader.load(prompt_path, query=query)
```

## ❓ 常见问题

### Q: 如何在提示词中使用大括号 `{}`？

A: 使用双大括号转义：

```markdown
使用 JSON 格式：{{ "key": "value" }}
```

### Q: 变量缺失会发生什么？

A: 抛出 `ValueError` 异常，提示缺少的变量名。

### Q: 如何处理多语言提示词？

A: 创建不同语言的目录：

```
prompts/
├── en/
│   └── clarify/
│       └── generate_question.md
└── zh/
    └── clarify/
        └── generate_question.md
```

```python
# 使用时指定语言
language = "zh"  # 或 "en"
prompt = prompt_loader.load(f"{language}/clarify/generate_question.md", query=query)
```

## 📊 性能

- **缓存机制**：首次加载后缓存在内存中
- **加载速度**：100次加载 < 1ms（使用缓存）
- **内存占用**：约 1-2KB per 文件

## 🔄 迁移指南

### 从硬编码迁移到 Markdown

**之前：**
```python
system_prompt = """你是一个任务澄清专家。
请生成澄清问题..."""

user_prompt = f"用户任务：{query}"
response = llm.invoke(system_prompt, user_prompt)
```

**现在：**
```python
# 1. 创建 prompts/clarify/generate_question.md
# 2. 使用 prompt_loader
prompt = prompt_loader.load("clarify/generate_question.md", query=query)
response = llm.invoke(prompt)
```

**优势：**
- ✅ 提示词与代码分离
- ✅ 易于修改和版本控制
- ✅ 支持团队协作（非开发人员也能修改）
- ✅ 统一管理和复用

---

**贡献者**: 如有问题或建议，请提 Issue 或 PR。


