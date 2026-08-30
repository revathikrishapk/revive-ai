import random
import uuid
from pathlib import Path

from app.schema import FailedPaymentEvent, FailureCategory, PaymentType


ONE_OFF_FAILURE_MESSAGES = {
    FailureCategory.NETWORK_ERROR: [
        "Payment gateway timeout",
        "Bank server unavailable",
        "Network connection interrupted",
    ],
    FailureCategory.INSUFFICIENT_FUNDS: [
        "Insufficient account balance",
        "Transaction declined due to insufficient funds",
    ],
    FailureCategory.EXPIRED_CARD: [
        "Card has expired",
        "Payment method is no longer valid",
    ],
    FailureCategory.FRAUD_HOLD: [
        "Transaction blocked for security review",
        "Payment temporarily held due to fraud detection",
    ],
}


SUBSCRIPTION_FAILURE_MESSAGES = {
    FailureCategory.NETWORK_ERROR: [
        "Recurring payment gateway timeout",
        "Bank server unavailable during subscription renewal",
    ],
    FailureCategory.INSUFFICIENT_FUNDS: [
        "Insufficient account balance for subscription renewal",
        "Recurring transaction declined due to insufficient funds",
    ],
    FailureCategory.EXPIRED_CARD: [
        "Subscription payment card has expired",
        "Recurring payment method is no longer valid",
    ],
    FailureCategory.FRAUD_HOLD: [
        "Subscription transaction blocked for security review",
        "Recurring payment held due to fraud detection",
    ],
    FailureCategory.MANDATE_FAILURE: [
        "Subscription mandate execution failed",
        "Recurring payment mandate could not be processed",
        "Mandate authorization failed during subscription renewal",
    ],
}


def generate_event() -> FailedPaymentEvent:
    payment_type = random.choice(list(PaymentType))

    if payment_type == PaymentType.SUBSCRIPTION:
        category = random.choice(list(SUBSCRIPTION_FAILURE_MESSAGES.keys()))
        failure_message = random.choice(
            SUBSCRIPTION_FAILURE_MESSAGES[category]
        )

        return FailedPaymentEvent(
            event_id=str(uuid.uuid4()),
            payment_type=payment_type,
            amount=round(random.uniform(199, 5000), 2),
            failure_message=failure_message,
            retry_count=random.randint(0, 3),
            subscription_id=f"sub_{uuid.uuid4().hex[:8]}",
        )

    category = random.choice(list(ONE_OFF_FAILURE_MESSAGES.keys()))
    failure_message = random.choice(
        ONE_OFF_FAILURE_MESSAGES[category]
    )

    return FailedPaymentEvent(
        event_id=str(uuid.uuid4()),
        payment_type=payment_type,
        amount=round(random.uniform(50, 10000), 2),
        failure_message=failure_message,
        retry_count=random.randint(0, 3),
        subscription_id=None,
    )


def generate_batch(count: int = 80) -> list[FailedPaymentEvent]:
    return [generate_event() for _ in range(count)]


def save_events(
    events: list[FailedPaymentEvent],
    output_path: str = "data/events.jsonl",
) -> None:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as file:
        for event in events:
            file.write(event.model_dump_json() + "\n")


if __name__ == "__main__":
    events = generate_batch(80)
    save_events(events)

    subscription_count = sum(
        event.payment_type == PaymentType.SUBSCRIPTION
        for event in events
    )

    one_off_count = len(events) - subscription_count

    print(f"Generated {len(events)} failed payment events")
    print(f"One-off events: {one_off_count}")
    print(f"Subscription events: {subscription_count}")
    print("Saved to data/events.jsonl")