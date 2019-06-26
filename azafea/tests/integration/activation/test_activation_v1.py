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
import multiprocessing
import os
from signal import SIGTERM
import time

from redis import Redis

from azafea import cli

from .. import IntegrationTest


class TestActivation(IntegrationTest):
    handler_module = 'azafea.event_processors.activation.v1'

    def test_activation_v1(self):
        from azafea.event_processors.activation.v1 import Activation

        redis = Redis(host=self.config.redis.host, port=self.config.redis.port,
                      password=self.config.redis.password)

        # Ensure Redis is empty
        assert redis.llen('test_activation_v1') == 0

        # Create the table
        args = cli.parse_args([
            '-c', self.config_file,
            'initdb',
        ])
        args.subcommand(args)

        # Run Azafea in the background
        args = cli.parse_args([
            '-c', self.config_file,
            'run',
        ])
        proc = multiprocessing.Process(target=args.subcommand, args=(args, ))
        proc.start()

        # Send an event to the Redis queue
        created_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        updated_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        redis.lpush('test_activation_v1', json.dumps({
            'image': 'image',
            'vendor': 'vendor',
            'product': 'product',
            'release': 'release',
            'created_at': created_at.strftime('%Y-%m-%d %H:%M:%S.%fZ'),
            'updated_at': updated_at.strftime('%Y-%m-%d %H:%M:%S.%fZ'),
        }))

        # Stop Azafea. Give the process a bit of time to register its signal handler and process the
        # event from the Redis queue
        time.sleep(0.2)
        os.kill(proc.pid, SIGTERM)

        proc.join()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            activation = dbsession.query(Activation).one()
            assert activation.image == 'image'
            assert activation.vendor == 'vendor'
            assert activation.product == 'product'
            assert activation.release == 'release'
            assert activation.created_at == created_at
            assert activation.updated_at == updated_at

        # Ensure Redis is empty
        assert redis.llen('test_activation_v1') == 0

    def test_activation_v1_valid_country(self):
        from azafea.event_processors.activation.v1 import Activation

        redis = Redis(host=self.config.redis.host, port=self.config.redis.port,
                      password=self.config.redis.password)

        # Ensure Redis is empty
        assert redis.llen('test_activation_v1_valid_country') == 0

        # Create the table
        args = cli.parse_args([
            '-c', self.config_file,
            'initdb',
        ])
        args.subcommand(args)

        # Run Azafea in the background
        args = cli.parse_args([
            '-c', self.config_file,
            'run',
        ])
        proc = multiprocessing.Process(target=args.subcommand, args=(args, ))
        proc.start()

        # Send an event to the Redis queue
        created_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        updated_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        redis.lpush('test_activation_v1_valid_country', json.dumps({
            'image': 'image',
            'vendor': 'vendor',
            'product': 'product',
            'release': 'release',
            'country': 'FRA',
            'created_at': created_at.strftime('%Y-%m-%d %H:%M:%S.%fZ'),
            'updated_at': updated_at.strftime('%Y-%m-%d %H:%M:%S.%fZ'),
        }))

        # Stop Azafea. Give the process a bit of time to register its signal handler and process the
        # event from the Redis queue
        time.sleep(0.2)
        os.kill(proc.pid, SIGTERM)

        proc.join()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            activation = dbsession.query(Activation).one()
            assert activation.image == 'image'
            assert activation.vendor == 'vendor'
            assert activation.product == 'product'
            assert activation.release == 'release'
            assert activation.country == 'FRA'
            assert activation.created_at == created_at
            assert activation.updated_at == updated_at

        # Ensure Redis is empty
        assert redis.llen('test_activation_v1_valid_country') == 0

    def test_activation_v1_empty_country(self):
        from azafea.event_processors.activation.v1 import Activation

        redis = Redis(host=self.config.redis.host, port=self.config.redis.port,
                      password=self.config.redis.password)

        # Ensure Redis is empty
        assert redis.llen('test_activation_v1_empty_country') == 0

        # Create the table
        args = cli.parse_args([
            '-c', self.config_file,
            'initdb',
        ])
        args.subcommand(args)

        # Run Azafea in the background
        args = cli.parse_args([
            '-c', self.config_file,
            'run',
        ])
        proc = multiprocessing.Process(target=args.subcommand, args=(args, ))
        proc.start()

        # Send an event to the Redis queue
        created_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        updated_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        redis.lpush('test_activation_v1_empty_country', json.dumps({
            'image': 'image',
            'vendor': 'vendor',
            'product': 'product',
            'release': 'release',
            'country': '',
            'created_at': created_at.strftime('%Y-%m-%d %H:%M:%S.%fZ'),
            'updated_at': updated_at.strftime('%Y-%m-%d %H:%M:%S.%fZ'),
        }))

        # Stop Azafea. Give the process a bit of time to register its signal handler and process the
        # event from the Redis queue
        time.sleep(0.2)
        os.kill(proc.pid, SIGTERM)

        proc.join()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            activation = dbsession.query(Activation).one()
            assert activation.image == 'image'
            assert activation.vendor == 'vendor'
            assert activation.product == 'product'
            assert activation.release == 'release'
            assert activation.country is None
            assert activation.created_at == created_at
            assert activation.updated_at == updated_at

        # Ensure Redis is empty
        assert redis.llen('test_activation_v1_empty_country') == 0

    def test_activation_v1_invalid_country(self):
        from azafea.event_processors.activation.v1 import Activation

        redis = Redis(host=self.config.redis.host, port=self.config.redis.port,
                      password=self.config.redis.password)

        # Ensure Redis is empty
        assert redis.llen('test_activation_v1_invalid_country') == 0

        # Create the table
        args = cli.parse_args([
            '-c', self.config_file,
            'initdb',
        ])
        args.subcommand(args)

        # Run Azafea in the background
        args = cli.parse_args([
            '-c', self.config_file,
            'run',
        ])
        proc = multiprocessing.Process(target=args.subcommand, args=(args, ))
        proc.start()

        # Send an event to the Redis queue
        created_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        updated_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        record = json.dumps({
            'image': 'image',
            'vendor': 'vendor',
            'product': 'product',
            'release': 'release',
            'country': 'FR',
            'created_at': created_at.strftime('%Y-%m-%d %H:%M:%S.%fZ'),
            'updated_at': updated_at.strftime('%Y-%m-%d %H:%M:%S.%fZ'),
        })
        redis.lpush('test_activation_v1_invalid_country', record)

        # Stop Azafea. Give the process a bit of time to register its signal handler and process the
        # event from the Redis queue
        time.sleep(0.2)
        os.kill(proc.pid, SIGTERM)

        proc.join()

        # Ensure the record was not inserted into the DB
        with self.db as dbsession:
            assert dbsession.query(Activation).count() == 0

        # Ensure Redis has the record back into the error queue
        assert redis.llen('test_activation_v1_invalid_country') == 0
        assert redis.llen('errors-test_activation_v1_invalid_country') == 1
        assert redis.rpop('errors-test_activation_v1_invalid_country').decode('utf-8') == record
