import os
import socket
import subprocess
import sys
import yaml
import tomllib
import logging
from enums.config_type import ConfigType
from enums.variable_importance import Importance
from typing import Any, Dict, Optional

from path import PathTo
from datetime import datetime


class Configuration:
    data: Dict[str, Any] = {}

    @classmethod
    def init_from_template(cls) -> None:
        """
        Initialize the configuration from a template file.
        """
        template_file_path = PathTo.TEMPLATE_CONFIG_FILE
        config_file_path = PathTo.CONFIG_FILE
        try:
            with open(template_file_path, "r") as template_file:
                data = yaml.safe_load(template_file)
            with open(config_file_path, "w") as config_file:
                yaml.safe_dump(data, config_file)
            logging.info("[Config] Config file created successfully.")
        except FileNotFoundError:
            logging.critical(f"[Config] The file '{template_file_path}' was not found.")
            logging.critical("[Config] Exiting program.")
            sys.exit(1)
        except yaml.YAMLError as e:
            logging.critical(f"[Config] Failed to parse YAML file: {e}")
            logging.critical("[Config] Exiting program.")
            sys.exit(1)

    @classmethod
    def load(cls) -> None:
        """
        Load configuration from file or create a new one from the template if it doesn't exist.
        """
        if os.path.exists(PathTo.TEMPORARY_CONFIG_FILE):
            try:
                with open(PathTo.TEMPORARY_CONFIG_FILE, "r") as f:
                    cls.data = yaml.safe_load(f)
                logging.info("[Config] Successfully loaded temporary config")
            except Exception as e:
                logging.error(f"[Config] Failed to load temporary config: {e}")
                cls.handle_fail_from(ConfigType.Temporary)
        else:
            try:
                with open(PathTo.CONFIG_FILE, "r") as f:
                    cls.data = yaml.safe_load(f)
                logging.info("[Config] Successfully loaded config")
            except Exception as e:
                logging.error(f"[Config] Failed to load config: {e}")
                cls.handle_fail_from(ConfigType.Current)

    @classmethod
    def handle_fail_from(cls, config: ConfigType) -> None:
        """
        Handle the failure of loading the configuration by backing up and deleting the current config file,
        and creating a new one from the template.

        :param config: The type of configuration that failed to load.
        """
        match config:
            case ConfigType.Temporary:
                if os.path.exists(PathTo.TEMPORARY_CONFIG_FILE):
                    try:
                        cls.backup_file(PathTo.TEMPORARY_CONFIG_FILE)
                        os.remove(PathTo.TEMPORARY_CONFIG_FILE)
                        logging.info(
                            "[Config] Backed up and deleted temporary config file"
                        )
                    except Exception as e:
                        logging.error(
                            f"[Config] Failed to delete temporary config: {e}"
                        )
                logging.warning("[Config] Temporary config does not exist, skipping...")
            case ConfigType.Current:
                if os.path.exists(PathTo.CONFIG_FILE):
                    try:
                        cls.backup_file(PathTo.CONFIG_FILE)
                        os.remove(PathTo.CONFIG_FILE)
                        logging.info(
                            "[Config] Backed up and deleted current config file"
                        )
                        cls.init_from_template()
                    except Exception as e:
                        logging.error(f"[Config] Failed to delete current config: {e}")
                logging.warning(
                    "[Config] Current config does not exist, creating a new one..."
                )
                cls.init_from_template()
                logging.info("[Config] New config file created successfully.")
            case _:
                logging.error(
                    "[Config] Unknown or inapropriate configuration type, skipping..."
                )
                return

        logging.critical(
            f"[Config] {config.name} configuration has failed to load properly, falling back to previous working config and restarting the system..."
        )
        subprocess.call(["sudo", "reboot"])

    @classmethod
    def save(cls) -> None:
        """
        Writes the class dictionary to a YAML file.
        """
        try:
            with open(cls.file_path, "w") as file:
                yaml.safe_dump(cls.data, file)
            logging.info("[Config] saved successfully.")
        except IOError as e:
            logging.error(f"[Config] Failed to write to file: {e}")

    @staticmethod
    def backup_file(file_path: str) -> None:
        """
        Creates a backup of the specified file by appending a .bak and a timestamp to its name,
        without deleting the original file.

        :param file_path: The path of the file to back up.
        """
        if not os.path.exists(file_path):
            logging.error(f"[Config] File not found: {file_path}")
            return

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{file_path}.bak.{timestamp}"
            with open(file_path, "rb") as original_file:
                with open(backup_path, "wb") as backup_file:
                    backup_file.write(original_file.read())
            logging.info(f"[Config] Backup created: {backup_path}")
        except Exception as e:
            logging.error(f"[Config] Failed to create backup for {file_path}: {e}")

    @classmethod
    def read_variable(
        cls,
        category: str,
        subcategory: str,
        var: str,
        importance: Importance = Importance.OPTIONAL,
    ) -> Optional[Any]:
        """
        Reads a specific variable from the class dictionary.

        :param category: The category key in the dictionary.
        :param subcategory: The subcategory key in the dictionary.
        :param var: The variable key within the category.
        :param importance: The importance level of the variable. Defaults to Importance.NORMAL.
        :return: The value of the variable if it exists, otherwise None.
        """
        value = cls.data.get(category, {}).get(subcategory, {}).get(var)
        if value is None:
            logging.warning(
                f"[Config] variable not found: {category} -> {subcategory} -> {var}"
            )
            if importance == Importance.REQUIRED:
                logging.critical(
                    f"[Config] required variable not found: {category} -> {subcategory} -> {var}"
                )
                logging.critical("[Config] Exiting program.")
                sys.exit(1)
            elif importance == Importance.OPTIONAL:
                logging.info(
                    f"[Config] optional variable not found: {category} -> {subcategory} -> {var}"
                )
                return None

        logging.info(f"[Config] variable found: {category} -> {subcategory} -> {var}")
        return value

    @classmethod
    def update_variable(
        cls,
        category: str,
        subcategory: str,
        var: str,
        value: Any,
    ) -> None:
        """
        Updates a specific variable in the class dictionary.

        :param category: The category key in the dictionary.
        :param subcategory: The subcategory key in the dictionary.
        :param var: The variable key within the category.
        :param value: The new value of the variable.
        """
        if category not in cls.data:
            cls.data[category] = {}
        if subcategory not in cls.data[category]:
            cls.data[category][subcategory] = {}
        cls.data[category][subcategory][var] = value
        cls.save()
        logging.info(f"[Config] updated variable: {category} -> {subcategory} -> {var}")

    @classmethod
    def get_version_from_pyproject(cls) -> str:
        """
        Reads the version from the pyproject.toml file.

        :return: The version string if found, otherwise 'unknown'.
        """
        with open(PathTo.PYPROJECT_FILE, "rb") as f:
            data = tomllib.load(f)

        version = data.get("project", {}).get("version", "unknown")
        return version

    @classmethod
    def get_addresses(cls) -> str:
        """
        Retrieves the local IP address of the machine and the hostname.

        :return: A tuple of the hostname and local IP address.
        """
        try:
            hostname = socket.gethostname()
            local_hostname = f"{hostname}.local"

            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("10.255.255.255", 1))
            local_ip = s.getsockname()[0]

            return local_hostname, local_ip
        except Exception as e:
            logging.warning(f"[Config] Failed to retrieve hostname or public IP: {e}")
            return "unknown", "unknown"
        finally:
            s.close()
