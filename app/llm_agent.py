from app.schema import Diagnosis, FailedPaymentEvent, FailureCategory


def diagnose_failure(event: FailedPaymentEvent) -> Diagnosis:
    """
    Mock LLM diagnosis.

    This simulates the structured output we will later get from
    a real LLM API.
    """

    message = event.failure_message.lower()

    if "timeout" in message or "network" in message or "server" in message:
        return Diagnosis(
            category=FailureCategory.NETWORK_ERROR,
            confidence=0.92,
            reasoning="The failure message indicates a temporary network or bank connectivity issue.",
        )

    if "insufficient" in message or "balance" in message:
        return Diagnosis(
            category=FailureCategory.INSUFFICIENT_FUNDS,
            confidence=0.95,
            reasoning="The failure message explicitly indicates insufficient funds.",
        )

    if "expired" in message or "no longer valid" in message:
        return Diagnosis(
            category=FailureCategory.EXPIRED_CARD,
            confidence=0.93,
            reasoning="The payment method appears to be expired or invalid.",
        )

    if "fraud" in message or "security review" in message:
        return Diagnosis(
            category=FailureCategory.FRAUD_HOLD,
            confidence=0.98,
            reasoning="The payment was blocked or held for fraud or security review.",
        )

    if "mandate" in message or "recurring" in message:
        return Diagnosis(
            category=FailureCategory.MANDATE_FAILURE,
            confidence=0.90,
            reasoning="The failure is related to a recurring subscription mandate.",
        )

    return Diagnosis(
        category=FailureCategory.UNKNOWN,
        confidence=0.0,
        reasoning="The failure could not be classified with sufficient confidence.",
    )