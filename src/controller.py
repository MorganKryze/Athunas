import configparser
from settings import Settings
from enums.variable_importance import Importance
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
from modules import  notification_module, weather_module, spotify_module

import queue
import math
import sys
import time
import copy
import logging
from PIL import Image
from utils import Utils

try:
    from gpiozero import Button, RotaryEncoder
except Exception:
    class Button:
        def __init__(self, num, pull_up=False):
            self.num = num
            self.pull_up = pull_up
            self.when_pressed = lambda: None
            self.when_pressed = lambda: None

    class RotaryEncoder:
        def __init__(self, encoding1, encoding2):
            self.encoding1 = encoding1
            self.encoding2 = encoding2
            self.when_rotated_clockwise = lambda: None
            self.when_rotated_counter_clockwise = lambda: None


def main():
    Utils.set_base_directory()
    
    Utils.start_logging()
    
    Settings.init('config.yaml')

    config = configparser.ConfigParser()
    parsed_configs = config.read("config.ini")
    if len(parsed_configs) == 0:
        print("no config file found")
        sys.exit()

    SCREEN_RATIO = 16
    screen_width = Settings.read_variable('System', 'screen_width', Importance.CRITICAL)
    if screen_width % SCREEN_RATIO != 0:
        logging.error("[System] screen_width must be a multiple of 16 to work with the 'rpi-rgb-led-matrix' library.")
        logging.error("[System] Exiting program.")
        sys.exit()
    screen_height = Settings.read_variable('System', 'screen_height', Importance.CRITICAL)
    if screen_height % SCREEN_RATIO != 0:
        logging.error("[System] screen_height must be a multiple of 32 to work with the 'rpi-rgb-led-matrix' library.")
        logging.error("[System] Exiting program.")
        sys.exit()
        
    encoder_A = Settings.read_variable('System', 'encoder_a')
    encoder_B = Settings.read_variable('System', 'encoder_b')
    encoder_button = Settings.read_variable('System', 'encoder_button')
    tilt_switch = Settings.read_variable('System', 'tilt_switch')
        
    brightness = Settings.read_variable('System', 'brightness')
    is_display_on = True

    black_screen = Image.new("RGB", (screen_width, screen_height), (0, 0, 0))

    encoder_button = Button(encoder_button, pull_up=True)
    input_status_dictionary = {"value": InputStatus.NOTHING}
    encoder_button.when_pressed = lambda button: encoder_button_function(button, input_status_dictionary)

    encoderQueue = queue.Queue()
    encoder = RotaryEncoder(encoder_A, encoder_B)
    encoder.when_rotated_clockwise = lambda enc: rotate_clockwise(enc, encoderQueue)
    encoder.when_rotated_counter_clockwise = lambda enc: rotate_counter_clockwise(enc, encoderQueue)
    encoder_state = 0

    tilt_switch = Button(tilt_switch, pull_up=True)
    is_horizontal_dictionary = {"value": True}
    tilt_switch.when_pressed = lambda button: tilt_callback(button, is_horizontal_dictionary)
    tilt_switch.when_released = lambda button: tilt_callback(button, is_horizontal_dictionary)

    def toggle_display():
        nonlocal is_display_on
        is_display_on = not is_display_on
        print("Display On: " + str(is_display_on))

    def increase_brightness():
        nonlocal brightness
        brightness = min(100, brightness + 5)

    def decrease_brightness():
        nonlocal brightness
        brightness = max(0, brightness - 5)

    current_app_idx = 0

    def switch_next_app():
        nonlocal current_app_idx
        current_app_idx += 1

    def switch_prev_app():
        nonlocal current_app_idx
        current_app_idx -= 1

    callbacks = {
        "toggle_display": toggle_display,
        "increase_brightness": increase_brightness,
        "decrease_brightness": decrease_brightness,
        "switch_next_app": switch_next_app,
        "switch_prev_app": switch_prev_app,
    }

    modules = {
        "weather": weather_module.WeatherModule(config),
        "notifications": notification_module.NotificationModule(config),
        "spotify": spotify_module.SpotifyModule(config),
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

    matrix = Utils.create_matrix(screen_height, screen_width, brightness)

    rotation_time = math.floor(time.time())
    while True:
        while not encoderQueue.empty():
            encoder_state += encoderQueue.get()
        if encoder_state > 1:
            print("encoder increased")
            input_status_dictionary["value"] = InputStatus.ENCODER_INCREASE
            encoder_state = 0
        elif encoder_state < -1:
            print("encoder decreased")
            input_status_dictionary["value"] = InputStatus.ENCODER_DECREASE
            encoder_state = 0

        inputStatusSnapshot = copy.copy(input_status_dictionary["value"])
        input_status_dictionary["value"] = InputStatus.NOTHING

        isHorizontalSnapshot = copy.copy(is_horizontal_dictionary["value"])

        new_rotation_time = math.floor(time.time())
        if new_rotation_time % 10 == 0 and new_rotation_time - rotation_time >= 10:
            current_app_idx += 1
            rotation_time = new_rotation_time

        frame = app_list[current_app_idx % len(app_list)].generate(
            isHorizontalSnapshot, inputStatusSnapshot
        )
        if not is_display_on:
            frame = black_screen

        matrix.SetImage(frame)
        time.sleep(0.05)


def encoder_button_function(enc_button, inputStatusDict):
    start_time = time.time()
    time_diff = 0
    hold_time = 1

    while enc_button.is_active and (time_diff < hold_time):
        time_diff = time.time() - start_time

    if time_diff >= hold_time:
        print("long press detected")
        inputStatusDict["value"] = InputStatus.LONG_PRESS
    else:
        enc_button.when_pressed = None
        start_time = time.time()
        while time.time() - start_time <= 0.3:
            time.sleep(0.1)
            if enc_button.is_pressed:
                time.sleep(0.1)
                new_start_time = time.time()
                while time.time() - new_start_time <= 0.3:
                    time.sleep(0.1)
                    if enc_button.is_pressed:
                        print("triple press detected")
                        inputStatusDict["value"] = InputStatus.TRIPLE_PRESS
                        enc_button.when_pressed = lambda button: encoder_button_function(
                            button, inputStatusDict
                        )
                        return
                print("double press detected")
                inputStatusDict["value"] = InputStatus.DOUBLE_PRESS
                enc_button.when_pressed = lambda button: encoder_button_function(
                    button, inputStatusDict
                )
                return
        print("single press detected")
        inputStatusDict["value"] = InputStatus.SINGLE_PRESS
        enc_button.when_pressed = lambda button: encoder_button_function(button, inputStatusDict)
        return


def rotate_clockwise(encoder, encoderQueue):
    encoderQueue.put(1)
    encoder.value = 0


def rotate_counter_clockwise(encoder, encoderQueue):
    encoderQueue.put(-1)
    encoder.value = 0


def tilt_callback(tilt_switch, isHorizontalDict):
    startTime = time.time()
    while time.time() - startTime < 0.25:
        pass
    isHorizontalDict["value"] = tilt_switch.is_pressed


def reduceFrameToString(frame):
    res = frame.flatten()
    return " ".join(map(str, res))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted with Ctrl-C")
        sys.exit(0)
