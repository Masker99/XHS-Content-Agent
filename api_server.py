from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from xhs_agent.service import WorkflowRunError, run_workflow_with_storage, save_failed_input
from xhs_agent.storage import get_workflow_run, list_workflow_runs


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


@app.post("/invoke")
def invoke_workflow(request: WorkflowRequest) -> dict[str, Any]:
    payload: str | dict[str, Any]
    instruction_for_record: str
    source_for_record: str
    if request.openclaw is not None:
        payload = request.openclaw
        instruction_for_record = str(request.openclaw)
        source_for_record = "openclaw"
    elif request.instruction:
        payload = request.instruction
        instruction_for_record = request.instruction
        source_for_record = "text"
    else:
        raise HTTPException(status_code=400, detail="Either instruction or openclaw is required.")

    try:
        return run_workflow_with_storage(
            payload,
            instruction=instruction_for_record,
            source=source_for_record,
        )
    except WorkflowRunError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/batch-invoke")
def batch_invoke_workflow(request: BatchWorkflowRequest) -> dict[str, list[dict[str, Any]]]:
    results: list[dict[str, Any]] = []

    for index, instruction in enumerate(request.instructions, start=1):
        item_id = f"item_{index:03d}"
        if not instruction.strip():
            run_id = save_failed_input(
                instruction=instruction,
                source="text",
                error="Instruction cannot be empty.",
                metadata={"batch_item_id": item_id},
            )
            results.append(
                {
                    "id": item_id,
                    "run_id": run_id,
                    "instruction": instruction,
                    "status": "failed",
                    "error": "Instruction cannot be empty.",
                }
            )
            continue

        try:
            result = run_workflow_with_storage(
                instruction,
                instruction=instruction,
                source="text",
                metadata={"batch_item_id": item_id},
            )
            results.append(
                {
                    "id": item_id,
                    "run_id": result["run_id"],
                    "instruction": instruction,
                    "status": "success",
                    "result": result,
                }
            )
        except WorkflowRunError as exc:
            # run_workflow_with_storage already persisted the failed run.
            results.append(
                {
                    "id": item_id,
                    "run_id": exc.run_id,
                    "instruction": instruction,
                    "status": "failed",
                    "error": str(exc),
                }
            )

    return {"results": results}


@app.get("/runs")
def list_runs(limit: int = 20) -> dict[str, list[dict[str, Any]]]:
    safe_limit = min(max(limit, 1), 100)
    return {"runs": list_workflow_runs(limit=safe_limit)}


@app.get("/runs/{run_id}")
def get_run(run_id: str) -> dict[str, Any]:
    run = get_workflow_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Workflow run not found.")
    return run
