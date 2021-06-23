# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import json
import logging
import math
from typing import Optional

from sqlalchemy.orm import validates
from sqlalchemy.schema import CheckConstraint, Column
from sqlalchemy.types import Boolean, DateTime, Integer, Numeric, Unicode

from azafea.model import Base, DbSession
from azafea.vendors import normalize_vendor

from ...image import parse_endless_os_image


log = logging.getLogger(__name__)


class Activation(Base):
    __tablename__ = 'activation_v1'

    id = Column(Integer, primary_key=True)
    image = Column(Unicode, nullable=False)
    vendor = Column(Unicode, nullable=False)
    product = Column(Unicode, nullable=False)
    release = Column(Unicode, nullable=False)
    dualboot = Column(Boolean)
    live = Column(Boolean)

    country = Column(Unicode(length=3))
    latitude = Column(Numeric)
    longitude = Column(Numeric)

    created_at = Column(DateTime(timezone=True), nullable=False, index=True)

    image_product = Column(Unicode, index=True)
    image_branch = Column(Unicode, index=True)
    image_arch = Column(Unicode, index=True)
    image_platform = Column(Unicode, index=True)
    image_timestamp = Column(DateTime(timezone=True), index=True)
    image_personality = Column(Unicode, index=True)

    __table_args__ = (
        CheckConstraint('char_length(country) = 2', name='country_code_2_chars'),
        CheckConstraint('latitude = floor(latitude) +0.5', name='latitude_precision_reduced'),
        CheckConstraint('longitude = floor(longitude) +0.5', name='longitude_precision_reduced'),
    )

    @validates('country')
    def validate_country(self, key: str, country: Optional[str]) -> Optional[str]:
        # Catch both None and the empty string
        if not country:
            return None

        if len(country) != 2:
            raise ValueError(f'country has wrong length: {country}')

        return country

    @validates('latitude')
    def validate_latitude(self, key: str, latitude: Optional[int]) -> Optional[int]:
        # Catch both None and the empty string
        if not latitude:
            return None

        if math.floor(latitude) + 0.5 != latitude:
            raise ValueError(f'latitude is not an integer + 0.5: {latitude}')

        return latitude

    @validates('longitude')
    def validate_longitude(self, key: str, longitude: Optional[int]) -> Optional[int]:
        # Catch both None and the empty string
        if not longitude:
            return None

        if math.floor(longitude) + 0.5 != longitude:
            raise ValueError(f'longitude is not an integer + 0.5: {longitude}')

        return longitude

    @classmethod
    def from_serialized(cls, serialized: bytes) -> 'Activation':
        record = json.loads(serialized.decode('utf-8'))

        record['vendor'] = normalize_vendor(record.get('vendor', 'unknown'))

        # Let's make the case of a missing "image" fail at the SQL level
        if 'image' in record:  # pragma: no branch
            record.update(**parse_endless_os_image(record['image']))
        return cls(**record)


def process(dbsession: DbSession, record: bytes) -> None:
    log.debug('Processing activation v1 record: %s', record)

    activation = Activation.from_serialized(record)
    dbsession.add(activation)
    log.debug('Inserting activation record:\n%s', activation)
