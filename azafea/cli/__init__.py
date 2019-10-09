# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import logging

from . import commands
from .errors import InvalidConfigExit
from ..config import Config, InvalidConfigurationError
from ..logging import setup_logging


log = logging.getLogger(__name__)


def run_command(*argv: str) -> None:
    setup_logging(verbose=False)

    parser = commands.get_parser()
    args = parser.parse_args(argv)

    try:
        config = Config.from_file(args.config)

    except InvalidConfigurationError as e:
        log.error(e)

        raise InvalidConfigExit()

    setup_logging(verbose=config.main.verbose)

    args.subcommand(config, args)
