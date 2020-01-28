# Copyright (c) 2020 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from datetime import datetime, timezone
import re
from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:  # pragma: no cover
    # FIXME: This can be taken from "typing" with Python 3.9.0:
    #        https://github.com/python/typing/blob/2b4749c4d9c79dd2439a1cbdd00230ef9d9b56e3/typing_extensions/src_py3/typing_extensions.py#L1572-L1575
    #        The fix might not be backported to a future 3.8.x:
    #        https://github.com/python/cpython/pull/17214#issuecomment-557855088
    from typing_extensions import TypedDict

    class ParsedImage(TypedDict):
        image_product: str
        image_branch: str
        image_arch: str
        image_platform: str
        image_timestamp: datetime
        image_personality: str

else:
    ParsedImage = Dict


IMAGE_PARSING_RE = r"""
^                       # e.g: eos-3.7-amd64-amd64.190419-225606.base
(?P<product>[^-]+)      # product: eos
-
(?P<branch>[^-]+)       # branch: 3.7
-
(?P<arch>[^-]+)         # arch: amd64
-
(?P<platform>[^-]+)     # platform: amd64
\.
(?P<date>\d{6}|\d{8,})  # date: 190419
-
(?P<time>\d{6})         # time: 225606
\.
(?P<personality>[^.]+)  # personality: base
$"""
IMAGE_PARSING_PATTERN = re.compile(IMAGE_PARSING_RE, re.VERBOSE)


class ImageParsingError(Exception):
    pass


def parse_endless_os_image(image_id: str) -> ParsedImage:
    match = IMAGE_PARSING_PATTERN.match(image_id)

    if match is None:
        raise ImageParsingError(
                f'Invalid image id {image_id!r}: Did not match the expected format')

    matched_date = match.group('date')

    if len(matched_date) == 6:
        # This is the current format, with the year on 2 digits; we'll eventually move to a format
        # with the full year
        matched_date = f'20{matched_date}'

    try:
        date = datetime.strptime(matched_date, '%Y%m%d')

    except ValueError as e:
        raise ImageParsingError(f'Invalid image id {image_id!r}: Could not parse the date: {e}')

    try:
        time = datetime.strptime(match.group('time'), '%H%M%S')

    except ValueError as e:
        raise ImageParsingError(f'Invalid image id {image_id!r}: Could not parse the time: {e}')

    return {
        'image_product': match.group('product'),
        'image_branch': match.group('branch'),
        'image_arch': match.group('arch'),
        'image_platform': match.group('platform'),
        'image_timestamp': datetime(date.year, date.month, date.day,
                                    time.hour, time.minute, time.second,
                                    tzinfo=timezone.utc),
        'image_personality': match.group('personality'),
    }
