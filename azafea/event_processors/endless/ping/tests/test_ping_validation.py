# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import pytest


def test_valid_country():
    from azafea.event_processors.endless.ping.v1.handler import Ping

    ping = Ping(country='HK')
    assert ping.country == 'HK'


@pytest.mark.parametrize('country', ['', None])
def test_empty_country(country):
    from azafea.event_processors.endless.ping.v1.handler import Ping

    ping = Ping(country=country)
    assert ping.country is None


@pytest.mark.parametrize('country', ['HOKG', 'Hong Kong'])
def test_invalid_country(country):
    from azafea.event_processors.endless.ping.v1.handler import Ping

    with pytest.raises(ValueError) as excinfo:
        Ping(country=country)

    assert f'country has wrong length: {country}' in str(excinfo.value)
