import hashlib

from app.schema import FailedPaymentEvent, RecoveryAction


class RecoveryExecutor:
    """
    Mock recovery executor.

    The executor simulates a payment recovery attempt.
    It does not connect to a real payment gateway.

    The policy engine remains the only component authorized
    to decide whether a recovery action is allowed.
    """

    RECOVERY_RATES = {
        "network_error": 0.85,
        "insufficient_funds": 0.45,
        "expired_card": 0.30,
        "mandate_failure": 0.60,
    }

    def __init__(self):
        self.executed_event_ids: set[str] = set()

    def execute(
        self,
        event: FailedPaymentEvent,
        action: RecoveryAction,
        failure_category: str | None = None,
    ) -> dict:
        """
        Execute an approved recovery action.

        Idempotency guarantees that the same event cannot
        be executed more than once.
        """

        # -------------------------------------------------
        # 1. Idempotency protection
        # -------------------------------------------------

        if event.event_id in self.executed_event_ids:
            return {
                "event_id": event.event_id,
                "action": action.value,
                "status": "duplicate_skipped",
                "execution_status": "not_executed",
                "recovery_status": "not_attempted",
                "recovered_amount": 0.0,
            }

        # -------------------------------------------------
        # 2. Non-recovery actions are not executed
        # -------------------------------------------------

        if action != RecoveryAction.RETRY_PAYMENT:
            return {
                "event_id": event.event_id,
                "action": action.value,
                "status": "not_executed",
                "execution_status": "not_executed",
                "recovery_status": "not_attempted",
                "recovered_amount": 0.0,
            }

        # -------------------------------------------------
        # 3. Mark event as executed
        # -------------------------------------------------

        self.executed_event_ids.add(event.event_id)

        # -------------------------------------------------
        # 4. Determine synthetic recovery probability
        # -------------------------------------------------

        recovery_rate = self.RECOVERY_RATES.get(
            failure_category or "unknown",
            0.0,
        )

        # -------------------------------------------------
        # 5. Generate deterministic outcome
        # -------------------------------------------------

        digest = hashlib.sha256(
            event.event_id.encode("utf-8")
        ).hexdigest()

        bucket = int(digest[:8], 16) / 0xFFFFFFFF

        if bucket < recovery_rate:
            recovery_status = "recovered"
            recovered_amount = event.amount
        else:
            recovery_status = "failed"
            recovered_amount = 0.0

        # -------------------------------------------------
        # 6. Return execution + recovery separately
        # -------------------------------------------------

        return {
            "event_id": event.event_id,
            "action": action.value,
            "status": "executed",
            "execution_status": "executed",
            "recovery_status": recovery_status,
            "recovered_amount": round(
                recovered_amount,
                2,
            ),
            "recovery_probability": recovery_rate,
        }