# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from datetime import datetime, timedelta, timezone
from hashlib import sha512

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
