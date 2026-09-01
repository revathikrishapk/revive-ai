import json
import os

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import ValidationError

from app.schema import (
    Diagnosis,
    FailedPaymentEvent,
    FailureCategory,
)


load_dotenv()


MODEL_NAME = os.getenv(
    "DEEPSEEK_MODEL",
    "deepseek-v4-flash",
)

MAX_DIAGNOSIS_ATTEMPTS = 3


class DiagnosisAgent:
    """
    AI diagnosis layer.

    The agent only diagnoses payment failures.

    It has NO authority to:
    - retry payments
    - stop recovery
    - escalate payments
    - execute payments
    - move money

    The deterministic policy engine handles those decisions.
    """

    def __init__(self):

        self.api_key = os.getenv("DEEPSEEK_API_KEY")

        self.client = None

        if self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com",
            )

    def diagnose(
        self,
        event: FailedPaymentEvent,
    ) -> Diagnosis:

        # -------------------------------------------------
        # DEVELOPMENT MODE
        # -------------------------------------------------
        #
        # If no API key is configured, use deterministic
        # mock diagnosis.
        #
        # This lets us build and test the complete system
        # without depending on an external API.
        # -------------------------------------------------

        if self.client is None:
            return self._mock_diagnosis(event)

        last_error = None

        # -------------------------------------------------
        # REAL AI MODE
        # -------------------------------------------------

        for attempt in range(MAX_DIAGNOSIS_ATTEMPTS):

            try:

                diagnosis = self._call_deepseek(event)

                return Diagnosis.model_validate(
                    diagnosis.model_dump()
                )

            except (
                ValidationError,
                ValueError,
                TypeError,
                json.JSONDecodeError,
            ) as error:

                last_error = error

        # -------------------------------------------------
        # SAFE FALLBACK
        # -------------------------------------------------
        #
        # Never guess if the AI repeatedly produces
        # invalid output.
        #
        # UNKNOWN + confidence 0.0 will cause the policy
        # engine to escalate the event.
        # -------------------------------------------------

        return Diagnosis(
            category=FailureCategory.UNKNOWN,
            confidence=0.0,
            reasoning=(
                "AI diagnosis failed validation after "
                f"{MAX_DIAGNOSIS_ATTEMPTS} attempts. "
                "Safe fallback applied."
            ),
        )

    def _call_deepseek(
        self,
        event: FailedPaymentEvent,
    ) -> Diagnosis:

        system_prompt = """
You are the diagnosis component of a payment recovery system.

Your ONLY responsibility is to classify the likely root cause
of a failed payment.

You MUST NOT:

- recommend retrying the payment
- recommend stopping recovery
- recommend human escalation
- execute any payment action
- make policy decisions

A separate deterministic policy engine handles all recovery
decisions.

Return ONLY valid JSON.

The JSON must contain exactly:

{
    "category": "network_error",
    "confidence": 0.92,
    "reasoning": "Short explanation based on the event."
}

The category MUST be exactly one of:

network_error
insufficient_funds
expired_card
fraud_hold
mandate_failure
unknown

Confidence MUST be between 0.0 and 1.0.

Keep reasoning concise and base it only on the supplied
payment event.
"""

        user_prompt = f"""
Diagnose this payment failure.

Payment type: {event.payment_type.value}
Amount: {event.amount}
Currency: {event.currency}
Failure message: {event.failure_message}
Retry count: {event.retry_count}
Subscription ID: {event.subscription_id}

Return JSON only.
"""

        response = self.client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            response_format={
                "type": "json_object",
            },
            temperature=0,
            max_tokens=200,
        )

        content = response.choices[0].message.content

        if not content:
            raise ValueError(
                "DeepSeek returned an empty response."
            )

        parsed = json.loads(content)

        return Diagnosis.model_validate(parsed)

    @staticmethod
    def _mock_diagnosis(
        event: FailedPaymentEvent,
    ) -> Diagnosis:

        message = event.failure_message.lower()

        if (
            "timeout" in message
            or "network" in message
            or "server" in message
        ):
            return Diagnosis(
                category=FailureCategory.NETWORK_ERROR,
                confidence=0.92,
                reasoning=(
                    "The failure message indicates "
                    "a temporary network or bank "
                    "connectivity issue."
                ),
            )

        if (
            "insufficient" in message
            or "balance" in message
        ):
            return Diagnosis(
                category=FailureCategory.INSUFFICIENT_FUNDS,
                confidence=0.95,
                reasoning=(
                    "The failure message indicates "
                    "insufficient funds."
                ),
            )

        if (
            "expired" in message
            or "no longer valid" in message
        ):
            return Diagnosis(
                category=FailureCategory.EXPIRED_CARD,
                confidence=0.93,
                reasoning=(
                    "The payment method appears "
                    "to be expired or invalid."
                ),
            )

        if (
            "fraud" in message
            or "security review" in message
        ):
            return Diagnosis(
                category=FailureCategory.FRAUD_HOLD,
                confidence=0.98,
                reasoning=(
                    "The payment was blocked or held "
                    "for fraud or security review."
                ),
            )

        if (
            "mandate" in message
            or "recurring" in message
        ):
            return Diagnosis(
                category=FailureCategory.MANDATE_FAILURE,
                confidence=0.90,
                reasoning=(
                    "The failure is related to a "
                    "recurring subscription mandate."
                ),
            )

        return Diagnosis(
            category=FailureCategory.UNKNOWN,
            confidence=0.0,
            reasoning=(
                "The failure could not be classified "
                "with sufficient confidence."
            ),
        )


# ---------------------------------------------------------
# Shared diagnosis agent
# ---------------------------------------------------------

_agent = DiagnosisAgent()


def diagnose_failure(
    event: FailedPaymentEvent,
) -> Diagnosis:

    return _agent.diagnose(event)