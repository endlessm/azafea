from pathlib import Path
from typing import Mapping

import pytest

import toml

from azafea.config import Config


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
def make_config_file(tmp_path):
    config_file_path = tmp_path.joinpath('azafea.conf')

    def maker(d: Mapping) -> Path:
        with config_file_path.open('w') as f:
            toml.dump(d, f)

        return config_file_path

    return maker


@pytest.fixture()
def make_config(make_config_file):
    def maker(d: Mapping) -> Config:
        config_file_path = make_config_file(d)

        return Config.from_file(str(config_file_path))

    return maker
