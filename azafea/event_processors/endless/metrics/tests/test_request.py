# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from datetime import datetime, timedelta, timezone
from hashlib import sha512

from gi.repository import GLib

import pytest


def test_request_builder():
    from azafea.event_processors.endless.metrics.request import RequestBuilder

    now = datetime.now(tz=timezone.utc)
    request = GLib.Variant(
        '(ixxaya(uayxmv)a(uayxxmv)a(uaya(xmv)))',
        (
            0,                                     # network send number
            2000000000,                            # request relative timestamp (2 secs)
            int(now.timestamp() * 1000000000),     # request absolute timestamp
            bytes.fromhex('ffffffffffffffffffffffffffffffff'),
            [],                                    # singular events
            [],                                    # aggregate events
            []                                     # sequence events
        )
    )
    assert request.is_normal_form()
    request_body = request.get_data_as_bytes().get_data()

    received_at = now + timedelta(minutes=2)
    received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
    received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

    record = received_at_timestamp_bytes + request_body

    builder = RequestBuilder.parse_bytes(record)
    assert builder.sha512 == sha512(request_body).hexdigest()
    assert builder.send_number == 0
    assert builder.relative_timestamp == 2000000000
    assert builder.absolute_timestamp == int(now.timestamp() * 1000000000)
    assert builder.machine_id == 'ffffffffffffffffffffffffffffffff'
    assert list(builder.singulars) == []
    assert list(builder.aggregates) == []
    assert list(builder.sequences) == []


def test_request_builder_invalid():
    from azafea.event_processors.endless.metrics.request import RequestBuilder

    now = datetime.now(tz=timezone.utc)
    request = GLib.Variant('(ix)', (0, 2000000000))
    assert request.is_normal_form()
    request_body = request.get_data_as_bytes().get_data()

    received_at = now + timedelta(minutes=2)
    received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
    received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

    record = received_at_timestamp_bytes + request_body

    with pytest.raises(ValueError) as excinfo:
        RequestBuilder.parse_bytes(record)

    assert ('Metric request is not in the expected format: '
            f'(ixxaya(uayxmv)a(uayxxmv)a(uaya(xmv)))') in str(excinfo.value)
