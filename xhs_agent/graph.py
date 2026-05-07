from __future__ import annotations

from typing import Any, Optional, cast

from langgraph.graph import END, START, StateGraph

from xhs_agent.io import normalize_openclaw_instruction
from xhs_agent.nodes import (
    build_framework,
    generate_cover_prompt,
    generate_keywords,
    generate_titles,
    humanize_copy,
    select_title,
)
from xhs_agent.state import XHSWorkflowState


def create_graph():
    graph_builder = StateGraph(XHSWorkflowState)
    graph_builder.add_node("build_framework", build_framework)
    graph_builder.add_node("generate_titles", generate_titles)
    graph_builder.add_node("select_title", select_title)
    graph_builder.add_node("generate_keywords", generate_keywords)
    graph_builder.add_node("humanize_copy", humanize_copy)
    graph_builder.add_node("generate_cover_prompt", generate_cover_prompt)

    graph_builder.add_edge(START, "build_framework")
    graph_builder.add_edge("build_framework", "generate_titles")
    graph_builder.add_edge("generate_titles", "select_title")
    graph_builder.add_edge("select_title", "generate_keywords")
    graph_builder.add_edge("generate_keywords", "humanize_copy")
    graph_builder.add_edge("humanize_copy", "generate_cover_prompt")
    graph_builder.add_edge("generate_cover_prompt", END)
    return graph_builder.compile()


graph = create_graph()


def run_xhs_workflow(payload: str | dict[str, Any]) -> XHSWorkflowState:
    instruction, source = normalize_openclaw_instruction(payload)
    return cast(XHSWorkflowState, graph.invoke({"instruction": instruction, "source": source}))


def stream_xhs_workflow(payload: str | dict[str, Any]):
    instruction, source = normalize_openclaw_instruction(payload)
    for event in graph.stream({"instruction": instruction, "source": source}):
        yield event


def format_result(result: XHSWorkflowState, section: Optional[str] = None) -> str:
    sections = {
        "framework": result.get("framework", ""),
        "titles": result.get("titles", ""),
        "selected_title": result.get("selected_title", ""),
        "keywords": result.get("keywords", ""),
        "final_copy": result.get("final_copy", ""),
        "cover_prompt": result.get("cover_prompt", ""),
    }
    if section:
        return sections.get(section, "")

    return "\n\n".join(
        [
            "=== 内容框架与草稿 ===\n" + sections["framework"],
            "=== 标题 ===\n" + sections["titles"],
            "=== 选中标题 ===\n" + sections["selected_title"],
            "=== 关键词与标签 ===\n" + sections["keywords"],
            "=== 去 AI 味最终版 ===\n" + sections["final_copy"],
            "=== 封面图提示词 ===\n" + sections["cover_prompt"],
        ]
    )
