import logging
import sys
import time
from PIL import Image

from enums.input_status import InputStatus
from enums.variable_importance import Importance
from settings import Settings

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


import queue


class Board:
    SCREEN_RATIO = 16

    def __init__(self):
        self.pixel_rows = Settings.read_variable(
            "System", "pixel_rows", Importance.CRITICAL
        )
        if self.pixel_rows % self.SCREEN_RATIO != 0:
            logging.error(
                "[System] pixel_rows must be a multiple of 16 to work with the 'rpi-rgb-led-matrix' library."
            )
            logging.error("[System] Exiting program.")
            sys.exit()

        self.pixel_cols = Settings.read_variable(
            "System", "pixel_cols", Importance.CRITICAL
        )
        if self.pixel_cols % self.SCREEN_RATIO != 0:
            logging.error(
                "[System] pixel_cols must be a multiple of 16 to work with the 'rpi-rgb-led-matrix' library."
            )
            logging.error("[System] Exiting program.")
            sys.exit()

        self.encoder_A = Settings.read_variable(
            "Pinout", "encoder_a", Importance.CRITICAL
        )
        self.encoder_B = Settings.read_variable(
            "Pinout", "encoder_b", Importance.CRITICAL
        )
        self.encoder_button = Settings.read_variable(
            "Pinout", "encoder_button", Importance.CRITICAL
        )
        self.tilt_switch = Settings.read_variable(
            "Pinout", "tilt_switch", Importance.CRITICAL
        )

        self.brightness = Settings.read_variable("System", "brightness") or 100
        self.is_display_on = True

        self.encoder_button = Button(self.encoder_button, pull_up=True)
        self.input_status_dictionary = {"value": InputStatus.NOTHING}
        self.encoder_button.when_pressed = lambda button: self.encoder_button_function(
            button, self.input_status_dictionary
        )

        self.encoderQueue = queue.Queue()
        self.encoder = RotaryEncoder(self.encoder_A, self.encoder_B)
        self.encoder.when_rotated_clockwise = lambda enc: self.rotate_clockwise(
            enc, self.encoderQueue
        )
        self.encoder.when_rotated_counter_clockwise = (
            lambda enc: self.rotate_counter_clockwise(enc, self.encoderQueue)
        )
        self.encoder_state = 0

        self.tilt_switch = Button(self.tilt_switch, pull_up=True)
        self.is_horizontal_dictionary = {"value": True}
        self.tilt_switch.when_pressed = lambda button: self.tilt_callback(
            button, self.is_horizontal_dictionary
        )
        self.tilt_switch.when_released = lambda button: self.tilt_callback(
            button, self.is_horizontal_dictionary
        )

    def rotate_clockwise(self, encoder, encoderQueue):
        encoderQueue.put(1)
        encoder.value = 0

    def rotate_counter_clockwise(self, encoder, encoderQueue):
        encoderQueue.put(-1)
        encoder.value = 0

    def tilt_callback(self, tilt_switch, isHorizontalDict):
        startTime = time.time()
        while time.time() - startTime < 0.25:
            pass
        isHorizontalDict["value"] = tilt_switch.is_pressed

    def encoder_button_function(self, enc_button, inputStatusDict):
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
                            enc_button.when_pressed = (
                                lambda button: self.encoder_button_function(
                                    button, inputStatusDict
                                )
                            )
                            return
                    print("double press detected")
                    inputStatusDict["value"] = InputStatus.DOUBLE_PRESS
                    enc_button.when_pressed = (
                        lambda button: self.encoder_button_function(
                            button, inputStatusDict
                        )
                    )
                    return
            print("single press detected")
            inputStatusDict["value"] = InputStatus.SINGLE_PRESS
            enc_button.when_pressed = lambda button: self.encoder_button_function(
                button, inputStatusDict
            )
            return
