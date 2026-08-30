from collections import Counter

from app.schema import PaymentType, RecoveryAction


def build_batch_report(results: list[dict]) -> dict:
    total_at_risk = 0.0
    total_recovered = 0.0

    category_stats = {
        PaymentType.ONE_OFF.value: {
            "events": 0,
            "at_risk": 0.0,
            "recovered": 0.0,
        },
        PaymentType.SUBSCRIPTION.value: {
            "events": 0,
            "at_risk": 0.0,
            "recovered": 0.0,
        },
    }

    decision_reasons = Counter()
    escalated_count = 0

    for item in results:
        event = item["event"]
        decision = item["decision"]
        result = item["result"]

        payment_type = event.payment_type.value
        recovered_amount = result["recovered_amount"]

        total_at_risk += event.amount
        total_recovered += recovered_amount

        category_stats[payment_type]["events"] += 1
        category_stats[payment_type]["at_risk"] += event.amount
        category_stats[payment_type]["recovered"] += recovered_amount

        decision_reasons[decision.reason.value] += 1

        if decision.action == RecoveryAction.ESCALATE_TO_HUMAN:
            escalated_count += 1

    for stats in category_stats.values():
        stats["at_risk"] = round(stats["at_risk"], 2)
        stats["recovered"] = round(stats["recovered"], 2)

        if stats["at_risk"] > 0:
            stats["recovery_rate"] = round(
                stats["recovered"] / stats["at_risk"] * 100,
                2,
            )
        else:
            stats["recovery_rate"] = 0.0

    total_at_risk = round(total_at_risk, 2)
    total_recovered = round(total_recovered, 2)

    recovery_rate = (
        round(total_recovered / total_at_risk * 100, 2)
        if total_at_risk > 0
        else 0.0
    )

    escalation_rate = (
        round(escalated_count / len(results) * 100, 2)
        if results
        else 0.0
    )

    return {
        "events_processed": len(results),
        "total_at_risk": total_at_risk,
        "total_recovered": total_recovered,
        "recovery_rate": recovery_rate,
        "escalated_count": escalated_count,
        "escalation_rate": escalation_rate,
        "by_payment_type": category_stats,
        "decision_reason_counts": dict(decision_reasons),
    }


def print_batch_report(report: dict) -> None:
    print("\n" + "=" * 50)
    print("           REVIVE BATCH REPORT")
    print("=" * 50)

    print(f"Events processed: {report['events_processed']}")
    print(f"Total at risk: ₹{report['total_at_risk']:,.2f}")
    print(f"Total recovered: ₹{report['total_recovered']:,.2f}")
    print(f"Overall recovery rate: {report['recovery_rate']:.2f}%")

    print("\n--- RECOVERY BY PAYMENT TYPE ---")

    for payment_type, stats in report["by_payment_type"].items():
        print(f"\n{payment_type.upper()}")
        print(f"  Events: {stats['events']}")
        print(f"  At risk: ₹{stats['at_risk']:,.2f}")
        print(f"  Recovered: ₹{stats['recovered']:,.2f}")
        print(f"  Recovery rate: {stats['recovery_rate']:.2f}%")

    print("\n--- ESCALATION ---")
    print(f"Escalated events: {report['escalated_count']}")
    print(f"Escalation rate: {report['escalation_rate']:.2f}%")

    print("\n--- POLICY / STOPPING RULE TRIGGERS ---")

    for reason, count in report["decision_reason_counts"].items():
        print(f"{reason}: {count}")

    print("=" * 50)