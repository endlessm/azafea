# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import logging
from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, Optional, Set, Tuple, Type, cast

from gi.repository import GLib

from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.declarative.api import DeclarativeMeta
from sqlalchemy.orm import relationship
from sqlalchemy.orm.query import Query
from sqlalchemy.schema import Column, ForeignKey, UniqueConstraint
from sqlalchemy.types import BigInteger, Boolean, Date, DateTime, Integer, LargeBinary, Unicode

from azafea.model import Base, DbSession

from ..utils import get_child_values, get_event_datetime, get_variant


log = logging.getLogger(__name__)

VARIANT_TYPE = GLib.VariantType('(xxsa{ss}ya(aysxmv)a(ayssumv))')

SINGULAR_EVENT_MODELS: Dict[str, Type['SingularEvent']] = {}
AGGREGATE_EVENT_MODELS: Dict[str, Type['AggregateEvent']] = {}

IGNORED_EVENTS: Set[str] = {
    '005096c4-9444-48c6-844b-6cb693c15235',
    '337fa66d-5163-46ae-ab20-dc605b5d7307',
    '3a4eff55-5d01-48c8-a827-fca5732fd767',
    '350ac4ff-3026-4c25-9e7e-e8103b4fd5d8',
    '566adb36-7701-4067-a971-a398312c2874',
    '5fae6179-e108-4962-83be-c909259c0584',
    '6dad6c44-f52f-4bca-8b4c-dc203f175b97',
    '72fea371-15d1-401d-8a40-c47f379f64fd',
    '7be59566-2b23-408a-acf6-91490fc1df1c',
    '8f70276e-3f78-45b2-99f8-94db231d42dd',
    '91de63ea-c7b7-412c-93f3-6f3d9b2f864c',
    '9a0cf836-12cd-4887-95d8-e48ccdf6e552',
    '9c33a734-7ed8-4348-9e39-3c27f4dc2e62',
    '9f06d0f7-677e-43ca-b732-ccbb40847a31',
    'ab839fd2-a927-456c-8c18-f1136722666b',
    'ae391c82-1937-4ae5-8539-8d1aceed037d',
    'af3e89b2-8293-4703-809c-8e0231c128cb',
    'b1f87a3f-a464-48d4-8e35-35dd45659010',
    'b2b17dfd-c30e-4789-abcc-4a38323127f6',
    'b89f9a4a-3035-4fc3-9bef-584367fe2c96',
    'bef3d12c-df9b-43cd-a67c-31abc5361f03',
    'c02a5764-7f81-48c7-aea4-1413fd4e829c',
    'ce179909-dacb-4b7e-83a5-690480bf21eb',
    'd936cd5c-08de-4d4e-8a87-8df1f4a33cba',
    'e6541049-9462-4db5-96df-1977f3051578',
    'fb59199e-5384-472e-af1e-00b7a419d5c2',
}
IGNORED_EMPTY_PAYLOAD_ERRORS: Set[str] = set()


class Channel(Base):
    __tablename__ = 'channel_v3'

    __table_args__ = (
        UniqueConstraint('image_id', 'site', 'dual_boot', 'live'),
    )

    id = Column(Integer, primary_key=True)

    #: image ID (e.g. ``eos-eos3.1-amd64-amd64.170115-071322.base``)
    image_id = Column(Unicode, nullable=False)
    #: dictionary of string keys (such as ``facility``, ``city`` and
    #: ``state``) to the values provided in the location.conf file (written by
    #: the ``eos-label-location`` utility)
    site = Column(JSONB, nullable=False)
    #: dual boot computer
    dual_boot = Column(Boolean, nullable=False)
    #: live sessions
    live = Column(Boolean, nullable=False)


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
            else:  # pragma: no cover
                raise NotImplementedError(f"Can't handle class {name} with bases {bases}")

            # Ignore empty payloads
            # FIXME: mypy can’t know that MetricMeta is only used as MetricEvent metaclass
            if cls.__ignore_empty_payload__:  # type: ignore
                IGNORED_EMPTY_PAYLOAD_ERRORS.add(event_uuid)

        # FIXME: Do we have to cast? https://github.com/python/typeshed/issues/3386
        return cast(MetricMeta, cls)


class MetricEvent(Base, metaclass=MetricMeta):
    __abstract__ = True

    __event_uuid__: str
    __payload_type__: Optional[str]
    __ignore_empty_payload__ = False

    id = Column(Integer, primary_key=True)
    os_version = Column(Unicode, nullable=False)

    @declared_attr
    def channel_id(cls) -> Column:
        return Column(Integer, ForeignKey(Channel.id), index=True)

    @declared_attr
    def channel(cls) -> relationship:
        return relationship(Channel)

    def __init__(self, payload: GLib.Variant, **kwargs: Dict[str, Any]) -> None:
        payload_fields = self._parse_payload(payload)
        fields = kwargs.copy()
        fields.pop('singulars', None)
        fields.pop('aggregates', None)
        fields.update(payload_fields)

        super().__init__(**fields)

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
        return {'payload_data': maybe_payload.get_data_as_bytes().get_data()}


class InvalidEvent(UnknownEvent):
    __abstract__ = True

    error = Column(Unicode, nullable=False)


class SingularEvent(MetricEvent):
    __abstract__ = True

    occured_at = Column(DateTime(timezone=True), nullable=False, index=True)


class InvalidSingularEvent(SingularEvent, InvalidEvent):
    __tablename__ = 'invalid_singular_event_v3'


class UnknownSingularEvent(SingularEvent, UnknownEvent):
    __tablename__ = 'unknown_singular_event_v3'


class AggregateEvent(MetricEvent):
    __abstract__ = True

    period_start = Column(Date, nullable=False, index=True)
    count = Column(BigInteger, nullable=False)


class InvalidAggregateEvent(AggregateEvent, InvalidEvent):
    __tablename__ = 'invalid_aggregate_event_v3'

    receveid_period_start = Column(Unicode)


class UnknownAggregateEvent(AggregateEvent, UnknownEvent):
    __tablename__ = 'unknown_aggregate_event_v3'

    receveid_period_start = Column(Unicode)


@dataclass
class RequestChannel:
    image_id: str
    site: Dict[str, str]
    dual_boot: bool
    live: bool


@dataclass
class RequestData:
    relative_timestamp: int
    absolute_timestamp: int
    singulars: Tuple[GLib.Variant, ...]
    aggregates: Tuple[GLib.Variant, ...]

    def asdict(self) -> Dict[str, Any]:
        return {
            'relative_timestamp': self.relative_timestamp,
            'absolute_timestamp': self.absolute_timestamp,
            'singulars': self.singulars,
            'aggregates': self.aggregates,
        }


def parse_record(record: bytes) -> Tuple[RequestData, RequestChannel]:
    # record is an array of bytes, the concatenation of:
    # - a datetime encoded on 8 bytes (a 64 bits integer timestamp in microseconds)
    # - the metrics request (a serialized GVariant)
    # timestamp_bytes, request_bytes = record[:8], record[8:]
    request_bytes = record[8:]

    # TODO: is this useful?
    # received_at_timestamp = int.from_bytes(timestamp_bytes, 'little')
    # received_at = datetime.fromtimestamp(received_at_timestamp / 1000000, tz=timezone.utc)

    payload = GLib.Variant.new_from_bytes(VARIANT_TYPE, GLib.Bytes.new(request_bytes), False)

    if not payload.is_normal_form():
        raise ValueError(
            f'Metric request is not in the expected format: {VARIANT_TYPE.dup_string()}')

    relative_timestamp = payload.get_child_value(0).get_int64()
    absolute_timestamp = payload.get_child_value(1).get_int64()
    image_id = payload.get_child_value(2).get_string()
    site = {key: value for (key, value) in payload.get_child_value(3).unpack().items() if value}
    flags = payload.get_child_value(4).get_byte()
    dual_boot, live = bool(flags & 1), bool(flags & 2)

    singulars = get_child_values(payload.get_child_value(5))
    aggregates = get_child_values(payload.get_child_value(6))

    channel = RequestChannel(image_id=image_id, site=site, dual_boot=dual_boot, live=live)
    request = RequestData(
        relative_timestamp, absolute_timestamp, singulars, aggregates
    )
    return request, channel


def new_singular_event(request: RequestData, channel: Channel, event_id: str,
                       event_variant: GLib.Variant, dbsession: DbSession
                       ) -> Optional[SingularEvent]:
    os_version = event_variant.get_child_value(1).get_string()
    event_relative_timestamp = event_variant.get_child_value(2).get_int64()
    payload = event_variant.get_child_value(3)

    event_date = get_event_datetime(
        request.absolute_timestamp, request.relative_timestamp, event_relative_timestamp
    )
    if event_id in SINGULAR_EVENT_MODELS:
        event_model = SINGULAR_EVENT_MODELS[event_id]
        try:
            # Mypy complains here, even though this should be fine:
            # https://github.com/dropbox/sqlalchemy-stubs/issues/97
            event = event_model(
                payload=payload,  # type: ignore
                os_version=os_version,
                occured_at=event_date, channel=channel, **request.asdict()
            )
        except Exception as e:
            if isinstance(e, EmptyPayloadError) and event_id in IGNORED_EMPTY_PAYLOAD_ERRORS:
                return None
            log.exception('An error occured while processing the event:')
            # Mypy complains here, even though this should be fine:
            # https://github.com/dropbox/sqlalchemy-stubs/issues/97
            event = InvalidSingularEvent(
                payload=payload,  # type: ignore
                event_id=event_id,
                os_version=os_version,
                occured_at=event_date,
                channel=channel,
                error=str(e),
                **request.asdict()
            )
    else:
        # Mypy complains here, even though this should be fine:
        # https://github.com/dropbox/sqlalchemy-stubs/issues/97
        event = UnknownSingularEvent(
            payload=payload,  # type: ignore
            event_id=event_id,
            os_version=os_version,
            occured_at=event_date,
            channel=channel,
            **request.asdict()
        )
    return event


def new_aggregate_event(request: RequestData, channel: Channel, event_id: str,
                        event_variant: GLib.Variant, dbsession: DbSession
                        ) -> Optional[AggregateEvent]:
    os_version = event_variant.get_child_value(1).get_string()
    period_start_str = event_variant.get_child_value(2).get_string()
    count = event_variant.get_child_value(3).get_uint32()
    payload = event_variant.get_child_value(4)

    if event_id in AGGREGATE_EVENT_MODELS:
        event_model = AGGREGATE_EVENT_MODELS[event_id]
        try:
            # Mypy complains here, even though this should be fine:
            # https://github.com/dropbox/sqlalchemy-stubs/issues/97
            event = event_model(
                payload=payload,  # type: ignore
                os_version=os_version,
                period_start=date.fromisoformat(period_start_str),
                count=count,
                channel=channel,
                **request.asdict()
            )
        except Exception as e:
            if isinstance(e, EmptyPayloadError) and event_id in IGNORED_EMPTY_PAYLOAD_ERRORS:
                return None
            log.exception('An error occured while processing the event:')
            # Mypy complains here, even though this should be fine:
            # https://github.com/dropbox/sqlalchemy-stubs/issues/97
            event = InvalidAggregateEvent(
                payload=payload,  # type: ignore
                event_id=event_id,
                os_version=os_version,
                period_start=date(1970, 1, 1),
                receveid_period_start=period_start_str,
                count=count,
                error=str(e),
                channel=channel,
                **request.asdict()
            )
    else:
        # Mypy complains here, even though this should be fine:
        # https://github.com/dropbox/sqlalchemy-stubs/issues/97
        event = UnknownAggregateEvent(
            payload=payload,  # type: ignore
            event_id=event_id,
            os_version=os_version,
            period_start=date(1970, 1, 1),
            receveid_period_start=period_start_str,
            channel=channel,
            count=count, **request.asdict())

    return event


def replay_invalid_singular_events(invalid_events: Query) -> None:
    for invalid in invalid_events:
        event_id = str(invalid.event_id)

        if event_id in IGNORED_EVENTS:
            invalid_events.session.delete(invalid)
            continue

        payload = GLib.Variant.new_from_bytes(GLib.VariantType('mv'),
                                              GLib.Bytes.new(invalid.payload_data),
                                              False)

        try:
            event_model = SINGULAR_EVENT_MODELS[event_id]

        except KeyError:
            # This event UUID is now unknown
            # Mypy complains here, even though this should be fine:
            # https://github.com/dropbox/sqlalchemy-stubs/issues/97
            event = UnknownSingularEvent(
                channel=invalid.channel,  # type: ignore
                occured_at=invalid.occured_at,
                event_id=event_id,
                payload=payload,
                os_version=invalid.os_version,
            )
            invalid_events.session.add(event)
            invalid_events.session.delete(invalid)
            continue

        # This event UUID was invalid and is a known event model, let's try and replay it

        try:
            # Mypy complains here, even though this should be fine:
            # https://github.com/dropbox/sqlalchemy-stubs/issues/97
            event = event_model(
                channel_id=invalid.channel_id,  # type: ignore
                occured_at=invalid.occured_at,
                os_version=invalid.os_version,
                payload=payload,
            )

        except Exception as e:
            if isinstance(e, EmptyPayloadError) and event_id in IGNORED_EMPTY_PAYLOAD_ERRORS:
                invalid_events.session.delete(invalid)
                continue

            # The event is still invalid
            continue

        invalid_events.session.add(event)
        invalid_events.session.delete(invalid)


def replay_invalid_aggregate_events(invalid_events: Query) -> None:  # pragma: no cover
    # TODO: Implement this when we actually have aggregate events
    raise NotImplementedError("Replaying invalid aggregate events is not yet implemented as we "
                              "don't have any")


def singular_event_is_known(event_id: str) -> bool:
    return (event_id in SINGULAR_EVENT_MODELS) or (event_id in IGNORED_EVENTS)


def replay_unknown_singular_events(unknown_events: Query) -> None:
    for unknown in unknown_events:
        event_id = str(unknown.event_id)

        if event_id in IGNORED_EVENTS:
            unknown_events.session.delete(unknown)
            continue

        event_model = SINGULAR_EVENT_MODELS[event_id]

        # This event UUID was unknown but is now known, let's process it
        payload = GLib.Variant.new_from_bytes(GLib.VariantType('mv'),
                                              GLib.Bytes.new(unknown.payload_data),
                                              False)

        try:
            # Mypy complains here, even though this should be fine:
            # https://github.com/dropbox/sqlalchemy-stubs/issues/97
            event = event_model(
                channel_id=unknown.channel_id,  # type: ignore
                occured_at=unknown.occured_at,
                os_version=unknown.os_version,
                payload=payload
            )

        except Exception as e:
            if isinstance(e, EmptyPayloadError) and event_id in IGNORED_EMPTY_PAYLOAD_ERRORS:
                unknown_events.session.delete(unknown)
                continue

            # The event is now invalid
            log.exception('An error occured while processing the event:')

            # Mypy complains here, even though this should be fine:
            # https://github.com/dropbox/sqlalchemy-stubs/issues/97
            event = InvalidSingularEvent(
                channel_id=unknown.channel_id,  # type: ignore
                occured_at=unknown.occured_at,
                os_version=unknown.os_version,
                event_id=event_id,
                payload=payload,
                error=str(e)
            )

        unknown_events.session.add(event)
        unknown_events.session.delete(unknown)


def aggregate_event_is_known(event_id: str) -> bool:
    return (event_id in AGGREGATE_EVENT_MODELS) or (event_id in IGNORED_EVENTS)


def replay_unknown_aggregate_events(unknown_events: Query) -> None:
    for unknown in unknown_events:
        event_id = str(unknown.event_id)

        if event_id in IGNORED_EVENTS:
            unknown_events.session.delete(unknown)
            continue

        # We don't have any aggregate event yet, therefore it can only be unknown

        # TODO: Implement this when we actually have aggregate events
        continue  # pragma: no cover
