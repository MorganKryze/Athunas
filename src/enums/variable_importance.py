from enum import Enum


class Importance(Enum):
    """
    Enum to represent the importance level of a variable.

    Attributes:
        OPTIONAL: The variable is optional.
        REQUIRED: The variable is required.
    """

    OPTIONAL = 1
    REQUIRED = 2
