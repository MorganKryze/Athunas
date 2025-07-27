import sys
import logging
from typing import Callable, Dict, List

from board import Board
from models.application import Application
from models.module import Module
from apps import main_screen, gif_viewer, pomodoro
import modules


class AppManager:
    """
    Manages the current application and provides methods to switch between applications.
    """

    current_app_index: int = 0
    modules: Dict[str, Module]
    apps: List[Application]
    enabled_apps: List[Application]

    @classmethod
    def init_apps(cls) -> None:
        """
        Initialize the applications.
        """
        logging.debug("[AppManager] Initializing apps.")
        try:
            cls.modules = cls.load_modules()
            cls.apps = cls.load_apps()
            cls.enabled_apps = [app for app in cls.apps if app.enabled]
            logging.debug("[AppManager] All enabled app initialized.")
        except Exception as e:
            logging.critical(f"[AppManager] Failed to initialize apps: {e}")
            logging.critical("[AppManager] Exiting program.")
            sys.exit(1)

    @staticmethod
    def load_modules() -> Dict[str, Module]:
        """
        Load and initialize the modules.

        :return: Dict[str, Module]: A dictionary of initialized modules.
        """
        return {
            # "notifications": modules.notification_module.Notifications(),
            # "weather": modules.weather_module.WeatherModule(),
            # "spotify": modules.spotify_module.SpotifyModule(),
        }

    @staticmethod
    def load_apps() -> List[Application]:
        """
        Load and initialize the apps.

        :return: List[Application]: A list of initialized applications.
        """
        callbacks: Dict[str, Callable] = {
            "toggle_display": AppManager.toggle_display,
            "switch_next_app": AppManager.switch_next_app,
            "switch_prev_app": AppManager.switch_prev_app,
            "increase_brightness": AppManager.increase_brightness,
            "decrease_brightness": AppManager.decrease_brightness,
            "get_app_by_name": AppManager.get_app_by_name,
            "get_module_by_name": AppManager.get_module_by_name,
        }
        return [
            main_screen.MainScreen(callbacks),
            gif_viewer.GifPlayer(callbacks),
            pomodoro.Pomodoro(callbacks),
            # life.GameOfLifeScreen(callbacks),
            # weather.WeatherScreen(config, modules, callbacks),
            # notion.NotionScreen(config, modules, callbacks),
            # subcount.SubcountScreen(config, modules, callbacks),
            # spotify_player.SpotifyScreen(config, modules, callbacks),
        ]

    @classmethod
    def get_app_by_name(cls, app_name: str) -> Application:
        """
        Get an application by its name.

        :param app_name: The name of the application.
        :return: Application: The application instance.
        """
        for app in cls.enabled_apps:
            if app.name == app_name:
                return app
        raise ValueError(f"Application '{app_name}' not found.")

    @classmethod
    def get_module_by_name(cls, module_name: str) -> Module:
        """
        Get a module by its name.

        :param module_name: The name of the module.
        :return: Module: The module instance.
        """
        if module_name in cls.modules:
            return cls.modules[module_name]
        raise ValueError(f"Module '{module_name}' not found.")

    @classmethod
    def get_current_app(cls) -> Application:
        """
        Get the current application.

        Returns:
            Any: The current application.
        """
        return cls.enabled_apps[cls.current_app_index]

    @classmethod
    def switch_next_app(cls) -> bool:
        """
        Switch to the next application.

        :return: bool: True if the switch was successful, False otherwise.
        """
        try:
            cls.current_app_index = (cls.current_app_index + 1) % len(cls.enabled_apps)
            logging.debug("[AppManager] Switched to next app.")
            return True
        except Exception as e:
            logging.error(f"[AppManager] Failed to switch to next app: {e}")
            cls.current_app_index = 0
            logging.debug("[AppManager] Resetting to first app.")
            return False

    @classmethod
    def switch_prev_app(cls) -> bool:
        """
        Switch to the previous application.

        :return: bool: True if the switch was successful, False otherwise.
        """
        try:
            cls.current_app_index = (cls.current_app_index - 1) % len(cls.enabled_apps)
            logging.debug("[AppManager] Switched to previous app.")
            return True
        except Exception as e:
            logging.error(f"[AppManager] Failed to switch to previous app: {e}")
            cls.current_app_index = 0
            logging.debug("[AppManager] Resetting to first app.")
            return False

    @staticmethod
    def toggle_display() -> bool:
        """
        Toggle the display on or off.

        :return: bool: True if the display was successfully toggled, False otherwise.
        """
        try:
            Board.is_display_on = not Board.is_display_on
            logging.debug(
                f"[Controller] Display set to: {'on' if Board.is_display_on else 'off'}"
            )
            return True
        except Exception as e:
            logging.error(f"[Controller] Failed to toggle display: {e}")
            Board.is_display_on = True
            logging.debug("[Controller] Display turned off due to error.")
            return False

    @staticmethod
    def increase_brightness() -> bool:
        """
        Increase the brightness of the display.

        :return: bool: True if brightness was successfully increased, False otherwise.
        """
        initial_value: int = Board.brightness
        try:
            Board.brightness = min(
                Board.BRIGHTNESS_MAX,
                Board.brightness + Board.BRIGHTNESS_STEP,
            )
            logging.debug(f"[Controller] Brightness increased to {Board.brightness}")
            return True
        except Exception as e:
            logging.error(f"[Controller] Failed to increase brightness: {e}")
            Board.brightness = initial_value
            logging.debug(
                f"[Controller] Brightness reset to default: {Board.brightness}"
            )
            return False

    @staticmethod
    def decrease_brightness() -> bool:
        """
        Decrease the brightness of the display.

        :return: bool: True if brightness was successfully decreased, False otherwise.
        """
        initial_value: int = Board.brightness
        try:
            Board.brightness = max(
                Board.BRIGHTNESS_MIN,
                Board.brightness - Board.BRIGHTNESS_STEP,
            )
            logging.debug(f"[Controller] Brightness decreased to {Board.brightness}")
            return True
        except Exception as e:
            logging.error(f"[Controller] Failed to decrease brightness: {e}")
            Board.brightness = initial_value
            logging.debug(
                f"[Controller] Brightness reset to default: {Board.brightness}"
            )
            return False
