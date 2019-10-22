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

from azafea.tests.integration import IntegrationTest


class TestMetrics(IntegrationTest):
    handler_module = 'azafea.event_processors.metrics.v2_import'

    def test_request(self):
        from azafea.event_processors.metrics.request import Request

        # Create the table
        self.run_subcommand('initdb')
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
            assert request.serialized is None

    def test_duplicate_request(self):
        from azafea.event_processors.metrics.events._base import UnknownSingularEvent
        from azafea.event_processors.metrics.request import Request

        # Create the table
        self.run_subcommand('initdb')
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
            assert request.serialized is None

            # Ensure we deduplicated the request and the events it contains
            assert dbsession.query(UnknownSingularEvent).count() == 1
