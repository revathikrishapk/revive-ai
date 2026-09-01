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
    "DEEPSEEK_MODEL",
    "deepseek-v4-flash",
)

MAX_DIAGNOSIS_ATTEMPTS = 3


# =========================================================
# DIAGNOSIS AGENT
# =========================================================

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

        self.api_key = os.getenv(
            "DEEPSEEK_API_KEY"
        )

        self.client = None

        # -------------------------------------------------
        # REAL AI MODE
        # -------------------------------------------------

        if self.api_key:

            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com",
            )


    # =====================================================
    # PUBLIC DIAGNOSIS METHOD
    # =====================================================

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
        # This allows the entire system to be developed
        # without depending on an external AI provider.
        # -------------------------------------------------

        if self.client is None:

            return self._mock_diagnosis(
                event
            )


        # -------------------------------------------------
        # REAL AI MODE
        # -------------------------------------------------

        last_error = None


        for attempt in range(
            MAX_DIAGNOSIS_ATTEMPTS
        ):

            try:

                # -----------------------------------------
                # Call DeepSeek
                # -----------------------------------------

                diagnosis = self._call_deepseek(
                    event
                )


                # -----------------------------------------
                # Validate AI output
                # -----------------------------------------
                #
                # _call_deepseek normally returns a
                # Diagnosis object.
                #
                # Tests may deliberately return a dict
                # to simulate malformed provider output.
                #
                # Handle both safely.
                # -----------------------------------------

                if isinstance(
                    diagnosis,
                    Diagnosis,
                ):

                    return Diagnosis.model_validate(
                        diagnosis.model_dump()
                    )


                return Diagnosis.model_validate(
                    diagnosis
                )


            except (
                ValidationError,
                ValueError,
                TypeError,
                json.JSONDecodeError,
            ) as error:

                last_error = error

                print(
                    f"AI diagnosis validation failed "
                    f"(attempt {attempt + 1}/"
                    f"{MAX_DIAGNOSIS_ATTEMPTS}): "
                    f"{error}"
                )


            except Exception as error:

                # -----------------------------------------
                # Provider/API failures
                # -----------------------------------------
                #
                # Examples:
                # - insufficient balance
                # - network error
                # - timeout
                # - authentication failure
                #
                # We DO NOT allow these failures to
                # automatically create a recovery decision.
                # -----------------------------------------

                last_error = error

                print(
                    f"AI provider error "
                    f"(attempt {attempt + 1}/"
                    f"{MAX_DIAGNOSIS_ATTEMPTS}): "
                    f"{error}"
                )


        # -------------------------------------------------
        # SAFE FALLBACK
        # -------------------------------------------------
        #
        # If AI repeatedly fails:
        #
        # UNKNOWN
        # confidence = 0.0
        #
        # The deterministic policy engine will therefore
        # refuse automatic recovery and escalate safely.
        # -------------------------------------------------

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
    # DEEPSEEK API CALL
    # =====================================================

    def _call_deepseek(
        self,
        event: FailedPaymentEvent,
    ) -> Diagnosis:

        # -------------------------------------------------
        # SYSTEM PROMPT
        # -------------------------------------------------

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


        # -------------------------------------------------
        # USER PROMPT
        # -------------------------------------------------

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


        # -------------------------------------------------
        # API REQUEST
        # -------------------------------------------------

        response = (
            self.client
            .chat
            .completions
            .create(
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
        )


        # -------------------------------------------------
        # RESPONSE VALIDATION
        # -------------------------------------------------

        if not response.choices:

            raise ValueError(
                "DeepSeek returned no choices."
            )


        content = (
            response
            .choices[0]
            .message
            .content
        )


        if not content:

            raise ValueError(
                "DeepSeek returned an empty response."
            )


        # -------------------------------------------------
        # PARSE JSON
        # -------------------------------------------------

        parsed = json.loads(
            content
        )


        # -------------------------------------------------
        # PYDANTIC VALIDATION
        # -------------------------------------------------
        #
        # This is the critical AI boundary.
        #
        # Invalid categories, invalid confidence values,
        # missing fields, etc. are rejected here.
        # -------------------------------------------------

        return Diagnosis.model_validate(
            parsed
        )


    # =====================================================
    # MOCK DIAGNOSIS
    # =====================================================

    @staticmethod
    def _mock_diagnosis(
        event: FailedPaymentEvent,
    ) -> Diagnosis:

        message = (
            event.failure_message
            .lower()
        )


        # -------------------------------------------------
        # NETWORK ERROR
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
        # INSUFFICIENT FUNDS
        # -------------------------------------------------

        if (
            "insufficient" in message
            or "balance" in message
        ):

            return Diagnosis(
                category=(
                    FailureCategory.INSUFFICIENT_FUNDS
                ),

                confidence=0.95,

                reasoning=(
                    "The failure message indicates "
                    "insufficient funds."
                ),
            )


        # -------------------------------------------------
        # EXPIRED CARD
        # -------------------------------------------------

        if (
            "expired" in message
            or "no longer valid" in message
        ):

            return Diagnosis(
                category=(
                    FailureCategory.EXPIRED_CARD
                ),

                confidence=0.93,

                reasoning=(
                    "The payment method appears "
                    "to be expired or invalid."
                ),
            )


        # -------------------------------------------------
        # FRAUD HOLD
        # -------------------------------------------------

        if (
            "fraud" in message
            or "security review" in message
        ):

            return Diagnosis(
                category=(
                    FailureCategory.FRAUD_HOLD
                ),

                confidence=0.98,

                reasoning=(
                    "The payment was blocked or held "
                    "for fraud or security review."
                ),
            )


        # -------------------------------------------------
        # MANDATE FAILURE
        # -------------------------------------------------

        if (
            "mandate" in message
            or "recurring" in message
        ):

            return Diagnosis(
                category=(
                    FailureCategory.MANDATE_FAILURE
                ),

                confidence=0.90,

                reasoning=(
                    "The failure is related to a "
                    "recurring subscription mandate."
                ),
            )


        # -------------------------------------------------
        # UNKNOWN
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


# =========================================================
# EXISTING FUNCTION INTERFACE
# =========================================================

def diagnose_failure(
    event: FailedPaymentEvent,
) -> Diagnosis:

    return _agent.diagnose(
        event
    )