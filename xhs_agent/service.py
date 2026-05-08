from __future__ import annotations

import os
import time
from collections.abc import Mapping
from typing import Any
from uuid import uuid4

from xhs_agent.graph import run_xhs_workflow
from xhs_agent.storage import save_workflow_run, utc_now_iso


class WorkflowRunError(RuntimeError):
    def __init__(self, run_id: str, message: str) -> None:
        super().__init__(message)
        self.run_id = run_id


def format_workflow_result(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source": result.get("source"),
        "framework": result.get("framework"),
        "titles": result.get("titles"),
        "selected_title": result.get("selected_title"),
        "keywords": result.get("keywords"),
        "final_copy": result.get("final_copy"),
        "cover_prompt": result.get("cover_prompt"),
    }


def _success_record(
    *,
    run_id: str,
    instruction: str,
    result: Mapping[str, Any],
    created_at: str,
    completed_at: str,
    duration_ms: int,
    metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    formatted = format_workflow_result(result)
    return {
        "id": run_id,
        "source": str(result.get("source") or "unknown"),
        "instruction": instruction,
        "status": "success",
        "model": os.getenv("DEEPSEEK_MODEL", "deepseek-v4-pro"),
        "mock": os.getenv("XHS_WORKFLOW_MOCK") == "1",
        "created_at": created_at,
        "completed_at": completed_at,
        "duration_ms": duration_ms,
        "metadata": dict(metadata or {}),
        **formatted,
    }


def _failed_record(
    *,
    run_id: str,
    source: str,
    instruction: str,
    error: str,
    created_at: str,
    completed_at: str,
    duration_ms: int,
    metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "id": run_id,
        "source": source,
        "instruction": instruction,
        "status": "failed",
        "error": error,
        "model": os.getenv("DEEPSEEK_MODEL", "deepseek-v4-pro"),
        "mock": os.getenv("XHS_WORKFLOW_MOCK") == "1",
        "created_at": created_at,
        "completed_at": completed_at,
        "duration_ms": duration_ms,
        "metadata": dict(metadata or {}),
    }


def run_workflow_with_storage(
    payload: str | dict[str, Any],
    *,
    instruction: str,
    source: str,
    metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    run_id = str(uuid4())
    created_at = utc_now_iso()
    start_time = time.perf_counter()

    try:
        result = run_xhs_workflow(payload)
    except Exception as exc:
        completed_at = utc_now_iso()
        duration_ms = int((time.perf_counter() - start_time) * 1000)
        save_workflow_run(
            _failed_record(
                run_id=run_id,
                source=source,
                instruction=instruction,
                error=str(exc),
                created_at=created_at,
                completed_at=completed_at,
                duration_ms=duration_ms,
                metadata=metadata,
            )
        )
        raise WorkflowRunError(run_id, str(exc)) from exc

    completed_at = utc_now_iso()
    duration_ms = int((time.perf_counter() - start_time) * 1000)
    save_workflow_run(
        _success_record(
            run_id=run_id,
            instruction=instruction,
            result=result,
            created_at=created_at,
            completed_at=completed_at,
            duration_ms=duration_ms,
            metadata=metadata,
        )
    )

    response = format_workflow_result(result)
    response["run_id"] = run_id
    return response


def save_failed_input(
    *,
    instruction: str,
    source: str,
    error: str,
    metadata: Mapping[str, Any] | None = None,
) -> str:
    run_id = str(uuid4())
    timestamp = utc_now_iso()
    save_workflow_run(
        _failed_record(
            run_id=run_id,
            source=source,
            instruction=instruction,
            error=error,
            created_at=timestamp,
            completed_at=timestamp,
            duration_ms=0,
            metadata=metadata,
        )
    )
    return run_id
