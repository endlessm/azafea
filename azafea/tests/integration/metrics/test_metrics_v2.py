# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from datetime import datetime, timedelta, timezone
from hashlib import sha512
from uuid import UUID

from gi.repository import GLib

from azafea import cli

from .. import IntegrationTest


class TestMetrics(IntegrationTest):
    handler_module = 'azafea.event_processors.metrics.v2'

    def test_request(self):
        from azafea.event_processors.metrics.request import Request

        # Create the table
        assert self.run_subcommand('initdb') == cli.ExitCode.OK
        self.ensure_tables(Request)

        # Build a request as it would have been sent to us
        now = datetime.now(tz=timezone.utc)
        machine_id = 'ffffffffffffffffffffffffffffffff'
        request = GLib.Variant(
            '(ixxaya(uayxmv)a(uayxxmv)a(uaya(xmv)))',
            (
                0,                                     # network send number
                2000000000,                            # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),     # request absolute timestamp
                bytes.fromhex(machine_id),
                [],                                    # singular events
                [],                                    # aggregate events
                []                                     # sequence events
            )
        )
        assert request.is_normal_form()
        request_body = request.get_data_as_bytes().get_data()

        received_at = now + timedelta(minutes=2)
        received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
        received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

        record = received_at_timestamp_bytes + request_body

        # Send the event request to the Redis queue
        self.redis.lpush('test_request', record)

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            request = dbsession.query(Request).one()

            assert request.send_number == 0
            assert request.machine_id == machine_id
            assert request.sha512 == sha512(request_body).hexdigest()
            assert request.received_at == received_at

    def test_duplicate_request(self):
        from azafea.event_processors.metrics.events._base import UnknownSingularEvent
        from azafea.event_processors.metrics.request import Request

        # Create the table
        assert self.run_subcommand('initdb') == cli.ExitCode.OK
        self.ensure_tables(Request)

        # Build a request as it would have been sent to us
        now = datetime.now(tz=timezone.utc)
        machine_id = 'ffffffffffffffffffffffffffffffff'
        request = GLib.Variant(
            '(ixxaya(uayxmv)a(uayxxmv)a(uaya(xmv)))',
            (
                0,                                     # network send number
                2000000000,                            # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),     # request absolute timestamp
                bytes.fromhex(machine_id),
                [                                      # singular events
                    (
                        1000,                          # user id
                        UUID('d3863909-8eff-43b6-9a33-ef7eda266195').bytes,
                        3000000000,                    # event relative timestamp (3 secs)
                        None,                          # empty payload
                    ),
                ],
                [],                                    # aggregate events
                []                                     # sequence events
            )
        )
        assert request.is_normal_form()
        request_body = request.get_data_as_bytes().get_data()

        received_at = now + timedelta(minutes=2)
        received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
        received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

        record = received_at_timestamp_bytes + request_body

        # Send the event request to the Redis queue, twice
        self.redis.lpush('test_duplicate_request', record)
        self.redis.lpush('test_duplicate_request', record)

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            request = dbsession.query(Request).one()

            assert request.send_number == 0
            assert request.machine_id == machine_id
            assert request.sha512 == sha512(request_body).hexdigest()
            assert request.received_at == received_at

            # Ensure we deduplicated the request and the events it contains
            assert dbsession.query(UnknownSingularEvent).count() == 1

    def test_invalid_request(self):
        from azafea.event_processors.metrics.request import Request

        # Create the table
        assert self.run_subcommand('initdb') == cli.ExitCode.OK
        self.ensure_tables(Request)

        # Build an invalid request (GVariant not in its normal form)
        request = GLib.Variant.new_from_bytes(
            GLib.VariantType('(ixxaya(uayxmv)a(uayxxmv)a(uaya(xmv)))'),
            GLib.Bytes.new(b'\x00'),
            False)
        assert not request.is_normal_form()
        request_body = request.get_data_as_bytes().get_data()

        now = datetime.now(tz=timezone.utc)
        received_at = now + timedelta(minutes=2)
        received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
        received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

        record = received_at_timestamp_bytes + request_body

        # Send the event request to the Redis queue
        self.redis.lpush('test_invalid_request', record)

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure no record was inserted into the DB
        with self.db as dbsession:
            assert dbsession.query(Request).count() == 0

        # Ensure the request was pushed back into Redis
        assert self.redis.llen('errors-test_invalid_request') == 1
        assert self.redis.rpop('errors-test_invalid_request') == record

    def test_singular_events(self):
        from azafea.event_processors.metrics.events import LiveUsbBooted, Uptime
        from azafea.event_processors.metrics.events._base import UnknownSingularEvent
        from azafea.event_processors.metrics.request import Request

        # Create the table
        assert self.run_subcommand('initdb') == cli.ExitCode.OK
        self.ensure_tables(Request, LiveUsbBooted, Uptime, UnknownSingularEvent)

        # Build a request as it would have been sent to us
        now = datetime.now(tz=timezone.utc)
        machine_id = 'ffffffffffffffffffffffffffffffff'
        user_id = 2000
        request = GLib.Variant(
            '(ixxaya(uayxmv)a(uayxxmv)a(uaya(xmv)))',
            (
                0,                                     # network send number
                2000000000,                            # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),     # request absolute timestamp
                bytes.fromhex(machine_id),
                [                                      # singular events
                    (
                        user_id,
                        UUID('56be0b38-e47b-4578-9599-00ff9bda54bb').bytes,
                        3000000000,                    # event relative timestamp (3 secs)
                        None,                          # empty payload
                    ),
                    (
                        user_id,
                        UUID('9af2cc74-d6dd-423f-ac44-600a6eee2d96').bytes,
                        4000000000,                    # event relative timestamp (4 secs)
                        # Pack uptime payload into 2 levels of variants, that's how we receive them
                        GLib.Variant('v', GLib.Variant('(xx)', (2, 1))),
                    ),
                ],
                [],                                    # aggregate events
                []                                     # sequence events
            )
        )
        assert request.is_normal_form()
        request_body = request.get_data_as_bytes().get_data()

        received_at = now + timedelta(minutes=2)
        received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
        received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

        record = received_at_timestamp_bytes + request_body

        # Send the event request to the Redis queue
        self.redis.lpush('test_singular_events', record)

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            request = dbsession.query(Request).one()
            assert request.send_number == 0
            assert request.machine_id == machine_id

            live_boot = dbsession.query(LiveUsbBooted).one()
            assert live_boot.request_id == request.id
            assert live_boot.user_id == user_id
            assert live_boot.occured_at == now - timedelta(seconds=2) + timedelta(seconds=3)

            uptime = dbsession.query(Uptime).one()
            assert uptime.request_id == request.id
            assert uptime.user_id == user_id
            assert uptime.occured_at == now - timedelta(seconds=2) + timedelta(seconds=4)
            assert uptime.accumulated_uptime == 2
            assert uptime.number_of_boots == 1

            assert dbsession.query(UnknownSingularEvent).count() == 0

    def test_no_payload_singular_event_with_payload(self, capfd):
        from azafea.event_processors.metrics.events import LiveUsbBooted
        from azafea.event_processors.metrics.request import Request

        # Create the table
        assert self.run_subcommand('initdb') == cli.ExitCode.OK
        self.ensure_tables(Request, LiveUsbBooted)

        # Build a request as it would have been sent to us
        now = datetime.now(tz=timezone.utc)
        machine_id = 'ffffffffffffffffffffffffffffffff'
        user_id = 2000
        request = GLib.Variant(
            '(ixxaya(uayxmv)a(uayxxmv)a(uaya(xmv)))',
            (
                0,                                     # network send number
                2000000000,                            # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),     # request absolute timestamp
                bytes.fromhex(machine_id),
                [                                      # singular events
                    (
                        user_id,
                        UUID('56be0b38-e47b-4578-9599-00ff9bda54bb').bytes,
                        3000000000,                    # event relative timestamp (3 secs)
                        GLib.Variant('x', 2),          # non-empty payload, expected empty
                    ),
                ],
                [],                                    # aggregate events
                []                                     # sequence events
            )
        )
        assert request.is_normal_form()
        request_body = request.get_data_as_bytes().get_data()

        received_at = now + timedelta(minutes=2)
        received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
        received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

        record = received_at_timestamp_bytes + request_body

        # Send the event request to the Redis queue
        self.redis.lpush('test_no_payload_singular_event_with_payload', record)

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            request = dbsession.query(Request).one()
            assert request.send_number == 0
            assert request.machine_id == machine_id

            live_boot = dbsession.query(LiveUsbBooted).one()
            assert live_boot.request_id == request.id
            assert live_boot.user_id == user_id
            assert live_boot.occured_at == now - timedelta(seconds=2) + timedelta(seconds=3)

        capture = capfd.readouterr()
        assert ('Metric event 56be0b38-e47b-4578-9599-00ff9bda54bb takes no payload, but got '
                '<int64 2>') in capture.err

    def test_unknown_singular_events(self):
        from azafea.event_processors.metrics.events._base import UnknownSingularEvent
        from azafea.event_processors.metrics.request import Request

        # Create the table
        assert self.run_subcommand('initdb') == cli.ExitCode.OK
        self.ensure_tables(Request, UnknownSingularEvent)

        # Build a request as it would have been sent to us
        now = datetime.now(tz=timezone.utc)
        machine_id = 'ffffffffffffffffffffffffffffffff'
        user_id = 2000
        event_id = UUID('d3863909-8eff-43b6-9a33-ef7eda266195')
        request = GLib.Variant(
            '(ixxaya(uayxmv)a(uayxxmv)a(uaya(xmv)))',
            (
                0,                                     # network send number
                2000000000,                            # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),     # request absolute timestamp
                bytes.fromhex(machine_id),
                [                                      # singular events
                    (
                        user_id,
                        event_id.bytes,
                        3000000000,                    # event relative timestamp (3 secs)
                        None,                          # empty payload
                    ),
                    (
                        user_id,
                        event_id.bytes,
                        4000000000,                    # event relative timestamp (4 secs)
                        GLib.Variant('(xx)', (1, 2)),  # Non empty payload
                    ),
                ],
                [],                                    # aggregate events
                []                                     # sequence events
            )
        )
        assert request.is_normal_form()
        request_body = request.get_data_as_bytes().get_data()

        received_at = now + timedelta(minutes=2)
        received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
        received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

        record = received_at_timestamp_bytes + request_body

        # Send the event request to the Redis queue
        self.redis.lpush('test_unknown_singular_events', record)

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            request = dbsession.query(Request).one()
            assert request.send_number == 0
            assert request.machine_id == machine_id

            events = dbsession.query(UnknownSingularEvent).order_by(UnknownSingularEvent.occured_at)
            assert events.count() == 2

            events = events.all()

            event = events[0]
            assert event.request_id == request.id
            assert event.user_id == user_id
            assert event.occured_at == now - timedelta(seconds=2) + timedelta(seconds=3)
            assert event.event_id == event_id
            assert event.payload_data == b''

            event = events[1]
            assert event.request_id == request.id
            assert event.user_id == user_id
            assert event.occured_at == now - timedelta(seconds=2) + timedelta(seconds=4)
            assert event.event_id == event_id
            assert GLib.Variant.new_from_bytes(GLib.VariantType('mv'),
                                               GLib.Bytes.new(event.payload_data),
                                               False).unpack() == (1, 2)

    def test_invalid_singular_event_payload(self, capfd):
        from azafea.event_processors.metrics.events import Uptime
        from azafea.event_processors.metrics.events._base import InvalidSingularEvent
        from azafea.event_processors.metrics.request import Request

        # Create the table
        assert self.run_subcommand('initdb') == cli.ExitCode.OK
        self.ensure_tables(Request, Uptime, InvalidSingularEvent)

        # Build a request as it would have been sent to us
        now = datetime.now(tz=timezone.utc)
        machine_id = 'ffffffffffffffffffffffffffffffff'
        user_id = 2000
        event_id = UUID('9af2cc74-d6dd-423f-ac44-600a6eee2d96')
        request = GLib.Variant(
            '(ixxaya(uayxmv)a(uayxxmv)a(uaya(xmv)))',
            (
                0,                                     # network send number
                2000000000,                            # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),     # request absolute timestamp
                bytes.fromhex(machine_id),
                [                                      # singular events
                    (
                        user_id,
                        event_id.bytes,
                        3000000000,                    # event relative timestamp (3 secs)
                        None,                          # empty payload, expected '(xx)'
                    ),
                    (
                        user_id,
                        event_id.bytes,
                        4000000000,                    # event relative timestamp (3 secs)
                        GLib.Variant('s', 'Up!'),      # 's' payload, expected '(xx)'
                    ),
                ],
                [],                                    # aggregate events
                []                                     # sequence events
            )
        )
        assert request.is_normal_form()
        request_body = request.get_data_as_bytes().get_data()

        received_at = now + timedelta(minutes=2)
        received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
        received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

        record = received_at_timestamp_bytes + request_body

        # Send the event request to the Redis queue
        self.redis.lpush('test_invalid_singular_event_payload', record)

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            request = dbsession.query(Request).one()
            assert request.send_number == 0
            assert request.machine_id == machine_id

            assert dbsession.query(Uptime).count() == 0

            events = dbsession.query(InvalidSingularEvent).order_by(InvalidSingularEvent.occured_at)
            assert events.count() == 2

            events = events.all()

            event = events[0]
            assert event.request_id == request.id
            assert event.user_id == user_id
            assert event.occured_at == now - timedelta(seconds=2) + timedelta(seconds=3)
            assert event.event_id == event_id
            assert event.payload_data == b''
            assert event.error == (
                'Metric event 9af2cc74-d6dd-423f-ac44-600a6eee2d96 needs a (xx) payload, '
                'but got none')

            event = events[1]
            assert event.request_id == request.id
            assert event.user_id == user_id
            assert event.occured_at == now - timedelta(seconds=2) + timedelta(seconds=4)
            assert event.event_id == event_id
            assert GLib.Variant.new_from_bytes(GLib.VariantType('mv'),
                                               GLib.Bytes.new(event.payload_data),
                                               False).unpack() == 'Up!'
            assert event.error == (
                'Metric event 9af2cc74-d6dd-423f-ac44-600a6eee2d96 needs a (xx) payload, '
                "but got 'Up!' (s)")

        capture = capfd.readouterr()
        assert 'An error occured while processing the event:' in capture.err
        assert ('ValueError: Metric event 9af2cc74-d6dd-423f-ac44-600a6eee2d96 needs a (xx) '
                "payload, but got 'Up!' (s)") in capture.err

    def test_unknown_aggregate_events(self):
        from azafea.event_processors.metrics.events._base import UnknownAggregateEvent
        from azafea.event_processors.metrics.request import Request

        # Create the table
        assert self.run_subcommand('initdb') == cli.ExitCode.OK
        self.ensure_tables(Request, UnknownAggregateEvent)

        # Build a request as it would have been sent to us
        now = datetime.now(tz=timezone.utc)
        machine_id = 'ffffffffffffffffffffffffffffffff'
        user_id = 2000
        event_id = UUID('d3863909-8eff-43b6-9a33-ef7eda266195')
        request = GLib.Variant(
            '(ixxaya(uayxmv)a(uayxxmv)a(uaya(xmv)))',
            (
                0,                                     # network send number
                2000000000,                            # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),     # request absolute timestamp
                bytes.fromhex(machine_id),
                [],                                    # singular events
                [                                      # aggregate events
                    (
                        user_id,
                        event_id.bytes,
                        0,                             # count
                        3000000000,                    # event relative timestamp (3 secs)
                        None,                          # empty payload
                    ),
                    (
                        user_id,
                        event_id.bytes,
                        10,                            # count
                        4000000000,                    # event relative timestamp (4 secs)
                        GLib.Variant('(xx)', (1, 2)),  # Non empty payload
                    ),
                ],
                []                                     # sequence events
            )
        )
        assert request.is_normal_form()
        request_body = request.get_data_as_bytes().get_data()

        received_at = now + timedelta(minutes=2)
        received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
        received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

        record = received_at_timestamp_bytes + request_body

        # Send the event request to the Redis queue
        self.redis.lpush('test_unknown_aggregate_events', record)

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            request = dbsession.query(Request).one()
            assert request.send_number == 0
            assert request.machine_id == machine_id

            events = dbsession.query(UnknownAggregateEvent) \
                              .order_by(UnknownAggregateEvent.occured_at)
            assert events.count() == 2

            events = events.all()

            event = events[0]
            assert event.request_id == request.id
            assert event.user_id == user_id
            assert event.occured_at == now - timedelta(seconds=2) + timedelta(seconds=3)
            assert event.count == 0
            assert event.event_id == event_id
            assert event.payload_data == b''

            event = events[1]
            assert event.request_id == request.id
            assert event.user_id == user_id
            assert event.occured_at == now - timedelta(seconds=2) + timedelta(seconds=4)
            assert event.count == 10
            assert event.event_id == event_id
            assert GLib.Variant.new_from_bytes(GLib.VariantType('mv'),
                                               GLib.Bytes.new(event.payload_data),
                                               False).unpack() == (1, 2)

    def test_sequence_events(self):
        from azafea.event_processors.metrics.events import ShellAppIsOpen
        from azafea.event_processors.metrics.request import Request

        # Create the table
        assert self.run_subcommand('initdb') == cli.ExitCode.OK
        self.ensure_tables(Request, ShellAppIsOpen)

        # Build a request as it would have been sent to us
        now = datetime.now(tz=timezone.utc)
        machine_id = 'ffffffffffffffffffffffffffffffff'
        user_id = 2000
        event_id = UUID('b5e11a3d-13f8-4219-84fd-c9ba0bf3d1f0')
        request = GLib.Variant(
            '(ixxaya(uayxmv)a(uayxxmv)a(uaya(xmv)))',
            (
                0,                                  # network send number
                2000000000,                         # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),  # request absolute timestamp
                bytes.fromhex(machine_id),
                [],                                 # singular events
                [],                                 # aggregate events
                [                                   # sequence events
                    (
                        user_id,
                        event_id.bytes,
                        [                           # events in the sequence
                            (
                                3000000000,         # event relative timestamp (3 secs)
                                GLib.Variant('s',   # app id
                                             'org.gnome.Podcasts'),
                            ),
                            (
                                120000000000,       # event relative timestamp (2 mins)
                                None,               # no payload on stop event
                            ),
                        ]
                    ),
                    (
                        user_id,
                        event_id.bytes,
                        [                           # events in the sequence
                            (
                                4000000000,         # event relative timestamp (4 secs)
                                GLib.Variant('s',   # app id
                                             'org.gnome.Fractal'),
                            ),
                            (
                                3600000000000,      # event relative timestamp (1 hour)
                                None,               # no payload on stop event
                            ),
                        ]
                    ),
                ]
            )
        )
        assert request.is_normal_form()
        request_body = request.get_data_as_bytes().get_data()

        received_at = now + timedelta(minutes=2)
        received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
        received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

        record = received_at_timestamp_bytes + request_body

        # Send the event request to the Redis queue
        self.redis.lpush('test_sequence_events', record)

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            request = dbsession.query(Request).one()
            assert request.send_number == 0
            assert request.machine_id == machine_id

            events = dbsession.query(ShellAppIsOpen).order_by(ShellAppIsOpen.started_at)
            assert events.count() == 2

            events = events.all()

            podcasts = events[0]
            assert podcasts.request_id == request.id
            assert podcasts.user_id == user_id
            assert podcasts.started_at == now - timedelta(seconds=2) + timedelta(seconds=3)
            assert podcasts.stopped_at == now - timedelta(seconds=2) + timedelta(minutes=2)
            assert podcasts.app_id == 'org.gnome.Podcasts'

            fractal = events[1]
            assert fractal.request_id == request.id
            assert fractal.user_id == user_id
            assert fractal.started_at == now - timedelta(seconds=2) + timedelta(seconds=4)
            assert fractal.stopped_at == now - timedelta(seconds=2) + timedelta(hours=1)
            assert fractal.app_id == 'org.gnome.Fractal'

    def test_unknown_sequence(self):
        from azafea.event_processors.metrics.events._base import UnknownSequence
        from azafea.event_processors.metrics.request import Request

        # Create the table
        assert self.run_subcommand('initdb') == cli.ExitCode.OK
        self.ensure_tables(Request, UnknownSequence)

        # Build a request as it would have been sent to us
        now = datetime.now(tz=timezone.utc)
        machine_id = 'ffffffffffffffffffffffffffffffff'
        user_id = 2000
        event_id = UUID('d3863909-8eff-43b6-9a33-ef7eda266195')
        request = GLib.Variant(
            '(ixxaya(uayxmv)a(uayxxmv)a(uaya(xmv)))',
            (
                0,                                         # network send number
                2000000000,                                # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),         # request absolute timestamp
                bytes.fromhex(machine_id),
                [],                                        # singular events
                [],                                        # aggregate events
                [                                          # sequence events
                    (
                        user_id,
                        event_id.bytes,
                        [                                  # events in the sequence
                            (
                                3000000000,                # event relative timestamp (3 secs)
                                GLib.Variant('s', 'foo'),  # app id
                            ),
                            (
                                60000000000,               # event relative timestamp (1 min)
                                None,                      # no payload on progress event
                            ),
                            (
                                120000000000,              # event relative timestamp (2 mins)
                                None,                      # no payload on progress event
                            ),
                            (
                                180000000000,              # event relative timestamp (3 mins)
                                None,                      # no payload on stop event
                            ),
                        ]
                    ),
                ]
            )
        )
        assert request.is_normal_form()
        request_body = request.get_data_as_bytes().get_data()

        received_at = now + timedelta(minutes=2)
        received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
        received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

        record = received_at_timestamp_bytes + request_body

        # Send the event request to the Redis queue
        self.redis.lpush('test_unknown_sequence', record)

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            request = dbsession.query(Request).one()
            assert request.send_number == 0
            assert request.machine_id == machine_id

            sequence = dbsession.query(UnknownSequence).one()
            assert sequence.request_id == request.id
            assert sequence.user_id == user_id
            assert GLib.Variant.new_from_bytes(GLib.VariantType('a(xmv)'),
                                               GLib.Bytes.new(sequence.payload_data),
                                               False).unpack() == [(3000000000, 'foo'),
                                                                   (60000000000, None),
                                                                   (120000000000, None),
                                                                   (180000000000, None)]

    def test_invalid_sequence(self, capfd):
        from azafea.event_processors.metrics.events._base import InvalidSequence
        from azafea.event_processors.metrics.request import Request

        # Create the table
        assert self.run_subcommand('initdb') == cli.ExitCode.OK
        self.ensure_tables(Request, InvalidSequence)

        # Build a request as it would have been sent to us
        now = datetime.now(tz=timezone.utc)
        machine_id = 'ffffffffffffffffffffffffffffffff'
        user_id = 2000
        event_id = UUID('b5e11a3d-13f8-4219-84fd-c9ba0bf3d1f0')
        request = GLib.Variant(
            '(ixxaya(uayxmv)a(uayxxmv)a(uaya(xmv)))',
            (
                0,                                         # network send number
                2000000000,                                # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),         # request absolute timestamp
                bytes.fromhex(machine_id),
                [],                                        # singular events
                [],                                        # aggregate events
                [                                          # sequence events
                    (
                        user_id,
                        event_id.bytes,
                        [                                  # INVALID: a single event in the sequence
                            (
                                3000000000,                # event relative timestamp (3 secs)
                                GLib.Variant('s', 'foo'),  # app id
                            )
                        ]
                    ),
                    (
                        user_id,
                        event_id.bytes,
                        [                                  # events in the sequence
                            (
                                3000000000,                # event relative timestamp (3 secs)
                                GLib.Variant('u', 42),     # INVALID: Should be an app id ('s')
                            ),
                            (
                                120000000000,              # event relative timestamp (2 mins)
                                None,                      # no payload on stop event
                            ),
                        ]
                    ),
                ]
            )
        )

        assert request.is_normal_form()
        request_body = request.get_data_as_bytes().get_data()

        received_at = now + timedelta(minutes=2)
        received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
        received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

        record = received_at_timestamp_bytes + request_body

        # Send the event request to the Redis queue
        self.redis.lpush('test_invalid_sequence', record)

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            request = dbsession.query(Request).one()
            assert request.send_number == 0
            assert request.machine_id == machine_id

            sequences = dbsession.query(InvalidSequence).order_by(InvalidSequence.event_id)
            assert sequences.count() == 2

            sequences = sequences.all()

            sequence = sequences[0]
            assert sequence.request_id == request.id
            assert sequence.user_id == user_id
            assert GLib.Variant.new_from_bytes(GLib.VariantType('a(xmv)'),
                                               GLib.Bytes.new(sequence.payload_data),
                                               False).unpack() == [(3000000000, 'foo')]

            sequence = sequences[1]
            assert sequence.request_id == request.id
            assert sequence.user_id == user_id
            assert GLib.Variant.new_from_bytes(GLib.VariantType('a(xmv)'),
                                               GLib.Bytes.new(sequence.payload_data),
                                               False).unpack() == [(3000000000, 42),
                                                                   (120000000000, None)]
            assert sequence.error == (
                'Metric event b5e11a3d-13f8-4219-84fd-c9ba0bf3d1f0 needs a s payload, '
                "but got uint32 42 (u)")

        capture = capfd.readouterr()
        assert 'An error occured while processing the sequence:' in capture.err
        assert ('ValueError: Metric event b5e11a3d-13f8-4219-84fd-c9ba0bf3d1f0 needs a s '
                "payload, but got uint32 42 (u)") in capture.err
