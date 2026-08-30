import json
from pathlib import Path

from fastapi import FastAPI, HTTPException

from app.orchestrator import run_batch
from app.reporting import build_batch_report


app = FastAPI(
    title="Revive AI",
    description="AI-powered revenue recovery with deterministic guardrails.",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "revive-ai",
    }


@app.post("/run-batch")
def run_recovery_batch(count: int = 80):
    if count < 1 or count > 500:
        raise HTTPException(
            status_code=400,
            detail="Batch size must be between 1 and 500.",
        )

    results = run_batch(count)
    report = build_batch_report(results)

    return report


@app.get("/audit-log/{event_id}")
def get_audit_log(event_id: str):
    audit_path = Path("data/audit_log.jsonl")

    if not audit_path.exists():
        raise HTTPException(
            status_code=404,
            detail="No audit log found. Run a batch first.",
        )

    records = []

    with open(audit_path, "r", encoding="utf-8") as file:
        for line in file:
            record = json.loads(line)

            if record["event_id"] == event_id:
                records.append(record)

    if not records:
        raise HTTPException(
            status_code=404,
            detail=f"No audit records found for event: {event_id}",
        )

    return {
        "event_id": event_id,
        "audit_trail": records,
    }