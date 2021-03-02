from typing import Optional

from restapi.customizer import FlaskApp


class Initializer:
    def __init__(self, app: Optional[FlaskApp] = None):
        pass

    # This method is called after normal initialization if TESTING mode is enabled
    def initialize_testing_environment(self) -> None:
        pass
