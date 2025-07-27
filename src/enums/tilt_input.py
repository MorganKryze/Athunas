from enum import Enum


class TiltState(Enum):
    """
    Enum to represent the state of a tilt switch.

    Attributes:
        HORIZONTAL (int): Represents a horizontal state.
        VERTICAL (int): Represents a vertical state.
    """
    HORIZONTAL = 1
    VERTICAL = 2
