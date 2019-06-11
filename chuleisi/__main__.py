import argparse
import sys

from .config import Config, InvalidConfigurationError
from .controller import Controller


parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-c', '--config', default='/etc/chuleisi/config.toml',
                    help='Optional path to a configuration file, if needed')

args = parser.parse_args()

try:
    config = Config.from_file(args.config)

except InvalidConfigurationError as e:
    sys.exit(str(e))

controller = Controller(config)
controller.main()
