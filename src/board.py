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
    BRIGHTNESS_MIN: int = 0
    BRIGHTNESS_MAX: int = 100
    BRIGHTNESS_STEP: int = 5

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
    def init_system(cls):
        """
        Initializes the system components.
        """
        cls._init_display()
        cls._init_encoder()
        cls._init_tilt_switch()
        logging.debug("[Board] All system components initialized.")

    @classmethod
    def _init_display(cls):
        """
        Initializes the display settings.
        """
        cls.pixel_rows = Settings.read_variable(
            "System", "pixel_rows", Importance.REQUIRED
        )
        if cls.pixel_rows % cls.SCREEN_RATIO != 0 or cls.pixel_rows <= 0:
            logging.error(
                f"[Board] pixel_rows must be a positive multiple of {cls.SCREEN_RATIO} to work with the 'rpi-rgb-led-matrix' library."
            )
            logging.error("[Board] Exiting program.")
            raise
        else:
            logging.debug(f"[Board] pixel_rows: {cls.pixel_rows}")

        cls.pixel_cols = Settings.read_variable(
            "System", "pixel_cols", Importance.REQUIRED
        )
        if cls.pixel_cols % cls.SCREEN_RATIO != 0 or cls.pixel_cols <= 0:
            logging.error(
                f"[Board] pixel_cols must be a multiple of {cls.SCREEN_RATIO} to work with the 'rpi-rgb-led-matrix' library."
            )
            logging.error("[Board] Exiting program.")
            raise
        else:
            logging.debug(f"[Board] pixel_cols: {cls.pixel_cols}")

        cls.brightness = Settings.read_variable(
            "System", "brightness", Importance.REQUIRED
        )
        if cls.brightness < cls.BRIGHTNESS_MIN or cls.brightness > cls.BRIGHTNESS_MAX:
            logging.error(
                f"[Board] brightness must be between {cls.BRIGHTNESS_MIN} and {cls.BRIGHTNESS_MAX}."
            )
            logging.error("[Board] Exiting program.")
            raise
        else:
            logging.debug(f"[Board] brightness: {cls.brightness}")
        logging.debug("[Board] All display settings initialized.")

        cls.black_screen = Image.new("RGB", (cls.pixel_rows, cls.pixel_cols), (0, 0, 0))

    @classmethod
    def _init_encoder(cls):
        """
        Initializes the encoder settings.
        """
        cls.encoder_clk = Settings.read_variable(
            "Pinout", "encoder_clk", Importance.REQUIRED
        )
        if cls.encoder_clk < cls.FIRST_GPIO_PIN or cls.encoder_clk > cls.LAST_GPIO_PIN:
            logging.error(
                f"[Board] encoder_clk must be between {cls.FIRST_GPIO_PIN} and {cls.LAST_GPIO_PIN}."
            )
            logging.error("[Board] Exiting program.")
            raise
        logging.debug(f"[Board] encoder_clk: {cls.encoder_clk}")

        cls.encoder_dt = Settings.read_variable(
            "Pinout", "encoder_dt", Importance.REQUIRED
        )
        if cls.encoder_dt < cls.FIRST_GPIO_PIN or cls.encoder_dt > cls.LAST_GPIO_PIN:
            logging.error(
                f"[Board] encoder_dt must be between {cls.FIRST_GPIO_PIN} and {cls.LAST_GPIO_PIN}."
            )
            logging.error("[Board] Exiting program.")
            raise
        logging.debug(f"[Board] encoder_dt: {cls.encoder_dt}")

        cls.encoder_sw = Settings.read_variable(
            "Pinout", "encoder_sw", Importance.REQUIRED
        )
        if cls.encoder_sw < cls.FIRST_GPIO_PIN or cls.encoder_sw > cls.LAST_GPIO_PIN:
            logging.error(
                f"[Board] encoder_sw must be between {cls.FIRST_GPIO_PIN} and {cls.LAST_GPIO_PIN}."
            )
            logging.error("[Board] Exiting program.")
            raise
        logging.debug(f"[Board] encoder_sw: {cls.encoder_sw}")

        cls.encoder_button = Button(cls.encoder_sw, pull_up=True)
        cls.encoder_button.when_pressed = lambda button: cls.encoder_button_callback(
            button
        )
        logging.debug("[Board] Encoder button initialized.")

        cls.encoder_queue = queue.Queue()
        cls.encoder = RotaryEncoder(cls.encoder_clk, cls.encoder_dt)
        cls.encoder.when_rotated_clockwise = lambda enc: cls.rotate_clockwise_callback(
            enc
        )
        cls.encoder.when_rotated_counter_clockwise = (
            lambda enc: cls.rotate_counter_clockwise_callback(enc)
        )
        logging.debug("[Board] Encoder initialized.")

    @classmethod
    def _init_tilt_switch(cls):
        """
        Initializes the tilt switch settings.
        """
        cls.tilt_switch = Settings.read_variable(
            "Pinout", "tilt_switch", Importance.REQUIRED
        )
        if cls.tilt_switch < cls.FIRST_GPIO_PIN or cls.tilt_switch > cls.LAST_GPIO_PIN:
            logging.error("[Board] tilt_switch must be between 0 and 27.")
            logging.error("[Board] Exiting program.")
            raise
        logging.debug(f"[Board] tilt_switch: {cls.tilt_switch}")

        cls.tilt_switch_button = Button(cls.tilt_switch, pull_up=True)
        cls.tilt_switch_button.when_pressed = lambda button: cls.tilt_callback(button)
        cls.tilt_switch_button.when_released = lambda button: cls.tilt_callback(button)
        logging.debug("[Board] Tilt switch button initialized.")

    @classmethod
    def rotate_clockwise_callback(cls, encoder):
        """
        Callback function for rotating the encoder clockwise.
        """
        cls.encoder_queue.put(1)
        cls.reset_encoder(encoder)

    @classmethod
    def rotate_counter_clockwise_callback(cls, encoder):
        """
        Callback function for rotating the encoder counter-clockwise.
        """
        cls.encoder_queue.put(-1)
        cls.reset_encoder(encoder)

    @classmethod
    def reset_encoder(cls, encoder):
        """
        Resets the encoder value to 0.
        """
        encoder.value = 0

    @classmethod
    def tilt_callback(cls, tilt_switch):
        """
        Callback function for the tilt switch.
        """
        TILT_DEBOUNCE_TIME = 0.25
        startTime = time.time()
        while time.time() - startTime < TILT_DEBOUNCE_TIME:
            pass
        cls.is_horizontal = tilt_switch.is_pressed

    @classmethod
    def encoder_button_callback(cls, enc_button):
        """
        Callback function for the encoder button.
        """
        start_time = time.time()
        time_diff = 0
        hold_time = 1

        while enc_button.is_active and (time_diff < hold_time):
            time_diff = time.time() - start_time

        if time_diff >= hold_time:
            # TODO: Change to a logging message
            print("long press detected")
            cls.encoder_input_status = InputStatus.LONG_PRESS
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
                            # TODO: Change to a logging message
                            print("triple press detected")
                            cls.encoder_input_status = InputStatus.TRIPLE_PRESS
                            enc_button.when_pressed = (
                                lambda button: cls.encoder_button_callback(button)
                            )
                            return
                    # TODO: Change to a logging message
                    print("double press detected")
                    cls.encoder_input_status = InputStatus.DOUBLE_PRESS
                    enc_button.when_pressed = (
                        lambda button: cls.encoder_button_callback(button)
                    )
                    return
            # TODO: Change to a logging message
            print("single press detected")
            cls.encoder_input_status = InputStatus.SINGLE_PRESS
            enc_button.when_pressed = lambda button: cls.encoder_button_callback(button)
            return
