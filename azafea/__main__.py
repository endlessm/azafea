# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import sys

from . import cli


try:
    cli.run_command(*sys.argv[1:])

except cli.errors.BaseExit as e:
    sys.exit(e.status_code)
