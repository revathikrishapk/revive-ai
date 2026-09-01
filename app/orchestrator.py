from app.audit_log import log_event
from app.executor import RecoveryExecutor
from app.fsm import RecoveryFSM, RecoveryState
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
    Process one payment through the Revive FSM.

    Architecture:

    Ingestion
        ↓
    Validation
        ↓
    AI Diagnosis
        ↓
    Deterministic Policy
        ↓
    Execution
        ↓
    Audit
    """

    fsm = RecoveryFSM()

    # -----------------------------------------------------
    # RECEIVED
    # -----------------------------------------------------

    log_event(
        event_id=event.event_id,
        stage="RECEIVED",
        details={
            "state": fsm.state.value,
        },
    )

    # -----------------------------------------------------
    # VALIDATED
    # -----------------------------------------------------

    fsm.transition(
        RecoveryState.VALIDATED
    )

    log_event(
        event_id=event.event_id,
        stage="VALIDATED",
        details={
            "state": fsm.state.value,
        },
    )

    # -----------------------------------------------------
    # DIAGNOSING
    # -----------------------------------------------------

    fsm.transition(
        RecoveryState.DIAGNOSING
    )

    log_event(
        event_id=event.event_id,
        stage="DIAGNOSING",
        details={
            "state": fsm.state.value,
        },
    )

    # -----------------------------------------------------
    # AI DIAGNOSIS
    # -----------------------------------------------------

    diagnosis = diagnose_failure(event)

    fsm.transition(
        RecoveryState.DIAGNOSED
    )

    log_event(
        event_id=event.event_id,
        stage="DIAGNOSED",
        details={
            "state": fsm.state.value,
            "category": diagnosis.category.value,
            "confidence": diagnosis.confidence,
            "reasoning": diagnosis.reasoning,
        },
    )

    # -----------------------------------------------------
    # DETERMINISTIC POLICY
    # -----------------------------------------------------

    fsm.transition(
        RecoveryState.DECIDING
    )

    log_event(
        event_id=event.event_id,
        stage="DECIDING",
        details={
            "state": fsm.state.value,
        },
    )

    decision = decide_action(
        event,
        diagnosis,
    )

    fsm.transition(
        RecoveryState.DECIDED
    )

    log_event(
        event_id=event.event_id,
        stage="DECIDED",
        details={
            "state": fsm.state.value,
            "action": decision.action.value,
            "reason": decision.reason.value,
            "retry_cadence": decision.retry_cadence.value,
        },
    )

    # -----------------------------------------------------
    # STOP / ESCALATE
    # -----------------------------------------------------

    if decision.action.value == "escalate_to_human":

        fsm.transition(
            RecoveryState.ESCALATED
        )

        log_event(
            event_id=event.event_id,
            stage="ESCALATED",
            details={
                "state": fsm.state.value,
            },
        )

        fsm.transition(
            RecoveryState.COMPLETED
        )

        log_event(
            event_id=event.event_id,
            stage="COMPLETED",
            details={
                "state": fsm.state.value,
            },
        )

        return {
            "event_id": event.event_id,
            "event": event,
            "diagnosis": diagnosis,
            "decision": decision,
            "result": {
                "event_id": event.event_id,
                "action": decision.action.value,
                "status": "not_executed",
                "execution_status": "not_executed",
                "recovery_status": "not_attempted",
                "recovered_amount": 0.0,
            },
        }

    # -----------------------------------------------------
    # STOPPED
    # -----------------------------------------------------

    if decision.action.value == "stop":

        fsm.transition(
            RecoveryState.STOPPED
        )

        log_event(
            event_id=event.event_id,
            stage="STOPPED",
            details={
                "state": fsm.state.value,
            },
        )

        fsm.transition(
            RecoveryState.COMPLETED
        )

        log_event(
            event_id=event.event_id,
            stage="COMPLETED",
            details={
                "state": fsm.state.value,
            },
        )

        return {
            "event_id": event.event_id,
            "event": event,
            "diagnosis": diagnosis,
            "decision": decision,
            "result": {
                "event_id": event.event_id,
                "action": decision.action.value,
                "status": "not_executed",
                "execution_status": "not_executed",
                "recovery_status": "not_attempted",
                "recovered_amount": 0.0,
            },
        }

    # -----------------------------------------------------
    # EXECUTION
    # -----------------------------------------------------

    fsm.transition(
        RecoveryState.EXECUTING
    )

    log_event(
        event_id=event.event_id,
        stage="EXECUTING",
        details={
            "state": fsm.state.value,
        },
    )

    result = executor.execute(
        event=event,
        action=decision.action,
        failure_category=diagnosis.category.value,
    )

    # -----------------------------------------------------
    # COMPLETED
    # -----------------------------------------------------

    fsm.transition(
        RecoveryState.COMPLETED
    )

    log_event(
        event_id=event.event_id,
        stage="COMPLETED",
        details={
            "state": fsm.state.value,
            "execution_result": result,
        },
    )

    return {
        "event_id": event.event_id,
        "event": event,
        "diagnosis": diagnosis,
        "decision": decision,
        "result": result,
    }


def run_batch(
    count: int = 80,
) -> list[dict]:
    """
    Generate and process a batch of payment events.
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