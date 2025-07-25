from enum import Enum

class EncoderInput(Enum):
    """
    Enum to represent the type of an input from an encoder.
    
    Attributes:
        NOTHING (int): Represents no input.
        SINGLE_PRESS (int): Represents a single press.
        DOUBLE_PRESS (int): Represents a double press.
        TRIPLE_PRESS (int): Represents a triple press.
        LONG_PRESS (int): Represents a long press.
        ENCODER_INCREASE (int): Represents an increase in the encoder value.
        ENCODER_DECREASE (int): Represents a decrease in the encoder value.
    """
    NOTHING = 1
    SINGLE_PRESS = 2
    DOUBLE_PRESS = 3
    TRIPLE_PRESS = 4
    LONG_PRESS = 5
    INCREASE_CLOCKWISE = 6
    DECREASE_COUNTERCLOCKWISE = 7
