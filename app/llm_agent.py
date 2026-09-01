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


# =========================================================
# CONFIGURATION
# =========================================================

MODEL_NAME = os.getenv(
    "OPENROUTER_MODEL",
    "openrouter/free",
)

MAX_DIAGNOSIS_ATTEMPTS = 3


# =========================================================
# DIAGNOSIS AGENT
# =========================================================

class DiagnosisAgent:
    """
    OpenRouter-powered diagnosis layer.

    The LLM ONLY diagnoses the payment failure.

    It has NO authority to:
    - retry payments
    - stop recovery
    - escalate payments
    - execute payments
    - move money

    The deterministic policy engine makes
    all recovery decisions.
    """

    def __init__(self):

        self.api_key = os.getenv(
            "OPENROUTER_API_KEY"
        )

        self.client = None

        if self.api_key:

            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.api_key,
            )

        # -------------------------------------------------
        # Diagnosis cache
        # -------------------------------------------------

        self._diagnosis_cache = {}

        # -------------------------------------------------
        # Runtime statistics
        # -------------------------------------------------

        self.diagnosis_stats = {
            "successful": 0,
            "fallback": 0,
            "validation_failures": 0,
            "provider_failures": 0,
            "cache_hits": 0,
            "api_calls": 0,
        }


    # =====================================================
    # PUBLIC DIAGNOSIS METHOD
    # =====================================================

    def diagnose(
        self,
        event: FailedPaymentEvent,
    ) -> Diagnosis:

        # -------------------------------------------------
        # CACHE
        # -------------------------------------------------

        cache_key = (
            event.payment_type.value,
            event.failure_message.strip().lower(),
        )

        if cache_key in self._diagnosis_cache:

            self.diagnosis_stats[
                "cache_hits"
            ] += 1

            return self._diagnosis_cache[
                cache_key
            ]


        # -------------------------------------------------
        # DEVELOPMENT FALLBACK
        # -------------------------------------------------

        if self.client is None:

            diagnosis = self._mock_diagnosis(
                event
            )

            self._diagnosis_cache[
                cache_key
            ] = diagnosis

            self.diagnosis_stats[
                "successful"
            ] += 1

            return diagnosis


        # -------------------------------------------------
        # REAL OPENROUTER MODE
        # -------------------------------------------------

        for attempt in range(
            MAX_DIAGNOSIS_ATTEMPTS
        ):

            try:

                self.diagnosis_stats[
                    "api_calls"
                ] += 1

                diagnosis = self._call_openrouter(
                    event
                )

                # -------------------------------------------------
                # Validate provider output
                # -------------------------------------------------

                if isinstance(
                    diagnosis,
                    Diagnosis,
                ):

                    diagnosis = (
                        Diagnosis.model_validate(
                            diagnosis.model_dump()
                        )
                    )

                else:

                    diagnosis = (
                        Diagnosis.model_validate(
                            diagnosis
                        )
                    )

                # -------------------------------------------------
                # Cache ONLY validated output
                # -------------------------------------------------

                self._diagnosis_cache[
                    cache_key
                ] = diagnosis

                self.diagnosis_stats[
                    "successful"
                ] += 1

                return diagnosis


            except (
                ValidationError,
                ValueError,
                TypeError,
                json.JSONDecodeError,
            ):

                self.diagnosis_stats[
                    "validation_failures"
                ] += 1


            except Exception:

                self.diagnosis_stats[
                    "provider_failures"
                ] += 1


        # -------------------------------------------------
        # SAFE FALLBACK
        # -------------------------------------------------

        self.diagnosis_stats[
            "fallback"
        ] += 1

        return Diagnosis(
            category=FailureCategory.UNKNOWN,
            confidence=0.0,
            reasoning=(
                "AI diagnosis failed validation or "
                "provider execution after "
                f"{MAX_DIAGNOSIS_ATTEMPTS} attempts. "
                "Safe fallback applied."
            ),
        )


    # =====================================================
    # STATISTICS
    # =====================================================

    def get_stats(self) -> dict:
        """
        Return a copy of diagnosis runtime statistics.
        """

        return self.diagnosis_stats.copy()


    def reset_stats(self) -> None:
        """
        Reset runtime statistics.

        The diagnosis cache is intentionally preserved.
        """

        self.diagnosis_stats = {
            "successful": 0,
            "fallback": 0,
            "validation_failures": 0,
            "provider_failures": 0,
            "cache_hits": 0,
            "api_calls": 0,
        }


    # =====================================================
    # OPENROUTER API CALL
    # =====================================================

    def _call_openrouter(
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
            temperature=0,
            response_format={
                "type": "json_object"
            },
        )

        content = (
            response.choices[0]
            .message
            .content
        )

        if not content:

            raise ValueError(
                "OpenRouter returned an empty response."
            )

        parsed = json.loads(
            content
        )

        return Diagnosis.model_validate(
            parsed
        )


    # =====================================================
    # BACKWARD-COMPATIBLE TEST HOOK
    # =====================================================

    def _call_deepseek(
        self,
        event: FailedPaymentEvent,
    ) -> Diagnosis:
        """
        Backward-compatible hook.

        The project uses OpenRouter.

        Existing tests or older code may still reference
        _call_deepseek, so this delegates to OpenRouter.
        """

        return self._call_openrouter(
            event
        )


    # =====================================================
    # MOCK DIAGNOSIS
    # =====================================================

    @staticmethod
    def _mock_diagnosis(
        event: FailedPaymentEvent,
    ) -> Diagnosis:

        message = (
            event.failure_message.lower()
        )


        # -------------------------------------------------
        # Network
        # -------------------------------------------------

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


        # -------------------------------------------------
        # Insufficient funds
        # -------------------------------------------------

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


        # -------------------------------------------------
        # Expired card
        # -------------------------------------------------

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


        # -------------------------------------------------
        # Fraud / security
        # -------------------------------------------------

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


        # -------------------------------------------------
        # Mandate
        # -------------------------------------------------

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


        # -------------------------------------------------
        # Unknown
        # -------------------------------------------------

        return Diagnosis(
            category=FailureCategory.UNKNOWN,
            confidence=0.0,
            reasoning=(
                "The failure could not be classified "
                "with sufficient confidence."
            ),
        )


# =========================================================
# SHARED DIAGNOSIS AGENT
# =========================================================

_agent = DiagnosisAgent()


def diagnose_failure(
    event: FailedPaymentEvent,
) -> Diagnosis:

    return _agent.diagnose(
        event
    )