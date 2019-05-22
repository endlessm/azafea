import sys

from .config import Config, InvalidConfigurationError
from .controller import Controller


try:
    config = Config.from_file('/etc/chuleisi/config.toml')

except InvalidConfigurationError as e:
    sys.exit(str(e))

controller = Controller(config)
controller.main()
