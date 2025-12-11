import json
import time
from functools import cmp_to_key
from queue import Queue
from threading import Thread
from typing import Any, Dict, List

import websocket
from loguru import logger

from config import Configuration
from enums.service_status import ServiceStatus
from models.module import Module
from webserver import WebServer


class Notifications(Module):
    def __init__(self):
        super().__init__()
        self.app_white_list: Dict[str, str] = Configuration.get_from_module(
            self.__class__.__name__, "app_white_list"
        )
        if len(self.app_white_list) == 0:
            logger.warning(
                "[Notifications Module] No applications found in the white list, no notifications will be received."
            )
        self.websocket_url: str = Configuration.get_from_module(
            self.__class__.__name__, "websocket_url"
        )
        if not self.websocket_url:
            logger.error(
                "[Notifications Module] Websocket URL is not set, setting the module on error."
            )
            self.status = ServiceStatus.ERROR_MODULE_CONFIG
        self.notifications_list: List[Notification] = []
        self.notification_queue: Queue = Queue()

        self.retry_delay_on_error: int = Configuration.get_from_module(
            self.__class__.__name__, "retry_delay_on_error"
        )
        if not self.retry_delay_on_error or self.retry_delay_on_error <= 0:
            logger.error(
                "[Notifications Module] Retry delay on error is not set or invalid, setting the module on error."
            )
            self.status = ServiceStatus.ERROR_MODULE_CONFIG
        Notification.retry_delay_on_error = self.retry_delay_on_error

        if not self.self_test():
            logger.error(
                "[Notifications Module] Self-test failed, setting the module on error."
            )
            self.status = ServiceStatus.ERROR_MODULE_CONFIG

        if self.status == ServiceStatus.ERROR_MODULE_CONFIG:
            logger.error(
                "[Notifications Module] Configuration error, module will not start."
            )
            return
        logger.debug("[Notifications Module] Starting websocket service")
        Thread(
            target=Notification.start_service,
            args=(self.notification_queue, self.websocket_url, self.app_white_list),
        ).start()

        logger.info("[Notifications Module] Initialized")
        self.status = ServiceStatus.RUNNING

    def self_test(self) -> bool:
        """
        Perform a self-test to ensure the module is functioning correctly.
        This method checks if the websocket service is running and can receive notifications.

        :returns: bool: True if the self-test passes, False otherwise.
        """
        logger.info("[Notifications Module] Performing self-test...")
        try:
            if not WebServer.check_internet_connectivity():
                logger.error(
                    "[Notifications Module] No internet connectivity detected."
                )
                self.status = ServiceStatus.ERROR_NO_INTERNET
                return False

            ws = websocket.WebSocket()
            ws.connect(self.websocket_url)
            ws.close()
            logger.info("[Notifications Module] Websocket service is reachable.")
            return True

        except (ConnectionRefusedError, ConnectionError, OSError) as e:
            # Connection issues, invalid address, DNS resolution failed
            logger.error(f"[Notifications Module] Connection error: {e}")
            self.status = ServiceStatus.ERROR_MODULE_CONFIG
            return False

        except Exception as e:
            logger.error(
                f"[Notifications Module] Unexpected error during self-test: {e}"
            )
            self.status = ServiceStatus.ERROR_MODULE_INTERNAL
            return False

    def get_notification_list(self) -> List[Any]:
        """
        Get the list of notifications.

        Returns:
            List[Notification]: The list of notifications.
        """
        if not self.enabled:
            return None
        need_to_sort = False
        while not self.notification_queue.empty():
            new_noti: Notification = self.notification_queue.get()
            logger.debug(f"[Notifications Module] Processing notification: {new_noti}")
            if new_noti.add_to_count:
                found = any(
                    noti.noti_id == new_noti.noti_id for noti in self.notifications_list
                )
                if not found:
                    need_to_sort = True
                    self.notifications_list.append(new_noti)
                    logger.info(
                        f"[Notifications Module] Added new notification: {new_noti}"
                    )
            else:
                self.notifications_list = [
                    noti
                    for noti in self.notifications_list
                    if noti.noti_id != new_noti.noti_id
                ]
                logger.info(f"[Notifications Module] Removed notification: {new_noti}")

        if need_to_sort:
            self.notifications_list.sort(key=cmp_to_key(Notification.compare))
            logger.debug("[Notifications Module] Sorted notification list")

        return self.notifications_list


class Notification:
    retry_delay_on_error: int = 0  # Default value, will be set in the module

    def __init__(
        self,
        application: str,
        add_to_count: bool,
        noti_id: int,
        title: str,
        body: str,
        noti_time: float,
    ) -> None:
        """
        Initialize a Notification object.

        Args:
            application (str): The application name.
            add_to_count (bool): Whether to add to the count.
            noti_id (int): The notification ID.
            title (str): The notification title.
            body (str): The notification body.
            noti_time (float): The notification time.
        """
        self.application = application
        self.add_to_count = add_to_count
        self.noti_id = noti_id
        self.title = title
        self.body = body
        self.noti_time = noti_time

    @staticmethod
    def compare(noti1: "Notification", noti2: "Notification") -> int:
        """
        Compare two notifications based on their time.

        Args:
            noti1 (Notification): The first notification.
            noti2 (Notification): The second notification.

        Returns:
            int: -1 if noti1 is newer, 1 if noti2 is newer, 0 if they are the same.
        """
        if noti1.noti_time > noti2.noti_time:
            return -1
        elif noti1.noti_time < noti2.noti_time:
            return 1
        else:
            return 0

    @classmethod
    def on_message(
        _: websocket.WebSocket,
        message: str,
        noti_queue: Queue,
        app_white_list: Dict[str, str],
    ) -> None:
        """
        Handle incoming messages from the websocket.

        Args:
            _ (WebSocketApp): The websocket app (unused).
            message (str): The message received.
            noti_queue (Queue): The notification queue.
            app_white_list (dict): The application white list.
        """
        logger.debug(f"[Notifications Module] Received message: {message}")
        message = json.loads(message)

        if message["type"] == "push":
            contents = message["push"]
            if contents["package_name"] in app_white_list:
                if contents["type"] == "mirror":
                    noti_queue.put(
                        Notification(
                            app_white_list[contents["package_name"]],
                            True,
                            int(contents["notification_id"]),
                            contents["title"],
                            contents["body"],
                            time.time(),
                        )
                    )
                    logger.info(
                        f"[Notifications Module] Added new notification from {contents['package_name']}"
                    )
                elif contents["type"] == "dismissal":
                    noti_queue.put(
                        Notification(
                            app_white_list[contents["package_name"]],
                            False,
                            int(contents["notification_id"]),
                            "",
                            "",
                            time.time(),
                        )
                    )
                    logger.info(
                        f"[Notifications Module] Dismissed notification from {contents['package_name']}"
                    )

    @classmethod
    def on_error(
        cls,
        _: websocket.WebSocket,
        error: Exception,
        noti_queue: Queue,
        pushbullet_ws: str,
        app_white_list: Dict[str, str],
    ) -> None:
        """
        Handle errors from the websocket.

        Args:
            _ (WebSocketApp): The websocket app (unused).
            error (Exception): The error encountered.
            noti_queue (Queue): The notification queue.
            pushbullet_ws (str): The pushbullet websocket URL.
            app_white_list (dict): The application white list.
        """
        logger.error(f"[Notification Module] WebSocket error: {error}")
        time.sleep(cls.retry_delay_on_error)
        logger.info("[Notification Module] Restarting websocket service")
        cls.start_service(noti_queue, pushbullet_ws, app_white_list)

    @classmethod
    def on_close(cls, _: websocket.WebSocket) -> None:
        """
        Handle the websocket close event.

        Args:
            _ (WebSocketApp): The websocket app (unused).
        """
        logger.warning("[Notifications Module] Websocket closed")

    @classmethod
    def start_service(
        cls, noti_queue: Queue, pushbullet_ws: str, app_white_list: Dict[str, str]
    ) -> None:
        """
        Start the websocket service.

        Args:
            noti_queue (Queue): The notification queue.
            pushbullet_ws (str): The pushbullet websocket URL.
            app_white_list (dict): The application white list.
        """
        logger.info("[Notifications Module] Starting websocket service")
        ws = websocket.WebSocket(
            pushbullet_ws,
            on_message=lambda ws, message: cls.on_message(
                ws, message, noti_queue, app_white_list
            ),
            on_error=lambda ws, error: cls.on_error(
                ws, error, noti_queue, pushbullet_ws, app_white_list
            ),
            on_close=cls.on_close,
        )
        ws.run_forever()
