from __future__ import annotations

from typing_extensions import TypedDict


class XHSWorkflowState(TypedDict, total=False):
    """State passed between LangGraph nodes."""

    instruction: str
    source: str
    framework: str
    draft: str
    titles: str
    selected_title: str
    keywords: str
    final_copy: str
    cover_prompt: str


def require_state_value(state: XHSWorkflowState, key: str) -> str:
    value = state.get(key)
    if value is None:
        raise ValueError(f"Missing workflow state field: {key}")
    return str(value)
