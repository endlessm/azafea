import os
import tempfile

import toml

from azafea.config import Config
from azafea.model import Db


class IntegrationTest:
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

    def teardown_method(self):
        os.unlink(self.config_file)
