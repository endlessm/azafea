# Copyright (c) 2020 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from datetime import datetime, timezone

import pytest


@pytest.mark.parametrize('image_id, expected', [
    (
        'eos-eos3.7-armv7hl-ec100.190419-225606.base',
        {
            'image_product': 'eos',
            'image_branch': 'eos3.7',
            'image_arch': 'armv7hl',
            'image_platform': 'ec100',
            'image_timestamp': datetime(2019, 4, 19, 22, 56, 6, tzinfo=timezone.utc),
            'image_personality': 'base'
        }
    ),
    (
        'eos-master-armv7hl-ec100.20190419-225606.pt_BR',
        {
            'image_product': 'eos',
            'image_branch': 'master',
            'image_arch': 'armv7hl',
            'image_platform': 'ec100',
            'image_timestamp': datetime(2019, 4, 19, 22, 56, 6, tzinfo=timezone.utc),
            'image_personality': 'pt_BR'
        }
    ),
    (
        # Back in 2015-2016, due to a bug images were generated with the personality field repeated
        'eos-master-armv7hl-ec100.20190419-225606.pt_BR.pt_BR',
        {
            'image_product': 'eos',
            'image_branch': 'master',
            'image_arch': 'armv7hl',
            'image_platform': 'ec100',
            'image_timestamp': datetime(2019, 4, 19, 22, 56, 6, tzinfo=timezone.utc),
            'image_personality': 'pt_BR'
        }
    ),
])
def test_parse_endless_os_image(image_id, expected):
    from azafea.event_processors.endless.image import parse_endless_os_image

    assert parse_endless_os_image(image_id) == expected


@pytest.mark.parametrize('invalid_image_id', [
    '',
    'image',
    '-master-armv7hl-ec100.190419-225606.base',
    'eos--armv7hl-ec100.190419-225606.base',
    'eos-master--ec100.190419-225606.base',
    'eos-master-armv7hl-.190419-225606.base',
    'eos-master-armv7hl-ec100.-225606.base',
    'eos-master-armv7hl-ec100.19419-225606.base',
    'eos-master-armv7hl-ec100.0190419-225606.base',
    'eos-master-armv7hl-ec100.190419-.base',
    'eos-master-armv7hl-ec100.190419-22566.base',
    'eos-master-armv7hl-ec100.190419-1225606.base',
    'eos-master-armv7hl-ec100.190419-225606.',
])
def test_parse_endless_os_invalid_image(invalid_image_id):
    from azafea.event_processors.endless.image import ImageParsingError, parse_endless_os_image

    with pytest.raises(ImageParsingError) as excinfo:
        parse_endless_os_image(invalid_image_id)

    assert (
        f'Invalid image id {invalid_image_id!r}: Did not match the expected format'
        ) in str(excinfo.value)


@pytest.mark.parametrize('invalid_image_id', [
    'eos-master-armv7hl-ec100.191319-225606.base',
    'eos-master-armv7hl-ec100.20190431-225606.base',
])
def test_parse_endless_os_image_invalid_date(invalid_image_id):
    from azafea.event_processors.endless.image import ImageParsingError, parse_endless_os_image

    with pytest.raises(ImageParsingError) as excinfo:
        parse_endless_os_image(invalid_image_id)

    assert f'Invalid image id {invalid_image_id!r}: Could not parse the date' in str(excinfo.value)


@pytest.mark.parametrize('invalid_image_id', [
    'eos-master-armv7hl-ec100.190419-245606.base',
    'eos-master-armv7hl-ec100.190419-006306.base',
    'eos-master-armv7hl-ec100.190419-225678.base',
])
def test_parse_endless_os_image_invalid_time(invalid_image_id):
    from azafea.event_processors.endless.image import ImageParsingError, parse_endless_os_image

    with pytest.raises(ImageParsingError) as excinfo:
        parse_endless_os_image(invalid_image_id)

    assert f'Invalid image id {invalid_image_id!r}: Could not parse the time' in str(excinfo.value)
