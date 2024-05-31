# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import logging
import multiprocessing
from pathlib import Path
import shutil
import sys
from typing import Optional

import pytest

from redis import Redis

import toml

from azafea import cli
from azafea.config import Config
from azafea.model import Base, Db

logger = logging.getLogger(__name__)

INTEGRATION_TEST_DIR = Path(__file__).parent


class IntegrationTest:
    test_path: Optional[str] = None
    handler_path: Path = INTEGRATION_TEST_DIR / 'stub_handler.py'
    handler_module: Optional[str] = None
    migrations_dir: Optional[str] = None

    def ensure_tables(self, *models):
        logger.info('Ensuring Postgres tables exist')
        for model in models:
            with self.db as dbsession:
                # Just check the query succeeds
                dbsession.query(model).count()

    def ensure_no_tables(self):
        logger.info('Ensuring no Postgres tables exist')
        with self.db._engine.connect() as connection:
            for table_name in Base.metadata.tables:
                if table_name == 'alembic_version':
                    continue
                assert not self.db._engine.dialect.has_table(connection, table_name)

    def clear_queues(self):
        logger.info('Clearing redis queues')
        queues = self.redis.keys()

        if queues:
            self.redis.delete(*queues)

    def ensure_no_queues(self):
        logger.info('Ensuring no redis queues exist')
        for queue_name in self.config.queues:
            assert self.redis.llen(queue_name) == 0
            assert self.redis.llen(f'errors-{queue_name}') == 0

    def run_azafea(self):
        proc = multiprocessing.Process(target=self.run_subcommand, args=('run', ))
        proc.start()
        proc.join()

    def run_subcommand(self, *cmd):
        cmdstr = '\n'.join(cmd)
        logger.info(f'Running azafea command {cmdstr}')
        cli.run_command('-c', str(self.config_file), *cmd)

    @pytest.fixture(autouse=True)
    def setup_teardown(self, request, tmp_path, monkeypatch):
        self.test_path = tmp_path

        if not self.handler_module:
            # Create a temporary handler package.
            handler_pkg = self.test_path / 'tmp_azafea_handler'
            handler_pkg_init = handler_pkg / '__init__.py'
            self.migrations_dir = handler_pkg / 'migrations'
            self.migrations_dir.mkdir(parents=True)

            shutil.copy(self.handler_path, handler_pkg_init)

            logger.info(f'Prepending {self.test_path} to sys.path')
            monkeypatch.syspath_prepend(self.test_path)
            self.handler_module = handler_pkg.name

        # Create a config file for the test, with a common base and some per-test options
        self.config_file = self.test_path / 'config'
        with self.config_file.open('w') as f:
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

        self.config = Config.from_file(str(self.config_file))

        self.db = Db(self.config.postgresql)
        self.redis = Redis(
            host=self.config.redis.host,
            port=self.config.redis.port,
            password=self.config.redis.password,
            ssl=self.config.redis.ssl,
        )

        # Ensure we start with a clean slate
        self.ensure_no_queues()
        self.ensure_no_tables()

        # Run the test function
        yield

        # Ensure we finish with a clean DB
        logger.info('Deleting all postgres tables')
        self.db.drop_all()
        self.ensure_no_tables()

        # Deregister the models, tables and events from SQLAlchemy
        logger.info('Clearing sqlalchemy metadata')
        Base._decl_class_registry.clear()
        Base.metadata.clear()
        Base.metadata.dispatch._clear()

        # Deregister the handler modules so the next tests reimport them completely; not doing so
        # confuses SQLAlchemy, leading to the tables only being created for the first test. :(
        modules_to_deregister = []

        for queue_config in self.config.queues.values():
            handler_root = queue_config.handler.rsplit('.', 1)[0]

            for module in sys.modules:
                if module == self.handler_module or module.startswith(handler_root):
                    modules_to_deregister.append(module)

        for module in modules_to_deregister:
            logger.info(f'Removing {module} from sys.modules')
            sys.modules.pop(module)

        # Ensure we finish with clean a Redis
        self.clear_queues()
        self.ensure_no_queues()

        self.db._engine.dispose()
