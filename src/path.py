import inspect
import os
import sys


class PathTo:
    base_directory: str = ""

    CONFIG_FILE: str = "configs/config.yaml"
    GENERATIONS_FOLDER: str = "configs/generations/"
    TEMPLATE_CONFIG_FILE: str = "configs/example.config.yaml"
    PYPROJECT_FILE: str = "pyproject.toml"

    LOGS_FOLDER: str = "logs"
    RESOURCES_FOLDER: str = "resources"
    GIF_FOLDER: str = os.path.join(RESOURCES_FOLDER, "gif/horizontal/")
    LIFE_PATTERNS_FOLDER: str = os.path.join(RESOURCES_FOLDER, "life_patterns/")
    MAIN_SCREEN_BACKGROUND_FOLDER: str = os.path.join(RESOURCES_FOLDER, "main_screen/")
    FONT_FILE: str = os.path.join(RESOURCES_FOLDER, "fonts/tiny.otf")
    TEMPLATES_FOLDER: str = "../resources/web/templates"
    STATIC_FOLDER: str = "../resources/web/static"

    @classmethod
    def set_base_directory(cls, base_dir_name: str = "Athunas") -> None:
        """
        Sets the base directory for the script to the specified directory name.

        :param base_dir_name: The name of the base directory (default is 'Athunas').
        """
        current_script_path = os.path.abspath(inspect.getfile(inspect.currentframe()))
        current_script_dir = os.path.dirname(current_script_path)
        cls.base_directory = os.path.abspath(
            os.path.join(current_script_dir, "..", "..", base_dir_name)
        )
        os.chdir(cls.base_directory)
        sys.path.append(cls.base_directory)

    @classmethod
    def add_library_to_path(cls) -> None:
        """
        Adds the library rpi-rgb-led-matrix path to the system path.
        """
        sys.path.append(
            os.path.join(cls.base_directory, "rpi-rgb-led-matrix", "bindings", "python")
        )
