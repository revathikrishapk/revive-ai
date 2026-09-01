from enum import Enum


class RecoveryState(str, Enum):
    """
    States in the Revive recovery workflow.
    """

    RECEIVED = "received"
    VALIDATED = "validated"

    DIAGNOSING = "diagnosing"
    DIAGNOSED = "diagnosed"

    DECIDING = "deciding"
    DECIDED = "decided"

    EXECUTING = "executing"

    COMPLETED = "completed"
    ESCALATED = "escalated"
    STOPPED = "stopped"


class RecoveryFSM:
    """
    Lightweight finite-state controller for a recovery event.

    The FSM controls workflow progression.

    It does NOT:
    - diagnose failures
    - make policy decisions
    - execute payments

    Those responsibilities remain in their respective layers.
    """

    VALID_TRANSITIONS = {

        RecoveryState.RECEIVED: {
            RecoveryState.VALIDATED,
        },

        RecoveryState.VALIDATED: {
            RecoveryState.DIAGNOSING,
        },

        RecoveryState.DIAGNOSING: {
            RecoveryState.DIAGNOSED,
        },

        RecoveryState.DIAGNOSED: {
            RecoveryState.DECIDING,
        },

        RecoveryState.DECIDING: {
            RecoveryState.DECIDED,
            RecoveryState.ESCALATED,
            RecoveryState.STOPPED,
        },

        RecoveryState.DECIDED: {
            RecoveryState.EXECUTING,
            RecoveryState.ESCALATED,
            RecoveryState.STOPPED,
        },

        RecoveryState.EXECUTING: {
            RecoveryState.COMPLETED,
        },

        RecoveryState.ESCALATED: {
            RecoveryState.COMPLETED,
        },

        RecoveryState.STOPPED: {
            RecoveryState.COMPLETED,
        },

        RecoveryState.COMPLETED: set(),
    }

    def __init__(self):
        self.state = RecoveryState.RECEIVED

    def transition(
        self,
        new_state: RecoveryState,
    ) -> RecoveryState:
        """
        Move to a new state only if the transition
        is explicitly allowed.
        """

        allowed_states = self.VALID_TRANSITIONS[
            self.state
        ]

        if new_state not in allowed_states:
            raise ValueError(
                f"Invalid FSM transition: "
                f"{self.state.value} -> "
                f"{new_state.value}"
            )

        self.state = new_state

        return self.state

    def is_terminal(self) -> bool:
        """
        Return True if the workflow has reached
        a terminal state.
        """

        return self.state == RecoveryState.COMPLETED