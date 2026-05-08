from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from xhs_agent import run_xhs_workflow


app = FastAPI(title="XHS Content Agent", version="0.1.0")


class WorkflowRequest(BaseModel):
    instruction: str | None = Field(default=None, description="Plain text instruction.")
    openclaw: dict[str, Any] | None = Field(default=None, description="OpenClaw command payload.")


class BatchWorkflowRequest(BaseModel):
    instructions: list[str] = Field(
        min_length=1,
        max_length=20,
        description="Plain text instructions to run as separate workflow tasks.",
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def _format_workflow_result(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source": result.get("source"),
        "framework": result.get("framework"),
        "titles": result.get("titles"),
        "selected_title": result.get("selected_title"),
        "keywords": result.get("keywords"),
        "final_copy": result.get("final_copy"),
        "cover_prompt": result.get("cover_prompt"),
    }


@app.post("/invoke")
def invoke_workflow(request: WorkflowRequest) -> dict[str, Any]:
    payload: str | dict[str, Any]
    if request.openclaw is not None:
        payload = request.openclaw
    elif request.instruction:
        payload = request.instruction
    else:
        raise HTTPException(status_code=400, detail="Either instruction or openclaw is required.")

    try:
        result = run_xhs_workflow(payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return _format_workflow_result(result)


@app.post("/batch-invoke")
def batch_invoke_workflow(request: BatchWorkflowRequest) -> dict[str, list[dict[str, Any]]]:
    results: list[dict[str, Any]] = []

    for index, instruction in enumerate(request.instructions, start=1):
        item_id = f"item_{index:03d}"
        if not instruction.strip():
            results.append(
                {
                    "id": item_id,
                    "instruction": instruction,
                    "status": "failed",
                    "error": "Instruction cannot be empty.",
                }
            )
            continue

        try:
            result = run_xhs_workflow(instruction)
            results.append(
                {
                    "id": item_id,
                    "instruction": instruction,
                    "status": "success",
                    "result": _format_workflow_result(result),
                }
            )
        except Exception as exc:
            results.append(
                {
                    "id": item_id,
                    "instruction": instruction,
                    "status": "failed",
                    "error": str(exc),
                }
            )

    return {"results": results}
