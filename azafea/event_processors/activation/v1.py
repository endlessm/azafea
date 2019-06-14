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


import json
import logging
from typing import Optional

from sqlalchemy.orm import validates
from sqlalchemy.orm.session import Session as DbSession
from sqlalchemy.schema import CheckConstraint, Column
from sqlalchemy.types import BigInteger, Boolean, DateTime, Integer, Numeric, Unicode

from azafea.model import Base


log = logging.getLogger(__name__)


class Activation(Base):
    __tablename__ = 'activation_v1'

    id = Column(Integer, primary_key=True)
    image = Column(Unicode, nullable=False)
    vendor = Column(Unicode, nullable=False)
    product = Column(Unicode, nullable=False)
    release = Column(Unicode, nullable=False)
    serial = Column(Unicode)
    dualboot = Column(Boolean)
    live = Column(Boolean)

    # This comes in as a uint32, but PostgreSQL only has signed types so we need a BIGINT (int64)
    mac_hash = Column(BigInteger)

    country = Column(Unicode(length=3))
    region = Column(Unicode)
    city = Column(Unicode)
    latitude = Column(Numeric)
    longitude = Column(Numeric)

    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        CheckConstraint('char_length(country) = 3', name='country_code_3_chars'),
    )

    @validates('country')
    def validate_country(self, key: str, country: Optional[str]) -> Optional[str]:
        # Catch both None and the empty string
        if not country:
            return None

        if len(country) != 3:
            raise ValueError('country is too short')

        return country

    @classmethod
    def from_serialized(cls, serialized: bytes) -> 'Activation':
        record = json.loads(serialized.decode('utf-8'))

        return cls(**record)


def process(dbsession: DbSession, record: bytes) -> None:
    log.debug('Processing activation v1 record: %s', record)

    activation = Activation.from_serialized(record)
    dbsession.add(activation)
    log.debug('Inserting activation record:\n%s', activation)
