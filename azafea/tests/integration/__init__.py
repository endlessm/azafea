# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import multiprocessing
import os
import sys
import tempfile

import pytest

from redis import Redis

import toml

from azafea import cli
from azafea.config import Config
from azafea.model import Base, Db


class IntegrationTest:
    def ensure_tables(self, *models):
        for model in models:
            with self.db as dbsession:
                # Just check the query succeeds
                dbsession.query(model).count()

    def ensure_no_tables(self):
        with self.db._engine.connect() as connection:
            for table_name in Base.metadata.tables:
                if table_name == 'alembic_version':
                    continue
                assert not self.db._engine.dialect.has_table(connection, table_name)

    def clear_queues(self):
        queues = self.redis.keys()

        if queues:
            self.redis.delete(*queues)

    def ensure_no_queues(self):
        for queue_name in self.config.queues:
            assert self.redis.llen(queue_name) == 0
            assert self.redis.llen(f'errors-{queue_name}') == 0

    def run_azafea(self):
        proc = multiprocessing.Process(target=self.run_subcommand, args=('run', ))
        proc.start()
        proc.join()

    def run_subcommand(self, *cmd):
        cli.run_command('-c', self.config_file, *cmd)

    @pytest.fixture(autouse=True)
    def setup_teardown(self, request):
        # Create a config file for the test, with a common base and some per-test options
        _, config_file = tempfile.mkstemp()

        with open(config_file, 'w') as f:
            f.write(toml.dumps({
                'main': {
                    'verbose': True,
                    'number_of_workers': 2,
                    'exit_on_empty_queues': True,
                },
                'postgresql': {
                    'database': 'azafea-tests',
                },
                'queues': {
                    request.node.name: {
                        'handler': self.handler_module,
                    },
                }
            }))

        self.config_file = config_file
        self.config = Config.from_file(self.config_file)

        self.db = Db(self.config.postgresql)
        self.redis = Redis(host=self.config.redis.host, port=self.config.redis.port,
                           password=self.config.redis.password)

        # Ensure we start with a clean slate
        self.ensure_no_queues()
        self.ensure_no_tables()

        # Run the test function
        yield

        # Ensure we finish with a clean DB
        self.db.drop_all()
        self.ensure_no_tables()

        # Deregister the models, tables and events from SQLAlchemy
        Base._decl_class_registry.clear()
        Base.metadata.clear()
        Base.metadata.dispatch._clear()

        # Deregister the handler modules so the next tests reimport them completely; not doing so
        # confuses SQLAlchemy, leading to the tables only being created for the first test. :(
        modules_to_deregister = []

        for queue_config in self.config.queues.values():
            handler_root = queue_config.handler.rsplit('.', 1)[0]

            for module in sys.modules:
                if module.startswith(handler_root):
                    modules_to_deregister.append(module)

        for module in modules_to_deregister:
            sys.modules.pop(module)

        # Ensure we finish with clean a Redis
        self.clear_queues()
        self.ensure_no_queues()

        # And remove the configuration file
        os.unlink(self.config_file)
