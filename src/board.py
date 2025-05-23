import logging
import sys
import time
from typing import Any
from PIL import Image
import queue

from enums.input_status import InputStatus
from enums.variable_importance import Importance
from config import Configuration
from gpiozero import Button, RotaryEncoder


class Board:
    SCREEN_RATIO: int = 16
    FIRST_GPIO_PIN: int = 0
    LAST_GPIO_PIN: int = 27
    BRIGHTNESS_MIN: int = 0
    BRIGHTNESS_MAX: int = 100
    BRIGHTNESS_STEP: int = 5

    led_rows: int
    led_cols: int
    refresh_rate: float
    encoder_clk: int
    encoder_dt: int
    encoder: RotaryEncoder
    encoder_sw: int
    encoder_button: Button
    tilt_switch: int
    tilt_switch_button: Button
    tilt_switch_bounce_time: float
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
        cls.led_rows = Configuration.read_variable(
            "System", "Matrix", "led_rows", Importance.REQUIRED
        )
        if cls.led_rows % cls.SCREEN_RATIO != 0 or cls.led_rows <= 0:
            logging.critical(
                f"[Board] led_rows must be a positive multiple of {cls.SCREEN_RATIO} to work with the 'rpi-rgb-led-matrix' library."
            )
            logging.critical("[Board] Exiting program.")
            sys.exit(1)

        cls.led_cols = Configuration.read_variable(
            "System", "Matrix", "led_cols", Importance.REQUIRED
        )
        if cls.led_cols % cls.SCREEN_RATIO != 0 or cls.led_cols <= 0:
            logging.critical(
                f"[Board] led_cols must be a multiple of {cls.SCREEN_RATIO} to work with the 'rpi-rgb-led-matrix' library."
            )
            logging.critical("[Board] Exiting program.")
            sys.exit(1)

        cls.brightness = Configuration.read_variable(
            "System", "Matrix", "brightness", Importance.REQUIRED
        )
        if cls.brightness < cls.BRIGHTNESS_MIN or cls.brightness > cls.BRIGHTNESS_MAX:
            logging.critical(
                f"[Board] brightness must be between {cls.BRIGHTNESS_MIN} and {cls.BRIGHTNESS_MAX}."
            )
            logging.critical("[Board] Exiting program.")
            sys.exit(1)

        cls.refresh_rate = Configuration.read_variable(
            "System", "Matrix", "refresh_rate", Importance.REQUIRED
        )
        if cls.refresh_rate <= 0:
            logging.critical("[Board] refresh_rate must be positive.")
            logging.critical("[Board] Exiting program.")
            sys.exit(1)

        logging.info("[Board] All display settings initialized.")

        cls.black_screen = Image.new("RGB", (cls.led_cols, cls.led_rows), (0, 0, 0))

    @classmethod
    def _init_encoder(cls):
        """
        Initializes the encoder settings.
        """
        cls.encoder_clk = Configuration.read_variable(
            "System", "Encoder", "gpio_clk", Importance.REQUIRED
        )
        if cls.encoder_clk < cls.FIRST_GPIO_PIN or cls.encoder_clk > cls.LAST_GPIO_PIN:
            logging.critical(
                f"[Board] encoder_clk must be between {cls.FIRST_GPIO_PIN} and {cls.LAST_GPIO_PIN}."
            )
            logging.critical("[Board] Exiting program.")
            sys.exit(1)

        cls.encoder_dt = Configuration.read_variable(
            "System", "Encoder", "gpio_dt", Importance.REQUIRED
        )
        if cls.encoder_dt < cls.FIRST_GPIO_PIN or cls.encoder_dt > cls.LAST_GPIO_PIN:
            logging.critical(
                f"[Board] encoder_dt must be between {cls.FIRST_GPIO_PIN} and {cls.LAST_GPIO_PIN}."
            )
            logging.critical("[Board] Exiting program.")
            sys.exit(1)

        cls.encoder_queue = queue.Queue()
        cls.encoder = RotaryEncoder(cls.encoder_clk, cls.encoder_dt)
        cls.encoder.when_rotated_clockwise = lambda enc: cls.rotate_clockwise_callback(
            enc
        )
        cls.encoder.when_rotated_counter_clockwise = (
            lambda enc: cls.rotate_counter_clockwise_callback(enc)
        )
        logging.info("[Board] Encoder rotation initialized.")

        cls.encoder_sw = Configuration.read_variable(
            "System", "Encoder", "gpio_sw", Importance.REQUIRED
        )
        if cls.encoder_sw < cls.FIRST_GPIO_PIN or cls.encoder_sw > cls.LAST_GPIO_PIN:
            logging.critical(
                f"[Board] encoder_sw must be between {cls.FIRST_GPIO_PIN} and {cls.LAST_GPIO_PIN}."
            )
            logging.critical("[Board] Exiting program.")
            sys.exit(1)

        cls.encoder_button = Button(cls.encoder_sw, pull_up=True, bounce_time=0.1)
        cls.encoder_button.when_pressed = lambda button: cls.encoder_button_callback(
            button
        )
        logging.info("[Board] Encoder button initialized.")

    @classmethod
    def _init_tilt_switch(cls):
        """
        Initializes the tilt switch settings.
        """
        cls.tilt_switch = Configuration.read_variable(
            "System", "Tilt-switch", "gpio", Importance.REQUIRED
        )
        if cls.tilt_switch < cls.FIRST_GPIO_PIN or cls.tilt_switch > cls.LAST_GPIO_PIN:
            logging.critical("[Board] tilt_switch must be between 0 and 27.")
            logging.critical("[Board] Exiting program.")
            sys.exit(1)

        cls.tilt_switch_bounce_time = Configuration.read_variable(
            "System", "Tilt-switch", "bounce_time", Importance.REQUIRED
        )
        if cls.tilt_switch_bounce_time < 0:
            logging.critical("[Board] tilt_switch_bounce_time must be positive.")
            logging.critical("[Board] Exiting program.")
            sys.exit(1)

        cls.tilt_switch_button = Button(
            cls.tilt_switch, pull_up=True, bounce_time=cls.tilt_switch_bounce_time
        )
        cls.tilt_switch_button.when_pressed = lambda button: cls.tilt_callback(button)
        cls.tilt_switch_button.when_released = lambda button: cls.tilt_callback(button)
        logging.debug("[Board] Tilt switch button initialized.")

    @classmethod
    def rotate_clockwise_callback(cls, encoder):
        """
        Callback function for rotating the encoder clockwise.
        """
        logging.debug("[Board] Rotated clockwise: (+).")
        cls.encoder_queue.put(1)
        cls.reset_encoder(encoder)

    @classmethod
    def rotate_counter_clockwise_callback(cls, encoder):
        """
        Callback function for rotating the encoder counter-clockwise.
        """
        logging.debug("[Board] Rotated counter-clockwise: (-).")
        cls.encoder_queue.put(-1)
        cls.reset_encoder(encoder)

    @classmethod
    def tilt_callback(cls, tilt_switch):
        """
        Callback function for the tilt switch.
        Only logs when orientation actually changes.
        """
        new_state = tilt_switch.is_pressed

        if new_state != cls.is_horizontal:
            orientation = "horizontal" if new_state else "vertical"
            logging.debug(f"[Board] Orientation changed to {orientation}")
            cls.is_horizontal = new_state

    @classmethod
    def encoder_button_callback(cls, enc_button):
        """
        Callback function for the encoder button.
        """
        HOLD_TIME = 1
        DOUBLE_PRESS_TIME = 0.3
        TRIPLE_PRESS_TIME = 0.3
        SLEEP_INTERVAL = 0.1

        start_time = time.time()
        time_diff = 0

        while enc_button.is_active and (time_diff < HOLD_TIME):
            time_diff = time.time() - start_time

        if time_diff >= HOLD_TIME:
            logging.debug("[Board] Long press detected (5).")
            cls.encoder_input_status = InputStatus.LONG_PRESS
        else:
            enc_button.when_pressed = None
            start_time = time.time()
            while time.time() - start_time <= DOUBLE_PRESS_TIME:
                time.sleep(SLEEP_INTERVAL)
                if enc_button.is_pressed:
                    time.sleep(SLEEP_INTERVAL)
                    new_start_time = time.time()
                    while time.time() - new_start_time <= TRIPLE_PRESS_TIME:
                        time.sleep(SLEEP_INTERVAL)
                        if enc_button.is_pressed:
                            logging.debug("[Board] Triple press detected (3).")
                            cls.encoder_input_status = InputStatus.TRIPLE_PRESS
                            enc_button.when_pressed = (
                                lambda button: cls.encoder_button_callback(button)
                            )
                            return
                        logging.debug("[Board] Double press detected (2).")
                        cls.encoder_input_status = InputStatus.DOUBLE_PRESS
                        enc_button.when_pressed = (
                            lambda button: cls.encoder_button_callback(button)
                        )
                        return
            logging.debug("[Board] Single press detected (1).")
            cls.encoder_input_status = InputStatus.SINGLE_PRESS
            enc_button.when_pressed = lambda button: cls.encoder_button_callback(button)
            return

    @classmethod
    def reset_encoder(cls, encoder):
        """
        Resets the encoder value to 0.
        """
        encoder.value = 0

    @classmethod
    def reset_encoder_state(cls):
        """
        Resets the encoder state to 0.
        """
        cls.encoder_state = 0

    @classmethod
    def reset_encoder_input_status(cls):
        """
        Resets the encoder input status to NOTHING.
        """
        cls.encoder_input_status = InputStatus.NOTHING

    @classmethod
    def has_encoder_increased(cls):
        """
        Returns True if the encoder has increased, False otherwise.
        """
        if cls.encoder_state > 0:
            return True
        return False

    @classmethod
    def has_encoder_decreased(cls):
        """
        Returns True if the encoder has decreased, False otherwise.
        """
        if cls.encoder_state < 0:
            return True
        return False

    @staticmethod
    def init_matrix(
        pixel_rows: int,
        pixel_cols: int,
        brightness: int,
        disable_hardware_pulsing: bool = True,
        hardware_mapping: str = "regular",
        use_emulator: bool = False,
    ) -> Any:
        """
        Creates an RGBMatrix object with the specified parameters.

        :param pixel_rows: The number of rows of the screen.
        :param pixel_cols: The number of columns of the screen.
        :param brightness: The brightness of the screen (default is 100).
        :param disable_hardware_pulsing: Disables hardware pulsing (default is True).
        :param hardware_mapping: The hardware mapping of the screen (default is 'regular'). For Adafruit HAT: 'adafruit-hat'.
        :return: An RGBMatrix object.
        """
        if use_emulator:
            from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions  # type: ignore
        else:
            from rgbmatrix import RGBMatrix, RGBMatrixOptions  # type: ignore

        logging.debug(
            f"[Config] Creating RGBMatrix options with screen height: {pixel_rows}, screen width: {pixel_cols}, brightness: {brightness}, disable hardware pulsing: {disable_hardware_pulsing}, hardware mapping: {hardware_mapping}"
        )
        try:
            options = RGBMatrixOptions()
            options.rows = pixel_rows
            options.cols = pixel_cols
            options.brightness = brightness
            options.disable_hardware_pulsing = disable_hardware_pulsing
            options.hardware_mapping = hardware_mapping
            logging.debug("[Config] RGBMatrix options set.")

            matrix = RGBMatrix(options=options)
            logging.debug("[Config] RGBMatrix object created.")
            return matrix
        except Exception as e:
            logging.critical(f"[Config] failed to create RGBMatrix object: {e}")
            logging.critical("[Config] Exiting program.")
            sys.exit(1)
