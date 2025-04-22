from datetime import datetime
import logging
import os

from path import PathTo
from config import Configuration


class Logs:
    @classmethod
    def start(
        cls, file_level: int = logging.DEBUG, console_level: int = logging.WARNING
    ) -> None:
        """
        Starts logging with the specified log levels.

        Args:
            :param file_level: The log level for file logging (default is logging.DEBUG).
            :param console_level: The log level for console logging (default is logging.WARNING).
        """
        cls.create_logger(file_level, console_level)
        logging.info(
            "--------------------------------------------------------------------------------------------------------------------------------"
        )
        logging.info(
            f"[Init] Application started, version: {Configuration.get_version_from_pyproject()}, "
            f"file log level: {logging.getLevelName(file_level)}, "
            f"console log level: {logging.getLevelName(console_level)}."
        )
        hostname, ip_address = Configuration.get_addresses()
        logging.info(f"[Init] Application running on {hostname} ({ip_address}).")

    @classmethod
    def create_logger(
        cls, file_level: int = logging.DEBUG, console_level: int = logging.WARNING
    ) -> None:
        """
        Creates a logger with the specified log levels.

        Args:
            :param file_level: The log level for file logging (default is logging.DEBUG).
            :param console_level: The log level for console logging (default is logging.WARNING).
        """
        os.makedirs(PathTo.LOGS_FOLDER, exist_ok=True)

        log_filename = datetime.now().strftime("%Y-%m-%d") + ".log"
        log_file_path = os.path.join(PathTo.LOGS_FOLDER, log_filename)

        logger = logging.getLogger()
        logger.setLevel(
            min(file_level, console_level)
        )  # Set to the lowest level to capture all relevant logs

        # Remove any existing handlers to avoid conflicts
        if logger.hasHandlers():
            logger.handlers.clear()

        file_handler = logging.FileHandler(log_file_path)
        console_handler = logging.StreamHandler()

        file_handler.setLevel(file_level)
        console_handler.setLevel(console_level)

        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
