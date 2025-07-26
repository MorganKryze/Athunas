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
        ERROR_MODULE_CONFIG (int): service is in error state due to bad module configuration.
        ERROR_MODULE_INTERNAL (int): service is in error state due to internal module error.
        ERROR_APP_CONFIG (int): service is in error state due to bad application configuration.
        ERROR_APP_INTERNAL (int): service is in error state due to internal application error.
        ERROR_UNKNOWN (int): service is in an unknown error state.
    """

    DISABLED = 1
    INITIALIZING = 2
    RUNNING = 3
    ERROR_NO_INTERNET = 4
    ERROR_SERVER = 5
    ERROR_MODULE_CONFIG = 6
    ERROR_MODULE_INTERNAL = 7
    ERROR_APP_CONFIG = 8
    ERROR_APP_INTERNAL = 9
    ERROR_UNKNOWN = 10
