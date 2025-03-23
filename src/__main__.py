import time
import logging
import argparse
from typing import Any

from enums.input_status import InputStatus
from board import Board
from path import PathTo
from logs import Logs
from app_manager import AppManager
from settings import Settings


def main() -> None:
    parser = argparse.ArgumentParser(description='Athunas LED matrix controller')
    parser.add_argument('--debug', action='store_true', help='Run with debug logging to console')
    args = parser.parse_args()
    
    PathTo.set_base_directory()
    PathTo.add_library_to_path()
    
    file_level = logging.DEBUG
    console_level = logging.DEBUG if args.debug else logging.WARNING
    
    Logs.start(file_level=file_level, console_level=console_level)
    Settings.load_config()
    Board.init_system()
    AppManager.init_apps()

    matrix = Settings.create_matrix(
        Board.led_rows, Board.led_cols, Board.brightness, use_emulator=True
    )

    while True:
        try:
            if not Board.encoder_queue.empty():
                Board.encoder_state += Board.encoder_queue.get()

            if Board.has_encoder_increased():
                Board.encoder_input_status = InputStatus.ENCODER_INCREASE
                Board.reset_encoder_state()
            elif Board.has_encoder_decreased():
                Board.encoder_input_status = InputStatus.ENCODER_DECREASE
                Board.reset_encoder_state()

            current_app = AppManager.get_current_app()
            frame: Any = current_app.generate(
                Board.is_horizontal, Board.encoder_input_status
            )
            matrix.SetImage(frame if Board.is_display_on else Board.black_screen)

            Board.reset_encoder_input_status()
            time.sleep(Board.refresh_rate)
        except KeyboardInterrupt:
            logging.info("[Controller] Application stopped by user.")
            break


if __name__ == "__main__":
    main()