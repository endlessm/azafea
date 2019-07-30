# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from typing import Any, Dict, Tuple, Type, cast
from uuid import UUID

from gi.repository import GLib

from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.declarative.api import DeclarativeMeta
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import Session as DbSession
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import BigInteger, DateTime, Integer, LargeBinary

from azafea.model import Base

from ..request import Request
from ..utils import get_bytes, get_event_datetime


SINGULAR_EVENT_MODELS: Dict[str, Type['SingularEvent']] = {}


class MetricMeta(DeclarativeMeta):
    def __new__(mcl: Type[type], name: str, bases: Tuple[type, ...], attrs: Dict[str, Any],
                **kwargs: Any) -> Type['MetricEvent']:
        cls = super().__new__(mcl, name, bases, attrs)
        event_uuid = attrs.get('__event_uuid__')

        if event_uuid is not None:
            # Register the event model
            if SingularEvent in bases:
                SINGULAR_EVENT_MODELS[event_uuid] = cast(Type[SingularEvent], cls)

            else:  # pragma: no cover
                raise NotImplementedError(f"Can't handle class {name} with bases {bases}")

        return cls


class MetricEvent(Base, metaclass=MetricMeta):
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

    def __init__(self, payload: GLib.Variant, **kwargs: Dict[str, Any]) -> None:
        payload_fields = self._parse_payload(payload)
        kwargs.update(payload_fields)

        super().__init__(**kwargs)

    def _parse_payload(self, maybe_payload: GLib.Variant) -> Dict[str, Any]:
        raise NotImplementedError('Implement this method in final event models')  # pragma: no cover


class SingularEvent(MetricEvent):
    __abstract__ = True

    occured_at = Column(DateTime(timezone=True), nullable=False)


class UnknownSingularEvent(SingularEvent):
    __tablename__ = 'unknown_singular_event'

    event_id = Column(postgresql.UUID(as_uuid=True), nullable=False)
    payload_data = Column(LargeBinary, nullable=False)

    def _parse_payload(self, maybe_payload: GLib.Variant) -> Dict[str, Any]:
        # Workaround an issue in GLib < 2.62
        #        https://gitlab.gnome.org/GNOME/glib/issues/1865
        as_bytes = maybe_payload.get_data_as_bytes()

        if as_bytes is None:
            payload_data = b''

        else:
            payload_data = as_bytes.get_data()

        return {'payload_data': payload_data}


class AggregateEvent(MetricEvent):
    __abstract__ = True


class SequenceEvent(MetricEvent):
    __abstract__ = True


def new_singular_event(request: Request, event_variant: GLib.Variant, dbsession: DbSession
                       ) -> SingularEvent:
    user_id = event_variant.get_child_value(0).get_uint32()
    event_id = str(UUID(bytes=get_bytes(event_variant.get_child_value(1))))
    event_relative_timestamp = event_variant.get_child_value(2).get_int64()
    payload = event_variant.get_child_value(3)

    event_date = get_event_datetime(request.absolute_timestamp, request.relative_timestamp,
                                    event_relative_timestamp)

    try:
        event_model = SINGULAR_EVENT_MODELS[event_id]

        # Mypy complains here, even though this should be fine:
        # https://github.com/dropbox/sqlalchemy-stubs/issues/97
        event = event_model(request=request, user_id=user_id, occured_at=event_date,  # type: ignore
                            payload=payload)

    except KeyError:
        # Mypy complains here, even though this should be fine:
        # https://github.com/dropbox/sqlalchemy-stubs/issues/97
        event = UnknownSingularEvent(request=request, user_id=user_id,  # type: ignore
                                     occured_at=event_date, event_id=event_id, payload=payload)

    dbsession.add(event)

    return event
