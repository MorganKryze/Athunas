from board import Board
from settings import Settings
from enums.input_status import InputStatus

from apps import (
    main_screen,
    notion,
    subcount,
    gif_viewer,
    weather,
    life,
    spotify_player,
)
from modules import notification_module, weather_module, spotify_module

import math
import sys
import time
import copy
import logging
import configparser
from PIL import Image
from utils import Utils


def main():
    Utils.set_base_directory()

    Utils.start_logging()

    Settings.load("./config.yaml")

    # TODO: Remove
    config = configparser.ConfigParser()
    parsed_configs = config.read("config.ini")
    if len(parsed_configs) == 0:
        print("no config file found")
        sys.exit()
    # TODO: Remove

    board = Board()
    matrix = Utils.create_matrix(board.pixel_rows, board.pixel_cols, board.brightness)

    def toggle_display():
        board.is_display_on = not board.is_display_on
        logging.debug(f"[Controller] Display {'on' if board.is_display_on else 'off'}")

    def increase_brightness():
        board.brightness = min(100, board.brightness + 5)
        logging.debug(f"[Controller] Brightness increased to {board.brightness}")

    def decrease_brightness():
        board.brightness = max(0, board.brightness - 5)
        logging.debug(f"[Controller] Brightness decreased to {board.brightness}")

    current_app_index = 0

    def switch_next_app():
        nonlocal current_app_index
        current_app_index += 1
        logging.debug(
            f"[Controller] Switched to next app {current_app_index % len(app_list)}"
        )

    def switch_prev_app():
        nonlocal current_app_index
        current_app_index -= 1
        logging.debug(
            f"[Controller] Switched to previous app {current_app_index % len(app_list)}"
        )

    callbacks = {
        "toggle_display": toggle_display,
        "increase_brightness": increase_brightness,
        "decrease_brightness": decrease_brightness,
        "switch_next_app": switch_next_app,
        "switch_prev_app": switch_prev_app,
    }

    modules = {
        # "weather": weather_module.WeatherModule(config),
        "notifications": notification_module.NotificationModule(config),
        # "spotify": spotify_module.SpotifyModule(config),
    }

    app_list = [
        gif_viewer.GifScreen(config, modules, callbacks),
        # main_screen.MainScreen(config, modules, callbacks),
        # notion.NotionScreen(config, modules, callbacks),
        # weather.WeatherScreen(config, modules, callbacks),
        # subcount.SubcountScreen(config, modules, callbacks),
        # life.GameOfLifeScreen(config, modules, callbacks),
        # spotify_player.SpotifyScreen(config, modules, callbacks),
    ]

    black_screen = Image.new("RGB", (board.pixel_rows, board.pixel_cols), (0, 0, 0))
    rotation_time = math.floor(time.time())
    while True:
        while not board.encoderQueue.empty():
            board.encoder_state += board.encoderQueue.get()
        if board.encoder_state > 1:
            print("encoder increased")
            board.input_status_dictionary["value"] = InputStatus.ENCODER_INCREASE
            board.encoder_state = 0
        elif board.encoder_state < -1:
            print("encoder decreased")
            board.input_status_dictionary["value"] = InputStatus.ENCODER_DECREASE
            board.encoder_state = 0

        inputStatusSnapshot = copy.copy(board.input_status_dictionary["value"])
        board.input_status_dictionary["value"] = InputStatus.NOTHING

        isHorizontalSnapshot = copy.copy(board.is_horizontal_dictionary["value"])

        new_rotation_time = math.floor(time.time())
        if new_rotation_time % 10 == 0 and new_rotation_time - rotation_time >= 10:
            current_app_index += 1
            rotation_time = new_rotation_time

        frame = app_list[current_app_index % len(app_list)].generate(
            isHorizontalSnapshot, inputStatusSnapshot
        )
        if not board.is_display_on:
            frame = black_screen

        matrix.SetImage(frame)
        time.sleep(0.05)


if __name__ == "__main__":
    try:
        main()
        logging.info("[Controller] Application stopped.")
        logging.info("-------------------------------------------------------------")
    except KeyboardInterrupt:
        logging.info("[Controller] Application stopped by user.")
        logging.info("-------------------------------------------------------------")
