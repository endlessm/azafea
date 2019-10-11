# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


class BaseExit(Exception):
    status_code: int


class InvalidConfigExit(BaseExit):
    status_code: int = -1


class NoEventQueueExit(BaseExit):
    status_code: int = -2


class ConnectionErrorExit(BaseExit):
    status_code: int = -3


class UnknownErrorExit(BaseExit):
    status_code: int = -4
