# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from typing import Any, Dict, List, Union

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.schema import Column
from sqlalchemy.sql import expression
from sqlalchemy.types import Boolean, DateTime, Integer, Unicode

from azafea.model import Base, DbSession

from ..image import parse_endless_os_image


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
    location_id = Column(Unicode, index=True)
    location_city = Column(Unicode, index=True)
    location_state = Column(Unicode, index=True)
    location_street = Column(Unicode, index=True)
    location_country = Column(Unicode, index=True)
    location_facility = Column(Unicode, index=True)


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
    if isinstance(info, dict):
        info = {f'location_{key}': value for key, value in info.items()}
        stmt = insert(Machine.__table__).values(machine_id=machine_id, **info)
        stmt = stmt.on_conflict_do_update(constraint='uq_metrics_machine_machine_id', set_=info)

        dbsession.connection().execute(stmt)
