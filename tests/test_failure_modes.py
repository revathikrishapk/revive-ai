import pytest

from app.executor import RecoveryExecutor
from app.policy_engine import decide_action
from app.schema import (
    Diagnosis,
    DecisionReason,
    FailedPaymentEvent,
    FailureCategory,
    PaymentType,
    RecoveryAction,
    RetryCadence,
)


def make_event(
    amount: float = 1000.0,
    retry_count: int = 0,
) -> FailedPaymentEvent:
    return FailedPaymentEvent(
        event_id="test_event_001",
        payment_type=PaymentType.ONE_OFF,
        amount=amount,
        failure_message="Payment gateway timeout",
        retry_count=retry_count,
    )


def make_diagnosis(
    category: FailureCategory = FailureCategory.NETWORK_ERROR,
    confidence: float = 0.9,
) -> Diagnosis:
    return Diagnosis(
        category=category,
        confidence=confidence,
        reasoning="Test diagnosis",
    )


def test_economic_floor_stops_recovery():
    event = make_event(amount=50.0)
    diagnosis = make_diagnosis()

    decision = decide_action(event, diagnosis)

    assert decision.action == RecoveryAction.STOP
    assert decision.reason == DecisionReason.ECONOMIC_FLOOR


def test_retry_cap_stops_recovery():
    event = make_event(retry_count=3)
    diagnosis = make_diagnosis()

    decision = decide_action(event, diagnosis)

    assert decision.action == RecoveryAction.STOP
    assert decision.reason == DecisionReason.RETRY_CAP_REACHED


def test_low_confidence_escalates_to_human():
    event = make_event()
    diagnosis = make_diagnosis(confidence=0.40)

    decision = decide_action(event, diagnosis)

    assert decision.action == RecoveryAction.ESCALATE_TO_HUMAN
    assert decision.reason == DecisionReason.LOW_CONFIDENCE


def test_fraud_hold_never_auto_retries():
    event = make_event()
    diagnosis = make_diagnosis(
        category=FailureCategory.FRAUD_HOLD,
        confidence=0.99,
    )

    decision = decide_action(event, diagnosis)

    assert decision.action == RecoveryAction.ESCALATE_TO_HUMAN
    assert decision.reason == DecisionReason.FRAUD_HOLD


def test_safe_event_can_retry():
    event = make_event()
    diagnosis = make_diagnosis(
        category=FailureCategory.NETWORK_ERROR,
        confidence=0.90,
    )

    decision = decide_action(event, diagnosis)

    assert decision.action == RecoveryAction.RETRY_PAYMENT
    assert decision.reason == DecisionReason.SAFE_TO_RETRY


def test_duplicate_event_is_not_executed_twice():
    executor = RecoveryExecutor()
    event = make_event()

    first_result = executor.execute(
        event,
        RecoveryAction.RETRY_PAYMENT,
    )

    second_result = executor.execute(
        event,
        RecoveryAction.RETRY_PAYMENT,
    )

    assert first_result["status"] == "executed"
    assert second_result["status"] == "duplicate_skipped"
    assert second_result["recovered_amount"] == 0.0


def test_invalid_confidence_is_rejected():
    with pytest.raises(Exception):
        Diagnosis(
            category=FailureCategory.NETWORK_ERROR,
            confidence=1.5,
            reasoning="Invalid confidence",
        )


def test_unknown_category_is_rejected():
    with pytest.raises(Exception):
        Diagnosis(
            category="random_category",
            confidence=0.9,
            reasoning="Invalid category",
        )

def test_subscription_retry_uses_delayed_cadence():
    event = FailedPaymentEvent(
        event_id="subscription_test_001",
        payment_type=PaymentType.SUBSCRIPTION,
        amount=1000.0,
        failure_message="Subscription mandate execution failed",
        retry_count=0,
        subscription_id="sub_001",
    )

    diagnosis = make_diagnosis(
        category=FailureCategory.MANDATE_FAILURE,
        confidence=0.90,
    )

    decision = decide_action(event, diagnosis)

    assert decision.action == RecoveryAction.RETRY_PAYMENT
    assert decision.retry_cadence == RetryCadence.AFTER_24_HOURS