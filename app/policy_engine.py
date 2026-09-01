from app.schema import (
    Diagnosis,
    DecisionReason,
    FailedPaymentEvent,
    FailureCategory,
    PaymentType,
    PolicyDecision,
    RecoveryAction,
    RetryCadence,
)


ECONOMIC_FLOOR = 100.0
CONFIDENCE_THRESHOLD = 0.55
MAX_RETRY_ATTEMPTS = 3


def decide_action(
    event: FailedPaymentEvent,
    diagnosis: Diagnosis,
) -> PolicyDecision:

    # -------------------------------------------------
    # HARD SAFETY GUARDRAILS
    # -------------------------------------------------

    # 1. Economic floor
    if event.amount < ECONOMIC_FLOOR:
        return PolicyDecision(
            action=RecoveryAction.STOP,
            reason=DecisionReason.ECONOMIC_FLOOR,
        )

    # 2. Retry cap
    if event.retry_count >= MAX_RETRY_ATTEMPTS:
        return PolicyDecision(
            action=RecoveryAction.STOP,
            reason=DecisionReason.RETRY_CAP_REACHED,
        )

    # 3. Fraud/security holds are never automated
    if diagnosis.category == FailureCategory.FRAUD_HOLD:
        return PolicyDecision(
            action=RecoveryAction.ESCALATE_TO_HUMAN,
            reason=DecisionReason.FRAUD_HOLD,
        )

    # 4. Low-confidence AI cannot authorize recovery
    if diagnosis.confidence < CONFIDENCE_THRESHOLD:
        return PolicyDecision(
            action=RecoveryAction.ESCALATE_TO_HUMAN,
            reason=DecisionReason.LOW_CONFIDENCE,
        )

    # -------------------------------------------------
    # CATEGORY-AWARE STRATEGY
    # -------------------------------------------------

    category = diagnosis.category

    # -------------------------------------------------
    # NETWORK ERROR
    # -------------------------------------------------

    if category == FailureCategory.NETWORK_ERROR:

        if event.payment_type == PaymentType.SUBSCRIPTION:

            cadence = (
                RetryCadence.AFTER_24_HOURS
                if event.retry_count == 0
                else RetryCadence.AFTER_72_HOURS
            )

        else:
            cadence = RetryCadence.IMMEDIATE

        return PolicyDecision(
            action=RecoveryAction.RETRY_PAYMENT,
            reason=DecisionReason.SAFE_TO_RETRY,
            retry_cadence=cadence,
        )

    # -------------------------------------------------
    # INSUFFICIENT FUNDS
    # -------------------------------------------------

    if category == FailureCategory.INSUFFICIENT_FUNDS:

        if event.payment_type == PaymentType.SUBSCRIPTION:

            cadence = (
                RetryCadence.AFTER_24_HOURS
                if event.retry_count == 0
                else RetryCadence.AFTER_72_HOURS
            )

        else:
            cadence = RetryCadence.AFTER_24_HOURS

        return PolicyDecision(
            action=RecoveryAction.RETRY_PAYMENT,
            reason=DecisionReason.SAFE_TO_RETRY,
            retry_cadence=cadence,
        )

    # -------------------------------------------------
    # EXPIRED CARD
    # -------------------------------------------------

    if category == FailureCategory.EXPIRED_CARD:

        # Give the customer time to update the
        # payment method before attempting recovery.

        if event.payment_type == PaymentType.SUBSCRIPTION:

            cadence = (
                RetryCadence.AFTER_24_HOURS
                if event.retry_count == 0
                else RetryCadence.AFTER_72_HOURS
            )

        else:
            cadence = RetryCadence.AFTER_72_HOURS

        return PolicyDecision(
            action=RecoveryAction.RETRY_PAYMENT,
            reason=DecisionReason.SAFE_TO_RETRY,
            retry_cadence=cadence,
        )

    # -------------------------------------------------
    # MANDATE FAILURE
    # -------------------------------------------------

    if category == FailureCategory.MANDATE_FAILURE:

        # Preserve the subscription retry contract:
        #
        # first retry  -> 24 hours
        # later retry  -> 72 hours

        cadence = (
            RetryCadence.AFTER_24_HOURS
            if event.retry_count == 0
            else RetryCadence.AFTER_72_HOURS
        )

        return PolicyDecision(
            action=RecoveryAction.RETRY_PAYMENT,
            reason=DecisionReason.SAFE_TO_RETRY,
            retry_cadence=cadence,
        )

    # -------------------------------------------------
    # UNKNOWN
    # -------------------------------------------------

    # Unknown categories must never automatically
    # authorize a payment retry.

    return PolicyDecision(
        action=RecoveryAction.ESCALATE_TO_HUMAN,
        reason=DecisionReason.LOW_CONFIDENCE,
    )