from datetime import datetime
import logging
import os

from path import PathTo
from settings import Settings


class Logs:
    @classmethod
    def start(cls, level: int = logging.DEBUG) -> None:
        """
        Starts logging with the specified log level.

        Args:
            :param level: The log level (default is logging.DEBUG).
        """
        cls.create_logger(level)
        logging.info("-------------------------------------------------------------")
        logging.info(
            f"[Utils] Application started, version: {Settings.get_version_from_pyproject()}, log level: {logging.getLevelName(level)}."
        )

    @classmethod
    def create_logger(cls, level: int = logging.DEBUG) -> None:
        """
        Creates a logger with the specified log level.

        Args:
            :param level: The log level (default is logging.DEBUG).
        """
        os.makedirs(PathTo.LOGS_FOLDER, exist_ok=True)

        log_filename = datetime.now().strftime("%Y-%m-%d") + ".log"
        log_file_path = os.path.join(PathTo.LOGS_FOLDER, log_filename)

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
