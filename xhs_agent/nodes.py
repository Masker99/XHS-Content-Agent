from __future__ import annotations

from xhs_agent.llm import invoke_llm
from xhs_agent.prompts import (
    BUILD_FRAMEWORK_SYSTEM,
    COVER_PROMPT_SYSTEM,
    GENERATE_KEYWORDS_SYSTEM,
    GENERATE_TITLES_SYSTEM,
    HUMANIZE_COPY_SYSTEM,
    SELECT_TITLE_SYSTEM,
    build_framework_user,
    generate_cover_prompt_user,
    generate_keywords_user,
    generate_titles_user,
    humanize_copy_user,
    select_title_user,
)
from xhs_agent.state import XHSWorkflowState, require_state_value


def build_framework(state: XHSWorkflowState) -> XHSWorkflowState:
    instruction = require_state_value(state, "instruction")
    result = invoke_llm(BUILD_FRAMEWORK_SYSTEM, build_framework_user(instruction))
    return {"framework": result, "draft": result}


def generate_titles(state: XHSWorkflowState) -> XHSWorkflowState:
    draft = require_state_value(state, "draft")
    return {"titles": invoke_llm(GENERATE_TITLES_SYSTEM, generate_titles_user(draft))}


def select_title(state: XHSWorkflowState) -> XHSWorkflowState:
    draft = require_state_value(state, "draft")
    titles = require_state_value(state, "titles")
    return {"selected_title": invoke_llm(SELECT_TITLE_SYSTEM, select_title_user(draft, titles))}


def generate_keywords(state: XHSWorkflowState) -> XHSWorkflowState:
    draft = require_state_value(state, "draft")
    titles = require_state_value(state, "titles")
    selected_title = require_state_value(state, "selected_title")
    return {
        "keywords": invoke_llm(
            GENERATE_KEYWORDS_SYSTEM,
            generate_keywords_user(draft, titles, selected_title),
        )
    }


def humanize_copy(state: XHSWorkflowState) -> XHSWorkflowState:
    draft = require_state_value(state, "draft")
    titles = require_state_value(state, "titles")
    selected_title = require_state_value(state, "selected_title")
    keywords = require_state_value(state, "keywords")
    return {
        "final_copy": invoke_llm(
            HUMANIZE_COPY_SYSTEM,
            humanize_copy_user(draft, titles, selected_title, keywords),
        )
    }


def generate_cover_prompt(state: XHSWorkflowState) -> XHSWorkflowState:
    final_copy = require_state_value(state, "final_copy")
    selected_title = require_state_value(state, "selected_title")
    keywords = require_state_value(state, "keywords")
    return {
        "cover_prompt": invoke_llm(
            COVER_PROMPT_SYSTEM,
            generate_cover_prompt_user(final_copy, selected_title, keywords),
        )
    }
