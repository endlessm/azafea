# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import pytest


def test_valid_country():
    from azafea.event_processors.endless.activation.v1.handler import Activation

    activation = Activation(country='HK')
    assert activation.country == 'HK'


@pytest.mark.parametrize('country', ['', None])
def test_empty_country(country):
    from azafea.event_processors.endless.activation.v1.handler import Activation

    activation = Activation(country=country)
    assert activation.country is None


@pytest.mark.parametrize('country', ['HOKG', 'Hong Kong'])
def test_invalid_country(country):
    from azafea.event_processors.endless.activation.v1.handler import Activation

    with pytest.raises(ValueError) as excinfo:
        Activation(country=country)

    assert f'country has wrong length: {country}' in str(excinfo.value)


def test_invalid_latitude():
    from azafea.event_processors.endless.activation.v1.handler import Activation
    latitude = 18.7
    with pytest.raises(ValueError) as excinfo:
        Activation(latitude=latitude)

    assert f'latitude is not an integer + 0.5: {latitude}' in str(excinfo.value)


def test_invalid_longitude():
    from azafea.event_processors.endless.activation.v1.handler import Activation
    longitude = 18.7
    with pytest.raises(ValueError) as excinfo:
        Activation(longitude=longitude)

    assert f'longitude is not an integer + 0.5: {longitude}' in str(excinfo.value)
