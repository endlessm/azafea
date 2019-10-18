# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import logging
from typing import Any, Dict, Optional, Set, Tuple, Type, Union, cast
from uuid import UUID

from gi.repository import GLib

from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.declarative.api import DeclarativeMeta
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import Session as DbSession
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import BigInteger, DateTime, Integer, LargeBinary, Unicode

from azafea.model import Base

from ..request import Request
from ..utils import get_bytes, get_child_values, get_event_datetime, get_variant


log = logging.getLogger(__name__)

SINGULAR_EVENT_MODELS: Dict[str, Type['SingularEvent']] = {}
AGGREGATE_EVENT_MODELS: Dict[str, Type['AggregateEvent']] = {}
SEQUENCE_EVENT_MODELS: Dict[str, Type['SequenceEvent']] = {}

IGNORED_EVENTS: Set[str] = {
    '005096c4-9444-48c6-844b-6cb693c15235',
    '337fa66d-5163-46ae-ab20-dc605b5d7307',
    '3a4eff55-5d01-48c8-a827-fca5732fd767',
    '566adb36-7701-4067-a971-a398312c2874',
    '6dad6c44-f52f-4bca-8b4c-dc203f175b97',
    '7be59566-2b23-408a-acf6-91490fc1df1c',
    '8f70276e-3f78-45b2-99f8-94db231d42dd',
    '91de63ea-c7b7-412c-93f3-6f3d9b2f864c',
    '9c33a734-7ed8-4348-9e39-3c27f4dc2e62',
    '9f06d0f7-677e-43ca-b732-ccbb40847a31',
    'ab839fd2-a927-456c-8c18-f1136722666b',
    'ae391c82-1937-4ae5-8539-8d1aceed037d',
    'af3e89b2-8293-4703-809c-8e0231c128cb',
    'bef3d12c-df9b-43cd-a67c-31abc5361f03',
    'c02a5764-7f81-48c7-aea4-1413fd4e829c',
    'ce179909-dacb-4b7e-83a5-690480bf21eb',
    'e6541049-9462-4db5-96df-1977f3051578',
}
IGNORED_EMPTY_PAYLOAD_ERRORS: Set[str] = {
    '9af2cc74-d6dd-423f-ac44-600a6eee2d96',
}


class EmptyPayloadError(Exception):
    pass


class WrongPayloadError(Exception):
    pass


class MetricMeta(DeclarativeMeta):
    def __new__(mcl, name: str, bases: Tuple[type, ...], attrs: Dict[str, Any], **kwargs: Any
                ) -> 'MetricMeta':
        cls = super().__new__(mcl, name, bases, attrs)
        event_uuid = attrs.get('__event_uuid__')

        if event_uuid is not None:
            # Register the event model
            if SingularEvent in bases:
                SINGULAR_EVENT_MODELS[event_uuid] = cast(Type[SingularEvent], cls)

            elif AggregateEvent in bases:
                AGGREGATE_EVENT_MODELS[event_uuid] = cast(Type[AggregateEvent], cls)

            elif SequenceEvent in bases:
                SEQUENCE_EVENT_MODELS[event_uuid] = cast(Type[SequenceEvent], cls)

            else:  # pragma: no cover
                raise NotImplementedError(f"Can't handle class {name} with bases {bases}")

        # FIXME: Do we have to cast? https://github.com/python/typeshed/issues/3386
        return cast(MetricMeta, cls)


class MetricEvent(Base, metaclass=MetricMeta):
    __abstract__ = True

    __event_uuid__: str
    __payload_type__: Optional[str]

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
        payload = maybe_payload.get_maybe()

        if self.__payload_type__ is None:
            if payload is not None:
                log.error('Metric event %s takes no payload, but got %s',
                          self.__event_uuid__, payload)

            return {}

        if payload is None:
            raise EmptyPayloadError(f'Metric event {self.__event_uuid__} needs a '
                                    f'{self.__payload_type__} payload, but got none')

        payload = get_variant(payload)
        payload_type = payload.get_type_string()

        if payload_type != self.__payload_type__:
            raise WrongPayloadError(f'Metric event {self.__event_uuid__} needs a '
                                    f'{self.__payload_type__} payload, but got '
                                    f'{payload} ({payload_type})')

        return self._get_fields_from_payload(payload)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        raise NotImplementedError('Implement this method in final event models')  # pragma: no cover


class UnknownEvent(MetricEvent):
    __abstract__ = True

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


class InvalidEvent(UnknownEvent):
    __abstract__ = True

    error = Column(Unicode, nullable=False)


class SingularEvent(MetricEvent):
    __abstract__ = True

    occured_at = Column(DateTime(timezone=True), nullable=False)


class InvalidSingularEvent(SingularEvent, InvalidEvent):
    __tablename__ = 'invalid_singular_event'


class UnknownSingularEvent(SingularEvent, UnknownEvent):
    __tablename__ = 'unknown_singular_event'


class AggregateEvent(MetricEvent):
    __abstract__ = True

    occured_at = Column(DateTime(timezone=True), nullable=False)
    count = Column(BigInteger, nullable=False)


class InvalidAggregateEvent(AggregateEvent, InvalidEvent):
    __tablename__ = 'invalid_aggregate_event'


class UnknownAggregateEvent(AggregateEvent, UnknownEvent):
    __tablename__ = 'unknown_aggregate_event'


class SequenceEvent(MetricEvent):
    __abstract__ = True

    started_at = Column(DateTime(timezone=True), nullable=False)
    stopped_at = Column(DateTime(timezone=True), nullable=False)


# This is not an event part of an unknown sequence: it is the whole sequence with start, progress
# and stop events in its payload_data
class InvalidSequence(InvalidEvent):
    __tablename__ = 'invalid_sequence'


# This is not an event part of an unknown sequence: it is the whole sequence with start, progress
# and stop events in its payload_data
class UnknownSequence(UnknownEvent):
    __tablename__ = 'unknown_sequence'


def new_singular_event(request: Request, event_variant: GLib.Variant, dbsession: DbSession
                       ) -> Optional[SingularEvent]:
    event_id = str(UUID(bytes=get_bytes(event_variant.get_child_value(1))))

    if event_id in IGNORED_EVENTS:
        return None

    user_id = event_variant.get_child_value(0).get_uint32()
    event_relative_timestamp = event_variant.get_child_value(2).get_int64()
    payload = event_variant.get_child_value(3)

    event_date = get_event_datetime(request.absolute_timestamp, request.relative_timestamp,
                                    event_relative_timestamp)

    try:
        try:
            event_model = SINGULAR_EVENT_MODELS[event_id]

            # Mypy complains here, even though this should be fine:
            # https://github.com/dropbox/sqlalchemy-stubs/issues/97
            event = event_model(request=request, user_id=user_id,  # type: ignore
                                occured_at=event_date, payload=payload)

        except KeyError:
            # Mypy complains here, even though this should be fine:
            # https://github.com/dropbox/sqlalchemy-stubs/issues/97
            event = UnknownSingularEvent(request=request, user_id=user_id,  # type: ignore
                                         occured_at=event_date, event_id=event_id, payload=payload)

        except EmptyPayloadError:
            if event_id in IGNORED_EMPTY_PAYLOAD_ERRORS:
                return None

            raise

    except Exception as e:
        log.exception('An error occured while processing the event:')

        # Mypy complains here, even though this should be fine:
        # https://github.com/dropbox/sqlalchemy-stubs/issues/97
        event = InvalidSingularEvent(request=request, user_id=user_id,  # type: ignore
                                     occured_at=event_date, event_id=event_id, payload=payload,
                                     error=str(e))

    dbsession.add(event)

    return event


def new_aggregate_event(request: Request, event_variant: GLib.Variant, dbsession: DbSession
                        ) -> Optional[AggregateEvent]:
    event_id = str(UUID(bytes=get_bytes(event_variant.get_child_value(1))))

    if event_id in IGNORED_EVENTS:
        return None

    user_id = event_variant.get_child_value(0).get_uint32()
    count = event_variant.get_child_value(2).get_int64()
    event_relative_timestamp = event_variant.get_child_value(3).get_int64()
    payload = event_variant.get_child_value(4)

    event_date = get_event_datetime(request.absolute_timestamp, request.relative_timestamp,
                                    event_relative_timestamp)

    try:
        event_model = AGGREGATE_EVENT_MODELS[event_id]

        # Mypy complains here, even though this should be fine:
        # https://github.com/dropbox/sqlalchemy-stubs/issues/97
        event = event_model(request=request, user_id=user_id, occured_at=event_date,  # type: ignore
                            count=count, payload=payload)

    except KeyError:
        # Mypy complains here, even though this should be fine:
        # https://github.com/dropbox/sqlalchemy-stubs/issues/97
        event = UnknownAggregateEvent(request=request, user_id=user_id,  # type: ignore
                                      occured_at=event_date, count=count, event_id=event_id,
                                      payload=payload)

    except Exception as e:
        log.exception('An error occured while processing the aggregate:')

        # Mypy complains here, even though this should be fine:
        # https://github.com/dropbox/sqlalchemy-stubs/issues/97
        event = InvalidAggregateEvent(request=request, user_id=user_id,  # type: ignore
                                      occured_at=event_date, count=count, event_id=event_id,
                                      payload=payload, error=str(e))

    dbsession.add(event)

    return event


def new_sequence_event(request: Request, sequence_variant: GLib.Variant, dbsession: DbSession
                       ) -> Optional[Union[SequenceEvent, InvalidSequence, UnknownSequence]]:
    event_id = str(UUID(bytes=get_bytes(sequence_variant.get_child_value(1))))

    if event_id in IGNORED_EVENTS:
        return None

    user_id = sequence_variant.get_child_value(0).get_uint32()
    events = sequence_variant.get_child_value(2)
    num_events = events.n_children()

    if num_events < 2:
        error = f'Sequence must have at least 2 elements, but only had {num_events}'

        # Mypy complains here, even though this should be fine:
        # https://github.com/dropbox/sqlalchemy-stubs/issues/97
        sequence = InvalidSequence(request=request, user_id=user_id,  # type: ignore
                                   event_id=event_id, payload=events, error=error)
        dbsession.add(sequence)

        return sequence

    start_variant, *_progress_variants, stop_variant = get_child_values(events)

    # For now, we ignore progress events entirely. We also assume the stop event always has a null
    # payload. This works for most sequence events we care about in priority.
    # TODO: Figure this out for the more complex events

    start_relative_timestamp = start_variant.get_child_value(0).get_int64()
    payload = start_variant.get_child_value(1)
    started_at = get_event_datetime(request.absolute_timestamp, request.relative_timestamp,
                                    start_relative_timestamp)

    stop_relative_timestamp = stop_variant.get_child_value(0).get_int64()
    stopped_at = get_event_datetime(request.absolute_timestamp, request.relative_timestamp,
                                    stop_relative_timestamp)

    try:
        event_model = SEQUENCE_EVENT_MODELS[event_id]

        # Mypy complains here, even though this should be fine:
        # https://github.com/dropbox/sqlalchemy-stubs/issues/97
        sequence = event_model(request=request, user_id=user_id,  # type: ignore
                               started_at=started_at, stopped_at=stopped_at, payload=payload)

    except KeyError:
        # Mypy complains here, even though this should be fine:
        # https://github.com/dropbox/sqlalchemy-stubs/issues/97
        sequence = UnknownSequence(request=request, user_id=user_id,  # type: ignore
                                   event_id=event_id, payload=events)

    except Exception as e:
        log.exception('An error occured while processing the sequence:')

        # Mypy complains here, even though this should be fine:
        # https://github.com/dropbox/sqlalchemy-stubs/issues/97
        sequence = InvalidSequence(request=request, user_id=user_id,  # type: ignore
                                   event_id=event_id, payload=events, error=str(e))

    dbsession.add(sequence)

    return sequence
