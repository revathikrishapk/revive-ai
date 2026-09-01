import json

from app.llm_agent import DiagnosisAgent
from app.schema import (
    Diagnosis,
    FailedPaymentEvent,
    FailureCategory,
    PaymentType,
    RecoveryAction,
)
from app.policy_engine import decide_action


def make_event():
    return FailedPaymentEvent(
        event_id="ai-failure-test",
        payment_type=PaymentType.ONE_OFF,
        amount=2500.0,
        currency="INR",
        failure_message="Network connection interrupted",
        retry_count=0,
        subscription_id=None,
    )


def test_malformed_json_falls_back_to_unknown(monkeypatch):
    agent = DiagnosisAgent()

    # Simulate an available OpenRouter client.
    agent.client = object()

    attempts = {"count": 0}

    def fake_call(event):
        attempts["count"] += 1

        raise json.JSONDecodeError(
            "Invalid JSON",
            "not-json",
            0,
        )

    monkeypatch.setattr(
        agent,
        "_call_openrouter",
        fake_call,
    )

    diagnosis = agent.diagnose(make_event())

    assert attempts["count"] == 3
    assert diagnosis.category == FailureCategory.UNKNOWN
    assert diagnosis.confidence == 0.0


def test_invalid_category_falls_back_to_unknown(monkeypatch):
    agent = DiagnosisAgent()

    agent.client = object()

    attempts = {"count": 0}

    def fake_call(event):
        attempts["count"] += 1

        # Simulate malformed AI data before
        # Pydantic validation.
        return {
            "category": "made_up_category",
            "confidence": 0.95,
            "reasoning": "Invalid category",
        }

    monkeypatch.setattr(
        agent,
        "_call_openrouter",
        fake_call,
    )

    diagnosis = agent.diagnose(make_event())

    assert attempts["count"] == 3
    assert diagnosis.category == FailureCategory.UNKNOWN
    assert diagnosis.confidence == 0.0


def test_ai_failure_cannot_create_retry_decision():
    event = make_event()

    diagnosis = Diagnosis(
        category=FailureCategory.UNKNOWN,
        confidence=0.0,
        reasoning="AI failure fallback.",
    )

    decision = decide_action(
        event,
        diagnosis,
    )

    assert (
        decision.action
        == RecoveryAction.ESCALATE_TO_HUMAN
    )


def test_valid_ai_output_is_still_accepted(monkeypatch):
    agent = DiagnosisAgent()

    agent.client = object()

    def fake_call(event):
        return Diagnosis(
            category=FailureCategory.NETWORK_ERROR,
            confidence=0.94,
            reasoning="Temporary network failure.",
        )

    monkeypatch.setattr(
        agent,
        "_call_openrouter",
        fake_call,
    )

    diagnosis = agent.diagnose(make_event())

    assert (
        diagnosis.category
        == FailureCategory.NETWORK_ERROR
    )

    assert diagnosis.confidence == 0.94