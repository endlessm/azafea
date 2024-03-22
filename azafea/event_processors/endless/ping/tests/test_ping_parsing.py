# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from datetime import datetime, timezone
import json


def test_from_bytes():
    from azafea.event_processors.endless.ping.v1.handler import Ping

    created_at = datetime.now(tz=timezone.utc)
    ping = Ping.from_serialized(json.dumps({
        'release': 'release',
        'count': 43,
        'created_at': created_at.strftime('%Y-%m-%d %H:%M:%S.%fZ'),
    }).encode('utf-8'))

    assert ping.release == 'release'
    assert ping.count == 43

    # SQLAlchemy only transforms the string into a datetime when querying from the DB
    assert ping.created_at == created_at.strftime('%Y-%m-%d %H:%M:%S.%fZ')


def test_from_bytes_missing_count():
    from azafea.event_processors.endless.ping.v1.handler import Ping

    created_at = datetime.now(tz=timezone.utc)
    ping = Ping.from_serialized(json.dumps({
        'release': 'release',
        'created_at': created_at.strftime('%Y-%m-%d %H:%M:%S.%fZ'),
    }).encode('utf-8'))

    assert ping.release == 'release'
    assert ping.count == 0

    # SQLAlchemy only transforms the string into a datetime when querying from the DB
    assert ping.created_at == created_at.strftime('%Y-%m-%d %H:%M:%S.%fZ')
