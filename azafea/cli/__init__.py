# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import argparse
import logging

from . import commands
from .errors import InvalidConfigExit
from ..config import Config, InvalidConfigurationError
from ..logging import setup_logging


log = logging.getLogger(__name__)


def _get_parser(*, add_help: bool = False) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='azafea', add_help=add_help,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-c', '--config', default='/etc/azafea/config.toml',
                        help='Optional path to a configuration file, if needed')

    return parser


def run_command(*argv: str) -> None:
    parser = _get_parser(add_help=False)
    base_args, remainder = parser.parse_known_args(argv)
    setup_logging(verbose=False)

    try:
        config = Config.from_file(base_args.config)

    except InvalidConfigurationError as e:
        log.error(e)

        raise InvalidConfigExit()

    setup_logging(verbose=config.main.verbose)

    parser = _get_parser(add_help=True)
    subs = parser.add_subparsers(title='subcommands', dest='subcommand', required=True)

    # Core commands
    commands.register_commands(subs)

    args = parser.parse_args(argv)
    args.subcommand(config, args)
