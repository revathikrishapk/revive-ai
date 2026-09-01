from collections import Counter, defaultdict

from app.schema import PaymentType, RecoveryAction


def build_batch_report(results: list[dict]) -> dict:
    """
    Build aggregate metrics for a Revive recovery batch.

    Tracks:

    - revenue at risk
    - gross revenue recovered
    - retry costs
    - net recovered revenue
    - revenue protected by guardrails
    - recovery attempts
    - successful recoveries
    - failed recovery attempts
    - escalations

    Also provides breakdowns by payment type,
    failure category, decision reason, and event.
    """

    total_at_risk = 0.0
    total_recovered = 0.0
    total_retry_cost = 0.0
    total_net_recovered = 0.0
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
            "retry_cost": 0.0,
            "net_recovered": 0.0,
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
            "retry_cost": 0.0,
            "net_recovered": 0.0,
            "protected": 0.0,
        },
        PaymentType.SUBSCRIPTION.value: {
            "events": 0,
            "at_risk": 0.0,
            "recovered": 0.0,
            "retry_cost": 0.0,
            "net_recovered": 0.0,
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
            result.get(
                "recovered_amount",
                0.0,
            )
        )

        retry_cost = float(
            result.get(
                "retry_cost",
                0.0,
            )
        )

        # Prefer executor-calculated net value.
        # Fall back safely for older result objects.
        net_recovered_amount = float(
            result.get(
                "net_recovered_amount",
                recovered_amount - retry_cost,
            )
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

        total_retry_cost += retry_cost

        total_net_recovered += (
            net_recovered_amount
        )

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

        if (
            action
            == RecoveryAction.ESCALATE_TO_HUMAN.value
        ):
            escalated_count += 1

        # -------------------------------------------------
        # Protected revenue
        # -------------------------------------------------

        if action in {
            RecoveryAction.ESCALATE_TO_HUMAN.value,
            RecoveryAction.STOP.value,
            "stop",
        }:

            total_protected += event.amount

        # -------------------------------------------------
        # Payment type statistics
        # -------------------------------------------------

        payment_type_stats[
            payment_type
        ]["events"] += 1

        payment_type_stats[
            payment_type
        ]["at_risk"] += event.amount

        payment_type_stats[
            payment_type
        ]["recovered"] += recovered_amount

        payment_type_stats[
            payment_type
        ]["retry_cost"] += retry_cost

        payment_type_stats[
            payment_type
        ]["net_recovered"] += (
            net_recovered_amount
        )

        if action in {
            RecoveryAction.ESCALATE_TO_HUMAN.value,
            RecoveryAction.STOP.value,
            "stop",
        }:

            payment_type_stats[
                payment_type
            ]["protected"] += event.amount

        # -------------------------------------------------
        # Failure category statistics
        # -------------------------------------------------

        stats = category_stats[category]

        stats["events"] += 1

        stats["at_risk"] += event.amount

        stats["recovered"] += recovered_amount

        stats["retry_cost"] += retry_cost

        stats["net_recovered"] += (
            net_recovered_amount
        )

        if action == RecoveryAction.RETRY_PAYMENT.value:

            stats["recovery_attempts"] += 1

            if recovery_status == "recovered":
                stats["successful_recoveries"] += 1

            elif recovery_status == "failed":
                stats["failed_recoveries"] += 1

        if action in {
            RecoveryAction.ESCALATE_TO_HUMAN.value,
            RecoveryAction.STOP.value,
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
        # Event summary
        # -------------------------------------------------

        event_summaries.append(
            {
                "event_id": event.event_id,
                "payment_type": payment_type,
                "amount": event.amount,
                "failure_message": (
                    event.failure_message
                ),

                "diagnosis": category,
                "confidence": diagnosis.confidence,
                "reasoning": diagnosis.reasoning,

                "decision": action,
                "decision_reason": (
                    decision.reason.value
                ),

                "retry_cadence": (
                    decision.retry_cadence.value
                ),

                "status": result.get(
                    "status"
                ),

                "recovery_status": (
                    recovery_status
                ),

                "recovered_amount": (
                    recovered_amount
                ),

                "retry_cost": retry_cost,

                "net_recovered_amount": (
                    net_recovered_amount
                ),
            }
        )

    # =====================================================
    # ROUND OVERALL VALUES
    # =====================================================

    total_at_risk = round(
        total_at_risk,
        2,
    )

    total_recovered = round(
        total_recovered,
        2,
    )

    total_retry_cost = round(
        total_retry_cost,
        2,
    )

    total_net_recovered = round(
        total_net_recovered,
        2,
    )

    total_protected = round(
        total_protected,
        2,
    )

    # =====================================================
    # RECOVERY RATE
    # =====================================================

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

    # =====================================================
    # NET RECOVERY RATE
    # =====================================================

    net_recovery_rate = (
        round(
            total_net_recovered
            / total_at_risk
            * 100,
            2,
        )
        if total_at_risk > 0
        else 0.0
    )

    # =====================================================
    # ESCALATION RATE
    # =====================================================

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

    # =====================================================
    # ATTEMPT SUCCESS RATE
    # =====================================================

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

    # =====================================================
    # PAYMENT TYPE FORMATTING
    # =====================================================

    for stats in payment_type_stats.values():

        stats["at_risk"] = round(
            stats["at_risk"],
            2,
        )

        stats["recovered"] = round(
            stats["recovered"],
            2,
        )

        stats["retry_cost"] = round(
            stats["retry_cost"],
            2,
        )

        stats["net_recovered"] = round(
            stats["net_recovered"],
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

        stats["net_recovery_rate"] = (
            round(
                stats["net_recovered"]
                / stats["at_risk"]
                * 100,
                2,
            )
            if stats["at_risk"] > 0
            else 0.0
        )

    # =====================================================
    # CATEGORY FORMATTING
    # =====================================================

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

        stats["retry_cost"] = round(
            stats["retry_cost"],
            2,
        )

        stats["net_recovered"] = round(
            stats["net_recovered"],
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

        stats["net_recovery_rate"] = (
            round(
                stats["net_recovered"]
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

        formatted_category_stats[
            category
        ] = stats

    # =====================================================
    # FINAL REPORT
    # =====================================================

    return {
        "events_processed": len(results),

        "total_at_risk": total_at_risk,

        "total_recovered": total_recovered,

        "total_retry_cost": total_retry_cost,

        "total_net_recovered": (
            total_net_recovered
        ),

        "total_protected": total_protected,

        "recovery_rate": recovery_rate,

        "net_recovery_rate": (
            net_recovery_rate
        ),

        "recovery_attempts": (
            recovery_attempts
        ),

        "successful_recoveries": (
            successful_recoveries
        ),

        "failed_recoveries": (
            failed_recoveries
        ),

        "recovery_attempt_success_rate": (
            recovery_attempt_success_rate
        ),

        "escalated_count": (
            escalated_count
        ),

        "escalation_rate": (
            escalation_rate
        ),

        "by_payment_type": (
            payment_type_stats
        ),

        "by_failure_category": (
            formatted_category_stats
        ),

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
    print(
        "              REVIVE BATCH REPORT"
    )
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
        f"Gross revenue recovered: "
        f"₹{report['total_recovered']:,.2f}"
    )

    print(
        f"Retry costs: "
        f"₹{report['total_retry_cost']:,.2f}"
    )

    print(
        f"Net revenue recovered: "
        f"₹{report['total_net_recovered']:,.2f}"
    )

    print(
        f"Revenue protected: "
        f"₹{report['total_protected']:,.2f}"
    )

    print(
        f"Gross recovery rate: "
        f"{report['recovery_rate']:.2f}%"
    )

    print(
        f"Net recovery rate: "
        f"{report['net_recovery_rate']:.2f}%"
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
            f"  Retry cost: "
            f"₹{stats['retry_cost']:,.2f}"
        )

        print(
            f"  Net recovered: "
            f"₹{stats['net_recovered']:,.2f}"
        )

        print(
            f"  Protected: "
            f"₹{stats['protected']:,.2f}"
        )

        print(
            f"  Recovery rate: "
            f"{stats['recovery_rate']:.2f}%"
        )

    print(
        "\n--- RECOVERY BY FAILURE CATEGORY ---"
    )

    for category, stats in (
        report[
            "by_failure_category"
        ].items()
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
            f"  Retry cost: "
            f"₹{stats['retry_cost']:,.2f}"
        )

        print(
            f"  Net recovered: "
            f"₹{stats['net_recovered']:,.2f}"
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
        report[
            "decision_reason_counts"
        ].items()
    ):

        print(
            f"{reason}: {count}"
        )

    print("\n--- ACTIONS ---")

    for action, count in (
        report[
            "action_counts"
        ].items()
    ):

        print(
            f"{action}: {count}"
        )

    print("=" * 60)