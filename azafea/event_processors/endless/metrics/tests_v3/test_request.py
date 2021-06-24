# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from datetime import datetime, timedelta, timezone

from gi.repository import GLib

import pytest


def test_request_builder():
    from azafea.event_processors.endless.metrics.v3.model import parse_record

    now = datetime.now(tz=timezone.utc)
    request = GLib.Variant(
        '(xxsa{ss}ya(aysxmv)a(ayssumv))',
        (
            2000000,   # request relative timestamp (2 secs)
            int(now.timestamp() * 1000000000),  # Absolute timestamp
            'image_id',
            {},
            2,
            [],                                    # singular events
            []                                     # sequence events
        )
    )
    assert request.is_normal_form()
    request_body = request.get_data_as_bytes().get_data()

    received_at = now + timedelta(minutes=2)
    received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
    received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

    record = received_at_timestamp_bytes + request_body

    request, channel = parse_record(record)
    assert request.relative_timestamp == 2000000
    assert request.absolute_timestamp == int(now.timestamp() * 1000000000)
    assert list(request.singulars) == []
    assert list(request.aggregates) == []

    assert channel.live
    assert not channel.dual_boot
    assert channel.image_id == 'image_id'


def test_request_builder_invalid():
    from azafea.event_processors.endless.metrics.v3.model import parse_record

    now = datetime.now(tz=timezone.utc)
    request = GLib.Variant('(ix)', (0, 2000000000))
    assert request.is_normal_form()
    request_body = request.get_data_as_bytes().get_data()

    received_at = now + timedelta(minutes=2)
    received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
    received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

    record = received_at_timestamp_bytes + request_body

    with pytest.raises(ValueError) as excinfo:
        parse_record(record)

    assert ('Metric request is not in the expected format: '
            '(xxsa{ss}ya(aysxmv)a(ayssumv))') in str(excinfo.value)
