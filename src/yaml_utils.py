import yaml
from typing import Any, Dict, Optional, Type

class YAMLUtils:
    file_path: str = ''
    data: Dict[str, Any] = {}

    @classmethod
    def set_file_path(cls, file_path: str) -> None:
        """
        Sets the file path for the class.

        :param file_path: Path to the YAML file.
        """
        cls.file_path = file_path
        cls.read_yaml()  # Automatically read the YAML file when setting the file path

    @classmethod
    def read_yaml(cls) -> None:
        """
        Reads a YAML file and stores its contents in the class dictionary.
        """
        try:
            with open(cls.file_path, 'r') as file:
                cls.data = yaml.safe_load(file)
        except FileNotFoundError:
            print(f"Error: The file {cls.file_path} was not found.")
        except yaml.YAMLError as e:
            print(f"Error parsing YAML file: {e}")

    @classmethod
    def write_yaml(cls) -> None:
        """
        Writes the class dictionary to a YAML file.
        """
        try:
            with open(cls.file_path, 'w') as file:
                yaml.safe_dump(cls.data, file)
        except IOError as e:
            print(f"Error writing to file {cls.file_path}: {e}")

    @classmethod
    def read_variable(cls, category: str, var: str) -> Optional[Any]:
        """
        Reads a specific variable from the class dictionary.

        :param category: The category key in the dictionary.
        :param var: The variable key within the category.
        :return: The value of the variable if it exists, otherwise None.
        """
        return cls.data.get(category, {}).get(var, None)