import os
import tempfile

import pytest

from sqlalchemy.exc import ProgrammingError

import toml

from azafea.config import Config
from azafea.model import Base, Db


class IntegrationTest:
    def ensure_no_tables(self):
        for model in Base._decl_class_registry.values():
            if not isinstance(model, type) or not issubclass(model, Base):
                # Internal SQLAlchemy stuff
                continue

            with pytest.raises(ProgrammingError) as exc_info:
                with self.db as dbsession:
                    dbsession.query(model).all()

            assert f'relation "{model.__tablename__}" does not exist' in str(exc_info.value)

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

        # Ensure we start with a clean DB
        self.ensure_no_tables()

    def teardown_method(self):
        os.unlink(self.config_file)
