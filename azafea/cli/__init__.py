# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import argparse
from typing import List

from .commands import get_parser


def parse_args(args: List[str]) -> argparse.Namespace:
    parser = get_parser()

    return parser.parse_args(args)
