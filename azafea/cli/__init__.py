# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from . import commands
from ..logging import setup_logging


def run_command(*argv: str) -> None:
    setup_logging(verbose=False)

    parser = commands.get_parser()
    args = parser.parse_args(argv)
    args.subcommand(args)
