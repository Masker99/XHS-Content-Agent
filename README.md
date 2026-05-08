# XHS Content Agent

![XHS Content Agent 宣传封面图](./XHS%20Content%20Agent%E5%AE%A3%E4%BC%A0%E5%B0%81%E9%9D%A2%E5%9B%BE.png)

一个基于 LangGraph + FastAPI 的小红书内容生成 Agent。项目将小红书笔记生产流程拆分为多个可观测节点，覆盖内容框架、标题生成、标题选择、关键词标签、正文去 AI 味和封面图提示词生成，并提供 CLI、本地 Python 调用和 HTTP API 三种使用方式。

## 项目定位

这个项目不是单次 Prompt 调用，而是一个多步骤内容工作流：

```text
用户指令 / OpenClaw JSON
  -> 内容框架与正文草稿
  -> 标题候选
  -> 最佳标题选择
  -> 搜索关键词与话题标签
  -> 去 AI 味最终正文
  -> 封面图提示词
```

适合用于展示：

- LangGraph 工作流编排
- LLM 应用节点拆分
- FastAPI 服务化封装
- Pydantic 请求模型校验
- Prompt 模板集中管理
- Mock 模式下的本地调试与演示
- OpenClaw 风格结构化输入适配

## 技术栈

| 模块 | 技术 |
|---|---|
| 工作流编排 | LangGraph |
| LLM 调用 | LangChain Core, langchain-deepseek |
| API 服务 | FastAPI, Pydantic |
| 命令行入口 | argparse |
| 配置管理 | python-dotenv, 环境变量 |
| 模型 | DeepSeek API，支持 mock 模式 |

## 项目结构

```text
.
├── api_server.py          # FastAPI HTTP 服务入口
├── cli.py                 # 命令行演示入口，支持流式输出
├── xhs_workflow.py        # SDK 风格聚合入口，方便外部 Python 代码 import
├── scripts/
│   └── batch_run.py       # 批量任务运行脚本
├── examples/              # 单条与批量请求样例
├── requirements.txt       # Python 依赖
├── .env.example           # 环境变量示例
└── xhs_agent/
    ├── __init__.py
    ├── graph.py           # LangGraph 节点编排与工作流执行入口
    ├── nodes.py           # 各个工作流节点的业务逻辑
    ├── prompts.py         # System/User Prompt 模板
    ├── llm.py             # LLM 调用封装与 mock 模式
    ├── io.py              # 普通文本 / OpenClaw JSON 输入适配
    └── state.py           # 工作流状态结构定义
```

## 核心工作流

工作流定义在 `xhs_agent/graph.py`：

```text
START
  -> build_framework
  -> generate_titles
  -> select_title
  -> generate_keywords
  -> humanize_copy
  -> generate_cover_prompt
  -> END
```

每个节点定义在 `xhs_agent/nodes.py`：

| 节点 | 作用 |
|---|---|
| `build_framework` | 根据输入指令生成内容框架和第一版正文草稿 |
| `generate_titles` | 基于正文生成小红书标题候选 |
| `select_title` | 从标题候选中选择最适合发布的标题 |
| `generate_keywords` | 生成搜索关键词和话题标签组合 |
| `humanize_copy` | 对正文做去 AI 味改写 |
| `generate_cover_prompt` | 生成可用于图片模型的小红书封面提示词 |

## 快速开始

### 1. 创建虚拟环境

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. 安装依赖

```powershell
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env`：

```powershell
Copy-Item .env.example .env
```

`.env.example` 示例：

```env
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_TEMPERATURE=0.7
XHS_WORKFLOW_MOCK=1
XHS_LLM_MAX_RETRIES=3
XHS_LLM_RETRY_BACKOFF_BASE=1
XHS_DB_PATH=data/xhs_agent.db

# Optional cover prompt branding
XHS_BRAND_NAME=内容方法实验室
XHS_BRAND_TAGLINE=内容方法 × AI 工作流
XHS_BRAND_STYLE=内容方法论、AI 辅助创作、轻手绘、实用但不死板
XHS_BRAND_BOOK_1=内容方法论
XHS_BRAND_BOOK_2=AI 辅助创作
XHS_BRAND_BOOK_3=工作流笔记
```

如果只是本地演示或测试，可以保留：

```env
XHS_WORKFLOW_MOCK=1
```

此时项目不会真实调用模型 API，而是返回 mock 输出。

## CLI 使用

普通运行：

```powershell
python cli.py "帮我写一篇小红书笔记，主题是普通上班族如何建立周末复盘习惯"
```

流式查看每个节点输出：

```powershell
python cli.py "帮我写一篇小红书笔记，主题是普通上班族如何建立周末复盘习惯" --stream
```

不传参数时进入交互模式：

```powershell
python cli.py
```

## FastAPI 使用

启动服务：

```powershell
uvicorn api_server:app --reload
```

打开接口文档：

```text
http://127.0.0.1:8000/docs
```

健康检查：

```http
GET /health
```

调用内容工作流：

```http
POST /invoke
Content-Type: application/json

{
  "instruction": "帮我写一篇小红书笔记，主题是普通上班族如何建立周末复盘习惯"
}
```

也支持 OpenClaw 风格结构化输入：

```json
{
  "openclaw": {
    "task": "generate_xhs_note",
    "topic": "普通上班族如何建立周末复盘习惯",
    "audience": "工作日很忙、周末容易摆烂，但希望生活和工作慢慢变有序的年轻上班族",
    "style": "真实、克制、有生活感"
  }
}
```

响应字段：

```json
{
  "run_id": "...",
  "source": "text",
  "framework": "...",
  "titles": "...",
  "selected_title": "...",
  "keywords": "...",
  "final_copy": "...",
  "cover_prompt": "..."
}
```

批量调用内容工作流：

```http
POST /batch-invoke
Content-Type: application/json

{
  "instructions": [
    "帮我写一篇小红书笔记，主题是普通上班族如何建立周末复盘习惯",
    "帮我写一篇小红书笔记，主题是租房党如何低成本布置一个舒服的书桌角",
    "帮我写一篇小红书笔记，主题是新手如何开始做一周早餐备餐"
  ]
}
```

批量接口会逐条执行工作流，并为每条输入记录 `success` 或 `failed`，单条失败不会中断整个批次。

查询最近运行记录：

```http
GET /runs?limit=20
```

查询单条运行详情：

```http
GET /runs/{run_id}
```

`/invoke` 和 `/batch-invoke` 都会自动保存运行记录，响应里的 `run_id` 可用于查询详情。

## 数据库存储

项目使用 SQLite 保存工作流运行记录，默认路径：

```text
data/xhs_agent.db
```

可通过环境变量调整：

```env
XHS_DB_PATH=data/xhs_agent.db
```

保存内容包括：

- 输入来源：`text` / `openclaw`
- 原始输入
- 执行状态：`success` / `failed`
- 工作流输出：框架、标题、关键词、正文、封面提示词
- 错误信息
- 模型名
- 是否 mock 模式
- 创建时间、完成时间、耗时
- 批量任务元信息

数据库文件属于运行时产物，已通过 `.gitignore` 忽略；仓库只保留 `data/.gitkeep` 用来保留目录结构。

## 批量运行

项目提供批量任务脚本，适合本地批量测试、评测样本运行和自动化内容生成。

默认读取：

```text
examples/batch_requests.json
```

默认输出：

```text
outputs/batch_results.json
```

运行：

```powershell
$env:XHS_WORKFLOW_MOCK="1"
python scripts/batch_run.py
```

也可以指定输入和输出路径：

```powershell
python scripts/batch_run.py --input examples/batch_requests.json --output outputs/batch_results.json
```

批量输入格式：

```json
[
  {
    "id": "note_001",
    "instruction": "帮我写一篇小红书笔记，主题是普通上班族如何建立周末复盘习惯。"
  }
]
```

输出结果会保存每条任务的 `id`、`instruction`、`status`、`result` 或 `error`，方便后续追踪和评测。

## Python 调用

`xhs_workflow.py` 提供 SDK 风格聚合入口，方便其他 Python 代码直接调用：

```python
from xhs_workflow import format_result, run_xhs_workflow

result = run_xhs_workflow("帮我写一篇关于 AI 自动化的笔记")
print(format_result(result))
```

也可以使用流式输出：

```python
from xhs_workflow import stream_xhs_workflow

for event in stream_xhs_workflow("帮我写一篇小红书笔记"):
    print(event)
```

## 示例文件

项目提供了两个请求样例和一个 mock 输出样例：

```text
examples/
├── sample_request.json       # 普通 instruction 请求
├── openclaw_request.json     # OpenClaw 风格结构化请求
├── batch_requests.json       # 批量任务请求
└── sample_output_mock.md     # mock 模式输出结构示例
```

可以在 FastAPI `/docs` 页面中复制 `sample_request.json` 或 `openclaw_request.json` 的内容进行测试。

## Mock 模式

Mock 模式在 `xhs_agent/llm.py` 中实现。

当环境变量为：

```env
XHS_WORKFLOW_MOCK=1
```

`invoke_llm()` 不会请求真实模型，而是返回包含 System Prompt 和 User Prompt 摘要的模拟结果。

这个设计用于：

- 无 API Key 时本地演示
- 避免开发阶段消耗模型额度
- 支持自动化测试
- 快速验证 LangGraph 节点流转是否正常

关闭 mock 并调用真实模型：

```env
XHS_WORKFLOW_MOCK=0
DEEPSEEK_API_KEY=your_real_api_key
```

真实模型调用会在 `invoke_llm()` 中做有限次数重试、指数退避等待和空内容检测。可通过环境变量调整：

```env
XHS_LLM_MAX_RETRIES=3
XHS_LLM_RETRY_BACKOFF_BASE=1
```

## 封面品牌配置

封面图提示词默认使用通用账号配置，不写死个人账号名称。可以通过环境变量自定义：

```env
XHS_BRAND_NAME=内容方法实验室
XHS_BRAND_TAGLINE=内容方法 × AI 工作流
XHS_BRAND_STYLE=内容方法论、AI 辅助创作、轻手绘、实用但不死板
XHS_BRAND_BOOK_1=内容方法论
XHS_BRAND_BOOK_2=AI 辅助创作
XHS_BRAND_BOOK_3=工作流笔记
```

## 输入设计

`/invoke` 接口支持两种输入：

| 字段 | 用途 |
|---|---|
| `instruction` | 普通文本指令，适合本地调试和普通用户调用 |
| `openclaw` | 结构化 JSON，适合接入上层 Agent、自动化平台或 OpenClaw 指挥官 |
| `instructions` | 批量文本指令数组，适合前端或自动化系统一次提交多条任务 |

如果两个字段都不传，接口会返回 `400`：

```json
{
  "detail": "Either instruction or openclaw is required."
}
```

## 项目亮点

1. **多节点 Agent 工作流**：用 LangGraph 将内容生成拆成可维护、可观测的节点，而不是单次 Prompt 调用。
2. **服务化封装**：通过 FastAPI 提供 HTTP API，便于前端、自动化平台或其他 Agent 调用。
3. **输入适配**：同时支持普通文本和 OpenClaw 风格 JSON，为后续多 Agent 编排预留接口。
4. **Prompt 工程化管理**：将不同节点的 Prompt 统一放在 `prompts.py`，方便迭代和版本管理。
5. **Mock 调试模式**：不依赖真实 API Key 也能验证流程，适合演示、调试和测试。
6. **批量处理能力**：支持 JSON 文件批量运行和 `/batch-invoke` 批量 API，单条失败不会中断整个批次。
7. **运行记录存储**：使用 SQLite 保存成功和失败任务，支持 `/runs` 和 `/runs/{run_id}` 查询历史记录。
8. **流式输出**：CLI 支持按节点查看中间结果，方便观察工作流执行过程。

## 后续计划

- 增加 `tests/`，覆盖输入适配、mock workflow、API health
- 增加 Dockerfile，支持一键部署
- 增加内容质量评测样例，记录标题、标签、正文改写效果
- 增加更多平台内容模板，例如公众号、知乎、视频脚本
- 将 `openclaw` 输入扩展为更明确的任务 schema
