import logging
import time
from PIL import Image
import queue

from enums.input_status import InputStatus
from enums.variable_importance import Importance
from settings import Settings
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
        cls.led_rows = Settings.read_variable("System", "led_rows", Importance.REQUIRED)
        if cls.led_rows % cls.SCREEN_RATIO != 0 or cls.led_rows <= 0:
            logging.critical(
                f"[Board] led_rows must be a positive multiple of {cls.SCREEN_RATIO} to work with the 'rpi-rgb-led-matrix' library."
            )
            logging.critical("[Board] Exiting program.")
            raise

        cls.led_cols = Settings.read_variable("System", "led_cols", Importance.REQUIRED)
        if cls.led_cols % cls.SCREEN_RATIO != 0 or cls.led_cols <= 0:
            logging.critical(
                f"[Board] led_cols must be a multiple of {cls.SCREEN_RATIO} to work with the 'rpi-rgb-led-matrix' library."
            )
            logging.critical("[Board] Exiting program.")
            raise

        cls.brightness = Settings.read_variable(
            "System", "brightness", Importance.REQUIRED
        )
        if cls.brightness < cls.BRIGHTNESS_MIN or cls.brightness > cls.BRIGHTNESS_MAX:
            logging.critical(
                f"[Board] brightness must be between {cls.BRIGHTNESS_MIN} and {cls.BRIGHTNESS_MAX}."
            )
            logging.critical("[Board] Exiting program.")
            raise
        logging.info("[Board] All display settings initialized.")

        cls.black_screen = Image.new("RGB", (cls.led_cols, cls.led_rows), (0, 0, 0))

    @classmethod
    def _init_encoder(cls):
        """
        Initializes the encoder settings.
        """
        cls.encoder_clk = Settings.read_variable(
            "Pinout", "encoder_clk", Importance.REQUIRED
        )
        if cls.encoder_clk < cls.FIRST_GPIO_PIN or cls.encoder_clk > cls.LAST_GPIO_PIN:
            logging.critical(
                f"[Board] encoder_clk must be between {cls.FIRST_GPIO_PIN} and {cls.LAST_GPIO_PIN}."
            )
            logging.critical("[Board] Exiting program.")
            raise

        cls.encoder_dt = Settings.read_variable(
            "Pinout", "encoder_dt", Importance.REQUIRED
        )
        if cls.encoder_dt < cls.FIRST_GPIO_PIN or cls.encoder_dt > cls.LAST_GPIO_PIN:
            logging.critical(
                f"[Board] encoder_dt must be between {cls.FIRST_GPIO_PIN} and {cls.LAST_GPIO_PIN}."
            )
            logging.critical("[Board] Exiting program.")
            raise

        cls.encoder_sw = Settings.read_variable(
            "Pinout", "encoder_sw", Importance.REQUIRED
        )
        if cls.encoder_sw < cls.FIRST_GPIO_PIN or cls.encoder_sw > cls.LAST_GPIO_PIN:
            logging.critical(
                f"[Board] encoder_sw must be between {cls.FIRST_GPIO_PIN} and {cls.LAST_GPIO_PIN}."
            )
            logging.critical("[Board] Exiting program.")
            raise

        cls.encoder_button = Button(cls.encoder_sw, pull_up=True, bounce_time=0.1)
        cls.encoder_button.when_pressed = lambda button: cls.encoder_button_callback(
            button
        )
        logging.info("[Board] Encoder button initialized.")

        cls.encoder_queue = queue.Queue()
        cls.encoder = RotaryEncoder(cls.encoder_clk, cls.encoder_dt)
        cls.encoder.when_rotated_clockwise = lambda enc: cls.rotate_clockwise_callback(
            enc
        )
        cls.encoder.when_rotated_counter_clockwise = (
            lambda enc: cls.rotate_counter_clockwise_callback(enc)
        )
        logging.info("[Board] Encoder initialized.")

    @classmethod
    def _init_tilt_switch(cls):
        """
        Initializes the tilt switch settings.
        """
        cls.tilt_switch = Settings.read_variable(
            "Pinout", "tilt_switch", Importance.REQUIRED
        )
        if cls.tilt_switch < cls.FIRST_GPIO_PIN or cls.tilt_switch > cls.LAST_GPIO_PIN:
            logging.critical("[Board] tilt_switch must be between 0 and 27.")
            logging.critical("[Board] Exiting program.")
            raise

        cls.tilt_switch_button = Button(cls.tilt_switch, pull_up=True)
        cls.tilt_switch_button.when_pressed = lambda button: cls.tilt_callback(button)
        cls.tilt_switch_button.when_released = lambda button: cls.tilt_callback(button)
        logging.debug("[Board] Tilt switch button initialized.")

    @classmethod
    def rotate_clockwise_callback(cls, encoder):
        """
        Callback function for rotating the encoder clockwise.
        """
        logging.debug(f"[Board] Rotated clockwise: {cls.encoder_state}.")
        cls.encoder_queue.put(1)
        cls.reset_encoder(encoder)

    @classmethod
    def rotate_counter_clockwise_callback(cls, encoder):
        """
        Callback function for rotating the encoder counter-clockwise.
        """
        logging.debug(f"[Board] Rotated counter-clockwise: {cls.encoder_state}.")
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
        logging.debug("[Board] Tilt switch activated.")
        cls.is_horizontal = tilt_switch.is_pressed

    @classmethod
    def encoder_button_callback(cls, enc_button):
        """
        Callback function for the encoder button.
        """
        # TODO: NOW ONLY SINGLE PRESS AND LONG ARE PARTIALLY RECOGNIZED
        start_time = time.time()
        hold_time = 1
        press_count = 0

        while enc_button.is_active and (time.time() - start_time < hold_time):
            time.sleep(0.1)
            if not enc_button.is_active:
                press_count += 1
                start_time = time.time()
                if press_count == 3:
                    logging.debug("[Board] Triple press detected (3).")
                    cls.encoder_input_status = InputStatus.TRIPLE_PRESS
                    return
                elif press_count == 2:
                    logging.debug("[Board] Double press detected (2).")
                    cls.encoder_input_status = InputStatus.DOUBLE_PRESS
                    return

        if time.time() - start_time >= hold_time:
            logging.debug("[Board] Long press detected (5).")
            cls.encoder_input_status = InputStatus.LONG_PRESS
        elif press_count == 1:
            logging.debug("[Board] Single press detected (1).")
            cls.encoder_input_status = InputStatus.SINGLE_PRESS

        # Reset the button state
        enc_button.when_pressed = lambda button: cls.encoder_button_callback(button)
