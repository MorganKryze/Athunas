import datetime
import os
import sys
import inspect
import logging
from rgbmatrix import RGBMatrix, RGBMatrixOptions


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
    def create_matrix(screen_width: int, screen_height: int, brightness: int = 100, disable_hardware_pulsing: bool = True, hardware_mapping: str = "regular") -> RGBMatrix:
        """
        Creates an RGBMatrix object with the specified parameters.
        
        :param screen_width: The width of the screen.
        :param screen_height: The height of the screen.
        :param brightness: The brightness of the screen (default is 100).
        :param disable_hardware_pulsing: Disables hardware pulsing (default is True).
        :param hardware_mapping: The hardware mapping of the screen (default is 'regular'). For Adafruit HAT: 'adafruit-hat'.
        :return: An RGBMatrix object.
        """
        logging.debug(f"[Utils] Creating RGBMatrix options with screen width: {screen_width}, screen height: {screen_height}, brightness: {brightness}, disable hardware pulsing: {disable_hardware_pulsing}, hardware mapping: {hardware_mapping}")
        try:
            options = RGBMatrixOptions()
            options.rows = screen_height
            options.cols = screen_width
            options.brightness = brightness
            options.disable_hardware_pulsing = disable_hardware_pulsing
            options.hardware_mapping = hardware_mapping
            options.chain_length = 1
            options.parallel = 1
            options.pixel_mapper_config = "U-mapper;Rotate:180"
            options.gpio_slowdown = 1
            options.pwm_lsb_nanoseconds = 80
            options.limit_refresh_rate_hz = 150
            options.drop_privileges = False
            
            logging.debug("[Utils] RGBMatrix options set.")
        except Exception as e:
            logging.error(f"[Utils] failed to set RGBMatrix options: {e}")
            raise
        
        logging.debug(f"[Utils] Creating RGBMatrix object with options: {options}")
        try:
            matrix = RGBMatrix(options=options)
            logging.debug("[Utils] RGBMatrix object created.")
            return matrix
        except Exception as e:
            logging.error(f"[Utils] failed to create RGBMatrix object: {e}")
            raise
        