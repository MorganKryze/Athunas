import yaml
import logging
from typing import Any, Dict, Optional

class Settings:
    file_path: str = ''
    data: Dict[str, Any] = {}

    @classmethod
    def init(cls, file_path: str) -> None:
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
            logging.info(f"[Settings] loaded successfully: {cls.data}")
        except FileNotFoundError:
            logging.error(f"[Settings] The file '{cls.file_path}' was not found.")
        except yaml.YAMLError as e:
            logging.error(f"[Settings] Failed to parse YAML file: {e}")

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
    def read_variable(cls, category: str, var: str) -> Optional[Any]:
        """
        Reads a specific variable from the class dictionary.

        :param category: The category key in the dictionary.
        :param var: The variable key within the category.
        :return: The value of the variable if it exists, otherwise None.
        """
        return cls.data.get(category, {}).get(var)