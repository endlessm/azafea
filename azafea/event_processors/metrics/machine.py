# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, Unicode

from azafea.model import Base, DbSession


class Machine(Base):
    __tablename__ = 'metrics_machine'

    id = Column(Integer, primary_key=True)
    machine_id = Column(Unicode(32), nullable=False, unique=True)
    image_id = Column(Unicode, nullable=False)


def insert_machine(dbsession: DbSession, machine_id: str, image_id: str) -> None:
    stmt = insert(Machine.__table__).values(machine_id=machine_id, image_id=image_id)
    stmt = stmt.on_conflict_do_nothing()

    dbsession.connection().execute(stmt)