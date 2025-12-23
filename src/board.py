import queue
import time
from typing import Any

from gpiozero import Button, RotaryEncoder
from gpiozero.pins.pigpio import PiGPIOFactory
from loguru import logger

from config import Configuration
from custom_frames import CustomFrames
from enums.encoder_input import EncoderInput
from enums.tilt_input import TiltState

# TODO: separate the Matrix from the IO, rename the calss to IO and create a Matrix class for example

class Board:
    """Class to manage the board's hardware components and their interactions."""

    factory: PiGPIOFactory = PiGPIOFactory()
    SCREEN_RATIO: int = 16
    FIRST_GPIO_PIN: int = 0
    LAST_GPIO_PIN: int = 27
    BRIGHTNESS_MIN: int = 0
    BRIGHTNESS_MAX: int = 100
    BRIGHTNESS_STEP: int = 5

    led_rows: int
    led_cols: int
    brightness: int
    disable_hardware_pulsing: bool
    hardware_mapping: str
    refresh_rate: float
    encoder_clk: int
    encoder_dt: int
    encoder: RotaryEncoder
    encoder_sw: int
    encoder_button: Button
    tilt_switch: int
    tilt_switch_button: Button
    tilt_switch_bounce_time: float
    is_display_on: bool = True
    encoder_queue: queue.Queue
    encoder_state: int = 0
    tilt_state: TiltState = TiltState.HORIZONTAL
    encoder_input: EncoderInput = EncoderInput.NOTHING
    matrix: Any

    @classmethod
    def cleanup_gpio(cls) -> None:
        """
        Cleanup GPIO resources to prevent conflicts.
        """
        try:
            if hasattr(cls, "encoder") and cls.encoder:
                cls.encoder.close()
                logger.debug("Encoder cleaned up.")
        except Exception as e:
            logger.warning(f"Error cleaning up encoder: {e}")

        try:
            if hasattr(cls, "encoder_button") and cls.encoder_button:
                cls.encoder_button.close()
                logger.debug("Encoder button cleaned up.")
        except Exception as e:
            logger.warning(f"Error cleaning up encoder button: {e}")

        try:
            if hasattr(cls, "tilt_switch_button") and cls.tilt_switch_button:
                cls.tilt_switch_button.close()
                logger.debug("Tilt switch button cleaned up.")
        except Exception as e:
            logger.warning(f"Error cleaning up tilt switch button: {e}")

    @classmethod
    def init_system(cls, use_emulator: bool = False) -> None:
        """
        Initializes the system components.

        :param use_emulator: Whether to use the emulator for the RGB matrix (default is False).
        """
        cls.cleanup_gpio()

        cls._init_display()
        cls.init_matrix(use_emulator=use_emulator)
        CustomFrames.init(cls.led_rows, cls.led_cols)

        try:
            cls._init_encoder()
            cls._init_tilt_switch()
            logger.debug("All system components initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize GPIO components: {e}")
            cls.cleanup_gpio()
            Configuration.critical_exit(
                f"Failed to initialize GPIO components: {e}. "
                "Please ensure no other processes are using the GPIO pins and try running with sudo."
            )

    @classmethod
    def _init_display(cls) -> None:
        """
        Initializes the display settings.
        """
        cls.led_rows = Configuration.get("System", "Matrix", "led_rows", required=True)
        if cls.led_rows % cls.SCREEN_RATIO != 0 or cls.led_rows <= 0:
            Configuration.critical_exit(
                f"System.Matrix.led_rows must be a positive multiple of {cls.SCREEN_RATIO} to work with the 'rpi-rgb-led-matrix' library."
            )

        cls.led_cols = Configuration.get("System", "Matrix", "led_cols", required=True)
        if cls.led_cols % cls.SCREEN_RATIO != 0 or cls.led_cols <= 0:
            Configuration.critical_exit(
                f"System.Matrix.led_cols must be a positive multiple of {cls.SCREEN_RATIO} to work with the 'rpi-rgb-led-matrix' library."
            )

        cls.brightness = Configuration.get(
            "System", "Matrix", "brightness", required=True
        )
        if cls.brightness < cls.BRIGHTNESS_MIN or cls.brightness > cls.BRIGHTNESS_MAX:
            Configuration.critical_exit(
                f"System.Matrix.brightness must be between {cls.BRIGHTNESS_MIN} and {cls.BRIGHTNESS_MAX}."
            )

        cls.disable_hardware_pulsing = Configuration.get(
            "System", "Matrix", "disable_hardware_pulsing", required=True
        )
        if not isinstance(cls.disable_hardware_pulsing, bool):
            Configuration.critical_exit(
                "System.Matrix.disable_hardware_pulsing must be a boolean value."
            )

        cls.hardware_mapping = Configuration.get(
            "System", "Matrix", "hardware_mapping", required=True
        )
        if cls.hardware_mapping not in ["regular", "adafruit-hat"]:
            Configuration.critical_exit(
                "System.Matrix.hardware_mapping must be either 'regular' or 'adafruit-hat'."
            )

        cls.refresh_rate = Configuration.get(
            "System", "Matrix", "refresh_rate", required=True
        )
        if cls.refresh_rate <= 0:
            Configuration.critical_exit(
                "System.Matrix.refresh_rate must be a positive number."
            )

        logger.info("All display settings initialized.")

    @classmethod
    def init_matrix(cls, use_emulator: bool = False) -> None:
        """
        Creates an RGBMatrix object with the specified parameters.

        :param use_emulator: Whether to use the emulator (default is False).
        """
        if use_emulator:
            from RGBMatrixEmulator import RGBMatrix  # type: ignore
            from RGBMatrixEmulator import RGBMatrixOptions  # type: ignore
        else:
            from rgbmatrix import RGBMatrix, RGBMatrixOptions  # type: ignore

        logger.debug(
            f"Creating RGBMatrix options with screen height: {cls.led_rows}, screen width: {cls.led_cols}, brightness: {cls.brightness}, disable hardware pulsing: {cls.disable_hardware_pulsing}, hardware mapping: {cls.hardware_mapping}"
        )
        try:
            options: RGBMatrixOptions = RGBMatrixOptions()
            options.rows = cls.led_rows
            options.cols = cls.led_cols
            options.brightness = cls.brightness
            options.disable_hardware_pulsing = cls.disable_hardware_pulsing
            options.hardware_mapping = cls.hardware_mapping
            logger.debug("RGBMatrix options set.")

            cls.matrix: RGBMatrix = RGBMatrix(options=options)
            logger.debug("RGBMatrix object created.")
        except Exception as e:
            Configuration.critical_exit(
                f"Failed to create RGBMatrix object: {e}. Please check your configuration."
            )

    @classmethod
    def _init_encoder(cls) -> None:
        """
        Initializes the encoder settings.
        """
        cls.encoder_clk = Configuration.get(
            "System", "Encoder", "gpio_clk", required=True
        )
        if cls.encoder_clk < cls.FIRST_GPIO_PIN or cls.encoder_clk > cls.LAST_GPIO_PIN:
            Configuration.critical_exit(
                f"System.Encoder.gpio_clk must be between {cls.FIRST_GPIO_PIN} and {cls.LAST_GPIO_PIN}."
            )

        cls.encoder_dt = Configuration.get(
            "System", "Encoder", "gpio_dt", required=True
        )
        if cls.encoder_dt < cls.FIRST_GPIO_PIN or cls.encoder_dt > cls.LAST_GPIO_PIN:
            Configuration.critical_exit(
                f"System.Encoder.gpio_dt must be between {cls.FIRST_GPIO_PIN} and {cls.LAST_GPIO_PIN}."
            )

        cls.encoder_queue = queue.Queue()

        logger.debug(
            f"About to create RotaryEncoder on pins CLK={cls.encoder_clk}, DT={cls.encoder_dt}"
        )
        logger.debug(f"Current pin factory: {cls.factory}")
        try:
            cls.encoder = RotaryEncoder(
                cls.encoder_clk,
                cls.encoder_dt,
                pin_factory=cls.factory,
            )
            cls.encoder.when_rotated_clockwise = (
                lambda enc: cls.rotate_clockwise_callback(enc)
            )
            cls.encoder.when_rotated_counter_clockwise = (
                lambda enc: cls.rotate_counter_clockwise_callback(enc)
            )
            logger.info("Encoder rotation initialized.")
        except RuntimeError as e:
            if "Failed to add edge detection" in str(e):
                raise RuntimeError(
                    f"GPIO pins {cls.encoder_clk} or {cls.encoder_dt} are already in use or unavailable. "
                    "Please check if another process is using these pins or try different GPIO pins."
                ) from e
            raise

        cls.encoder_sw = Configuration.get(
            "System", "Encoder", "gpio_sw", required=True
        )
        if cls.encoder_sw < cls.FIRST_GPIO_PIN or cls.encoder_sw > cls.LAST_GPIO_PIN:
            Configuration.critical_exit(
                f"System.Encoder.gpio_sw must be between {cls.FIRST_GPIO_PIN} and {cls.LAST_GPIO_PIN}."
            )

        try:
            cls.encoder_button = Button(
                cls.encoder_sw,
                pull_up=True,
                bounce_time=0.1,
                pin_factory=cls.factory,
            )
            cls.encoder_button.when_pressed = (
                lambda button: cls.encoder_button_callback(button)
            )
            logger.info("Encoder button initialized.")
        except RuntimeError as e:
            if "Failed to add edge detection" in str(e):
                raise RuntimeError(
                    f"GPIO pin {cls.encoder_sw} is already in use or unavailable. "
                    "Please check if another process is using this pin or try a different GPIO pin."
                ) from e
            raise

    @classmethod
    def _init_tilt_switch(cls) -> None:
        """
        Initializes the tilt switch settings.
        """
        cls.tilt_switch = Configuration.get(
            "System", "Tilt-switch", "gpio", required=True
        )
        if cls.tilt_switch < cls.FIRST_GPIO_PIN or cls.tilt_switch > cls.LAST_GPIO_PIN:
            Configuration.critical_exit(
                f"System.Tilt-switch.gpio must be between {cls.FIRST_GPIO_PIN} and {cls.LAST_GPIO_PIN}."
            )

        cls.tilt_switch_bounce_time = Configuration.get(
            "System", "Tilt-switch", "bounce_time", required=True
        )
        if cls.tilt_switch_bounce_time < 0:
            Configuration.critical_exit(
                "System.Tilt-switch.bounce_time must be a non-negative number."
            )

        try:
            cls.tilt_switch_button = Button(
                cls.tilt_switch,
                pull_up=True,
                bounce_time=cls.tilt_switch_bounce_time,
                pin_factory=cls.factory,
            )
            cls.tilt_switch_button.when_pressed = lambda button: cls.tilt_callback(
                button
            )
            cls.tilt_switch_button.when_released = lambda button: cls.tilt_callback(
                button
            )
            logger.debug("Tilt switch button initialized.")
        except RuntimeError as e:
            if "Failed to add edge detection" in str(e):
                raise RuntimeError(
                    f"GPIO pin {cls.tilt_switch} is already in use or unavailable. "
                    "Please check if another process is using this pin or try a different GPIO pin."
                ) from e
            raise

    @classmethod
    def rotate_clockwise_callback(cls, encoder: RotaryEncoder) -> None:
        """
        Callback function for rotating the encoder clockwise.

        :param encoder: The RotaryEncoder instance.
        """
        logger.debug("Rotated clockwise: (+).")
        cls.encoder_queue.put(1)
        cls.reset_encoder(encoder)

    @classmethod
    def rotate_counter_clockwise_callback(cls, encoder: RotaryEncoder) -> None:
        """
        Callback function for rotating the encoder counter-clockwise.

        :param encoder: The RotaryEncoder instance.
        """
        logger.debug("Rotated counter-clockwise: (-).")
        cls.encoder_queue.put(-1)
        cls.reset_encoder(encoder)

    @classmethod
    def tilt_callback(cls, tilt_switch: Button) -> None:
        """
        Callback function for the tilt switch.
        Only logs when orientation actually changes.

        :param tilt_switch: The Button instance for the tilt switch.
        """
        new_state: bool = tilt_switch.is_pressed

        if new_state != cls.tilt_state:
            cls.tilt_state = TiltState.HORIZONTAL if new_state else TiltState.VERTICAL
            logger.debug(
                f"Orientation changed to {cls.tilt_state.name.lower()}."
            )

    @classmethod
    def encoder_button_callback(cls, enc_button: Button) -> None:
        """
        Callback function for the encoder button.

        :param enc_button: The Button instance for the encoder button.
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
            logger.debug("Long press detected (5).")
            cls.encoder_input = EncoderInput.LONG_PRESS
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
                            logger.debug("Triple press detected (3).")
                            cls.encoder_input = EncoderInput.TRIPLE_PRESS
                            enc_button.when_pressed = (
                                lambda button: cls.encoder_button_callback(button)
                            )
                            return
                        logger.debug("Double press detected (2).")
                        cls.encoder_input = EncoderInput.DOUBLE_PRESS
                        enc_button.when_pressed = (
                            lambda button: cls.encoder_button_callback(button)
                        )
                        return
            logger.debug("Single press detected (1).")
            cls.encoder_input = EncoderInput.SINGLE_PRESS
            enc_button.when_pressed = lambda button: cls.encoder_button_callback(button)
            return

    @classmethod
    def reset_encoder(cls, encoder: RotaryEncoder) -> None:
        """
        Resets the encoder value to 0.

        :param encoder: The RotaryEncoder instance.
        """
        encoder.value = 0

    @classmethod
    def reset_encoder_state(cls) -> None:
        """
        Resets the encoder state to 0.
        """
        cls.encoder_state = 0

    @classmethod
    def reset_encoder_input_status(cls) -> None:
        """
        Resets the encoder input status to NOTHING.
        """
        cls.encoder_input = EncoderInput.NOTHING

    @classmethod
    def has_encoder_increased(cls) -> bool:
        """
        Checks if the encoder has increased.

        :returns: True if the encoder has increased, False otherwise.
        """
        if cls.encoder_state > 0:
            return True
        return False

    @classmethod
    def has_encoder_decreased(cls) -> bool:
        """
        Checks if the encoder has decreased.

        :returns: True if the encoder has decreased, False otherwise.
        """
        if cls.encoder_state < 0:
            return True
        return False

    @classmethod
    def loading_animation(cls, duration_in_seconds: int = 4) -> None:
        """
        Displays a loading animation on the matrix.

        :param duration_in_seconds: Duration of the loading animation in seconds (default is 10).
        """
        if duration_in_seconds <= 0:
            logger.warning(
                "Duration for loading animation must be positive. Skipped."
            )
            return
        logger.debug("Starting loading animation.")
        start_time = time.time()
        while time.time() - start_time < duration_in_seconds:
            elapsed = time.time() - start_time
            percentage = min(100, int((elapsed / duration_in_seconds) * 100))
            frame = CustomFrames.loading(percentage)
            if frame is None:
                logger.error(
                    "CustomFrames.loading() returned None. Ensure CustomFrames.init() was called."
                )
                break
            cls.matrix.SetImage(frame)
            time.sleep(0.1)

        final_frame = CustomFrames.loading(100)
        if final_frame is not None:
            cls.matrix.SetImage(final_frame)
            time.sleep(0.5)

        logger.debug("Loading animation completed.")
        black_frame = CustomFrames.black()
        if black_frame is not None:
            cls.matrix.SetImage(black_frame)
            time.sleep(0.5)
        logger.debug("Display cleared after loading animation.")
