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
    from azafea.event_processors.activation.v1 import Activation

    created_at = datetime.utcnow().replace(tzinfo=timezone.utc)
    activation = Activation.from_serialized(json.dumps({
        'image': 'image',
        'vendor': 'vendor',
        'product': 'product',
        'release': 'release',
        'created_at': created_at.strftime('%Y-%m-%d %H:%M:%S.%fZ'),
    }).encode('utf-8'))

    assert activation.image == 'image'
    assert activation.vendor == 'vendor'
    assert activation.product == 'product'
    assert activation.release == 'release'

    # SQLAlchemy only transforms the string into a datetime when querying from the DB
    assert activation.created_at == created_at.strftime('%Y-%m-%d %H:%M:%S.%fZ')
