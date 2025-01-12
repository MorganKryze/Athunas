import time
from app_manager import AppManager
from board import Board
from enums.input_status import InputStatus
from settings import Settings
from utils import Utils
import logging
from typing import Any


def main() -> None:
    Utils.set_base_directory()
    Utils.start_logging()
    Settings.load("./config.yaml")
    Board.init_system()

    matrix = Utils.create_matrix(
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
            time.sleep(Board.FRAME_TIME)
        except KeyboardInterrupt:
            logging.info("[Controller] Application stopped by user.")
            break


if __name__ == "__main__":
    main()
