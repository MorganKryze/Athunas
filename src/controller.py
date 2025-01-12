import logging
from typing import Dict, Callable

from app_manager import AppManager
from board import Board


class Controller:
    """
    Manages the control operations for the board and applications.
    """

    @classmethod
    def toggle_display(cls) -> None:
        """
        Toggle the display on or off.
        """
        Board.is_display_on = not Board.is_display_on
        logging.debug(
            f"[Controller] Display set to: {'on' if Board.is_display_on else 'off'}"
        )

    @classmethod
    def increase_brightness(cls) -> None:
        """
        Increase the brightness of the display.
        """
        Board.brightness = min(
            Board.BRIGHTNESS_MAX,
            Board.brightness + Board.BRIGHTNESS_STEP,
        )
        logging.debug(f"[Controller] Brightness increased to {Board.brightness}")

    @classmethod
    def decrease_brightness(cls) -> None:
        """
        Decrease the brightness of the display.
        """
        Board.brightness = max(
            Board.BRIGHTNESS_MIN,
            Board.brightness - Board.BRIGHTNESS_STEP,
        )
        logging.debug(f"[Controller] Brightness decreased to {Board.brightness}")

    @classmethod
    def get_callbacks(cls) -> Dict[str, Callable[[], None]]:
        """
        Get the callback functions for various control operations.

        Returns:
            Dict[str, Callable[[], None]]: A dictionary of callback functions.
        """
        return {
            "toggle_display": cls.toggle_display,
            "increase_brightness": cls.increase_brightness,
            "decrease_brightness": cls.decrease_brightness,
            "switch_next_app": AppManager.switch_next_app,
            "switch_prev_app": AppManager.switch_prev_app,
        }
