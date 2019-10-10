# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import sys

from .cli import BaseExit, parse_args
from .logging import setup_logging


setup_logging(verbose=False)
args = parse_args(sys.argv[1:])

try:
    args.subcommand(args)

except BaseExit as e:
    sys.exit(e.status_code)
