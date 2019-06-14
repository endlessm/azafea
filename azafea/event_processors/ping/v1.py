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


from datetime import datetime
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

    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        UniqueConstraint(image, vendor, product, dualboot,
                         name='uq_ping_configuration_v1_image_vendor_product_dualboot'),
    )

    @classmethod
    def from_serialized(cls, serialized: bytes, dbsession: DbSession) -> 'PingConfiguration':
        record = json.loads(serialized.decode('utf-8'))

        columns = inspect(cls).attrs
        record = {k: v for (k, v) in record.items() if k in columns}

        record['vendor'] = normalize_vendor(record.get('vendor', 'unknown'))

        # Postgresql's 'INSERT … ON CONFLICT …' is not available at the ORM layer, so let's
        # drop down to the SQL layer
        stmt = insert(PingConfiguration.__table__).values(**record)
        stmt = stmt.returning(PingConfiguration.__table__.c.id)
        stmt = stmt.on_conflict_do_update(
            constraint='uq_ping_configuration_v1_image_vendor_product_dualboot',
            set_={'updated_at': record['updated_at']}
        )
        result = dbsession.connection().execute(stmt)
        dbsession.commit()
        upserted_id = result.first()[0]

        return dbsession.query(cls).get(upserted_id)


class Ping(Base):
    __tablename__ = 'ping_v1'

    id = Column(Integer, primary_key=True)
    config_id = Column(Integer, ForeignKey('ping_configuration_v1.id'), nullable=False)
    release = Column(Unicode, nullable=False)
    count = Column(Integer, nullable=False)
    country = Column(Unicode(length=3))
    metrics_enabled = Column(Boolean)
    metrics_environment = Column(Unicode)

    created_at = Column(DateTime(timezone=True), index=True, nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)

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

        return cls(**record)


def process(dbsession: DbSession, record: bytes) -> None:
    log.debug('Processing ping v1 record: %s', record)

    ping_config = PingConfiguration.from_serialized(record, dbsession)
    dbsession.add(ping_config)
    log.debug('Upserting ping configuration record:\n%s', ping_config)

    ping = Ping.from_serialized(record)
    ping.config = ping_config
    dbsession.add(ping)
    log.debug('Inserting ping record:\n%s', ping)

    dt = datetime.now()
    log.info('  -> %s', dt)
