# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import logging

from sqlalchemy.orm.session import Session as DbSession


log = logging.getLogger(__name__)


def process(dbsession: DbSession, record: bytes) -> None:
    log.debug('Processing metric v2 record: %s', record)
