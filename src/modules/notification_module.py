from threading import Thread
from queue import Queue
import websocket
import json
import time
from functools import cmp_to_key
import logging


class NotificationModule:
    def __init__(self, config):
        """
        Initialize the NotificationModule with the given configuration.

        Args:
            config (dict): Configuration settings.
        """
        app_white_list = parse_white_list(
            config.get("Notification Module", "white_list", fallback=None)
        )
        pushbullet_ws = config.get(
            "Notification Module", "pushbullet_ws", fallback=None
        )

        self.noti_list = []
        self.noti_queue = Queue()

        if pushbullet_ws is None or app_white_list is None or len(app_white_list) == 0:
            logging.error(
                "[Notification Module] Pushbullet websocket URL or app white list is not specified in config"
            )
        else:
            logging.info("[Notification Module] Starting websocket service")
            Thread(
                target=start_service,
                args=(self.noti_queue, pushbullet_ws, app_white_list),
            ).start()

    def get_notification_list(self):
        """
        Get the list of notifications.

        Returns:
            list: The list of notifications.
        """
        need_to_sort = False
        while not self.noti_queue.empty():
            new_noti = self.noti_queue.get()
            logging.debug(f"[Notification Module] Processing notification: {new_noti}")
            if new_noti.add_to_count:
                found = any(noti.noti_id == new_noti.noti_id for noti in self.noti_list)
                if not found:
                    need_to_sort = True
                    self.noti_list.append(new_noti)
                    logging.info(
                        f"[Notification Module] Added new notification: {new_noti}"
                    )
            else:
                self.noti_list = [
                    noti for noti in self.noti_list if noti.noti_id != new_noti.noti_id
                ]
                logging.info(f"[Notification Module] Removed notification: {new_noti}")

        if need_to_sort:
            self.noti_list.sort(key=cmp_to_key(Notification.compare))
            logging.debug("[Notification Module] Sorted notification list")

        return self.noti_list


class Notification:
    def __init__(self, application, add_to_count, noti_id, title, body, noti_time):
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
    def compare(noti1, noti2):
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


def on_message(_, message, noti_queue, app_white_list):
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


def on_error(_, error, noti_queue, pushbullet_ws, app_white_list):
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
    time.sleep(1000)
    logging.info("[Notification Module] Restarting websocket service")
    start_service(noti_queue, pushbullet_ws, app_white_list)


def on_close(_):
    """
    Handle the websocket close event.

    Args:
        _ (WebSocketApp): The websocket app (unused).
    """
    logging.warning("### websocket closed ###")


def start_service(noti_queue, pushbullet_ws, app_white_list):
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


def parse_white_list(str_list):
    """
    Parse the white list string into a dictionary.

    Args:
        str_list (str): The white list string.

    Returns:
        dict: The parsed white list dictionary.
    """
    if str_list is None:
        return None

    result = {}
    pairs = str_list.split(",")
    for pair in pairs:
        pkg, name = pair.split(":")
        result[pkg] = name
    logging.debug(f"[Notification Module] Parsed white list: {result}")
    return result
