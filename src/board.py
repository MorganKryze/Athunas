import logging
import time
from PIL import Image
import queue

from enums.input_status import InputStatus
from enums.variable_importance import Importance
from settings import Settings

try:
    logging.debug("[Board] Attempting to import gpiozero")
    from gpiozero import Button, RotaryEncoder
except Exception:
    logging.error("[Board] Failed to import gpiozero. Using mock instead.")

    class Button:
        def __init__(self, num, pull_up=False):
            self.num = num
            self.pull_up = pull_up
            self.when_pressed = lambda: None
            self.when_released = lambda: None

    class RotaryEncoder:
        def __init__(self, encoding1, encoding2):
            self.encoding1 = encoding1
            self.encoding2 = encoding2
            self.when_rotated_clockwise = lambda: None
            self.when_rotated_counter_clockwise = lambda: None


class Board:
    SCREEN_RATIO: int = 16
    FIRST_GPIO_PIN: int = 0
    LAST_GPIO_PIN: int = 27
    MIN_BRIGHTNESS: int = 0
    MAX_BRIGHTNESS: int = 100

    pixel_rows: int
    pixel_cols: int
    encoder_clk: int
    encoder_dt: int
    encoder: RotaryEncoder
    encoder_sw: int
    encoder_button: Button
    tilt_switch: int
    tilt_switch_button: Button
    brightness: int
    is_display_on: bool = True
    encoder_queue: queue.Queue
    encoder_state: int = 0
    is_horizontal: bool = True
    encoder_input_status: InputStatus = InputStatus.NOTHING
    black_screen: Image

    @classmethod
    def init_system():
        """
        Initializes the system components.
        """
        Board._init_display()
        Board._init_encoder()
        Board._init_tilt_switch()
        logging.debug("[Board] All system components initialized.")

    @classmethod
    def _init_display():
        """
        Initializes the display settings.
        """
        Board.pixel_rows = Settings.read_variable(
            "System", "pixel_rows", Importance.CRITICAL
        )
        if (
            Board.pixel_rows % Board.SCREEN_RATIO != 0
            or Board.pixel_rows <= 0
            or Board.pixel_rows is None
        ):
            logging.error(
                f"[Board] pixel_rows must be a positive multiple of {Board.SCREEN_RATIO} to work with the 'rpi-rgb-led-matrix' library."
            )
            logging.error("[Board] Exiting program.")
            raise
        else:
            logging.debug(f"[Board] pixel_rows: {Board.pixel_rows}")

        Board.pixel_cols = Settings.read_variable(
            "System", "pixel_cols", Importance.CRITICAL
        )
        if (
            Board.pixel_cols % Board.SCREEN_RATIO != 0
            or Board.pixel_cols <= 0
            or Board.pixel_cols is None
        ):
            logging.error(
                f"[Board] pixel_cols must be a multiple of {Board.SCREEN_RATIO} to work with the 'rpi-rgb-led-matrix' library."
            )
            logging.error("[Board] Exiting program.")
            raise
        else:
            logging.debug(f"[Board] pixel_cols: {Board.pixel_cols}")

        Board.brightness = Settings.read_variable("System", "brightness")
        if (
            Board.brightness < Board.MIN_BRIGHTNESS
            or Board.brightness > Board.MAX_BRIGHTNESS
            or Board.brightness is None
        ):
            logging.error(
                f"[Board] brightness must be between {Board.MIN_BRIGHTNESS} and {Board.MAX_BRIGHTNESS}."
            )
            logging.error("[Board] Exiting program.")
            raise
        else:
            logging.debug(f"[Board] brightness: {Board.brightness}")
        logging.debug("[Board] All display settings initialized.")

        Board.black_screen = Image.new(
            "RGB", (Board.pixel_rows, Board.pixel_cols), (0, 0, 0)
        )

    @classmethod
    def _init_encoder():
        """
        Initializes the encoder settings.
        """
        Board.encoder_clk = Settings.read_variable(
            "Pinout", "encoder_clk", Importance.CRITICAL
        )
        if (
            Board.encoder_clk < Board.FIRST_GPIO_PIN
            or Board.encoder_clk > Board.LAST_GPIO_PIN
            or Board.encoder_clk is None
        ):
            logging.error(
                f"[Board] encoder_clk must be between {Board.FIRST_GPIO_PIN} and {Board.LAST_GPIO_PIN}."
            )
            logging.error("[Board] Exiting program.")
            raise
        logging.debug(f"[Board] encoder_clk: {Board.encoder_clk}")

        Board.encoder_dt = Settings.read_variable(
            "Pinout", "encoder_dt", Importance.CRITICAL
        )
        if (
            Board.encoder_dt < Board.FIRST_GPIO_PIN
            or Board.encoder_dt > Board.LAST_GPIO_PIN
            or Board.encoder_dt is None
        ):
            logging.error(
                f"[Board] encoder_dt must be between {Board.FIRST_GPIO_PIN} and {Board.LAST_GPIO_PIN}."
            )
            logging.error("[Board] Exiting program.")
            raise
        logging.debug(f"[Board] encoder_dt: {Board.encoder_dt}")

        Board.encoder_sw = Settings.read_variable(
            "Pinout", "encoder_sw", Importance.CRITICAL
        )
        if (
            Board.encoder_sw < Board.FIRST_GPIO_PIN
            or Board.encoder_sw > Board.LAST_GPIO_PIN
            or Board.encoder_sw is None
        ):
            logging.error(
                f"[Board] encoder_sw must be between {Board.FIRST_GPIO_PIN} and {Board.LAST_GPIO_PIN}."
            )
            logging.error("[Board] Exiting program.")
            raise
        logging.debug(f"[Board] encoder_sw: {Board.encoder_sw}")

        Board.encoder_button = Button(Board.encoder_sw, pull_up=True)
        Board.encoder_button.when_pressed = (
            lambda button: Board.encoder_button_callback(button)
        )
        logging.debug("[Board] Encoder button initialized.")

        Board.encoder_queue = queue.Queue()
        Board.encoder = RotaryEncoder(Board.encoder_clk, Board.encoder_dt)
        Board.encoder.when_rotated_clockwise = (
            lambda enc: Board.rotate_clockwise_callback(enc)
        )
        Board.encoder.when_rotated_counter_clockwise = (
            lambda enc: Board.rotate_counter_clockwise_callback(enc)
        )
        logging.debug("[Board] Encoder initialized.")

    @classmethod
    def _init_tilt_switch():
        """
        Initializes the tilt switch settings.
        """
        Board.tilt_switch = Settings.read_variable(
            "Pinout", "tilt_switch", Importance.CRITICAL
        )
        if (
            Board.tilt_switch < Board.FIRST_GPIO_PIN
            or Board.tilt_switch > Board.LAST_GPIO_PIN
            or Board.tilt_switch is None
        ):
            logging.error("[Board] tilt_switch must be between 0 and 27.")
            logging.error("[Board] Exiting program.")
            raise
        logging.debug(f"[Board] tilt_switch: {Board.tilt_switch}")

        Board.tilt_switch_button = Button(Board.tilt_switch_button, pull_up=True)
        Board.tilt_switch_button.when_pressed = lambda button: Board.tilt_callback(
            button
        )
        Board.tilt_switch_button.when_released = lambda button: Board.tilt_callback(
            button
        )
        logging.debug("[Board] Tilt switch button initialized.")

    @classmethod
    def rotate_clockwise_callback(encoder):
        """
        Callback function for rotating the encoder clockwise.
        """
        Board.encoder_queue.put(1)
        Board.reset_encoder(encoder)

    @classmethod
    def rotate_counter_clockwise_callback(encoder):
        """
        Callback function for rotating the encoder counter-clockwise.
        """
        Board.encoder_queue.put(-1)
        Board.reset_encoder(encoder)

    @classmethod
    def reset_encoder(encoder):
        """
        Resets the encoder value to 0.
        """
        encoder.value = 0

    @classmethod
    def tilt_callback(tilt_switch):
        """
        Callback function for the tilt switch.
        """
        TILT_DEBOUNCE_TIME = 0.25
        startTime = time.time()
        while time.time() - startTime < TILT_DEBOUNCE_TIME:
            pass
        Board.is_horizontal = tilt_switch.is_pressed

    @classmethod
    def encoder_button_callback(enc_button):
        """
        Callback function for the encoder button.
        """
        start_time = time.time()
        time_diff = 0
        hold_time = 1

        while enc_button.is_active and (time_diff < hold_time):
            time_diff = time.time() - start_time

        if time_diff >= hold_time:
            print("long press detected")
            Board.encoder_input_status = InputStatus.LONG_PRESS
        else:
            enc_button.when_pressed = None
            start_time = time.time()
            while time.time() - start_time <= 0.3:
                time.sleep(0.1)
                if enc_button.is_pressed:
                    time.sleep(0.1)
                    new_start_time = time.time()
                    while time.time() - new_start_time <= 0.3:
                        time.sleep(0.1)
                        if enc_button.is_pressed:
                            print("triple press detected")
                            Board.encoder_input_status = InputStatus.TRIPLE_PRESS
                            enc_button.when_pressed = (
                                lambda button: Board.encoder_button_callback(button)
                            )
                            return
                    print("double press detected")
                    Board.encoder_input_status = InputStatus.DOUBLE_PRESS
                    enc_button.when_pressed = (
                        lambda button: Board.encoder_button_callback(button)
                    )
                    return
            print("single press detected")
            Board.encoder_input_status = InputStatus.SINGLE_PRESS
            enc_button.when_pressed = lambda button: Board.encoder_button_callback(
                button
            )
            return
