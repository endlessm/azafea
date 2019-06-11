from .config import Config
from .controller import Controller


config = Config()

controller = Controller(config)
controller.main()
