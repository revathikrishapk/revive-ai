from app.executor import RecoveryExecutor
from app.policy_engine import decide_action
from app.schema import (
    Diagnosis,
    FailedPaymentEvent,
    FailureCategory,
    PaymentType,
    RecoveryAction,
    DecisionReason,
)


def make_event(
    amount=1000.0,
    retry_count=0,
    payment_type=PaymentType.ONE_OFF,
    failure_message="Network connection interrupted",
):
    return FailedPaymentEvent(
        event_id="test-safety-event",
        payment_type=payment_type,
        amount=amount,
        currency="INR",
        failure_message=failure_message,
        retry_count=retry_count,
        subscription_id=(
            "sub_test123"
            if payment_type == PaymentType.SUBSCRIPTION
            else None
        ),
    )


def test_unknown_diagnosis_is_never_retried():
    event = make_event()

    diagnosis = Diagnosis(
        category=FailureCategory.UNKNOWN,
        confidence=0.0,
        reasoning="Unable to classify failure.",
    )

    decision = decide_action(event, diagnosis)

    assert decision.action == RecoveryAction.ESCALATE_TO_HUMAN


def test_low_confidence_diagnosis_is_never_retried():
    event = make_event()

    diagnosis = Diagnosis(
        category=FailureCategory.NETWORK_ERROR,
        confidence=0.40,
        reasoning="Weak evidence of network failure.",
    )

    decision = decide_action(event, diagnosis)

    assert decision.action == RecoveryAction.ESCALATE_TO_HUMAN


def test_fraud_diagnosis_is_never_retried():
    event = make_event(
        failure_message="Transaction blocked for security review"
    )

    diagnosis = Diagnosis(
        category=FailureCategory.FRAUD_HOLD,
        confidence=0.99,
        reasoning="Strong fraud/security signal.",
    )

    decision = decide_action(event, diagnosis)

    assert decision.action != RecoveryAction.RETRY_PAYMENT


def test_retry_cap_prevents_execution():
    event = make_event(retry_count=3)

    diagnosis = Diagnosis(
        category=FailureCategory.NETWORK_ERROR,
        confidence=0.95,
        reasoning="Temporary network failure.",
    )

    decision = decide_action(event, diagnosis)

    assert decision.action != RecoveryAction.RETRY_PAYMENT


def test_economic_floor_prevents_execution():
    event = make_event(amount=50.0)

    diagnosis = Diagnosis(
        category=FailureCategory.NETWORK_ERROR,
        confidence=0.95,
        reasoning="Temporary network failure.",
    )

    decision = decide_action(event, diagnosis)

    assert decision.action != RecoveryAction.RETRY_PAYMENT


def test_duplicate_event_cannot_execute_twice():
    executor = RecoveryExecutor()

    event = make_event()

    first = executor.execute(
        event=event,
        action=RecoveryAction.RETRY_PAYMENT,
        failure_category="network_error",
    )

    second = executor.execute(
        event=event,
        action=RecoveryAction.RETRY_PAYMENT,
        failure_category="network_error",
    )

    assert first["status"] == "executed"
    assert second["status"] == "duplicate_skipped"


def test_escalation_never_reaches_executor():
    executor = RecoveryExecutor()

    event = make_event(
        failure_message="Transaction blocked for security review"
    )

    result = executor.execute(
        event=event,
        action=RecoveryAction.ESCALATE_TO_HUMAN,
        failure_category="fraud_hold",
    )

    assert result["status"] == "not_executed"
    assert result["recovered_amount"] == 0.0


def test_unknown_category_has_zero_recovery_probability():
    executor = RecoveryExecutor()

    event = make_event()

    result = executor.execute(
        event=event,
        action=RecoveryAction.RETRY_PAYMENT,
        failure_category="unknown",
    )

    assert result["status"] == "executed"
    assert result["recovery_probability"] == 0.0
    assert result["recovered_amount"] == 0.0