import logging
from PIL import Image, ImageFont, ImageDraw


from enums.service_status import ServiceStatus
from path import PathTo

# Constants
FONT_SIZE = 5

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)


class CustomFrames:
    """Custom frames for the application."""

    led_rows: int
    led_cols: int
    font = ImageFont.truetype(PathTo.FONT_FILE, FONT_SIZE)

    @classmethod
    def init(cls, led_rows: int, led_cols: int) -> None:
        """Initialize custom frames."""

        cls.led_rows = led_rows
        cls.led_cols = led_cols
        logging.debug("[CustomFrames] Custom frames initialized.")

    @classmethod
    def loading(cls, percentage: int) -> Image:
        """
        Generate a loading frame with the given percentage.

        :param percentage: The loading percentage.
        :return: Image: The loading frame.
        """
        # TODO: Implement loading frame depending on the percentage
        pass

    @classmethod
    def black(cls) -> Image:
        """
        Generate a black screen frame.

        :return: Image: The black screen frame.
        """
        return Image.new("RGB", (cls.led_cols, cls.led_rows), BLACK)

    @classmethod
    def error(cls, error_status: ServiceStatus) -> Image:
        """
        Generate an error frame with the provided error status.

        :param error_status: The status of the application.
        :return: Image: The error frame.
        """
        # TODO: assert that this is working
        if (
            error_status == ServiceStatus.INITIALIZING
            or error_status == ServiceStatus.RUNNING
        ):
            logging.error(
                f"[{cls.__name__}] The app is not going under availability issue. status: {error_status.name}"
            )
            return cls.black()

        error_title = f"[{cls.__name__}]"
        error_status_description = {
            ServiceStatus.DISABLED: "The app is disabled.",
            ServiceStatus.ERROR_NO_INTERNET: "No Internet connection.",
            ServiceStatus.ERROR_SERVER: "External server error.",
            ServiceStatus.ERROR_MODULE_CONFIG: "Module configuration error.",
            ServiceStatus.ERROR_MODULE_INTERNAL: "Module internal error.",
            ServiceStatus.ERROR_APP_CONFIG: "App configuration error.",
            ServiceStatus.ERROR_APP_INTERNAL: "App internal error.",
            ServiceStatus.ERROR_UNKNOWN: "Unknown error.",
        }
        error_description = error_status_description.get(
            error_status, "Unknown error status."
        )
        frame = cls.black()
        draw = ImageDraw.Draw(frame)
        draw.text((5, 5), error_title, fill=RED, font=cls.font)
        draw.text((5, 15), error_description, fill=RED, font=cls.font)
        draw.textsize(error_description, font=cls.font)
        draw.text(
            (
                cls.led_cols // 2
                - draw.textsize(error_description, font=cls.font)[0] // 2,
                cls.led_rows // 2,
            ),
            error_description,
            fill=RED,
            font=cls.font,
        )
        draw.rectangle((0, 0, cls.led_cols - 1, cls.led_rows - 1), outline=RED, width=1)
        return frame
