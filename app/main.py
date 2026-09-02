import json
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.orchestrator import run_batch
from app.reporting import build_batch_report


app = FastAPI(
    title="Revive AI",
    description="AI-powered revenue recovery with deterministic guardrails.",
    version="0.1.0",
)


app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)


templates = Jinja2Templates(
    directory="app/templates"
)


# =========================================================
# DASHBOARD
# =========================================================

@app.get("/")
def dashboard(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )


# =========================================================
# HEALTH
# =========================================================

@app.get("/health")
def health_check():

    return {
        "status": "healthy",
        "service": "revive-ai",
    }


# =========================================================
# RUN RECOVERY BATCH
# =========================================================

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


# =========================================================
# AUDIT LOG
# =========================================================

@app.get("/audit-log/{event_id}")
def get_audit_log(event_id: str):

    audit_path = Path(
        "data/audit_log.jsonl"
    )

    # -----------------------------------------------------
    # Audit file does not exist
    # -----------------------------------------------------

    if not audit_path.exists():

        raise HTTPException(
            status_code=404,
            detail="No audit log found. Run a batch first.",
        )


    records = []


    # -----------------------------------------------------
    # Read JSONL safely
    # -----------------------------------------------------

    try:

        with open(
            audit_path,
            "r",
            encoding="utf-8",
        ) as file:

            for line_number, line in enumerate(
                file,
                start=1,
            ):

                line = line.strip()

                # Ignore empty lines
                if not line:
                    continue


                try:

                    record = json.loads(line)

                except json.JSONDecodeError:

                    print(
                        f"Skipping malformed audit record "
                        f"at line {line_number}."
                    )

                    continue


                # Make sure the decoded object is a dict
                if not isinstance(record, dict):

                    print(
                        f"Skipping invalid audit record "
                        f"at line {line_number}."
                    )

                    continue


                # Ignore records without matching event_id
                if record.get("event_id") != event_id:
                    continue


                records.append(record)


    except OSError as error:

        raise HTTPException(
            status_code=500,
            detail=f"Unable to read audit log: {error}",
        )


    # -----------------------------------------------------
    # Event not found
    # -----------------------------------------------------

    if not records:

        raise HTTPException(
            status_code=404,
            detail=(
                f"No audit records found for event: "
                f"{event_id}"
            ),
        )


    # -----------------------------------------------------
    # Return complete audit trail
    # -----------------------------------------------------

    return {
        "event_id": event_id,
        "audit_trail": records,
    }


# =========================================================
# LATEST EXPERIMENT
# =========================================================

@app.get("/experiment/latest")
def get_latest_experiment():

    results_dir = Path(
        "experiment_results"
    )


    if not results_dir.exists():

        raise HTTPException(
            status_code=404,
            detail="No experiment results found.",
        )


    files = sorted(
        results_dir.glob(
            "experiment_*.json"
        )
    )


    if not files:

        raise HTTPException(
            status_code=404,
            detail="No experiment results found.",
        )


    latest_file = files[-1]


    try:

        with open(
            latest_file,
            "r",
            encoding="utf-8",
        ) as file:

            return json.load(file)


    except json.JSONDecodeError as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Latest experiment file contains "
                f"invalid JSON: {error}"
            ),
        )

    except OSError as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Unable to read latest experiment: "
                f"{error}"
            ),
        )