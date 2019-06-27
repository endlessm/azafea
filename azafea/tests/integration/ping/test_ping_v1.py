# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# Azafea is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Azafea is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Azafea.  If not, see <http://www.gnu.org/licenses/>.


from datetime import datetime, timezone
import json

from azafea import cli

from .. import IntegrationTest


class TestPing(IntegrationTest):
    handler_module = 'azafea.event_processors.ping.v1'

    def test_ping_v1(self):
        from azafea.event_processors.ping.v1 import PingConfiguration, Ping

        # Create the tables
        assert self.run_subcommand('initdb') == cli.ExitCode.OK
        self.ensure_tables(Ping, PingConfiguration)

        # Send an event to the Redis queue
        created_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        updated_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        self.redis.lpush('test_ping_v1', json.dumps({
            'image': 'image',
            'vendor': 'vendor',
            'product': 'product',
            'dualboot': True,
            'release': 'release',
            'count': 0,
            'created_at': created_at.strftime('%Y-%m-%d %H:%M:%S.%fZ'),
            'updated_at': updated_at.strftime('%Y-%m-%d %H:%M:%S.%fZ'),
        }))

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            config = dbsession.query(PingConfiguration).one()
            assert config.image == 'image'
            assert config.vendor == 'vendor'
            assert config.product == 'product'
            assert config.dualboot is True
            assert config.created_at == created_at
            assert config.updated_at == updated_at

            ping = dbsession.query(Ping).one()
            assert ping.release == 'release'
            assert ping.count == 0
            assert ping.created_at == created_at
            assert ping.updated_at == updated_at

    def test_ping_v1_valid_country(self):
        from azafea.event_processors.ping.v1 import PingConfiguration, Ping

        # Create the tables
        assert self.run_subcommand('initdb') == cli.ExitCode.OK
        self.ensure_tables(Ping, PingConfiguration)

        # Send an event to the Redis queue
        created_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        updated_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        self.redis.lpush('test_ping_v1_valid_country', json.dumps({
            'image': 'image',
            'vendor': 'vendor',
            'product': 'product',
            'dualboot': True,
            'release': 'release',
            'count': 0,
            'country': 'FRA',
            'created_at': created_at.strftime('%Y-%m-%d %H:%M:%S.%fZ'),
            'updated_at': updated_at.strftime('%Y-%m-%d %H:%M:%S.%fZ'),
        }))

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            config = dbsession.query(PingConfiguration).one()
            assert config.image == 'image'
            assert config.vendor == 'vendor'
            assert config.product == 'product'
            assert config.dualboot is True
            assert config.created_at == created_at
            assert config.updated_at == updated_at

            ping = dbsession.query(Ping).one()
            assert ping.release == 'release'
            assert ping.count == 0
            assert ping.country == 'FRA'
            assert ping.created_at == created_at
            assert ping.updated_at == updated_at

    def test_ping_v1_empty_country(self):
        from azafea.event_processors.ping.v1 import PingConfiguration, Ping

        # Create the tables
        assert self.run_subcommand('initdb') == cli.ExitCode.OK
        self.ensure_tables(Ping, PingConfiguration)

        # Send an event to the Redis queue
        created_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        updated_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        self.redis.lpush('test_ping_v1_empty_country', json.dumps({
            'image': 'image',
            'vendor': 'vendor',
            'product': 'product',
            'dualboot': True,
            'release': 'release',
            'count': 0,
            'country': '',
            'created_at': created_at.strftime('%Y-%m-%d %H:%M:%S.%fZ'),
            'updated_at': updated_at.strftime('%Y-%m-%d %H:%M:%S.%fZ'),
        }))

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            config = dbsession.query(PingConfiguration).one()
            assert config.image == 'image'
            assert config.vendor == 'vendor'
            assert config.product == 'product'
            assert config.dualboot is True
            assert config.created_at == created_at
            assert config.updated_at == updated_at

            ping = dbsession.query(Ping).one()
            assert ping.release == 'release'
            assert ping.count == 0
            assert ping.country is None
            assert ping.created_at == created_at
            assert ping.updated_at == updated_at

    def test_ping_v1_invalid_country(self):
        from azafea.event_processors.ping.v1 import PingConfiguration, Ping

        # Create the tables
        assert self.run_subcommand('initdb') == cli.ExitCode.OK
        self.ensure_tables(Ping, PingConfiguration)

        # Send an event to the Redis queue
        created_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        updated_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        record = json.dumps({
            'image': 'image',
            'vendor': 'vendor',
            'product': 'product',
            'dualboot': True,
            'release': 'release',
            'count': 0,
            'country': 'FR',
            'created_at': created_at.strftime('%Y-%m-%d %H:%M:%S.%fZ'),
            'updated_at': updated_at.strftime('%Y-%m-%d %H:%M:%S.%fZ'),
        })
        self.redis.lpush('test_ping_v1_invalid_country', record)

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was not inserted into the DB
        with self.db as dbsession:
            assert dbsession.query(Ping).count() == 0

        # Ensure Redis has the record back into the error queue
        assert self.redis.llen('test_ping_v1_invalid_country') == 0
        assert self.redis.llen('errors-test_ping_v1_invalid_country') == 1
        assert self.redis.rpop('errors-test_ping_v1_invalid_country').decode('utf-8') == record

    def test_ping_configuration_v1_dualboot_unicity(self):
        from azafea.event_processors.ping.v1 import PingConfiguration, Ping

        # Create the tables
        assert self.run_subcommand('initdb') == cli.ExitCode.OK
        self.ensure_tables(Ping, PingConfiguration)

        # Send events to the Redis queue
        created_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        updated_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        for i in range(10):
            self.redis.lpush('test_ping_configuration_v1_dualboot_unicity', json.dumps({
                'image': 'image',
                'vendor': 'vendor',
                'product': 'product',
                'dualboot': (True, False, None)[i % 3],
                'release': 'release',
                'count': 0,
                'created_at': created_at.strftime('%Y-%m-%d %H:%M:%S.%fZ'),
                'updated_at': updated_at.strftime('%Y-%m-%d %H:%M:%S.%fZ'),
            }))

        # Run Azafea so it processes the events
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            configs = dbsession.query(PingConfiguration)
            assert configs.count() == 3

            configs = configs.order_by(PingConfiguration.dualboot)

            for i, config in enumerate(configs):
                assert config.image == 'image'
                assert config.vendor == 'vendor'
                assert config.product == 'product'
                assert config.dualboot == (True, False, None)[i % 3]
                assert config.created_at == created_at
                assert config.updated_at == updated_at

            pings = dbsession.query(Ping)
            assert pings.count() == 10
