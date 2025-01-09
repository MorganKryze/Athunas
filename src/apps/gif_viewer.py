import logging
from board import Board
from enums.variable_importance import Importance
import numpy as np
from enums.input_status import InputStatus
from PIL import Image, ImageSequence, ImageDraw
import time
import os

from settings import Settings

white = (230, 255, 255)


class GifScreen:
    GIFS_LOCATION = "./src/apps/res/gif/horizontal/"

    def __init__(self, default_actions):
        self.pixel_cols = Board.pixel_cols
        self.pixel_rows = Board.pixel_rows
        self.animations = GifScreen.loadAnimations()
        self.currentIdx = 0
        self.selectMode = False
        self.default_actions = default_actions
        self.cnt = 0
        self.was_horizontal = True

    def generate(self, isHorizontal, inputStatus):
        if inputStatus == InputStatus.LONG_PRESS:
            self.selectMode = not self.selectMode

        if self.selectMode:
            if inputStatus is InputStatus.ENCODER_INCREASE:
                self.currentIdx += 1
                self.cnt = 0
            elif inputStatus is InputStatus.ENCODER_DECREASE:
                self.currentIdx -= 1
                self.cnt = 0
        else:
            if inputStatus is InputStatus.SINGLE_PRESS:
                self.default_actions["toggle_display"]()
            elif inputStatus is InputStatus.ENCODER_INCREASE:
                self.default_actions["switch_next_app"]()
            elif inputStatus is InputStatus.ENCODER_DECREASE:
                self.default_actions["switch_prev_app"]()

        curr_gif = ImageSequence.Iterator(
            self.animations[self.currentIdx % len(self.animations)]
        )
        try:
            frame = curr_gif[self.cnt].convert("RGB")
        except IndexError:
            self.cnt = 0
            frame = curr_gif[self.cnt].convert("RGB")
        self.cnt += 1

        draw = ImageDraw.Draw(frame)

        if self.selectMode:
            draw.rectangle(
                (0, 0, self.pixel_cols - 1, self.pixel_rows - 1), outline=white
            )

        time.sleep(0.04)
        return frame

    @classmethod
    def loadAnimations(cls):
        """
        Loads all GIFs from the GIFS_LOCATION directory.

        Returns:
            List[Image]: A list of all loaded GIFs.
        """
        logging.debug("[GifScreen] Loading GIFs.")
        result = []
        for filename in os.listdir(cls.GIFS_LOCATION):
            if filename.endswith(".gif"):
                logging.debug(f"[GifScreen] Loading GIF: {filename}")
                result.append(Image.open(os.path.join(cls.GIFS_LOCATION, filename)))
        logging.debug("[GifScreen] All GIFs loaded.")
        return result
