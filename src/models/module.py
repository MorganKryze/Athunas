"""Module model class."""

import logging

from config import Configuration
from enums.service_status import ServiceStatus
from enums.variable_importance import Importance


class Module:
    """Modules are components that provide resources or functionnalities that can be used by multiple applications."""

    def __init__(self):
        self.status: ServiceStatus = ServiceStatus.INITIALIZING
        logging.debug(f"[{self.__class__.__name__}] Initializing metadata...")
        self.name: str = Configuration.read_module_variable(
            self.__class__.__name__, "name", Importance.REQUIRED
        )
        self.description: str = Configuration.read_module_variable(
            self.__class__.__name__, "description", Importance.REQUIRED
        )
        

    def self_test(self) -> None:
        """
        Perform a self-test to ensure the module is functioning correctly.
        This method should be overridden by subclasses to implement specific self-test logic.
        """
        raise NotImplementedError(
            f"[{self.__class__.__name__}] self_test method not implemented. Please implement this method logic in the subclass."
        )
