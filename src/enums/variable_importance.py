from enum import Enum

class Importance(Enum):
    """
    Enum to represent the importance level of a variable.

    Attributes:
        NORMAL (int): Represents a normal importance level.
        CRITICAL (int): Represents a critical importance level.
    """
    NORMAL = 1
    CRITICAL = 2