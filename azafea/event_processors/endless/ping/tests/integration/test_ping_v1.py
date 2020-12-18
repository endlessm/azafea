# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from datetime import datetime, timezone
import json

from azafea.tests.integration import IntegrationTest


class TestPing(IntegrationTest):
    handler_module = 'azafea.event_processors.endless.ping.v1'

    def test_ping_v1(self):
        from azafea.event_processors.endless.ping.v1.handler import PingConfiguration, Ping

        # Create the tables
        self.run_subcommand('initdb')
        self.ensure_tables(Ping, PingConfiguration)

        # Send an event to the Redis queue
        created_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        self.redis.lpush('test_ping_v1', json.dumps({
            'image': 'eos-eos3.7-amd64-amd64.190419-225606.base',
            'vendor': 'the vendor',
            'product': 'product',
            'dualboot': True,
            'release': 'release',
            'count': 0,
            'created_at': created_at.strftime('%Y-%m-%d %H:%M:%S.%fZ'),
        }))

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            config = dbsession.query(PingConfiguration).one()
            assert config.image == 'eos-eos3.7-amd64-amd64.190419-225606.base'
            assert config.vendor == 'the vendor'
            assert config.product == 'product'
            assert config.dualboot is True
            assert config.created_at == created_at
            assert config.image_product == 'eos'
            assert config.image_branch == 'eos3.7'
            assert config.image_arch == 'amd64'
            assert config.image_platform == 'amd64'
            assert config.image_timestamp == datetime(2019, 4, 19, 22, 56, 6, tzinfo=timezone.utc)
            assert config.image_personality == 'base'

            ping = dbsession.query(Ping).one()
            assert ping.release == 'release'
            assert ping.count == 0
            assert ping.created_at == created_at

    def test_ping_configuration_v1_dualboot_unicity(self):
        from azafea.event_processors.endless.ping.v1.handler import PingConfiguration, Ping

        # Create the tables
        self.run_subcommand('initdb')
        self.ensure_tables(Ping, PingConfiguration)

        # Send events to the Redis queue
        created_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        for i in range(10):
            self.redis.lpush('test_ping_configuration_v1_dualboot_unicity', json.dumps({
                'image': 'eos-eos3.7-amd64-amd64.190419-225606.base',
                'vendor': 'the vendor',
                'product': 'product',
                'dualboot': (True, False, None)[i % 3],
                'release': 'release',
                'count': 0,
                'created_at': created_at.strftime('%Y-%m-%d %H:%M:%S.%fZ'),
            }))

        # Run Azafea so it processes the events
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            configs = dbsession.query(PingConfiguration)
            assert configs.count() == 3

            configs = configs.order_by(PingConfiguration.dualboot)

            for i, config in enumerate(configs):
                assert config.image == 'eos-eos3.7-amd64-amd64.190419-225606.base'
                assert config.vendor == 'the vendor'
                assert config.product == 'product'
                assert config.dualboot == (True, False, None)[i % 3]
                assert config.created_at == created_at

            pings = dbsession.query(Ping)
            assert pings.count() == 10

    def test_ping_v1_unknown_image(self):
        from azafea.event_processors.endless.ping.v1.handler import PingConfiguration, Ping

        # Create the tables
        self.run_subcommand('initdb')
        self.ensure_tables(Ping, PingConfiguration)

        # Send an event to the Redis queue
        created_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        self.redis.lpush('test_ping_v1_unknown_image', json.dumps({
            'image': 'unknown',
            'vendor': 'the vendor',
            'product': 'product',
            'dualboot': True,
            'release': 'release',
            'count': 0,
            'created_at': created_at.strftime('%Y-%m-%d %H:%M:%S.%fZ'),
        }))

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            config = dbsession.query(PingConfiguration).one()
            assert config.image == 'unknown'
            assert config.vendor == 'the vendor'
            assert config.product == 'product'
            assert config.dualboot is True
            assert config.created_at == created_at
            assert config.image_product is None
            assert config.image_branch is None
            assert config.image_arch is None
            assert config.image_platform is None
            assert config.image_timestamp is None
            assert config.image_personality is None

            ping = dbsession.query(Ping).one()
            assert ping.release == 'release'
            assert ping.count == 0
            assert ping.created_at == created_at

    def test_ping_v1_invalid_image(self, capfd):
        from azafea.event_processors.endless.ping.v1.handler import PingConfiguration, Ping

        # Create the tables
        self.run_subcommand('initdb')
        self.ensure_tables(Ping, PingConfiguration)

        # Send an event to the Redis queue
        created_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        self.redis.lpush('test_ping_v1_invalid_image', json.dumps({
            'image': 'image',
            'vendor': 'the vendor',
            'product': 'product',
            'dualboot': True,
            'release': 'release',
            'count': 0,
            'created_at': created_at.strftime('%Y-%m-%d %H:%M:%S.%fZ'),
        }))

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            assert dbsession.query(PingConfiguration).count() == 0
            assert dbsession.query(Ping).count() == 0

        capture = capfd.readouterr()
        "Invalid image id 'image': Did not match the expected format" in capture.err
