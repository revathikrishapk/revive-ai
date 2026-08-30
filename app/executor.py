from app.schema import FailedPaymentEvent, RecoveryAction


class RecoveryExecutor:
    def __init__(self):
        self.executed_event_ids: set[str] = set()

    def execute(
        self,
        event: FailedPaymentEvent,
        action: RecoveryAction,
    ) -> dict:
        # Idempotency guard:
        # Never execute the same event twice.
        if event.event_id in self.executed_event_ids:
            return {
                "event_id": event.event_id,
                "action": action.value,
                "status": "duplicate_skipped",
                "recovered_amount": 0.0,
            }

        # stop and escalate do not execute a payment retry.
        if action != RecoveryAction.RETRY_PAYMENT:
            return {
                "event_id": event.event_id,
                "action": action.value,
                "status": "not_executed",
                "recovered_amount": 0.0,
            }

        # Mark BEFORE executing.
        # This prevents a duplicate from triggering another execution.
        self.executed_event_ids.add(event.event_id)

        # Mock payment recovery outcome.
        # We use this for now because there is no real payment gateway.
        recovered = event.amount * 0.7

        return {
            "event_id": event.event_id,
            "action": action.value,
            "status": "executed",
            "recovered_amount": round(recovered, 2),
        }