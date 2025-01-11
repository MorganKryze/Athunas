from threading import Thread
from queue import Queue
from enums.variable_importance import Importance
from settings import Settings
import websocket
import json
import time
from functools import cmp_to_key
import logging
from typing import List, Dict, Any

# Constants
RETRY_DELAY_SECONDS = 1000


class NotificationModule:
    def __init__(self) -> None:
        """
        Initialize the NotificationModule with the given configuration.
        """
        self.enabled: bool = Settings.read_variable(
            "Notification-Module", "enabled", Importance.REQUIRED
        )
        if not self.enabled:
            logging.info("[Notification Module] Disabled")
            return

        logging.debug("[Notification Module] Initializing")
        self.app_white_list: Dict[str, str] = Settings.read_variable(
            "Notification-Module", "app_white_list"
        )
        if len(self.app_white_list) == 0:
            logging.warning(
                "[Notification Module] No applications found in the white list, no notifications will be received."
            )
        self.websocket_url: str = Settings.read_variable(
            "Notification-Module", "websocket_url", Importance.REQUIRED
        )
        self.notifications_list: List[Notification] = []
        self.notification_queue: Queue = Queue()

        logging.debug("[Notification Module] Starting websocket service")
        Thread(
            target=start_service,
            args=(self.notification_queue, self.websocket_url, self.app_white_list),
        ).start()

        logging.info("[Notification Module] Initialized")

    def get_notification_list(self) -> List[Any]:
        """
        Get the list of notifications.

        Returns:
            List[Notification]: The list of notifications.
        """
        need_to_sort = False
        while not self.notification_queue.empty():
            new_noti: Notification = self.notification_queue.get()
            logging.debug(f"[Notification Module] Processing notification: {new_noti}")
            if new_noti.add_to_count:
                found = any(
                    noti.noti_id == new_noti.noti_id for noti in self.notifications_list
                )
                if not found:
                    need_to_sort = True
                    self.notifications_list.append(new_noti)
                    logging.info(
                        f"[Notification Module] Added new notification: {new_noti}"
                    )
            else:
                self.notifications_list = [
                    noti
                    for noti in self.notifications_list
                    if noti.noti_id != new_noti.noti_id
                ]
                logging.info(f"[Notification Module] Removed notification: {new_noti}")

        if need_to_sort:
            self.notifications_list.sort(key=cmp_to_key(Notification.compare))
            logging.debug("[Notification Module] Sorted notification list")

        return self.notifications_list


class Notification:
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


def on_message(
    _: websocket.WebSocketApp,
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
    logging.debug(f"[Notification Module] Received message: {message}")
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
                logging.info(
                    f"[Notification Module] Added new notification from {contents['package_name']}"
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
                logging.info(
                    f"[Notification Module] Dismissed notification from {contents['package_name']}"
                )


def on_error(
    _: websocket.WebSocketApp,
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
    logging.error(f"[Notification Module] WebSocket error: {error}")
    time.sleep(RETRY_DELAY_SECONDS)
    logging.info("[Notification Module] Restarting websocket service")
    start_service(noti_queue, pushbullet_ws, app_white_list)


def on_close(_: websocket.WebSocketApp) -> None:
    """
    Handle the websocket close event.

    Args:
        _ (WebSocketApp): The websocket app (unused).
    """
    logging.warning("[Notification Module] Websocket closed")


def start_service(
    noti_queue: Queue, pushbullet_ws: str, app_white_list: Dict[str, str]
) -> None:
    """
    Start the websocket service.

    Args:
        noti_queue (Queue): The notification queue.
        pushbullet_ws (str): The pushbullet websocket URL.
        app_white_list (dict): The application white list.
    """
    logging.info("[Notification Module] Starting websocket service")
    ws = websocket.WebSocketApp(
        pushbullet_ws,
        on_message=lambda ws, message: on_message(
            ws, message, noti_queue, app_white_list
        ),
        on_error=lambda ws, error: on_error(
            ws, error, noti_queue, pushbullet_ws, app_white_list
        ),
        on_close=on_close,
    )
    ws.run_forever()
