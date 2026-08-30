from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class PaymentType(str, Enum):
    ONE_OFF = "one_off"
    SUBSCRIPTION = "subscription"


class FailureCategory(str, Enum):
    NETWORK_ERROR = "network_error"
    INSUFFICIENT_FUNDS = "insufficient_funds"
    EXPIRED_CARD = "expired_card"
    FRAUD_HOLD = "fraud_hold"
    MANDATE_FAILURE = "mandate_failure"
    UNKNOWN = "unknown"

class RecoveryAction(str, Enum):
    RETRY_PAYMENT = "retry_payment"
    ESCALATE_TO_HUMAN = "escalate_to_human"
    STOP = "stop"


class DecisionReason(str, Enum):
    ECONOMIC_FLOOR = "economic_floor"
    LOW_CONFIDENCE = "low_confidence"
    RETRY_CAP_REACHED = "retry_cap_reached"
    FRAUD_HOLD = "fraud_hold"
    SAFE_TO_RETRY = "safe_to_retry"


class FailedPaymentEvent(BaseModel):
    event_id: str
    payment_type: PaymentType

    amount: float = Field(gt=0)
    currency: str = "INR"

    failure_message: str
    retry_count: int = Field(default=0, ge=0)

    subscription_id: Optional[str] = None


class Diagnosis(BaseModel):
    category: FailureCategory
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str

class PolicyDecision(BaseModel):
    action: RecoveryAction
    reason: DecisionReason