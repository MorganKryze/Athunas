import yaml
import logging
from enums.variable_importance import Importance
from typing import Any, Dict, Optional

class Settings:
    file_path: str = ''
    data: Dict[str, Any] = {}

    @classmethod
    def load(cls, file_path: str) -> None:
        """
        Reads the specified file and store its value.

        :param file_path: Path to the YAML file.
        """
        cls.file_path = file_path
        logging.debug(f"[Settings] file path set: {cls.file_path}")
        cls.read_yaml()

    @classmethod
    def read_yaml(cls) -> None:
        """
        Reads a YAML file and stores its contents in the class dictionary.
        """
        try:
            with open(cls.file_path, 'r') as file:
                cls.data = yaml.safe_load(file)
            logging.info("[Settings] loaded successfully.")
        except FileNotFoundError:
            logging.error(f"[Settings] The file '{cls.file_path}' was not found.")
            logging.error("[Settings] Exiting program.")
            raise
        except yaml.YAMLError as e:
            logging.error(f"[Settings] Failed to parse YAML file: {e}")
            logging.error("[Settings] Exiting program.")
            raise

    @classmethod
    def write_yaml(cls) -> None:
        """
        Writes the class dictionary to a YAML file.
        """
        try:
            with open(cls.file_path, 'w') as file:
                yaml.safe_dump(cls.data, file)
            logging.info("[Settings] saved successfully.")
        except IOError as e:
            logging.error(f"[Settings] Failed to write to file: {e}")

    @classmethod
    def read_variable(cls, category: str, var: str, importance: Importance=Importance.NORMAL) -> Optional[Any]:
        """
        Reads a specific variable from the class dictionary.

        :param category: The category key in the dictionary.
        :param var: The variable key within the category.
        :param importance: The importance level of the variable. Defaults to Importance.NORMAL.
        :return: The value of the variable if it exists, otherwise None.
        """
        value = cls.data.get(category, {}).get(var)
        logging.debug(f"[Settings] read variable: {category} -> {var}")
        if value is None:
            logging.warning(f"[Settings] variable not found: {category} -> {var}")
            if importance == Importance.CRITICAL:
                logging.error(f"[Settings] Critical variable not found: {category} -> {var}")
                logging.error("[Settings] Exiting program.")
                raise
        return value