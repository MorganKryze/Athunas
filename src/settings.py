import sys
import yaml
import tomllib
import logging
from enums.variable_importance import Importance
from typing import Any, Dict, Optional

from path import PathTo


class Settings:
    data: Dict[str, Any] = {}

    @classmethod
    def load_config(cls) -> None:
        """
        Reads a YAML file and stores its contents in the class dictionary.
        """
        config_file_path = PathTo.CONFIG_FILE
        try:
            with open(config_file_path, "r") as file:
                cls.data = yaml.safe_load(file)
            logging.info("[Settings] Config file loaded successfully.")
        except FileNotFoundError:
            logging.info(f"[Settings] The file '{config_file_path}' was not found.")
            logging.info("[Settings] Creating a new config file from project template.")
            cls.create_config()
        except yaml.YAMLError as e:
            logging.critical(f"[Settings] Failed to parse YAML file: {e}")
            logging.critical("[Settings] Exiting program.")
            sys.exit(1)

    @classmethod
    def create_config(cls) -> None:
        """
        Creates a new YAML file from a project template.
        """
        template_file_path = PathTo.TEMPLATE_CONFIG_FILE
        config_file_path = PathTo.CONFIG_FILE
        try:
            with open(template_file_path, "r") as template_file:
                data = yaml.safe_load(template_file)
            with open(config_file_path, "w") as config_file:
                yaml.safe_dump(data, config_file)
            logging.info("[Settings] Config file created successfully.")
        except FileNotFoundError:
            logging.critical(
                f"[Settings] The file '{template_file_path}' was not found."
            )
            logging.critical("[Settings] Exiting program.")
            sys.exit(1)
        except yaml.YAMLError as e:
            logging.critical(f"[Settings] Failed to parse YAML file: {e}")
            logging.critical("[Settings] Exiting program.")
            sys.exit(1)

    @classmethod
    def save(cls) -> None:
        """
        Writes the class dictionary to a YAML file.
        """
        try:
            with open(cls.file_path, "w") as file:
                yaml.safe_dump(cls.data, file)
            logging.info("[Settings] saved successfully.")
        except IOError as e:
            logging.error(f"[Settings] Failed to write to file: {e}")

    @classmethod
    def read_variable(
        cls, category: str, var: str, importance: Importance = Importance.OPTIONAL
    ) -> Optional[Any]:
        """
        Reads a specific variable from the class dictionary.

        :param category: The category key in the dictionary.
        :param var: The variable key within the category.
        :param importance: The importance level of the variable. Defaults to Importance.NORMAL.
        :return: The value of the variable if it exists, otherwise None.
        """
        value = cls.data.get(category, {}).get(var)
        if value is None:
            logging.warning(f"[Settings] variable not found: {category} -> {var}")
            if importance == Importance.REQUIRED:
                logging.critical(
                    f"[Settings] Required variable not found: {category} -> {var}"
                )
                logging.critical("[Settings] Exiting program.")
                sys.exit(1)
        logging.debug(f"[Settings] read variable: {category} -> {var}={value}")
        return value

    @classmethod
    def update_variable(
        cls,
        category: str,
        var: str,
        value: Any,
    ) -> None:
        """
        Updates a specific variable in the class dictionary.

        :param category: The category key in the dictionary.
        :param var: The variable key within the category.
        :param value: The new value of the variable.
        """
        if category not in cls.data:
            raise ValueError(f"[Settings] category not found: {category}")
        cls.data[category][var] = value
        cls.save()
        logging.info(f"[Settings] updated variable: {category} -> {var}={value}")

    @classmethod
    def get_version_from_pyproject(cls) -> str:
        """
        Reads the version from the pyproject.toml file.

        :return: The version string if found, otherwise 'unknown'.
        """
        with open("pyproject.toml", "rb") as f:
            data = tomllib.load(f)

        version = data.get("project", {}).get("version", "unknown")
        return version

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
            from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions  # type: ignore
        else:
            from rgbmatrix import RGBMatrix, RGBMatrixOptions  # type: ignore

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
            logging.critical(f"[Utils] failed to set RGBMatrix options: {e}")
            logging.critical("[Utils] Exiting program.")
            sys.exit(1)

        try:
            matrix = RGBMatrix(options=options)
            logging.info("[Utils] RGBMatrix object created.")
            return matrix
        except Exception as e:
            logging.critical(f"[Utils] failed to create RGBMatrix object: {e}")
            logging.critical("[Utils] Exiting program.")
            sys.exit(1)
