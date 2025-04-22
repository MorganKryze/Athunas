from enum import Enum

class ConfigType(Enum):
    """
    Enum to represent the type of configuration.

    Attributes:
        Template (int): Represents the default configuration delivered with the software.
        Current (int): Represents the last working configuration that may have been modified.
        Temporary (int): Represents a temporary configuration that is not saved.
    """
    Recovery = 0
    Template = 1
    Current = 2
    Temporary = 3