from app.schema import (
    Diagnosis,
    DecisionReason,
    FailedPaymentEvent,
    FailureCategory,
    PolicyDecision,
    RecoveryAction,
)


ECONOMIC_FLOOR = 100.0
CONFIDENCE_THRESHOLD = 0.55
MAX_RETRY_ATTEMPTS = 3


def decide_action(
    event: FailedPaymentEvent,
    diagnosis: Diagnosis,
) -> PolicyDecision:

    # Guardrail 1: Never pursue trivial amounts
    if event.amount < ECONOMIC_FLOOR:
        return PolicyDecision(
            action=RecoveryAction.STOP,
            reason=DecisionReason.ECONOMIC_FLOOR,
        )

    # Guardrail 2: Hard stopping rule after max retries
    if event.retry_count >= MAX_RETRY_ATTEMPTS:
        return PolicyDecision(
            action=RecoveryAction.STOP,
            reason=DecisionReason.RETRY_CAP_REACHED,
        )

    # Guardrail 3: Fraud holds are never auto-retried
    if diagnosis.category == FailureCategory.FRAUD_HOLD:
        return PolicyDecision(
            action=RecoveryAction.ESCALATE_TO_HUMAN,
            reason=DecisionReason.FRAUD_HOLD,
        )

    # Guardrail 4: Low-confidence AI output cannot trigger action
    if diagnosis.confidence < CONFIDENCE_THRESHOLD:
        return PolicyDecision(
            action=RecoveryAction.ESCALATE_TO_HUMAN,
            reason=DecisionReason.LOW_CONFIDENCE,
        )

    # Safe recovery path
    return PolicyDecision(
        action=RecoveryAction.RETRY_PAYMENT,
        reason=DecisionReason.SAFE_TO_RETRY,
    )