import os
import sys
import inspect
import logging
from datetime import datetime
from typing import Any


class Utils:
    base_directory: str = ""

    @classmethod
    def set_base_directory(cls, base_dir_name: str = "Athunas") -> str:
        """
        Sets the base directory for the script to the specified directory name.

        :param base_dir_name: The name of the base directory (default is 'Athunas').
        :return: The absolute path of the base directory.
        """
        current_script_path = os.path.abspath(inspect.getfile(inspect.currentframe()))
        current_script_dir = os.path.dirname(current_script_path)
        base_dir = os.path.abspath(
            os.path.join(current_script_dir, "..", "..", base_dir_name)
        )
        os.chdir(base_dir)
        sys.path.append(base_dir)
        sys.path.append(
            os.path.join(base_dir, "rpi-rgb-led-matrix", "bindings", "python")
        )
        cls.base_directory = base_dir
        return base_dir

    @staticmethod
    def start_logging(level: int = logging.DEBUG) -> None:
        """
        Starts logging with the specified log level.

        :param level: The log level (default is logging.DEBUG).
        """
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)

        log_filename = datetime.now().strftime("%Y-%m-%d") + ".log"
        log_file_path = os.path.join(log_dir, log_filename)

        logger = logging.getLogger()
        logger.setLevel(level)

        # Remove any existing handlers to avoid conflicts
        if logger.hasHandlers():
            logger.handlers.clear()

        file_handler = logging.FileHandler(log_file_path)
        console_handler = logging.StreamHandler()

        file_handler.setLevel(level)
        console_handler.setLevel(level)

        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        logging.info("-------------------------------------------------------------")
        logging.info("[Utils] Application started.")

    @staticmethod
    def create_matrix(
        pixel_rows: int,
        pixel_cols: int,
        brightness: int = 100,
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
            from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions
        else:
            from rgbmatrix import RGBMatrix, RGBMatrixOptions

        logging.debug(
            f"[Utils] Creating RGBMatrix options with screen height: {pixel_rows}, screen width: {pixel_cols}, brightness: {brightness}, disable hardware pulsing: {disable_hardware_pulsing}, hardware mapping: {hardware_mapping}"
        )
        try:
            options = RGBMatrixOptions()
            options.rows = pixel_rows
            options.cols = pixel_cols
            options.brightness = brightness
            options.disable_hardware_pulsing = disable_hardware_pulsing
            options.hardware_mapping = hardware_mapping

            logging.debug("[Utils] RGBMatrix options set.")
        except Exception as e:
            logging.error(f"[Utils] failed to set RGBMatrix options: {e}")
            raise

        logging.debug("[Utils] Creating RGBMatrix object with options.")
        try:
            matrix = RGBMatrix(options=options)
            logging.debug("[Utils] RGBMatrix object created.")
            return matrix
        except Exception as e:
            logging.error(f"[Utils] failed to create RGBMatrix object: {e}")
            raise
