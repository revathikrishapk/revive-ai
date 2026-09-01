from dataclasses import dataclass
import hashlib

from app.executor import RecoveryExecutor
from app.generate_data import (
    ONE_OFF_FAILURE_MESSAGES,
    SUBSCRIPTION_FAILURE_MESSAGES,
)
from app.policy_engine import (
    ECONOMIC_FLOOR,
    MAX_RETRY_ATTEMPTS,
)
from app.schema import (
    FailedPaymentEvent,
    FailureCategory,
)


@dataclass
class BaselineResult:
    """
    Result produced by the naive retry baseline.

    IMPORTANT:
    The baseline itself remains naive.

    It always attempts one retry.

    The additional safety fields are used ONLY
    by the experiment evaluator to measure what
    the baseline violated.
    """

    attempted: bool
    recovered_amount: float
    recovery_status: str
    reason: str

    economic_floor_violation: bool = False
    retry_cap_violation: bool = False
    fraud_violation: bool = False


def get_ground_truth_category(
    event: FailedPaymentEvent,
) -> FailureCategory:
    """
    Recover the synthetic ground-truth category.

    This information is NOT available to the
    naive strategy when making its decision.

    It is only used by the experiment evaluator
    to determine the simulated recovery outcome.
    """

    for category, messages in (
        ONE_OFF_FAILURE_MESSAGES.items()
    ):
        if event.failure_message in messages:
            return category

    for category, messages in (
        SUBSCRIPTION_FAILURE_MESSAGES.items()
    ):
        if event.failure_message in messages:
            return category

    return FailureCategory.UNKNOWN


def simulate_recovery_outcome(
    event: FailedPaymentEvent,
    category: FailureCategory,
) -> tuple[str, float]:
    """
    Simulate the same deterministic recovery outcome
    used by the Revive executor.

    Both strategies therefore face the same synthetic
    recovery probability for the same event.
    """

    recovery_rate = RecoveryExecutor.RECOVERY_RATES.get(
        category.value,
        0.0,
    )

    digest = hashlib.sha256(
        event.event_id.encode("utf-8")
    ).hexdigest()

    bucket = (
        int(digest[:8], 16)
        / 0xFFFFFFFF
    )

    if bucket < recovery_rate:
        return (
            "recovered",
            round(event.amount, 2),
        )

    return (
        "failed",
        0.0,
    )


def is_fraud_hold(
    event: FailedPaymentEvent,
) -> bool:
    """
    Identify synthetic fraud/security events.

    This function is used only for measuring
    unsafe baseline behavior.
    """

    message = event.failure_message.lower()

    return (
        "security review" in message
        or "fraud detection" in message
    )


def naive_retry(
    event: FailedPaymentEvent,
) -> BaselineResult:
    """
    Conventional retry baseline.

    Decision:

        FAILED PAYMENT
              ↓
          RETRY ONCE

    The baseline deliberately does NOT inspect:

    - AI diagnosis
    - confidence
    - fraud status
    - economic floor
    - retry cap
    - subscription cadence
    - human escalation

    Ground-truth category is used only to simulate
    the recovery outcome after the retry decision.
    """

    category = get_ground_truth_category(event)

    recovery_status, recovered_amount = (
        simulate_recovery_outcome(
            event,
            category,
        )
    )

    economic_floor_violation = (
        event.amount < ECONOMIC_FLOOR
    )

    retry_cap_violation = (
        event.retry_count >= MAX_RETRY_ATTEMPTS
    )

    fraud_violation = is_fraud_hold(event)

    return BaselineResult(
        attempted=True,
        recovered_amount=recovered_amount,
        recovery_status=recovery_status,
        reason=(
            "Naive retry: every failed payment "
            "is retried once."
        ),
        economic_floor_violation=(
            economic_floor_violation
        ),
        retry_cap_violation=(
            retry_cap_violation
        ),
        fraud_violation=(
            fraud_violation
        ),
    )