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
    from azafea.event_processors.endless.activation.v1.handler import Activation

    created_at = datetime.utcnow().replace(tzinfo=timezone.utc)
    activation = Activation.from_serialized(json.dumps({
        'image': 'eos-eos3.7-amd64-amd64.190419-225606.base',
        'vendor': 'the vendor',
        'product': 'product',
        'release': 'release',
        'serial': 'serial',
        'mac_hash': 694551690,
        'created_at': created_at.strftime('%Y-%m-%d %H:%M:%S.%fZ'),
    }).encode('utf-8'))

    assert activation.image == 'eos-eos3.7-amd64-amd64.190419-225606.base'
    assert activation.vendor == 'the vendor'
    assert activation.product == 'product'
    assert activation.release == 'release'
    assert activation.image_product == 'eos'
    assert activation.image_branch == 'eos3.7'
    assert activation.image_arch == 'amd64'
    assert activation.image_platform == 'amd64'
    assert activation.image_timestamp == datetime(2019, 4, 19, 22, 56, 6, tzinfo=timezone.utc)
    assert activation.image_personality == 'base'

    # SQLAlchemy only transforms the string into a datetime when querying from the DB
    assert activation.created_at == created_at.strftime('%Y-%m-%d %H:%M:%S.%fZ')
