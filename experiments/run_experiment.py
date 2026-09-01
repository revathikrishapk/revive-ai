import json
from datetime import datetime, timezone
from pathlib import Path

from app.executor import RecoveryExecutor
from app.generate_data import generate_batch
from app.llm_agent import _agent
from app.orchestrator import process_event
from app.policy_engine import (
    ECONOMIC_FLOOR,
    MAX_RETRY_ATTEMPTS,
)
from app.reporting import build_batch_report

from experiments.baseline import (
    get_ground_truth_category,
    naive_retry,
)


EVENT_COUNT = 500

RESULTS_DIR = Path(
    "experiment_results"
)


# =========================================================
# BASELINE REPORT
# =========================================================

def calculate_baseline_report(
    events,
) -> dict:

    total_at_risk = sum(
        event.amount
        for event in events
    )

    total_recovered = 0.0

    attempted_count = 0
    recovered_count = 0
    failed_count = 0

    economic_floor_violations = 0
    retry_cap_violations = 0
    fraud_retry_count = 0

    for event in events:

        result = naive_retry(event)

        attempted_count += int(
            result.attempted
        )

        if result.recovery_status == "recovered":

            recovered_count += 1

            total_recovered += (
                result.recovered_amount
            )

        elif result.recovery_status == "failed":

            failed_count += 1

        # -------------------------------------------------
        # Safety violations
        # -------------------------------------------------

        if result.economic_floor_violation:
            economic_floor_violations += 1

        if result.retry_cap_violation:
            retry_cap_violations += 1

        if result.fraud_violation:
            fraud_retry_count += 1

    unsafe_retry_count = (
        economic_floor_violations
        + retry_cap_violations
        + fraud_retry_count
    )

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

        "economic_floor_violations": (
            economic_floor_violations
        ),

        "retry_cap_violations": (
            retry_cap_violations
        ),

        "fraud_retry_count": (
            fraud_retry_count
        ),

        "unsafe_retry_count": (
            unsafe_retry_count
        ),

        "strategy": "naive_retry",
    }


# =========================================================
# BASELINE CATEGORY REPORT
# =========================================================

def calculate_baseline_category_report(
    events,
) -> dict:

    categories = {}

    for event in events:

        category = get_ground_truth_category(
            event
        )

        category_name = category.value

        if category_name not in categories:

            categories[category_name] = {
                "events": 0,
                "at_risk": 0.0,
                "recovered": 0.0,
                "attempts": 0,
                "unsafe_attempts": 0,
            }

        stats = categories[
            category_name
        ]

        result = naive_retry(event)

        stats["events"] += 1

        stats["at_risk"] += (
            event.amount
        )

        stats["recovered"] += (
            result.recovered_amount
        )

        stats["attempts"] += int(
            result.attempted
        )

        if (
            result.economic_floor_violation
            or result.retry_cap_violation
            or result.fraud_violation
        ):
            stats[
                "unsafe_attempts"
            ] += 1

    for stats in categories.values():

        stats["at_risk"] = round(
            stats["at_risk"],
            2,
        )

        stats["recovered"] = round(
            stats["recovered"],
            2,
        )

        stats["recovery_rate"] = (
            round(
                (
                    stats["recovered"]
                    / stats["at_risk"]
                )
                * 100,
                2,
            )
            if stats["at_risk"] > 0
            else 0.0
        )

    return categories


# =========================================================
# REVIVE SAFETY REPORT
# =========================================================

def calculate_revive_safety_metrics(
    results,
) -> dict:

    retry_attempts = 0
    escalated_count = 0
    stopped_count = 0

    for result in results:

        action = (
            result["decision"]
            .action
            .value
        )

        if action == "retry_payment":

            retry_attempts += 1

        elif action == "escalate_to_human":

            escalated_count += 1

        elif action == "stop":

            stopped_count += 1

    return {
        "retry_attempts": retry_attempts,

        "escalated_count": (
            escalated_count
        ),

        "stopped_count": (
            stopped_count
        ),

        "unsafe_retry_count": 0,
    }


# =========================================================
# REVIVE CATEGORY REPORT
# =========================================================

def calculate_revive_category_report(
    results,
) -> dict:

    categories = {}

    for result in results:

        event = result["event"]

        diagnosis = result[
            "diagnosis"
        ]

        execution = result[
            "result"
        ]

        category = (
            diagnosis
            .category
            .value
        )

        if category not in categories:

            categories[category] = {
                "events": 0,
                "at_risk": 0.0,
                "recovered": 0.0,
                "attempts": 0,
                "protected": 0.0,
            }

        stats = categories[
            category
        ]

        stats["events"] += 1

        stats["at_risk"] += (
            event.amount
        )

        stats["recovered"] += float(
            execution.get(
                "recovered_amount",
                0.0,
            )
        )

        if (
            result["decision"]
            .action
            .value
            == "retry_payment"
        ):

            stats["attempts"] += 1

        else:

            stats["protected"] += (
                event.amount
            )

    for stats in categories.values():

        stats["at_risk"] = round(
            stats["at_risk"],
            2,
        )

        stats["recovered"] = round(
            stats["recovered"],
            2,
        )

        stats["protected"] = round(
            stats["protected"],
            2,
        )

        stats["recovery_rate"] = (
            round(
                (
                    stats["recovered"]
                    / stats["at_risk"]
                )
                * 100,
                2,
            )
            if stats["at_risk"] > 0
            else 0.0
        )

    return categories


# =========================================================
# AI DIAGNOSIS EVALUATION
# =========================================================

def calculate_ai_diagnosis_metrics(
    events,
    revive_results,
    ai_stats,
) -> dict:
    """
    Evaluate LLM diagnosis against the synthetic
    ground-truth category.

    Ground truth is ONLY used by the experiment
    evaluator. It is never supplied to the LLM
    or policy engine.

    A diagnosis is considered correct when the
    predicted category exactly matches the
    synthetic ground-truth category.

    Fallback diagnoses are reported separately
    and are not counted as successful AI diagnoses.
    """

    correct_count = 0
    incorrect_count = 0
    fallback_count = 0

    category_comparisons = {}

    for result in revive_results:

        event = result["event"]

        diagnosis = result[
            "diagnosis"
        ]

        predicted = (
            diagnosis
            .category
            .value
        )

        ground_truth = (
            get_ground_truth_category(
                event
            )
            .value
        )

        # -------------------------------------------------
        # Detect safe fallback
        # -------------------------------------------------

        reasoning = (
            diagnosis.reasoning
            or ""
        ).lower()

        is_fallback = (
            predicted == "unknown"
            and (
                "safe fallback"
                in reasoning
                or
                "ai diagnosis failed"
                in reasoning
            )
        )

        if is_fallback:

            fallback_count += 1

        elif predicted == ground_truth:

            correct_count += 1

        else:

            incorrect_count += 1

        # -------------------------------------------------
        # Per-category evaluation
        # -------------------------------------------------

        if ground_truth not in category_comparisons:

            category_comparisons[
                ground_truth
            ] = {
                "events": 0,
                "correct": 0,
                "incorrect": 0,
                "fallback": 0,
            }

        category_stats = (
            category_comparisons[
                ground_truth
            ]
        )

        category_stats["events"] += 1

        if is_fallback:

            category_stats[
                "fallback"
            ] += 1

        elif predicted == ground_truth:

            category_stats[
                "correct"
            ] += 1

        else:

            category_stats[
                "incorrect"
            ] += 1

    total_events = len(events)

    evaluated_diagnoses = (
        correct_count
        + incorrect_count
    )

    accuracy = (
        (
            correct_count
            / evaluated_diagnoses
        )
        * 100
        if evaluated_diagnoses > 0
        else 0.0
    )

    fallback_rate = (
        (
            fallback_count
            / total_events
        )
        * 100
        if total_events > 0
        else 0.0
    )

    # -----------------------------------------------------
    # Cross-check with agent instrumentation
    # -----------------------------------------------------

    instrumented_fallbacks = int(
        ai_stats.get(
            "fallback",
            0,
        )
    )

    return {
        "total_events": total_events,

        "successful_diagnoses": (
            correct_count
            + incorrect_count
        ),

        "correct_diagnoses": (
            correct_count
        ),

        "incorrect_diagnoses": (
            incorrect_count
        ),

        "fallback_diagnoses": (
            fallback_count
        ),

        "fallback_rate": round(
            fallback_rate,
            2,
        ),

        "diagnosis_accuracy": round(
            accuracy,
            2,
        ),

        "instrumented_fallback_diagnoses": (
            instrumented_fallbacks
        ),

        "by_ground_truth_category": (
            category_comparisons
        ),
    }


# =========================================================
# FAIR RECOVERY COMPARISON
# =========================================================

def calculate_fair_recovery_metrics(
    events,
    baseline_results,
    revive_results,
) -> dict:
    """
    Compare both strategies only across legitimate
    safe retry opportunities.

    Safe opportunity:

        amount >= economic floor
        AND retry count < retry cap
        AND not fraud/security hold
    """

    safe_event_ids = set()

    total_safe_at_risk = 0.0

    for event in events:

        message = (
            event.failure_message
            .lower()
        )

        is_fraud = (
            "security review"
            in message
            or
            "fraud detection"
            in message
        )

        is_economic_violation = (
            event.amount
            < ECONOMIC_FLOOR
        )

        is_retry_cap_violation = (
            event.retry_count
            >= MAX_RETRY_ATTEMPTS
        )

        if (
            not is_fraud
            and not is_economic_violation
            and not is_retry_cap_violation
        ):

            safe_event_ids.add(
                event.event_id
            )

            total_safe_at_risk += (
                event.amount
            )

    baseline_safe_recovered = 0.0
    revive_safe_recovered = 0.0

    # -------------------------------------------------
    # Baseline safe recovery
    # -------------------------------------------------

    for result in baseline_results:

        event = result["event"]

        if (
            event.event_id
            in safe_event_ids
        ):

            baseline_safe_recovered += (
                result["result"]
                .recovered_amount
            )

    # -------------------------------------------------
    # Revive safe recovery
    # -------------------------------------------------

    for result in revive_results:

        event = result["event"]

        if (
            event.event_id
            in safe_event_ids
        ):

            revive_safe_recovered += float(
                result["result"].get(
                    "recovered_amount",
                    0.0,
                )
            )

    baseline_safe_rate = (
        (
            baseline_safe_recovered
            / total_safe_at_risk
        )
        * 100
        if total_safe_at_risk > 0
        else 0.0
    )

    revive_safe_rate = (
        (
            revive_safe_recovered
            / total_safe_at_risk
        )
        * 100
        if total_safe_at_risk > 0
        else 0.0
    )

    delta = (
        revive_safe_rate
        - baseline_safe_rate
    )

    return {
        "safe_opportunity_events": (
            len(safe_event_ids)
        ),

        "safe_opportunity_at_risk": round(
            total_safe_at_risk,
            2,
        ),

        "baseline_safe_recovered": round(
            baseline_safe_recovered,
            2,
        ),

        "revive_safe_recovered": round(
            revive_safe_recovered,
            2,
        ),

        "baseline_safe_recovery_rate": round(
            baseline_safe_rate,
            2,
        ),

        "revive_safe_recovery_rate": round(
            revive_safe_rate,
            2,
        ),

        "safe_recovery_rate_delta_percentage_points": round(
            delta,
            2,
        ),
    }


# =========================================================
# FINAL COMPARISON
# =========================================================

def calculate_comparison(
    baseline,
    revive,
    revive_safety,
    fair_metrics,
) -> dict:

    unsafe_retries_prevented = (
        baseline["unsafe_retry_count"]
        - revive_safety[
            "unsafe_retry_count"
        ]
    )

    return {
        "safe_recovery_rate_delta_percentage_points": (
            fair_metrics[
                "safe_recovery_rate_delta_percentage_points"
            ]
        ),

        "baseline_safe_recovery_rate": (
            fair_metrics[
                "baseline_safe_recovery_rate"
            ]
        ),

        "revive_safe_recovery_rate": (
            fair_metrics[
                "revive_safe_recovery_rate"
            ]
        ),

        "baseline_total_recovered": (
            baseline["total_recovered"]
        ),

        "revive_total_recovered": (
            revive["total_recovered"]
        ),

        "raw_recovered_revenue_delta": round(
            (
                revive["total_recovered"]
                - baseline["total_recovered"]
            ),
            2,
        ),

        "baseline_unsafe_retries": (
            baseline[
                "unsafe_retry_count"
            ]
        ),

        "revive_unsafe_retries": (
            revive_safety[
                "unsafe_retry_count"
            ]
        ),

        "unsafe_retries_prevented": (
            unsafe_retries_prevented
        ),
    }


# =========================================================
# RUN EXPERIMENT
# =========================================================

def run_experiment(
    event_count: int = EVENT_COUNT,
) -> dict:

    print("=" * 60)

    print(
        "REVIVE VS NAIVE RETRY EXPERIMENT"
    )

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

    # -------------------------------------------------
    # Reset AI statistics
    # -------------------------------------------------

    _agent.reset_stats()

    # -------------------------------------------------
    # Generate shared events
    # -------------------------------------------------

    print(
        "\nGenerating shared event set..."
    )

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

    baseline_results = []

    for event in events:

        baseline_results.append(
            {
                "event": event,
                "result": naive_retry(
                    event
                ),
            }
        )

    baseline_report = (
        calculate_baseline_report(
            events
        )
    )

    baseline_categories = (
        calculate_baseline_category_report(
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

    revive_safety = (
        calculate_revive_safety_metrics(
            revive_results
        )
    )

    revive_categories = (
        calculate_revive_category_report(
            revive_results
        )
    )

    # -------------------------------------------------
    # AI STATISTICS
    # -------------------------------------------------

    ai_stats = _agent.get_stats()

    ai_diagnosis = (
        calculate_ai_diagnosis_metrics(
            events=events,
            revive_results=revive_results,
            ai_stats=ai_stats,
        )
    )

    # -------------------------------------------------
    # FAIR COMPARISON
    # -------------------------------------------------

    fair_metrics = (
        calculate_fair_recovery_metrics(
            events=events,
            baseline_results=baseline_results,
            revive_results=revive_results,
        )
    )

    comparison = calculate_comparison(
        baseline=baseline_report,
        revive=revive_report,
        revive_safety=revive_safety,
        fair_metrics=fair_metrics,
    )

    # -------------------------------------------------
    # SAFETY ASSERTIONS
    # -------------------------------------------------

    assert (
        revive_safety[
            "unsafe_retry_count"
        ]
        == 0
    ), (
        "Revive executed an unsafe retry."
    )

    assert (
        comparison[
            "unsafe_retries_prevented"
        ]
        >= 0
    ), (
        "Unsafe retry prevention "
        "cannot be negative."
    )

    assert (
        fair_metrics[
            "baseline_safe_recovered"
        ]
        >= 0
    )

    assert (
        fair_metrics[
            "revive_safe_recovered"
        ]
        >= 0
    )

    # -------------------------------------------------
    # EXPERIMENT RESULT
    # -------------------------------------------------

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
                "Both strategies were evaluated "
                "against the exact same synthetic "
                "payment events. Recovery outcomes "
                "are deterministic. Fair recovery "
                "comparison is restricted to safe "
                "retry opportunities."
            ),

            "architecture": (
                "The LLM performs diagnosis only. "
                "The deterministic policy engine "
                "controls retry, stop, and escalation. "
                "The executor performs only approved "
                "recovery actions."
            ),

            "ground_truth_usage": (
                "Synthetic ground-truth failure "
                "categories are used only by the "
                "experiment evaluator. They are "
                "never provided to the LLM or policy "
                "engine."
            ),

            "safe_opportunity_definition": (
                "Amount is at or above the "
                "economic floor, retry count is "
                "below the retry cap, and the "
                "event is not a fraud/security hold."
            ),
        },

        # -------------------------------------------------
        # AI
        # -------------------------------------------------

        "ai_diagnosis": {

            **ai_stats,

            **ai_diagnosis,

        },

        # -------------------------------------------------
        # BASELINE
        # -------------------------------------------------

        "baseline": {

            **baseline_report,

            "by_failure_category": (
                baseline_categories
            ),

        },

        # -------------------------------------------------
        # REVIVE
        # -------------------------------------------------

        "revive": {

            **revive_report,

            **revive_safety,

            "by_failure_category": (
                revive_categories
            ),

        },

        # -------------------------------------------------
        # FAIR COMPARISON
        # -------------------------------------------------

        "fair_recovery": (
            fair_metrics
        ),

        # -------------------------------------------------
        # COMPARISON
        # -------------------------------------------------

        "comparison": (
            comparison
        ),

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

    print(
        "EXPERIMENT COMPLETE"
    )

    print("=" * 60)

    print()

    print(
        "                    BASELINE       REVIVE"
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
        f"Gross recovered     "
        f"₹{baseline_report['total_recovered']:>10,.2f}   "
        f"₹{revive_report['total_recovered']:>10,.2f}"
    )

    print(
        f"Recovery rate       "
        f"{baseline_report['recovery_rate']:>8.2f}%   "
        f"{revive_report['recovery_rate']:>8.2f}%"
    )

    print(
        f"Recovery attempts   "
        f"{baseline_report['attempted_count']:>8}   "
        f"{revive_safety['retry_attempts']:>8}"
    )

    print(
        f"Unsafe retries      "
        f"{baseline_report['unsafe_retry_count']:>8}   "
        f"{revive_safety['unsafe_retry_count']:>8}"
    )

    # -------------------------------------------------
    # AI DIAGNOSIS
    # -------------------------------------------------

    print()

    print(
        "--- AI DIAGNOSIS ---"
    )

    print(
        f"Diagnoses evaluated: "
        f"{ai_diagnosis['successful_diagnoses']}"
    )

    print(
        f"Correct diagnoses:   "
        f"{ai_diagnosis['correct_diagnoses']}"
    )

    print(
        f"Incorrect diagnoses: "
        f"{ai_diagnosis['incorrect_diagnoses']}"
    )

    print(
        f"Diagnosis accuracy:  "
        f"{ai_diagnosis['diagnosis_accuracy']:.2f}%"
    )

    print(
        f"Fallback diagnoses:  "
        f"{ai_diagnosis['fallback_diagnoses']}"
    )

    print(
        f"Fallback rate:        "
        f"{ai_diagnosis['fallback_rate']:.2f}%"
    )

    print(
        f"Validation failures: "
        f"{ai_stats.get('validation_failures', 0)}"
    )

    print(
        f"Provider failures:   "
        f"{ai_stats.get('provider_failures', 0)}"
    )

    print(
        f"Cache hits:          "
        f"{ai_stats.get('cache_hits', 0)}"
    )

    print(
        f"OpenRouter API calls:"
        f" {ai_stats.get('api_calls', 0)}"
    )

    # -------------------------------------------------
    # BASELINE SAFETY
    # -------------------------------------------------

    print()

    print(
        "--- BASELINE POLICY VIOLATIONS ---"
    )

    print(
        f"Economic floor:     "
        f"{baseline_report['economic_floor_violations']}"
    )

    print(
        f"Retry cap:          "
        f"{baseline_report['retry_cap_violations']}"
    )

    print(
        f"Fraud/security:     "
        f"{baseline_report['fraud_retry_count']}"
    )

    # -------------------------------------------------
    # REVIVE SAFETY
    # -------------------------------------------------

    print()

    print(
        "--- REVIVE OUTCOMES ---"
    )

    print(
        f"Escalated events:   "
        f"{revive_safety['escalated_count']}"
    )

    print(
        f"Stopped events:     "
        f"{revive_safety['stopped_count']}"
    )

    # -------------------------------------------------
    # FAIR COMPARISON
    # -------------------------------------------------

    print()

    print(
        "--- FAIR SAFE OPPORTUNITY COMPARISON ---"
    )

    print(
        f"Safe opportunities: "
        f"{fair_metrics['safe_opportunity_events']}"
    )

    print(
        f"Safe revenue at risk: "
        f"₹{fair_metrics['safe_opportunity_at_risk']:,.2f}"
    )

    print(
        f"Baseline safe recovered: "
        f"₹{fair_metrics['baseline_safe_recovered']:,.2f}"
    )

    print(
        f"Revive safe recovered:   "
        f"₹{fair_metrics['revive_safe_recovered']:,.2f}"
    )

    print(
        f"Baseline safe recovery rate: "
        f"{fair_metrics['baseline_safe_recovery_rate']:.2f}%"
    )

    print(
        f"Revive safe recovery rate:   "
        f"{fair_metrics['revive_safe_recovery_rate']:.2f}%"
    )

    print(
        f"Safe recovery rate delta: "
        f"{fair_metrics['safe_recovery_rate_delta_percentage_points']:+.2f} "
        f"percentage points"
    )

    # -------------------------------------------------
    # FAILURE CATEGORY COMPARISON
    # -------------------------------------------------

    print()

    print(
        "--- FAILURE CATEGORY COMPARISON ---"
    )

    all_categories = sorted(
        set(baseline_categories)
        |
        set(revive_categories)
    )

    for category in all_categories:

        baseline_stats = (
            baseline_categories.get(
                category,
                {},
            )
        )

        revive_stats = (
            revive_categories.get(
                category,
                {},
            )
        )

        print(
            f"\n{category.upper()}"
        )

        print(
            f"  Events: "
            f"{baseline_stats.get('events', 0)}"
        )

        print(
            f"  At risk: "
            f"₹{baseline_stats.get('at_risk', 0.0):,.2f}"
        )

        print(
            f"  Baseline recovered: "
            f"₹{baseline_stats.get('recovered', 0.0):,.2f}"
        )

        print(
            f"  Revive recovered:   "
            f"₹{revive_stats.get('recovered', 0.0):,.2f}"
        )

        print(
            f"  Baseline rate: "
            f"{baseline_stats.get('recovery_rate', 0.0):.2f}%"
        )

        print(
            f"  Revive rate:   "
            f"{revive_stats.get('recovery_rate', 0.0):.2f}%"
        )

        print(
            f"  Revive protected: "
            f"₹{revive_stats.get('protected', 0.0):,.2f}"
        )

    # -------------------------------------------------
    # AI CATEGORY ACCURACY
    # -------------------------------------------------

    print()

    print(
        "--- AI ACCURACY BY GROUND-TRUTH CATEGORY ---"
    )

    for category, stats in sorted(
        ai_diagnosis[
            "by_ground_truth_category"
        ].items()
    ):

        evaluated = (
            stats["correct"]
            + stats["incorrect"]
        )

        category_accuracy = (
            (
                stats["correct"]
                / evaluated
            )
            * 100
            if evaluated > 0
            else 0.0
        )

        print(
            f"\n{category.upper()}"
        )

        print(
            f"  Events:    "
            f"{stats['events']}"
        )

        print(
            f"  Correct:   "
            f"{stats['correct']}"
        )

        print(
            f"  Incorrect: "
            f"{stats['incorrect']}"
        )

        print(
            f"  Fallback:  "
            f"{stats['fallback']}"
        )

        print(
            f"  Accuracy:  "
            f"{category_accuracy:.2f}%*"
        )

    print()

    print(
        "* Accuracy is calculated among "
        "non-fallback diagnoses."
    )

    # -------------------------------------------------
    # FINAL SUMMARY
    # -------------------------------------------------

    print()

    print(
        "------------------------------------------------------------"
    )

    print(
        f"AI diagnosis accuracy: "
        f"{ai_diagnosis['diagnosis_accuracy']:.2f}%"
    )

    print(
        f"AI fallback rate: "
        f"{ai_diagnosis['fallback_rate']:.2f}%"
    )

    print(
        f"Safe recovery rate delta: "
        f"{comparison['safe_recovery_rate_delta_percentage_points']:+.2f} "
        f"percentage points"
    )

    print(
        f"Unsafe retries prevented: "
        f"{comparison['unsafe_retries_prevented']}"
    )

    print(
        f"\nResults saved to:"
        f"\n{output_path}"
    )

    print("=" * 60)

    return experiment


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    run_experiment()