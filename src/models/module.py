"""Module model class."""

import logging

from config import Configuration
from enums.variable_importance import Importance


class Module:
    """Modules are components that provide resources or functionnalities that can be used by multiple applications."""

    def __init__(self):
        self.enabled: bool = Configuration.read_module_variable(
            self.__class__.__name__, "enabled", Importance.REQUIRED
        )
        if not self.enabled:
            logging.info(f"[{self.__class__.__name__}] Module disabled.")
            return
        logging.debug(f"[{self.__class__.__name__}] Initializing setup...")

    def self_test(self) -> bool:
        """
        Perform a self-test to ensure the module is functioning correctly.
        This method should be overridden by subclasses to implement specific self-test logic.

        Returns:
            bool: True if the self-test passes, False otherwise.
        """
        raise NotImplementedError(
            f"[{self.__class__.__name__}] self_test method not implemented. Please implement this method logic in the subclass."
        )

    def disable_on_error(self) -> bool:
        """
        Disable the module if an error occurs to prevent further issues.
        This method should be called when an error is detected in the module's operation.

        :return: True if the module was successfully disabled, False otherwise.
        """
        self.enabled = False
        if not Configuration.update_module_variable(
            self.__class__.__name__, "enabled", False
        ):
            logging.error(
                f"[{self.__class__.__name__}] Failed to update module configuration to disable the module."
            )
            return False
        logging.info(
            f"[{self.__class__.__name__}] Module has been disabled due to an error. See logs for details."
        )
        return True
        # TODO: This action should generate a chain reaction if the module is a dependency for other modules or applications if this method is called in the runtime (not in the init).
