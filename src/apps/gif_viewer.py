import logging
import os
from typing import List, Dict, Callable

from PIL import Image, ImageSequence, ImageDraw

from board import Board
from enums.variable_importance import Importance
from enums.input_status import InputStatus
from path import PathTo
from config import Configuration

WHITE = (230, 255, 255)


class GifScreen:
    def __init__(self, modules: Dict, callbacks: Dict[str, Callable]):
        """
        Initialize the GifScreen with modules and callbacks.

        Args:
            modules (Dict): Dictionary of modules.
            callbacks (Dict[str, Callable]): Dictionary of callback functions.
        """
        self.enabled = Configuration.read_variable(
            "Apps", "GifViewer", "enabled", Importance.REQUIRED
        )
        if not self.enabled:
            logging.debug("[GifScreen App] GifViewer is disabled.")
            return

        logging.debug("[GifScreen App] Initializing GifScreen.")
        self.modules = modules
        self.callbacks = callbacks

        self.led_cols = Board.led_cols
        self.led_rows = Board.led_rows
        self.animations = self.load_animations()
        if not self.animations:
            self.enabled = False
            logging.debug(
                "[GifScreen App] Due to loading error, GifViewer has been disabled."
            )
            return

        self.current_animation_index = 0
        self.selection_mode = False
        self.current_frame_index = 0
        self.was_horizontal = True
        self.auto_play_mode = False
        self.play_count = 0
        self.play_limit = Configuration.read_variable("Apps", "GifViewer", "play_limit")
        if self.play_limit < 1 or self.play_limit is None:
            logging.error(
                "[GifScreen App] Play limit must be greater than or equal to 1."
            )
            self.enabled = False
            return

        logging.debug("[GifScreen App] GifScreen initialized.")

    def generate(
        self, encoder_input_status: InputStatus
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
            logging.debug("[GifScreen App] Toggling selection mode.")
            self.selection_mode = not self.selection_mode

        if encoder_input_status == InputStatus.DOUBLE_PRESS:
            logging.debug("[GifScreen App] Toggling auto play mode.")
            self.auto_play_mode = not self.auto_play_mode
            if self.auto_play_mode:
                self.play_count = 0
                self.current_animation_index = (self.current_animation_index + 1) % len(self.animations)

        if self.selection_mode:
            if encoder_input_status == InputStatus.ENCODER_INCREASE:
                logging.debug("[GifScreen App] Switching to next GIF.")
                self.current_animation_index = (self.current_animation_index + 1) % len(
                    self.animations
                )
                self.current_frame_index = 0
            elif encoder_input_status == InputStatus.ENCODER_DECREASE:
                logging.debug("[GifScreen App] Switching to previous GIF.")
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
            self.animations[self.current_animation_index % len(self.animations)]
        )
        try:
            frame = current_gif[self.current_frame_index].convert("RGB")
        except IndexError:
            logging.debug(
                "[GifScreen App] Reached the end of the GIF. Restarting from the beginning."
            )
            self.current_frame_index = 0
            frame = current_gif[self.current_frame_index].convert("RGB")

        self.current_frame_index += 1

        if self.auto_play_mode:
            frame_count = sum(
                1
                for _ in ImageSequence.Iterator(
                    self.animations[self.current_animation_index % len(self.animations)]
                )
            )
            if self.current_frame_index >= frame_count:
                self.play_count += 1
                if self.play_count >= self.play_limit:
                    self.play_count = 0
                    self.current_animation_index = (
                        self.current_animation_index + 1
                    ) % len(self.animations)
                self.current_frame_index = 0

        draw = ImageDraw.Draw(frame)
        if self.selection_mode:
            draw.rectangle(
                (0, 0, self.led_cols - 1, self.led_rows - 1), outline=WHITE
            )

        return frame

    def load_animations(self) -> List[Image.Image]:
        """
        Loads all GIFs from their respective folder.

        Returns:
            List[Image.Image]: A list of all loaded GIFs.
        """
        logging.debug("[GifScreen App] Loading GIFs.")
        result = []
        try:
            for filename in os.listdir(PathTo.GIF_FOLDER):
                if filename.endswith(".gif"):
                    logging.debug(f"[GifScreen App] Loading GIF: {filename}")
                    result.append(Image.open(os.path.join(PathTo.GIF_FOLDER, filename)))
        except Exception as e:
            logging.error(f"[GifScreen App] Error loading GIFs: {e}")
            logging.debug("[GifScreen App] Disabling GifScreen for safety.")
            Configuration.update_variable("Apps", "GifViewer", "enabled", False)
            self.enabled = False
            logging.debug(
                "[GifScreen App] Due to loading error, GifViewer has been disabled."
            )
            return []
        logging.info(f"[GifScreen App] All {len(result)} GIFs loaded successfully.")
        return result
