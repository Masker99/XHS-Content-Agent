from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from xhs_agent import run_xhs_workflow  # noqa: E402


def _format_result(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "source": result.get("source"),
        "framework": result.get("framework"),
        "titles": result.get("titles"),
        "selected_title": result.get("selected_title"),
        "keywords": result.get("keywords"),
        "final_copy": result.get("final_copy"),
        "cover_prompt": result.get("cover_prompt"),
    }


def load_tasks(input_path: Path) -> list[dict[str, Any]]:
    data = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Batch input must be a JSON array.")

    tasks: list[dict[str, Any]] = []
    for index, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Batch item {index} must be an object.")
        item_id = str(item.get("id") or f"item_{index:03d}")
        instruction = str(item.get("instruction") or "").strip()
        tasks.append({"id": item_id, "instruction": instruction})
    return tasks


def run_batch(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    total = len(tasks)

    for index, task in enumerate(tasks, start=1):
        item_id = task["id"]
        instruction = task["instruction"]

        if not instruction:
            print(f"[{index}/{total}] {item_id} failed: empty instruction")
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
            workflow_result = run_xhs_workflow(instruction)
            print(f"[{index}/{total}] {item_id} success")
            results.append(
                {
                    "id": item_id,
                    "instruction": instruction,
                    "status": "success",
                    "result": _format_result(workflow_result),
                }
            )
        except Exception as exc:
            print(f"[{index}/{total}] {item_id} failed: {exc}")
            results.append(
                {
                    "id": item_id,
                    "instruction": instruction,
                    "status": "failed",
                    "error": str(exc),
                }
            )

    return results


def save_results(results: list[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run XHS Content Agent tasks in batch.")
    parser.add_argument(
        "--input",
        default="examples/batch_requests.json",
        help="Path to a JSON array of batch tasks.",
    )
    parser.add_argument(
        "--output",
        default="outputs/batch_results.json",
        help="Path to save batch results.",
    )
    args = parser.parse_args()

    input_path = PROJECT_ROOT / args.input
    output_path = PROJECT_ROOT / args.output

    tasks = load_tasks(input_path)
    print(f"Loaded {len(tasks)} tasks.")
    results = run_batch(tasks)
    save_results(results, output_path)
    print(f"Saved results to {output_path}")


if __name__ == "__main__":
    main()
