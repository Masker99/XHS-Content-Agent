from __future__ import annotations

import json
import os
import sqlite3
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DEFAULT_DB_PATH = Path("data/xhs_agent.db")


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def get_db_path() -> Path:
    return Path(os.getenv("XHS_DB_PATH", str(DEFAULT_DB_PATH)))


def _connect() -> sqlite3.Connection:
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS workflow_runs (
                id TEXT PRIMARY KEY,
                source TEXT NOT NULL,
                instruction TEXT NOT NULL,
                status TEXT NOT NULL,
                framework TEXT,
                titles TEXT,
                selected_title TEXT,
                keywords TEXT,
                final_copy TEXT,
                cover_prompt TEXT,
                error TEXT,
                model TEXT,
                mock INTEGER NOT NULL DEFAULT 0,
                metadata_json TEXT,
                created_at TEXT NOT NULL,
                completed_at TEXT NOT NULL,
                duration_ms INTEGER NOT NULL
            )
            """
        )
        conn.commit()


def save_workflow_run(record: Mapping[str, Any]) -> None:
    init_db()
    metadata = record.get("metadata") or {}
    metadata_json = json.dumps(metadata, ensure_ascii=False) if metadata else None

    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO workflow_runs (
                id,
                source,
                instruction,
                status,
                framework,
                titles,
                selected_title,
                keywords,
                final_copy,
                cover_prompt,
                error,
                model,
                mock,
                metadata_json,
                created_at,
                completed_at,
                duration_ms
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record["id"],
                record.get("source", "unknown"),
                record.get("instruction", ""),
                record["status"],
                record.get("framework"),
                record.get("titles"),
                record.get("selected_title"),
                record.get("keywords"),
                record.get("final_copy"),
                record.get("cover_prompt"),
                record.get("error"),
                record.get("model"),
                1 if record.get("mock") else 0,
                metadata_json,
                record["created_at"],
                record["completed_at"],
                record["duration_ms"],
            ),
        )
        conn.commit()


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    item = dict(row)
    item["mock"] = bool(item["mock"])
    metadata_json = item.pop("metadata_json", None)
    item["metadata"] = json.loads(metadata_json) if metadata_json else {}
    return item


def list_workflow_runs(limit: int = 20) -> list[dict[str, Any]]:
    init_db()
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT
                id,
                source,
                instruction,
                status,
                selected_title,
                error,
                model,
                mock,
                metadata_json,
                created_at,
                completed_at,
                duration_ms
            FROM workflow_runs
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [_row_to_dict(row) for row in rows]


def get_workflow_run(run_id: str) -> dict[str, Any] | None:
    init_db()
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM workflow_runs WHERE id = ?",
            (run_id,),
        ).fetchone()
    if row is None:
        return None
    return _row_to_dict(row)
