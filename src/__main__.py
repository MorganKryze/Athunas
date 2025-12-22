import argparse
import time

from loguru import logger
from PIL import Image

from app_manager import AppManager
from board import Board
from config import Configuration
from custom_frames import CustomFrames
from enums.encoder_input import EncoderInput
from logs import Logs
from models.application import Application
from path import PathTo


@logger.catch
def main() -> None:
    parser = argparse.ArgumentParser(description="Carousel LED matrix controller")
    parser.add_argument("--debug", action="store_true", help="Run with debug console")
    parser.add_argument("--emulator", action="store_true", help="Run in emulator mode")
    args = parser.parse_args()

    PathTo.set_base_directory()
    PathTo.add_library_to_path()

    file_level = "DEBUG"
    console_level = "DEBUG" if args.debug else "WARNING"

    Logs.start(file_level=file_level, console_level=console_level)

    Configuration.load()

    Board.init_system(use_emulator=args.emulator)

    Board.loading_animation()

    AppManager.init_apps()

    # TODO: remove this when webserver is implemented with new config and workflow
    # server = WebServer()
    # TODO: port should be configurable
    # server.start(port=9000, debug=args.debug)

    previous_frame: Image = CustomFrames.black()
    previous_frame_bytes = previous_frame.tobytes()
    while True:
        try:
            # TODO: remove this check when webserver is implemented with new config and workflow
            if False:
                # if server.is_user_connected():
                Board.matrix.SetImage(CustomFrames.black())
            else:
                if not Board.encoder_queue.empty():
                    Board.encoder_state += Board.encoder_queue.get()

                if Board.has_encoder_increased():
                    Board.encoder_input = EncoderInput.INCREASE_CLOCKWISE
                    Board.reset_encoder_state()
                elif Board.has_encoder_decreased():
                    Board.encoder_input = EncoderInput.DECREASE_COUNTERCLOCKWISE
                    Board.reset_encoder_state()

                current_app: Application = AppManager.get_current_app()
                frame: Image = current_app.generate(
                    Board.tilt_state, Board.encoder_input
                )
                frame_bytes = frame.tobytes()
                if frame_bytes != previous_frame_bytes:
                    previous_frame = frame
                    previous_frame_bytes = frame_bytes
                    Board.matrix.SetImage(
                        frame if Board.is_display_on else CustomFrames.black()
                    )

                Board.reset_encoder_input_status()

            time.sleep(Board.refresh_rate)
        except KeyboardInterrupt:
            logger.info("[Main] Program stopped by user.")
            Board.matrix.SetImage(CustomFrames.black())
            break


if __name__ == "__main__":
    main()
