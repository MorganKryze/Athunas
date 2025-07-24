from enum import Enum


class ServiceStatus(Enum):
    """
    Enum to represent the status of a service.

    Attributes:
        DISABLED (int): service is disabled.
        STARTING (int): service is starting.
        RUNNING (int): service is running.
        ERROR_NO_INTERNET (int): service is in error state due to no internet connection
        ERROR_SERVER (int): service is in error state due to server issues.
        ERROR_MODULE (int): service is in error state due to module issues.
        ERROR_APP (int): service is in error state due to application issues.
        ERROR_UNKNOWN (int): service is in error state due to an unknown issue.
    """

    DISABLED = 1
    STARTING = 2
    RUNNING = 3
    ERROR_NO_INTERNET = 4
    ERROR_SERVER = 5
    ERROR_MODULE = 6
    ERROR_APP = 7
    ERROR_UNKNOWN = 8
