from app.audit_log import log_event
from app.executor import RecoveryExecutor
from app.generate_data import generate_batch
from app.llm_agent import diagnose_failure
from app.policy_engine import decide_action
from app.reporting import build_batch_report, print_batch_report
from app.schema import FailedPaymentEvent


def process_event(
    event: FailedPaymentEvent,
    executor: RecoveryExecutor,
) -> dict:
    """
    Process one failed payment event through the complete
    Revive revenue recovery pipeline.
    """

    # 1. Audit ingestion
    log_event(
        event_id=event.event_id,
        stage="INGESTED",
        details={
            "payment_type": event.payment_type.value,
            "amount": event.amount,
            "currency": event.currency,
            "retry_count": event.retry_count,
        },
    )

    # 2. AI diagnosis
    diagnosis = diagnose_failure(event)

    log_event(
        event_id=event.event_id,
        stage="DIAGNOSED",
        details={
            "category": diagnosis.category.value,
            "confidence": diagnosis.confidence,
            "reasoning": diagnosis.reasoning,
        },
    )

    # 3. Deterministic policy decision
    decision = decide_action(event, diagnosis)

    log_event(
        event_id=event.event_id,
        stage="DECIDED",
        details={
            "action": decision.action.value,
            "reason": decision.reason.value,
            "retry_cadence": decision.retry_cadence.value,
        },
    )

    # 4. Execute ONLY the action approved by the policy engine.
    result = executor.execute(
        event=event,
        action=decision.action,
        failure_category=diagnosis.category.value,
    )

    # 5. Audit execution result
    log_event(
        event_id=event.event_id,
        stage="EXECUTION_RESULT",
        details=result,
    )

    return {
        "event_id": event.event_id,
        "event": event,
        "diagnosis": diagnosis,
        "decision": decision,
        "result": result,
    }


def run_batch(count: int = 80) -> list[dict]:
    """
    Generate and process a batch of failed payment events.
    """

    executor = RecoveryExecutor()
    events = generate_batch(count)

    results = []

    for event in events:
        result = process_event(
            event=event,
            executor=executor,
        )

        results.append(result)

    return results


if __name__ == "__main__":
    results = run_batch(80)

    report = build_batch_report(results)

    print_batch_report(report)