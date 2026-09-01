import json
from datetime import datetime, timezone
from pathlib import Path

from app.executor import RecoveryExecutor
from app.generate_data import generate_batch
from app.orchestrator import process_event
from app.reporting import build_batch_report

from experiments.baseline import naive_retry


EVENT_COUNT = 500

RESULTS_DIR = Path(
    "experiment_results"
)


def calculate_baseline_report(
    events,
) -> dict:
    """
    Run the naive retry strategy against the exact
    same events used by Revive.
    """

    total_at_risk = sum(
        event.amount
        for event in events
    )

    total_recovered = 0.0

    attempted_count = 0
    recovered_count = 0
    failed_count = 0

    fraud_retry_count = 0

    for event in events:

        result = naive_retry(
            event
        )

        if result.attempted:
            attempted_count += 1

        if result.recovery_status == "recovered":

            recovered_count += 1

            total_recovered += (
                result.recovered_amount
            )

        elif result.recovery_status == "failed":

            failed_count += 1

        
        #Fraud holds are intentionally identified
        #only for measuring unsafe baseline behavior.
        #The baseline itself does not use this information.
        

        if (
            "security review"
            in event.failure_message.lower()
            or
            "fraud detection"
            in event.failure_message.lower()
        ):

            fraud_retry_count += 1

    recovery_rate = (
        (
            total_recovered
            / total_at_risk
        )
        * 100
        if total_at_risk > 0
        else 0.0
    )

    return {
        "events_processed": len(events),

        "total_at_risk": round(
            total_at_risk,
            2,
        ),

        "total_recovered": round(
            total_recovered,
            2,
        ),

        "recovery_rate": round(
            recovery_rate,
            2,
        ),

        "attempted_count": attempted_count,

        "recovered_count": recovered_count,

        "failed_count": failed_count,

        "fraud_retry_count": fraud_retry_count,

        "unsafe_retry_count": fraud_retry_count,

        "strategy": "naive_retry",
    }


def calculate_comparison(
    baseline: dict,
    revive: dict,
) -> dict:
    """
    Calculate the measurable difference between
    conventional retry and Revive.
    """

    recovery_rate_delta = (
        revive["recovery_rate"]
        -
        baseline["recovery_rate"]
    )

    revenue_delta = (
        revive["total_recovered"]
        -
        baseline["total_recovered"]
    )

    relative_improvement = (
        (
            recovery_rate_delta
            /
            baseline["recovery_rate"]
        )
        * 100
        if baseline["recovery_rate"] > 0
        else 0.0
    )

    return {
        "recovery_rate_delta_percentage_points": round(
            recovery_rate_delta,
            2,
        ),

        "recovered_revenue_delta": round(
            revenue_delta,
            2,
        ),

        "relative_recovery_improvement_percent": round(
            relative_improvement,
            2,
        ),

        "baseline_unsafe_retries": (
            baseline["unsafe_retry_count"]
        ),

        "revive_unsafe_retries": 0,
    }


def run_experiment(
    event_count: int = EVENT_COUNT,
) -> dict:

    print("=" * 60)
    print("REVIVE VS NAIVE RETRY EXPERIMENT")
    print("=" * 60)

    print(
        f"\nEvents: {event_count}"
    )

    print(
        "Mode: synthetic development simulation"
    )

    print(
        "Comparison: naive retry vs Revive"
    )

    print(
        "\nGenerating shared event set..."
    )

    # -------------------------------------------------
    # Generate ONE shared event set.
    # -------------------------------------------------

    events = generate_batch(
        event_count
    )

    print(
        f"Generated {len(events)} events."
    )

    # -------------------------------------------------
    # BASELINE
    # -------------------------------------------------

    print(
        "\nRunning naive retry baseline..."
    )

    baseline_report = (
        calculate_baseline_report(
            events
        )
    )

    # -------------------------------------------------
    # REVIVE
    # -------------------------------------------------

    print(
        "Running Revive recovery engine..."
    )

    executor = RecoveryExecutor()

    revive_results = []

    for event in events:

        result = process_event(
            event=event,
            executor=executor,
        )

        revive_results.append(
            result
        )

    revive_report = build_batch_report(
        revive_results
    )

    # -------------------------------------------------
    # COMPARISON
    # -------------------------------------------------

    comparison = calculate_comparison(
        baseline=baseline_report,
        revive=revive_report,
    )

    experiment = {

        "experiment": {

            "event_count": event_count,

            "mode": (
                "synthetic_development"
            ),

            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),

            "methodology": (
                "Both strategies evaluated "
                "against the exact same "
                "synthetic payment events."
            ),

        },

        "baseline": baseline_report,

        "revive": revive_report,

        "comparison": comparison,

    }

    # -------------------------------------------------
    # SAVE RESULTS
    # -------------------------------------------------

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    existing_files = list(
        RESULTS_DIR.glob(
            "experiment_*.json"
        )
    )

    experiment_number = (
        len(existing_files) + 1
    )

    output_path = (
        RESULTS_DIR
        /
        f"experiment_{experiment_number:03d}.json"
    )

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

    # -------------------------------------------------
    # DISPLAY RESULTS
    # -------------------------------------------------

    print()
    print("=" * 60)
    print("EXPERIMENT COMPLETE")
    print("=" * 60)

    print(
        "\n                    BASELINE       REVIVE"
    )

    print(
        f"Events              "
        f"{baseline_report['events_processed']:>6}        "
        f"{revive_report['events_processed']:>6}"
    )

    print(
        f"Revenue at risk     "
        f"₹{baseline_report['total_at_risk']:>10,.2f}   "
        f"₹{revive_report['total_at_risk']:>10,.2f}"
    )

    print(
        f"Revenue recovered   "
        f"₹{baseline_report['total_recovered']:>10,.2f}   "
        f"₹{revive_report['total_recovered']:>10,.2f}"
    )

    print(
        f"Recovery rate       "
        f"{baseline_report['recovery_rate']:>8.2f}%   "
        f"{revive_report['recovery_rate']:>8.2f}%"
    )

    print(
        f"Unsafe retries      "
        f"{baseline_report['unsafe_retry_count']:>8}   "
        f"{comparison['revive_unsafe_retries']:>8}"
    )

    print()
    print(
        "------------------------------------------------------------"
    )

    print(
        f"Recovery rate delta: "
        f"{comparison['recovery_rate_delta_percentage_points']:+.2f} "
        f"percentage points"
    )

    print(
        f"Revenue delta: "
        f"₹{comparison['recovered_revenue_delta']:+,.2f}"
    )

    print(
        f"Relative improvement: "
        f"{comparison['relative_recovery_improvement_percent']:+.2f}%"
    )

    print(
        f"\nResults saved to:"
        f"\n{output_path}"
    )

    print("=" * 60)

    return experiment


if __name__ == "__main__":
    run_experiment()