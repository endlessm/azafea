import argparse
from enum import IntEnum
from typing import List

from .config import Config
from .controller import Controller
from .model import Db


class ExitCode(IntEnum):
    OK = 0


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
    config = Config.from_file(args.config)
    db = Db(config.postgresql.host, config.postgresql.port, config.postgresql.user,
            config.postgresql.password, config.postgresql.database)
    db.create_all()

    return ExitCode.OK


def do_print_config(args: argparse.Namespace) -> int:
    print(Config.from_file(args.config))

    return ExitCode.OK


def do_run(args: argparse.Namespace) -> int:
    controller = Controller(Config.from_file(args.config))
    controller.main()

    return ExitCode.OK
