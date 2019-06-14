# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# Azafea is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Azafea is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Azafea.  If not, see <http://www.gnu.org/licenses/>.


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
