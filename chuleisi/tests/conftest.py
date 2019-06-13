from typing import Mapping

import pytest

import toml

from chuleisi.config import Config


class MockSqlAlchemySession:
    def __init__(self):
        self.open = True
        self.committed = False
        self.rolled_back = False

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def close(self):
        self.open = False


@pytest.fixture()
def mock_sessionmaker():
    def maker(bind=None):
        return MockSqlAlchemySession

    return maker


@pytest.fixture()
def make_config(tmp_path):
    config_file_path = tmp_path.joinpath('chuleisi.conf')

    def maker(d: Mapping) -> Config:
        with config_file_path.open('w') as f:
            toml.dump(d, f)

        return Config.from_file(str(config_file_path))

    return maker
