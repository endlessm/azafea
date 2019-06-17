import argparse
from enum import IntEnum
import logging
from typing import List
import sys

from .config import Config, InvalidConfigurationError
from .controller import Controller
from .logging import setup_logging
from .model import Db


log = logging.getLogger(__name__)


class ExitCode(IntEnum):
    OK = 0
    INVALID_CONFIG = -1


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='azafea',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-c', '--config', default='/etc/azafea/config.toml',
                        help='Optional path to a configuration file, if needed')

    subs = parser.add_subparsers(title='subcommands', dest='subcommand', required=True)

    initdb = subs.add_parser('initdb', help='Initialize the database, creating the tables')
    initdb.set_defaults(subcommand=do_initdb)

    print_config = subs.add_parser('print-config',
                                   help='Print the loaded configuration then exit')
    print_config.set_defaults(subcommand=do_print_config)

    run = subs.add_parser('run', help='Run azafea')
    run.set_defaults(subcommand=do_run)

    return parser


def parse_args(args: List[str]) -> argparse.Namespace:
    parser = get_parser()

    return parser.parse_args(args)


def do_initdb(args: argparse.Namespace) -> int:
    try:
        config = Config.from_file(args.config)

    except InvalidConfigurationError as e:
        print(str(e), file=sys.stderr)
        return ExitCode.INVALID_CONFIG

    setup_logging(verbose=config.main.verbose)

    db = Db(config.postgresql.host, config.postgresql.port, config.postgresql.user,
            config.postgresql.password, config.postgresql.database)
    db.create_all()

    return ExitCode.OK


def do_print_config(args: argparse.Namespace) -> int:
    try:
        config = Config.from_file(args.config)

    except InvalidConfigurationError as e:
        print(str(e), file=sys.stderr)
        return ExitCode.INVALID_CONFIG

    print(config)

    return ExitCode.OK


def do_run(args: argparse.Namespace) -> int:
    try:
        config = Config.from_file(args.config)

    except InvalidConfigurationError as e:
        print(str(e), file=sys.stderr)
        return ExitCode.INVALID_CONFIG

    setup_logging(verbose=config.main.verbose)

    controller = Controller(config)
    controller.main()

    return ExitCode.OK
