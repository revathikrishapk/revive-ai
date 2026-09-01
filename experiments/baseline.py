from dataclasses import dataclass
import hashlib

from app.executor import RecoveryExecutor
from app.generate_data import (
    ONE_OFF_FAILURE_MESSAGES,
    SUBSCRIPTION_FAILURE_MESSAGES,
)
from app.schema import (
    FailedPaymentEvent,
    FailureCategory,
)


@dataclass
class BaselineResult:
    """
    Result produced by the naive retry baseline.
    """

    attempted: bool
    recovered_amount: float
    recovery_status: str
    reason: str


def get_ground_truth_category(
    event: FailedPaymentEvent,
) -> FailureCategory:
    """
    Recover the synthetic ground-truth category.

    IMPORTANT:
    This is ONLY used by the experiment evaluator.

    The naive baseline does NOT receive this information
    when deciding whether to retry.

    The synthetic generator creates the failure message
    from a known category, so we can reconstruct that
    hidden category for measuring the outcome fairly.
    """

    message = event.failure_message

    for category, messages in (
        ONE_OFF_FAILURE_MESSAGES.items()
    ):

        if message in messages:
            return category

    for category, messages in (
        SUBSCRIPTION_FAILURE_MESSAGES.items()
    ):

        if message in messages:
            return category

    return FailureCategory.UNKNOWN


def simulate_recovery_outcome(
    event: FailedPaymentEvent,
    category: FailureCategory,
) -> tuple[str, float]:
    """
    Simulate the same deterministic recovery outcome
    used by the production executor.

    This makes the baseline and Revive comparable.
    """

    recovery_rate = RecoveryExecutor.RECOVERY_RATES.get(
        category.value,
        0.0,
    )

    digest = hashlib.sha256(
        event.event_id.encode("utf-8")
    ).hexdigest()

    bucket = int(
        digest[:8],
        16,
    ) / 0xFFFFFFFF

    if bucket < recovery_rate:

        return (
            "recovered",
            round(event.amount, 2),
        )

    return (
        "failed",
        0.0,
    )


def naive_retry(
    event: FailedPaymentEvent,
) -> BaselineResult:
    """
    Conventional retry baseline.

    The baseline decision is intentionally naive:

        FAILED PAYMENT
              ↓
          RETRY ONCE

    It does NOT inspect:
    - AI diagnosis
    - confidence
    - fraud status
    - economic floor
    - retry cap
    - subscription cadence
    - human escalation

    The hidden category is NOT used to decide whether
    to retry.

    It is only used after the decision to simulate the
    same payment outcome as the Revive executor.
    """

    category = get_ground_truth_category(
        event
    )

    recovery_status, recovered_amount = (
        simulate_recovery_outcome(
            event,
            category,
        )
    )

    return BaselineResult(
        attempted=True,
        recovered_amount=recovered_amount,
        recovery_status=recovery_status,
        reason=(
            "Naive retry: every failed payment "
            "is retried once."
        ),
    )