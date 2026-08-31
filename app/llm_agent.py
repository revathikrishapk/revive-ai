import os

from google import genai
from google.genai import types
from pydantic import ValidationError

from app.schema import Diagnosis, FailedPaymentEvent, FailureCategory

from dotenv import load_dotenv

load_dotenv()


MODEL_NAME = "gemini-2.5-flash-lite"
MAX_DIAGNOSIS_ATTEMPTS = 3


class DiagnosisAgent:
    """
    AI diagnosis layer.

    IMPORTANT:
    This class can only diagnose a payment failure.
    It has no access to the policy engine or executor.
    """

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        self.client = (
            genai.Client(api_key=api_key)
            if api_key
            else None
        )

    def diagnose(
        self,
        event: FailedPaymentEvent,
    ) -> Diagnosis:

        if self.client is None:
            return self._mock_diagnosis(event)

        last_error = None

        for attempt in range(MAX_DIAGNOSIS_ATTEMPTS):

            try:
                diagnosis = self._call_gemini(event)

                # Explicit application-level validation.
                return Diagnosis.model_validate(
                    diagnosis.model_dump()
                )

            except (
                ValidationError,
                ValueError,
                TypeError,
            ) as error:

                last_error = error

        # Safe fallback:
        # malformed/invalid AI output never reaches
        # the policy engine as a confident diagnosis.
        return Diagnosis(
            category=FailureCategory.UNKNOWN,
            confidence=0.0,
            reasoning=(
                "AI diagnosis failed validation after "
                f"{MAX_DIAGNOSIS_ATTEMPTS} attempts. "
                f"Fallback applied. Error: {last_error}"
            ),
        )

    def _call_gemini(
        self,
        event: FailedPaymentEvent,
    ) -> Diagnosis:

        prompt = f"""
You are a payment failure diagnosis system.

Your ONLY responsibility is to classify the likely
root cause of a failed payment.

You MUST NOT recommend:
- retrying the payment
- stopping recovery
- escalating to a human
- executing any payment action

Those decisions belong to a separate deterministic
policy engine.

Classify the failure into exactly one category:

- network_error
- insufficient_funds
- expired_card
- fraud_hold
- mandate_failure
- unknown

Return:
1. category
2. confidence between 0.0 and 1.0
3. concise reasoning based only on the event

Payment event:

Payment type: {event.payment_type.value}
Amount: {event.amount}
Currency: {event.currency}
Failure message: {event.failure_message}
Retry count: {event.retry_count}
Subscription ID: {event.subscription_id}
"""

        response = self.client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=Diagnosis,
                temperature=0,
            ),
        )

        if not response.text:
            raise ValueError(
                "Gemini returned an empty response"
            )

        return Diagnosis.model_validate_json(
            response.text
        )

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


# Keep the existing function interface so the rest
# of the pipeline does not need to know whether we're
# using Gemini or mock mode.

_agent = DiagnosisAgent()


def diagnose_failure(
    event: FailedPaymentEvent,
) -> Diagnosis:
    return _agent.diagnose(event)