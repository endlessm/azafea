# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from datetime import datetime, timezone
import json

from azafea import cli

from .. import IntegrationTest


class TestActivation(IntegrationTest):
    handler_module = 'azafea.event_processors.activation.v1'

    def test_activation_v1(self):
        from azafea.event_processors.activation.v1 import Activation

        # Create the table
        assert self.run_subcommand('initdb') == cli.ExitCode.OK
        self.ensure_tables(Activation)

        # Send an event to the Redis queue
        created_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        self.redis.lpush('test_activation_v1', json.dumps({
            'image': 'image',
            'vendor': 'vendor',
            'product': 'product',
            'release': 'release',
            'created_at': created_at.strftime('%Y-%m-%d %H:%M:%S.%fZ'),
        }))

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            activation = dbsession.query(Activation).one()
            assert activation.image == 'image'
            assert activation.vendor == 'vendor'
            assert activation.product == 'product'
            assert activation.release == 'release'
            assert activation.created_at == created_at

    def test_activation_v1_valid_country(self):
        from azafea.event_processors.activation.v1 import Activation

        # Create the table
        assert self.run_subcommand('initdb') == cli.ExitCode.OK
        self.ensure_tables(Activation)

        # Send an event to the Redis queue
        created_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        self.redis.lpush('test_activation_v1_valid_country', json.dumps({
            'image': 'image',
            'vendor': 'vendor',
            'product': 'product',
            'release': 'release',
            'country': 'FRA',
            'created_at': created_at.strftime('%Y-%m-%d %H:%M:%S.%fZ'),
        }))

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            activation = dbsession.query(Activation).one()
            assert activation.image == 'image'
            assert activation.vendor == 'vendor'
            assert activation.product == 'product'
            assert activation.release == 'release'
            assert activation.country == 'FRA'
            assert activation.created_at == created_at

    def test_activation_v1_empty_country(self):
        from azafea.event_processors.activation.v1 import Activation

        # Create the table
        assert self.run_subcommand('initdb') == cli.ExitCode.OK
        self.ensure_tables(Activation)

        # Send an event to the Redis queue
        created_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        self.redis.lpush('test_activation_v1_empty_country', json.dumps({
            'image': 'image',
            'vendor': 'vendor',
            'product': 'product',
            'release': 'release',
            'country': '',
            'created_at': created_at.strftime('%Y-%m-%d %H:%M:%S.%fZ'),
        }))

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            activation = dbsession.query(Activation).one()
            assert activation.image == 'image'
            assert activation.vendor == 'vendor'
            assert activation.product == 'product'
            assert activation.release == 'release'
            assert activation.country is None
            assert activation.created_at == created_at

    def test_activation_v1_invalid_country(self):
        from azafea.event_processors.activation.v1 import Activation

        # Create the table
        assert self.run_subcommand('initdb') == cli.ExitCode.OK
        self.ensure_tables(Activation)

        # Send an event to the Redis queue
        created_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        record = json.dumps({
            'image': 'image',
            'vendor': 'vendor',
            'product': 'product',
            'release': 'release',
            'country': 'FR',
            'created_at': created_at.strftime('%Y-%m-%d %H:%M:%S.%fZ'),
        })
        self.redis.lpush('test_activation_v1_invalid_country', record)

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was not inserted into the DB
        with self.db as dbsession:
            assert dbsession.query(Activation).count() == 0

        # Ensure Redis has the record back into the error queue
        assert self.redis.llen('test_activation_v1_invalid_country') == 0
        assert self.redis.llen('errors-test_activation_v1_invalid_country') == 1
        assert self.redis.rpop('errors-test_activation_v1_invalid_country').decode('utf-8') \
            == record
