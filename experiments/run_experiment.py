import json
from datetime import datetime, timezone
from pathlib import Path

from app.orchestrator import run_batch
from app.reporting import build_batch_report


EVENT_COUNT = 500

RESULTS_DIR = Path("experiment_results")


def run_experiment(
    event_count: int = EVENT_COUNT,
) -> dict:
    """
    Run a reproducible Revive recovery experiment.

    The experiment:
    1. Generates synthetic payment failures.
    2. Processes them through the complete Revive pipeline.
    3. Calculates recovery metrics.
    4. Saves the results as JSON.
    """

    print("=" * 60)
    print("REVIVE RECOVERY EXPERIMENT")
    print("=" * 60)

    print(f"\nEvents: {event_count}")
    print("Mode: synthetic development simulation")
    print("AI provider: mock diagnosis")
    print("\nRunning...\n")

    # Run the complete Revive pipeline.
    results = run_batch(event_count)

    # Calculate aggregate metrics.
    report = build_batch_report(results)

    # Add experiment metadata.
    experiment = {
        "experiment": {
            "event_count": event_count,
            "mode": "synthetic_development",
            "ai_provider": "mock",
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
        },
        "results": report,
    }

    # Create output directory.
    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Find the next experiment number.
    existing_files = list(
        RESULTS_DIR.glob("experiment_*.json")
    )

    experiment_number = len(existing_files) + 1

    output_path = (
        RESULTS_DIR
        / f"experiment_{experiment_number:03d}.json"
    )

    # Save experiment results.
    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            experiment,
            file,
            indent=2,
        )

    # Display summary.
    print("=" * 60)
    print("EXPERIMENT COMPLETE")
    print("=" * 60)

    print(
        f"\nEvents processed: "
        f"{report['events_processed']}"
    )

    print(
        f"Revenue at risk: "
        f"₹{report['total_at_risk']:,.2f}"
    )

    print(
        f"Revenue recovered: "
        f"₹{report['total_recovered']:,.2f}"
    )

    print(
        f"Recovery rate: "
        f"{report['recovery_rate']:.2f}%"
    )

    print(
        f"Escalated events: "
        f"{report['escalated_count']}"
    )

    print(
        f"Escalation rate: "
        f"{report['escalation_rate']:.2f}%"
    )

    print(
        f"\nResults saved to:"
        f"\n{output_path}"
    )

    print("=" * 60)

    return experiment


if __name__ == "__main__":
    run_experiment()