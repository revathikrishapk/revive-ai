import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


AUDIT_LOG_PATH = Path("data/audit_log.jsonl")


def log_event(
    event_id: str,
    stage: str,
    details: dict[str, Any],
    output_path: Path = AUDIT_LOG_PATH,
) -> None:
    """
    Append one immutable record to the audit trail.
    Existing records are never modified or deleted.
    """

    output_path.parent.mkdir(parents=True, exist_ok=True)

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_id": event_id,
        "stage": stage,
        "details": details,
    }

    with open(output_path, "a", encoding="utf-8") as file:
        file.write(json.dumps(record) + "\n")