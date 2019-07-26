# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import BigInteger, Integer

from azafea.model import Base

from ..request import Request


class MetricEvent(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True)

    @declared_attr
    def request_id(cls) -> Column:
        return Column(Integer, ForeignKey('metrics_request_v2.id'), index=True)

    @declared_attr
    def request(cls) -> relationship:
        return relationship(Request)

    # This comes in as a uint32, but PostgreSQL only has signed types so we need a BIGINT (int64)
    user_id = Column(BigInteger, nullable=False)


class SingularEvent(MetricEvent):
    __abstract__ = True


class AggregateEvent(MetricEvent):
    __abstract__ = True


class SequenceEvent(MetricEvent):
    __abstract__ = True
