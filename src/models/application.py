"""App model class."""

import logging
from typing import Callable, Dict
from PIL import Image


from config import Configuration
from custom_frames import CustomFrames
from enums.encoder_input_status import EncoderInputStatus
from enums.service_status import ServiceStatus


class Application:
    """Modules are components that provide resources or functionnalities that can be used by multiple applications."""

    def __init__(self, callbacks: Dict[str, Callable]):
        self.status: ServiceStatus = ServiceStatus.INITIALIZING
        logging.debug(f"[{self.__class__.__name__}] Initializing metadata...")
        self.enabled = Configuration.get_from_app(
            self.__class__.__name__, "enabled", required=True
        )
        self.name: str = Configuration.get_from_app_meta(
            self.__class__.__name__, "name", required=True
        )
        self.description: str = Configuration.get_from_app_meta(
            self.__class__.__name__, "description", required=True
        )
        self.provides_horizontal_content = Configuration.get_from_app_meta(
            self.__class__.__name__, "provides_horizontal_content", required=True
        )
        self.provides_vertical_content = Configuration.get_from_app_meta(
            self.__class__.__name__, "provides_vertical_content", required=True
        )

        logging.debug(f"[{self.__class__.__name__}] Initializing configuration...")
        self.callbacks = callbacks
        self.horizontal_replacement_app_name = Configuration.get_from_app_config(
            self.__class__.__name__, "horizontal_replacement_app"
        )
        self.vertical_replacement_app_name = Configuration.get_from_app_config(
            self.__class__.__name__, "vertical_replacement_app"
        )

        if not self.enabled:
            self.status = ServiceStatus.DISABLED

    def generate(
        self, is_horizontal: bool, encoder_input_status: EncoderInputStatus
    ) -> Image:
        """
        Generate the frame for the app.
        This method should be extended by subclasses to implement specific frame generation logic.

        :param is_horizontal: bool: Whether the screen is horizontal.
        :param encoder_input_status: InputStatus: The status of the encoder input.
        :return: Image: The generated frame.
        """
        if self.status != ServiceStatus.RUNNING:
            return self.generate_on_error()

        if is_horizontal and not self.provides_horizontal_content:
            replacement_app: Application = self.callbacks["get_app_by_name"](
                self.horizontal_replacement_app_name
            )
            if replacement_app:
                return replacement_app.generate(is_horizontal, encoder_input_status)
            else:
                return CustomFrames.black()

        if not is_horizontal and not self.provides_vertical_content:
            replacement_app: Application = self.callbacks["get_app_by_name"](
                self.vertical_replacement_app_name
            )
            if replacement_app:
                return replacement_app.generate(is_horizontal, encoder_input_status)
            else:
                return CustomFrames.black()

    def generate_on_error(self) -> Image:
        """
        Generate the frame for the app when an error occurs.

        :return: Image: The error frame.
        """
        return CustomFrames.error(self.status)
