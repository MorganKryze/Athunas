import yaml
from typing import Any, Dict, Optional

class YAMLUtils:
    def __init__(self, file_path: str):
        self.file_path: str = file_path
        self.data: Dict[str, Any] = {}
        self.read_yaml()

    def read_yaml(self) -> None:
        """
        Reads a YAML file and stores its contents in the class dictionary.
        """
        try:
            with open(self.file_path, 'r') as file:
                self.data = yaml.safe_load(file)
        except FileNotFoundError:
            print(f"Error: The file {self.file_path} was not found.")
        except yaml.YAMLError as e:
            print(f"Error parsing YAML file: {e}")

    def write_yaml(self) -> None:
        """
        Writes the class dictionary to a YAML file.
        """
        try:
            with open(self.file_path, 'w') as file:
                yaml.safe_dump(self.data, file)
        except IOError as e:
            print(f"Error writing to file {self.file_path}: {e}")

    def read_variable(self, category: str, var: str) -> Optional[Any]:
        """
        Reads a specific variable from the class dictionary.

        :param category: The category key in the dictionary.
        :param var: The variable key within the category.
        :return: The value of the variable if it exists, otherwise None.
        """
        return self.data.get(category, {}).get(var, None)
