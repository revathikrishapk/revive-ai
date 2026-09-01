from collections import Counter, defaultdict

from app.schema import PaymentType, RecoveryAction


def build_batch_report(results: list[dict]) -> dict:
    """
    Build aggregate metrics for a Revive recovery batch.

    The report distinguishes between:

    - revenue at risk
    - revenue recovered
    - revenue protected by guardrails
    - recovery attempts
    - successful recoveries
    - failed recovery attempts
    - escalations

    It also provides breakdowns by payment type and
    diagnosis category.
    """

    total_at_risk = 0.0
    total_recovered = 0.0
    total_protected = 0.0

    recovery_attempts = 0
    successful_recoveries = 0
    failed_recoveries = 0
    escalated_count = 0

    category_stats = defaultdict(
        lambda: {
            "events": 0,
            "at_risk": 0.0,
            "recovered": 0.0,
            "protected": 0.0,
            "recovery_attempts": 0,
            "successful_recoveries": 0,
            "failed_recoveries": 0,
        }
    )

    payment_type_stats = {
        PaymentType.ONE_OFF.value: {
            "events": 0,
            "at_risk": 0.0,
            "recovered": 0.0,
            "protected": 0.0,
        },
        PaymentType.SUBSCRIPTION.value: {
            "events": 0,
            "at_risk": 0.0,
            "recovered": 0.0,
            "protected": 0.0,
        },
    }

    decision_reason_counts = Counter()
    action_counts = Counter()

    event_summaries = []

    for item in results:

        event = item["event"]
        diagnosis = item["diagnosis"]
        decision = item["decision"]
        result = item["result"]

        payment_type = event.payment_type.value
        category = diagnosis.category.value

        recovered_amount = float(
            result.get("recovered_amount", 0.0)
        )

        action = decision.action.value

        recovery_status = result.get(
            "recovery_status",
            "not_attempted",
        )

        # -------------------------------------------------
        # Overall revenue metrics
        # -------------------------------------------------

        total_at_risk += event.amount
        total_recovered += recovered_amount

        # -------------------------------------------------
        # Attempt metrics
        # -------------------------------------------------

        if action == RecoveryAction.RETRY_PAYMENT.value:

            recovery_attempts += 1

            if recovery_status == "recovered":
                successful_recoveries += 1

            elif recovery_status == "failed":
                failed_recoveries += 1

        # -------------------------------------------------
        # Escalation metrics
        # -------------------------------------------------

        if action == RecoveryAction.ESCALATE_TO_HUMAN.value:
            escalated_count += 1

        # -------------------------------------------------
        # Protected revenue
        #
        # An event is considered protected when the policy
        # engine prevents automatic execution.
        #
        # We do NOT count duplicate events as protected.
        # -------------------------------------------------

        if action in {
            RecoveryAction.ESCALATE_TO_HUMAN.value,
            "stop",
        }:
            total_protected += event.amount

        # -------------------------------------------------
        # Payment type statistics
        # -------------------------------------------------

        payment_type_stats[payment_type]["events"] += 1

        payment_type_stats[payment_type]["at_risk"] += (
            event.amount
        )

        payment_type_stats[payment_type]["recovered"] += (
            recovered_amount
        )

        if action in {
            RecoveryAction.ESCALATE_TO_HUMAN.value,
            "stop",
        }:
            payment_type_stats[payment_type]["protected"] += (
                event.amount
            )

        # -------------------------------------------------
        # Failure category statistics
        # -------------------------------------------------

        stats = category_stats[category]

        stats["events"] += 1
        stats["at_risk"] += event.amount
        stats["recovered"] += recovered_amount

        if action == RecoveryAction.RETRY_PAYMENT.value:

            stats["recovery_attempts"] += 1

            if recovery_status == "recovered":
                stats["successful_recoveries"] += 1

            elif recovery_status == "failed":
                stats["failed_recoveries"] += 1

        if action in {
            RecoveryAction.ESCALATE_TO_HUMAN.value,
            "stop",
        }:
            stats["protected"] += event.amount

        # -------------------------------------------------
        # Decision statistics
        # -------------------------------------------------

        decision_reason_counts[
            decision.reason.value
        ] += 1

        action_counts[action] += 1

        # -------------------------------------------------
        # Event summary for dashboard
        # -------------------------------------------------

        event_summaries.append(
            {
                "event_id": event.event_id,
                "payment_type": payment_type,
                "amount": event.amount,
                "failure_message": event.failure_message,
                "diagnosis": category,
                "confidence": diagnosis.confidence,
                "reasoning": diagnosis.reasoning,
                "decision": action,
                "decision_reason": decision.reason.value,
                "retry_cadence": decision.retry_cadence.value,
                "status": result.get("status"),
                "recovery_status": recovery_status,
                "recovered_amount": recovered_amount,
            }
        )

    # -----------------------------------------------------
    # Round monetary values
    # -----------------------------------------------------

    total_at_risk = round(
        total_at_risk,
        2,
    )

    total_recovered = round(
        total_recovered,
        2,
    )

    total_protected = round(
        total_protected,
        2,
    )

    # -----------------------------------------------------
    # Overall recovery rate
    # -----------------------------------------------------

    recovery_rate = (
        round(
            total_recovered
            / total_at_risk
            * 100,
            2,
        )
        if total_at_risk > 0
        else 0.0
    )

    # -----------------------------------------------------
    # Escalation rate
    # -----------------------------------------------------

    escalation_rate = (
        round(
            escalated_count
            / len(results)
            * 100,
            2,
        )
        if results
        else 0.0
    )

    # -----------------------------------------------------
    # Recovery attempt success rate
    # -----------------------------------------------------

    recovery_attempt_success_rate = (
        round(
            successful_recoveries
            / recovery_attempts
            * 100,
            2,
        )
        if recovery_attempts > 0
        else 0.0
    )

    # -----------------------------------------------------
    # Format payment type stats
    # -----------------------------------------------------

    for stats in payment_type_stats.values():

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
                stats["recovered"]
                / stats["at_risk"]
                * 100,
                2,
            )
            if stats["at_risk"] > 0
            else 0.0
        )

    # -----------------------------------------------------
    # Format category stats
    # -----------------------------------------------------

    formatted_category_stats = {}

    for category, stats in category_stats.items():

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
                stats["recovered"]
                / stats["at_risk"]
                * 100,
                2,
            )
            if stats["at_risk"] > 0
            else 0.0
        )

        stats["attempt_success_rate"] = (
            round(
                stats["successful_recoveries"]
                / stats["recovery_attempts"]
                * 100,
                2,
            )
            if stats["recovery_attempts"] > 0
            else 0.0
        )

        formatted_category_stats[category] = stats

    return {
        "events_processed": len(results),
        "total_at_risk": total_at_risk,
        "total_recovered": total_recovered,
        "total_protected": total_protected,
        "recovery_rate": recovery_rate,
        "recovery_attempts": recovery_attempts,
        "successful_recoveries": successful_recoveries,
        "failed_recoveries": failed_recoveries,
        "recovery_attempt_success_rate": (
            recovery_attempt_success_rate
        ),
        "escalated_count": escalated_count,
        "escalation_rate": escalation_rate,
        "by_payment_type": payment_type_stats,
        "by_failure_category": formatted_category_stats,
        "decision_reason_counts": dict(
            decision_reason_counts
        ),
        "action_counts": dict(
            action_counts
        ),
        "events": event_summaries,
    }


def print_batch_report(report: dict) -> None:
    """
    Print a human-readable batch report.
    """

    print("\n" + "=" * 60)
    print("              REVIVE BATCH REPORT")
    print("=" * 60)

    print(
        f"Events processed: "
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
        f"Revenue protected: "
        f"₹{report['total_protected']:,.2f}"
    )

    print(
        f"Overall recovery rate: "
        f"{report['recovery_rate']:.2f}%"
    )

    print("\n--- RECOVERY EXECUTION ---")

    print(
        f"Recovery attempts: "
        f"{report['recovery_attempts']}"
    )

    print(
        f"Successful recoveries: "
        f"{report['successful_recoveries']}"
    )

    print(
        f"Failed recovery attempts: "
        f"{report['failed_recoveries']}"
    )

    print(
        f"Attempt success rate: "
        f"{report['recovery_attempt_success_rate']:.2f}%"
    )

    print("\n--- ESCALATION ---")

    print(
        f"Escalated events: "
        f"{report['escalated_count']}"
    )

    print(
        f"Escalation rate: "
        f"{report['escalation_rate']:.2f}%"
    )

    print("\n--- RECOVERY BY PAYMENT TYPE ---")

    for payment_type, stats in (
        report["by_payment_type"].items()
    ):

        print(
            f"\n{payment_type.upper()}"
        )

        print(
            f"  Events: "
            f"{stats['events']}"
        )

        print(
            f"  At risk: "
            f"₹{stats['at_risk']:,.2f}"
        )

        print(
            f"  Recovered: "
            f"₹{stats['recovered']:,.2f}"
        )

        print(
            f"  Protected: "
            f"₹{stats['protected']:,.2f}"
        )

        print(
            f"  Recovery rate: "
            f"{stats['recovery_rate']:.2f}%"
        )

    print("\n--- RECOVERY BY FAILURE CATEGORY ---")

    for category, stats in (
        report["by_failure_category"].items()
    ):

        print(
            f"\n{category.upper()}"
        )

        print(
            f"  Events: "
            f"{stats['events']}"
        )

        print(
            f"  At risk: "
            f"₹{stats['at_risk']:,.2f}"
        )

        print(
            f"  Recovered: "
            f"₹{stats['recovered']:,.2f}"
        )

        print(
            f"  Recovery rate: "
            f"{stats['recovery_rate']:.2f}%"
        )

        print(
            f"  Attempts: "
            f"{stats['recovery_attempts']}"
        )

    print("\n--- POLICY DECISIONS ---")

    for reason, count in (
        report["decision_reason_counts"].items()
    ):

        print(
            f"{reason}: {count}"
        )

    print("\n--- ACTIONS ---")

    for action, count in (
        report["action_counts"].items()
    ):

        print(
            f"{action}: {count}"
        )

    print("=" * 60)