# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import json
import logging
from typing import Optional

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import relationship, validates
from sqlalchemy.orm.session import Session as DbSession
from sqlalchemy.schema import CheckConstraint, Column, ForeignKey, UniqueConstraint
from sqlalchemy.types import Boolean, DateTime, Integer, Unicode

from azafea.model import Base, NullableBoolean
from azafea.vendors import normalize_vendor


log = logging.getLogger(__name__)


class PingConfiguration(Base):
    __tablename__ = 'ping_configuration_v1'

    id = Column(Integer, primary_key=True)
    image = Column(Unicode, nullable=False)
    vendor = Column(Unicode, nullable=False)
    product = Column(Unicode, nullable=False)
    dualboot = Column(NullableBoolean, nullable=False, server_default='unknown')
    created_at = Column(DateTime(timezone=True), nullable=False, index=True)

    __table_args__ = (
        UniqueConstraint(image, vendor, product, dualboot,
                         name='uq_ping_configuration_v1_image_vendor_product_dualboot'),
    )

    @classmethod
    def id_from_serialized(cls, serialized: bytes, dbsession: DbSession) -> int:
        record = json.loads(serialized.decode('utf-8'))

        columns = inspect(cls).attrs
        record = {k: v for (k, v) in record.items() if k in columns}

        record['vendor'] = normalize_vendor(record.get('vendor', 'unknown'))

        # Postgresql's 'INSERT … ON CONFLICT …' is not available at the ORM layer, so let's
        # drop down to the SQL layer
        stmt = insert(PingConfiguration.__table__).values(**record)
        stmt = stmt.returning(PingConfiguration.__table__.c.id)

        # We have to use 'ON CONFLICT … DO UPDATE …' because 'ON CONFLICT DO NOTHING' does not
        # return anything, and we need to get the id back; in addition we have to actually
        # update something, anything, so let's arbitrarily update the image to its existing value
        stmt = stmt.on_conflict_do_update(
            constraint='uq_ping_configuration_v1_image_vendor_product_dualboot',
            set_={'image': record['image']}
        )
        result = dbsession.connection().execute(stmt)
        dbsession.commit()

        return result.first()[0]


class Ping(Base):
    __tablename__ = 'ping_v1'

    id = Column(Integer, primary_key=True)
    config_id = Column(Integer, ForeignKey('ping_configuration_v1.id'), nullable=False, index=True)
    release = Column(Unicode, nullable=False)
    count = Column(Integer, nullable=False)
    country = Column(Unicode(length=3))
    metrics_enabled = Column(Boolean)
    metrics_environment = Column(Unicode)
    created_at = Column(DateTime(timezone=True), nullable=False, index=True)

    __table_args__ = (
        CheckConstraint('char_length(country) = 3', name='country_code_3_chars'),
        CheckConstraint('count >= 0', name='count_positive'),
    )

    config = relationship('PingConfiguration')

    # TODO: share with activation?
    @validates('country')
    def validate_country(self, key: str, country: Optional[str]) -> Optional[str]:
        # Catch both None and the empty string
        if not country:
            return None

        if len(country) != 3:
            raise ValueError('country is too short')

        return country

    @classmethod
    def from_serialized(cls, serialized: bytes) -> 'Ping':
        record = json.loads(serialized.decode('utf-8'))

        # Older images had a bug where count=0 would not be sent
        record.setdefault('count', 0)

        return cls(**record)


def process(dbsession: DbSession, record: bytes) -> None:
    log.debug('Processing ping v1 record: %s', record)

    ping_config_id = PingConfiguration.id_from_serialized(record, dbsession)

    ping = Ping.from_serialized(record)
    ping.config_id = ping_config_id
    dbsession.add(ping)
    log.debug('Inserting ping record:\n%s', ping)
