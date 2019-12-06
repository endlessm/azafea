# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, Unicode

from azafea.model import Base


class Event(Base):
    __tablename__ = 'migration_event'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode, nullable=False)


def process(*args, **kwargs):
    pass
