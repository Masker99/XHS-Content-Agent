from __future__ import annotations

import os
from typing import cast

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_deepseek import ChatDeepSeek
from pydantic import SecretStr

load_dotenv()

_llm: ChatDeepSeek | None = None


def build_llm() -> ChatDeepSeek:
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY environment variable is not set.")

    return ChatDeepSeek(
        model=os.getenv("DEEPSEEK_MODEL", "deepseek-v4-pro"),
        api_key=SecretStr(api_key),
        temperature=float(os.getenv("DEEPSEEK_TEMPERATURE", "0.7")),
    )


def invoke_llm(system_prompt: str, user_prompt: str) -> str:
    if os.getenv("XHS_WORKFLOW_MOCK") == "1":
        return (
            "[MOCK OUTPUT]\n"
            f"System: {system_prompt[:80]}\n"
            f"User: {user_prompt[:240]}..."
        )

    global _llm
    if _llm is None:
        _llm = build_llm()

    response = cast(ChatDeepSeek, _llm).invoke(
        [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
    )
    return str(response.content).strip()
