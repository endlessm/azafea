# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from typing import Any, Dict, List, Union
import logging

from sqlalchemy.dialects.postgresql import JSONB, insert
from sqlalchemy.schema import Column, Index
from sqlalchemy.sql import expression
from sqlalchemy.types import Boolean, DateTime, Integer, Unicode

from azafea.model import Base, DbSession

from ....image import parse_endless_os_image


log = logging.getLogger(__name__)


class Machine(Base):
    __tablename__ = 'metrics_machine'

    id = Column(Integer, primary_key=True)
    machine_id = Column(Unicode(32), nullable=False, unique=True)
    image_id = Column(Unicode)
    image_product = Column(Unicode, index=True)
    image_branch = Column(Unicode, index=True)
    image_arch = Column(Unicode, index=True)
    image_platform = Column(Unicode, index=True)
    image_timestamp = Column(DateTime(timezone=True), index=True)
    image_personality = Column(Unicode, index=True)
    demo = Column(Boolean, server_default=expression.false())
    dualboot = Column(Boolean, server_default=expression.false())
    live = Column(Boolean, server_default=expression.false())
    location = Column(JSONB)
    location_id = Column(Unicode)
    location_city = Column(Unicode)
    location_state = Column(Unicode)
    location_street = Column(Unicode)
    location_country = Column(Unicode)
    location_facility = Column(Unicode)

    __table_args__ = (
        Index('ix_metrics_machine_location_id', location_id,
              postgresql_where=(location_id.isnot(None))),
        Index('ix_metrics_machine_location_city', location_city,
              postgresql_where=(location_city.isnot(None))),
        Index('ix_metrics_machine_location_state', location_state,
              postgresql_where=(location_state.isnot(None))),
        Index('ix_metrics_machine_location_street', location_street,
              postgresql_where=(location_street.isnot(None))),
        Index('ix_metrics_machine_location_country', location_country,
              postgresql_where=(location_country.isnot(None))),
        Index('ix_metrics_machine_location_facility', location_facility,
              postgresql_where=(location_facility.isnot(None))),
    )


def upsert_machine_demo(dbsession: DbSession, machine_id: str) -> None:
    stmt = insert(Machine.__table__).values(machine_id=machine_id, demo=True)
    stmt = stmt.on_conflict_do_update(constraint='uq_metrics_machine_machine_id',
                                      set_={'demo': True})

    dbsession.connection().execute(stmt)


def upsert_machine_dualboot(dbsession: DbSession, machine_id: str) -> None:
    stmt = insert(Machine.__table__).values(machine_id=machine_id, dualboot=True)
    stmt = stmt.on_conflict_do_update(constraint='uq_metrics_machine_machine_id',
                                      set_={'dualboot': True})

    dbsession.connection().execute(stmt)


def upsert_machine_image(dbsession: DbSession, machine_id: str, image_id: str) -> None:
    image_values: Dict[str, Any] = {'image_id': image_id, **parse_endless_os_image(image_id)}

    stmt = insert(Machine.__table__).values(machine_id=machine_id, **image_values)
    stmt = stmt.on_conflict_do_update(constraint='uq_metrics_machine_machine_id', set_=image_values)

    dbsession.connection().execute(stmt)


def upsert_machine_live(dbsession: DbSession, machine_id: str) -> None:
    stmt = insert(Machine.__table__).values(machine_id=machine_id, live=True)
    stmt = stmt.on_conflict_do_update(constraint='uq_metrics_machine_machine_id',
                                      set_={'live': True})

    dbsession.connection().execute(stmt)


def upsert_machine_location(dbsession: DbSession, machine_id: str,
                            info: Union[Dict[str, Any], List[Any]]) -> None:
    """Update the relevant Machine record with information from a LocationLabel event.

    Although the info is guaranteed to be a `Dict[str, str]` when received from
    the client, the database column is of type JSONB, so the
    `LocationLabel.info` field has a more general type. As a result, the
    function parameter also has a more general type, and this runtime type
    check is needed to satisfy mypy.

    """
    if isinstance(info, dict):
        location_columns = [column.name for column in Machine.__table__.columns]
        values = {
            f'location_{key}': value for key, value in info.items()
            if f'location_{key}' in location_columns}
        stmt = insert(Machine.__table__).values(machine_id=machine_id, location=info, **values)
        stmt = stmt.on_conflict_do_update(constraint='uq_metrics_machine_machine_id', set_=values)

        dbsession.connection().execute(stmt)
    else:  # pragma: no cover
        log.warning('Data received for machine location is not a dict: %r', info)
