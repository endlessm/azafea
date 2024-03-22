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


class TestActivation(IntegrationTest):
    handler_module = 'azafea.event_processors.endless.activation.v1'

    def test_activation_v1(self):
        from azafea.event_processors.endless.activation.v1.handler import Activation

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Activation)

        # Send an event to the Redis queue
        created_at = datetime.now(tz=timezone.utc)
        self.redis.lpush('test_activation_v1', json.dumps({
            'image': 'eos-eos3.7-amd64-amd64.190419-225606.base',
            'vendor': 'the vendor',
            'product': 'product',
            'release': 'release',
            'country': 'FR',
            'created_at': created_at.strftime('%Y-%m-%d %H:%M:%S.%fZ'),
        }))

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            activation = dbsession.query(Activation).one()
            assert activation.image == 'eos-eos3.7-amd64-amd64.190419-225606.base'
            assert activation.vendor == 'the vendor'
            assert activation.product == 'product'
            assert activation.release == 'release'
            assert activation.country == 'FR'
            assert activation.created_at == created_at
            assert activation.image_product == 'eos'
            assert activation.image_branch == 'eos3.7'
            assert activation.image_arch == 'amd64'
            assert activation.image_platform == 'amd64'
            assert activation.image_timestamp == datetime(2019, 4, 19, 22, 56, 6,
                                                          tzinfo=timezone.utc)
            assert activation.image_personality == 'base'

    def test_activation_v1_unknown_image(self):
        from azafea.event_processors.endless.activation.v1.handler import Activation

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Activation)

        # Send an event to the Redis queue
        created_at = datetime.now(tz=timezone.utc)
        self.redis.lpush('test_activation_v1_unknown_image', json.dumps({
            'image': 'unknown',
            'vendor': 'the vendor',
            'product': 'product',
            'release': 'release',
            'country': 'FR',
            'created_at': created_at.strftime('%Y-%m-%d %H:%M:%S.%fZ'),
        }))

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            activation = dbsession.query(Activation).one()
            assert activation.image == 'unknown'
            assert activation.vendor == 'the vendor'
            assert activation.product == 'product'
            assert activation.release == 'release'
            assert activation.country == 'FR'
            assert activation.created_at == created_at
            assert activation.image_product is None
            assert activation.image_branch is None
            assert activation.image_arch is None
            assert activation.image_platform is None
            assert activation.image_timestamp is None
            assert activation.image_personality is None

    def test_activation_v1_invalid_image(self, capfd):
        from azafea.event_processors.endless.activation.v1.handler import Activation

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Activation)

        # Send an event to the Redis queue
        created_at = datetime.now(tz=timezone.utc)
        self.redis.lpush('test_activation_v1_invalid_image', json.dumps({
            'image': 'image',
            'vendor': 'the vendor',
            'product': 'product',
            'release': 'release',
            'country': 'FR',
            'created_at': created_at.strftime('%Y-%m-%d %H:%M:%S.%fZ'),
        }))

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was not inserted into the DB
        with self.db as dbsession:
            assert dbsession.query(Activation).count() == 0

        capture = capfd.readouterr()
        assert "Invalid image id 'image': Did not match the expected format" in capture.err
