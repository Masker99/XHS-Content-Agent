# Mock Output Example

下面是开启 mock 模式后的示例输出。mock 模式用于验证 LangGraph 工作流能否跑通，不代表真实模型的最终内容质量。

运行命令：

```powershell
$env:XHS_WORKFLOW_MOCK="1"
python cli.py "帮我写一篇小红书笔记，主题是普通上班族如何建立周末复盘习惯" --stream
```

示例输出结构：

```text
--- build_framework 完成 ---
[MOCK OUTPUT]
System: 你是资深小红书内容策划，擅长把 OpenClaw/用户指令拆成可执行的爆款笔记结构...
User: 根据下面的 OpenClaw/用户指令，搭建一篇小红书笔记框架，并产出第一版正文草稿...

--- generate_titles 完成 ---
[MOCK OUTPUT]
System: 你是小红书爆文标题策划...
User: 基于下面的内容框架和正文草稿，生成 8 个小红书标题...

--- select_title 完成 ---
[MOCK OUTPUT]
System: 你是小红书标题主编...
User: 请从下面的标题候选中，选择 1 个最适合发布的小红书标题...

--- generate_keywords 完成 ---
[MOCK OUTPUT]
System: 你是小红书 SEO 和话题标签策略师...
User: 基于下面的文案内容和选中标题，生成小红书发布可用的搜索关键词与话题标签组合...

--- humanize_copy 完成 ---
[MOCK OUTPUT]
System: 你是中文内容编辑，专门去除 AI 写作痕迹...
User: 请对下面的小红书正文草稿做“去 AI 味”改写...

--- generate_cover_prompt 完成 ---
[MOCK OUTPUT]
System: 你是小红书知识分享封面图提示词设计师...
User: 请根据下面的选中标题、最终正文和话题标签，生成一段完整的“小红书封面图图片生成提示词”...
```

真实模型模式下，输出会包含完整的内容框架、标题、关键词、最终正文和封面提示词。
