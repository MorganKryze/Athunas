import logging
import sys
from typing import Callable, Dict, List, Any
from modules import weather_module, notification_module, spotify_module
from apps import (
    main_screen,
    notion,
    subcount,
    gif_viewer,
    weather,
    life,
    spotify_player,
)
from controller import Controller


def load_modules() -> Dict[str, Any]:
    """
    Load and initialize the modules.

    Returns:
        Dict[str, Any]: A dictionary of initialized modules.
    """
    return {
        "weather": weather_module.WeatherModule(),
        "notifications": notification_module.NotificationModule(),
        "spotify": spotify_module.SpotifyModule(),
    }


def load_apps(modules: Dict[str, Any], callbacks: Dict[str, Any]) -> List[Any]:
    """
    Load and initialize the apps.

    Args:
        modules (Dict[str, Any]): A dictionary of initialized modules.
        callbacks (Dict[str, Any]): A dictionary of callback functions.

    Returns:
        List[Any]: A list of initialized apps.
    """
    return [
        # main_screen.MainScreen(config, modules, callbacks),
        gif_viewer.GifScreen(modules, callbacks),
        # notion.NotionScreen(config, modules, callbacks),
        # weather.WeatherScreen(config, modules, callbacks),
        # subcount.SubcountScreen(config, modules, callbacks),
        # life.GameOfLifeScreen(modules, callbacks),
        # spotify_player.SpotifyScreen(config, modules, callbacks),
    ]


def load_callbacks() -> Dict[str, Callable[[], None]]:
    """
    Get the callback functions for various control operations.
    Returns:
        Dict[str, Callable[[], None]]: A dictionary of callback functions.
    """
    return {
        "toggle_display": Controller.toggle_display,
        "increase_brightness": Controller.increase_brightness,
        "decrease_brightness": Controller.decrease_brightness,
        "switch_next_app": AppManager.switch_next_app,
        "switch_prev_app": AppManager.switch_prev_app,
    }


class AppManager:
    """
    Manages the current application and provides methods to switch between applications.
    """

    current_app_index: int = 0
    modules: Dict[str, Any]
    callbacks: Dict[str, Any]
    apps: List[Any]
    enabled_apps: List[Any]

    @classmethod
    def init_apps(cls) -> None:
        """
        Initialize the applications.
        """
        logging.debug("[AppManager] Initializing apps.")
        try:
            cls.modules = load_modules()
            cls.callbacks = load_callbacks()
            cls.apps = load_apps(cls.modules, cls.callbacks)
            cls.enabled_apps = [app for app in cls.apps if app.enabled]
            logging.debug(f"[AppManager] Enabled apps: {cls.enabled_apps}")
        except Exception as e:
            logging.critical(f"[AppManager] Failed to initialize apps: {e}")
            logging.critical("[AppManager] Exiting program.")
            sys.exit(1)

    @classmethod
    def get_current_app(cls) -> Any:
        """
        Get the current application.

        Returns:
            Any: The current application.
        """
        return cls.enabled_apps[cls.current_app_index]

    @classmethod
    def switch_next_app(cls) -> None:
        """
        Switch to the next application.
        """
        logging.debug("[AppManager] Switching to next app.")
        cls.current_app_index = (cls.current_app_index + 1) % len(cls.enabled_apps)

    @classmethod
    def switch_prev_app(cls) -> None:
        """
        Switch to the previous application.
        """
        logging.debug("[AppManager] Switching to previous app.")
        cls.current_app_index = (cls.current_app_index - 1) % len(cls.enabled_apps)
