import os
import sys
import tempfile

import pytest

from redis import Redis

from sqlalchemy.exc import ProgrammingError

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
        for model in Base._decl_class_registry.values():
            if not isinstance(model, type) or not issubclass(model, Base):
                # Internal SQLAlchemy stuff
                continue

            with pytest.raises(ProgrammingError) as exc_info:
                with self.db as dbsession:
                    dbsession.query(model).all()

            assert f'relation "{model.__tablename__}" does not exist' in str(exc_info.value)

    def clear_queues(self):
        queues = self.redis.keys()

        if queues:
            self.redis.delete(*queues)

    def ensure_no_queues(self):
        for queue_name in self.config.queues:
            assert self.redis.llen(queue_name) == 0
            assert self.redis.llen(f'errors-{queue_name}') == 0

    def run_subcommand(self, *cmd):
        args = cli.parse_args([
            '-c', self.config_file,
            *cmd,
        ])

        return args.subcommand(args)

    def setup_method(self, method):
        # Create a config file for the test, with a common base and some per-test options
        _, config_file = tempfile.mkstemp()

        with open(config_file, 'w') as f:
            f.write(toml.dumps({
                'main': {
                    'verbose': True,
                    'number_of_workers': 2,
                },
                'postgresql': {
                    'database': 'azafea-tests',
                },
                'queues': {
                    method.__name__: {
                        'handler': self.handler_module,
                    },
                }
            }))

        self.config_file = config_file
        self.config = Config.from_file(self.config_file)

        self.db = Db(self.config.postgresql.host, self.config.postgresql.port,
                     self.config.postgresql.user, self.config.postgresql.password,
                     self.config.postgresql.database)

        self.redis = Redis(host=self.config.redis.host, port=self.config.redis.port,
                           password=self.config.redis.password)

        # Ensure we start with a clean slate
        self.ensure_no_queues()
        self.ensure_no_tables()

    def teardown_method(self):
        # Ensure we finish with a clean DB
        self.db.drop_all()
        self.ensure_no_tables()

        # Deregister the models and tables from SQLAlchemy
        Base._decl_class_registry.clear()
        Base.metadata.clear()

        # Deregister the handler modules so the next tests reimport them completely; not doing so
        # confuses SQLAlchemy, leading to the tables only being created for the first test. :(
        for queue_config in self.config.queues.values():
            sys.modules.pop(queue_config.handler.__module__)

        # Ensure we finish with clean a Redis
        self.clear_queues()
        self.ensure_no_queues()

        # And remove the configuration file
        os.unlink(self.config_file)
