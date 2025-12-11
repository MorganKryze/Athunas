import os
from datetime import datetime

from loguru import logger

from config import Configuration
from path import PathTo


class Logs:
    @classmethod
    def start(cls, file_level: str = "DEBUG", console_level: str = "WARNING") -> None:
        """
        Starts logging with the specified log levels.

        Args:
            :param file_level: The log level for file logging (default is "DEBUG").
            :param console_level: The log level for console logging (default is "WARNING").
        """
        cls.create_logger(file_level, console_level)
        logger.info(
            "--------------------------------------------------------------------------------------------------------------------------------"
        )
        logger.info(
            f"[Init] Application started, version: {Configuration.get_version_from_pyproject()}, "
            f"file log level: {file_level}, "
            f"console log level: {console_level}."
        )
        hostname, ip_address = Configuration.get_addresses()
        logger.info(f"[Init] Application running on {hostname} ({ip_address}).")

    @classmethod
    def create_logger(
        cls, file_level: str = "DEBUG", console_level: str = "WARNING"
    ) -> None:
        """
        Creates a logger with the specified log levels.

        Args:
            :param file_level: The log level for file logging (default is "DEBUG").
            :param console_level: The log level for console logging (default is "WARNING").
        """
        # Remove default handler
        logger.remove()

        os.makedirs(PathTo.LOGS_FOLDER, exist_ok=True)

        log_filename = datetime.now().strftime("%Y-%m-%d") + ".log"
        log_file_path = os.path.join(PathTo.LOGS_FOLDER, log_filename)

        # Add file handler with rotation
        logger.add(
            log_file_path,
            format="{time:YYYY-MM-DD HH:mm:ss} - {level} - {message}",
            level=file_level,
            rotation="00:00",  # Rotate at midnight
            retention="30 days",  # Keep logs for 30 days
        )

        # Add console handler
        logger.add(
            lambda msg: print(msg, end=""),
            format="{time:YYYY-MM-DD HH:mm:ss} - {level} - {message}\n",
            level=console_level,
        )
