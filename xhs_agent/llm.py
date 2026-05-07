from __future__ import annotations

import os
import time
from typing import cast

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_deepseek import ChatDeepSeek
from pydantic import SecretStr

load_dotenv()

_llm: ChatDeepSeek | None = None


def _get_int_env(name: str, default: int) -> int:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    try:
        value = int(raw_value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer.") from exc
    if value < 1:
        raise ValueError(f"{name} must be greater than or equal to 1.")
    return value


def _get_float_env(name: str, default: float) -> float:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    try:
        value = float(raw_value)
    except ValueError as exc:
        raise ValueError(f"{name} must be a number.") from exc
    if value < 0:
        raise ValueError(f"{name} must be greater than or equal to 0.")
    return value


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

    max_retries = _get_int_env("XHS_LLM_MAX_RETRIES", 3)
    backoff_base = _get_float_env("XHS_LLM_RETRY_BACKOFF_BASE", 1.0)
    last_error: Exception | None = None

    for attempt in range(1, max_retries + 1):
        try:
            response = cast(ChatDeepSeek, _llm).invoke(
                [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_prompt),
                ]
            )
            content = str(response.content).strip()
            if not content:
                raise ValueError("LLM returned empty content.")
            return content
        except Exception as exc:
            last_error = exc
            if attempt < max_retries:
                time.sleep(backoff_base * (2 ** (attempt - 1)))

    raise RuntimeError(f"LLM invocation failed after {max_retries} attempts: {last_error}")
