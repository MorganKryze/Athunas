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

    Board.init_system()

    # TODO: Remove
    config = configparser.ConfigParser()
    parsed_configs = config.read("config.ini")
    if len(parsed_configs) == 0:
        print("no config file found")
        sys.exit()
    # TODO: Remove

    matrix = Utils.create_matrix(Board.pixel_rows, Board.pixel_cols, Board.brightness)

    def toggle_display():
        Board.is_display_on = not Board.is_display_on
        logging.debug(
            f"[Controller] Display set to: {'on' if Board.is_display_on else 'off'}"
        )

    def increase_brightness():
        Board.brightness = min(100, Board.brightness + 5)
        logging.debug(f"[Controller] Brightness increased to {Board.brightness}")

    def decrease_brightness():
        Board.brightness = max(0, Board.brightness - 5)
        logging.debug(f"[Controller] Brightness decreased to {Board.brightness}")

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
        # main_screen.MainScreen(config, modules, callbacks),
        gif_viewer.GifScreen(callbacks),
        # notion.NotionScreen(config, modules, callbacks),
        # weather.WeatherScreen(config, modules, callbacks),
        # subcount.SubcountScreen(config, modules, callbacks),
        # life.GameOfLifeScreen(config, modules, callbacks),
        # spotify_player.SpotifyScreen(config, modules, callbacks),
    ]

    # TODO: Find a better way to implement app rotation
    # rotation_time = math.floor(time.time())
    SLEEP_TIME = 0.05
    while True:
        while not Board.encoder_queue.empty():
            Board.encoder_state += Board.encoder_queue.get()
        if Board.encoder_state > 1:
            print("DEBUG: encoder ---")
            Board.encoder_input_status = InputStatus.ENCODER_INCREASE
            Board.encoder_state = 0
        elif Board.encoder_state < -1:
            print("DEBUG: encoder +++")
            Board.encoder_input_status = InputStatus.ENCODER_DECREASE
            Board.encoder_state = 0

        is_horizontal_snapshot = copy.copy(Board.is_horizontal)
        input_status_snapshot = copy.copy(Board.encoder_input_status)
        Board.encoder_input_status = InputStatus.NOTHING

        # TODO: Find a better way to implement app rotation
        # new_rotation_time = math.floor(time.time())
        # if new_rotation_time % 10 == 0 and new_rotation_time - rotation_time >= 10:
        #     current_app_index += 1
        #     rotation_time = new_rotation_time

        frame = app_list[current_app_index % len(app_list)].generate(
            is_horizontal_snapshot, input_status_snapshot
        )

        matrix.SetImage(frame if Board.is_display_on else Board.black_screen)
        time.sleep(SLEEP_TIME)


if __name__ == "__main__":
    try:
        main()
        logging.info("[Controller] Application stopped.")
        logging.info("-------------------------------------------------------------")
    except KeyboardInterrupt:
        logging.info("[Controller] Application stopped by user.")
        logging.info("-------------------------------------------------------------")
