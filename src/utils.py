import os
import sys
import inspect
import logging
from datetime import datetime
from typing import Any

class Utils:
    @staticmethod
    def start_logging(level: int = logging.DEBUG) -> None:
        """
        Starts logging with the specified log level.

        :param level: The log level (default is logging.DEBUG).
        """
        log_dir = 'logs'
        os.makedirs(log_dir, exist_ok=True)

        log_filename = datetime.now().strftime('%Y-%m-%d') + '.log'
        log_file_path = os.path.join(log_dir, log_filename)

        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            filename=log_file_path,
            filemode='a'
        )

        logging.debug(f"[Utils] Log level set to: {level}")
        logging.info("[Utils] Application started.")
    
    @staticmethod
    def set_base_directory(base_dir_name: str = 'Athunas') -> str:
        """
        Sets the base directory for the script to the specified directory name.

        :param base_dir_name: The name of the base directory (default is 'Athunas').
        :return: The absolute path of the base directory.
        """
        current_script_path = os.path.abspath(inspect.getfile(inspect.currentframe()))
        current_script_dir = os.path.dirname(current_script_path)
        base_dir = os.path.abspath(os.path.join(current_script_dir, '..', '..', base_dir_name))
        os.chdir(base_dir)
        sys.path.append(base_dir)
        return base_dir
        
    @staticmethod
    def create_matrix(pixel_rows: int, pixel_cols: int, brightness: int = 100, disable_hardware_pulsing: bool = False, hardware_mapping: str = "regular") -> Any:
        """
        Creates an RGBMatrix object with the specified parameters.
        
        :param pixel_rows: The number of rows of the screen.
        :param pixel_cols: The number of columns of the screen.
        :param brightness: The brightness of the screen (default is 100).
        :param disable_hardware_pulsing: Disables hardware pulsing (default is True).
        :param hardware_mapping: The hardware mapping of the screen (default is 'regular'). For Adafruit HAT: 'adafruit-hat'.
        :return: An RGBMatrix object.
        """
        from rgbmatrix import RGBMatrix, RGBMatrixOptions
        
        logging.debug(f"[Utils] Creating RGBMatrix options with screen height: {pixel_rows}, screen width: {pixel_cols}, brightness: {brightness}, disable hardware pulsing: {disable_hardware_pulsing}, hardware mapping: {hardware_mapping}")
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
        