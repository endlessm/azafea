# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import pytest

from azafea.vendors import normalize_vendor


@pytest.mark.parametrize('vendor, expected', [
    ('', ''),
    ('endless', 'Endless'),
    ('EnDlEsS', 'Endless'),
    ('no such vendor', 'no such vendor'),
    ('', ''),
])
def test_normalize_vendor(vendor, expected):
    assert normalize_vendor(vendor) == expected
