import json
import random
import uuid
from pathlib import Path

from app.schema import FailedPaymentEvent, FailureCategory, PaymentType


FAILURE_MESSAGES = {
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
    FailureCategory.MANDATE_FAILURE: [
        "Subscription mandate execution failed",
        "Recurring payment mandate could not be processed",
    ],
}


def generate_event() -> FailedPaymentEvent:
    category = random.choice(list(FailureCategory))
    payment_type = random.choice(list(PaymentType))

    # Mandate failures only make sense for subscriptions
    if category == FailureCategory.MANDATE_FAILURE:
        payment_type = PaymentType.SUBSCRIPTION

    return FailedPaymentEvent(
        event_id=str(uuid.uuid4()),
        payment_type=payment_type,
        amount=round(random.uniform(50, 10000), 2),
        failure_message=random.choice(FAILURE_MESSAGES.get(
            category,
            ["Unknown payment failure"]
        )),
        retry_count=random.randint(0, 3),
        subscription_id=(
            f"sub_{uuid.uuid4().hex[:8]}"
            if payment_type == PaymentType.SUBSCRIPTION
            else None
        ),
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

    print(f"Generated {len(events)} failed payment events")
    print("Saved to data/events.jsonl")