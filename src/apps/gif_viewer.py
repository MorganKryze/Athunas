import logging
import os
import time
from typing import List, Dict, Callable

from PIL import Image, ImageSequence, ImageDraw

from board import Board
from enums.variable_importance import Importance
from enums.input_status import InputStatus
from settings import Settings

# Constants
GIFS_LOCATION = "./src/apps/res/gif/horizontal/"
WHITE = (230, 255, 255)
FRAME_DELAY = 0.04


class GifScreen:
    def __init__(self, modules: Dict, callbacks: Dict[str, Callable]):
        """
        Initialize the GifScreen with modules and callbacks.

        Args:
            modules (Dict): Dictionary of modules.
            callbacks (Dict[str, Callable]): Dictionary of callback functions.
        """
        self.enabled = Settings.read_variable(
            "GifViewer", "enabled", Importance.REQUIRED
        )
        if not self.enabled:
            logging.debug("[GifScreen] GifViewer is disabled.")
            return

        self.callbacks = callbacks
        self.led_cols = Board.led_cols
        self.led_rows = Board.led_rows
        self.animations = load_animations()
        self.current_animation_index = 0
        self.selection_mode = False
        self.current_frame_index = 0
        self.was_horizontal = True

    def generate(
        self, is_horizontal: bool, encoder_input_status: InputStatus
    ) -> Image.Image:
        """
        Generate the frame to draw on the LED matrix.

        Args:
            is_horizontal (bool): Whether the LED matrix is horizontal.
            encoder_input_status (InputStatus): The current input status.

        Returns:
            Image.Image: The generated frame.
        """
        if encoder_input_status == InputStatus.LONG_PRESS:
            self.selection_mode = not self.selection_mode

        if self.selection_mode:
            if encoder_input_status == InputStatus.ENCODER_INCREASE:
                self.current_animation_index = (self.current_animation_index + 1) % len(
                    self.animations
                )
                self.current_frame_index = 0
            elif encoder_input_status == InputStatus.ENCODER_DECREASE:
                self.current_animation_index = (self.current_animation_index - 1) % len(
                    self.animations
                )
                self.current_frame_index = 0
        else:
            if encoder_input_status == InputStatus.SINGLE_PRESS:
                self.callbacks["toggle_display"]()
            elif encoder_input_status == InputStatus.ENCODER_INCREASE:
                self.callbacks["switch_next_app"]()
            elif encoder_input_status == InputStatus.ENCODER_DECREASE:
                self.callbacks["switch_prev_app"]()

        current_gif = ImageSequence.Iterator(
            self.animations[self.current_animation_index]
        )
        try:
            frame = current_gif[self.current_frame_index].convert("RGB")
        except IndexError:
            logging.warning(
                "[GifScreen] IndexError encountered. Resetting frame index."
            )
            self.current_frame_index = 0
            frame = current_gif[self.current_frame_index].convert("RGB")
        self.current_frame_index = (self.current_frame_index + 1) % len(current_gif)

        draw = ImageDraw.Draw(frame)
        if self.selection_mode:
            draw.rectangle((0, 0, self.led_cols - 1, self.led_rows - 1), outline=WHITE)

        time.sleep(FRAME_DELAY)
        return frame


def load_animations() -> List[Image.Image]:
    """
    Loads all GIFs from the GIFS_LOCATION directory.

    Returns:
        List[Image.Image]: A list of all loaded GIFs.
    """
    logging.debug("[GifScreen] Loading GIFs.")
    result = []
    try:
        for filename in os.listdir(GIFS_LOCATION):
            if filename.endswith(".gif"):
                logging.debug(f"[GifScreen] Loading GIF: {filename}")
                result.append(Image.open(os.path.join(GIFS_LOCATION, filename)))
    except Exception as e:
        logging.error(f"[GifScreen] Error loading GIFs: {e}")
    logging.debug("[GifScreen] All GIFs loaded.")
    return result
