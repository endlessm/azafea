# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from fnmatch import fnmatch
from pathlib import Path
from typing import Mapping
import sys

import pytest

import toml

from azafea.config import Config


def pytest_collection_modifyitems(items):
    for item in items:
        if fnmatch(item.nodeid, '*/tests*/integration/*'):
            item.add_marker(pytest.mark.integration)


class MockSqlAlchemySession:
    def __init__(self):
        self.open = True
        self.committed = False
        self.rolled_back = False
        self.is_active = True

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True
        self.is_active = False

    def close(self):
        self.open = False

    def connection(self):
        pass


@pytest.fixture()
def mock_sessionmaker():
    def maker(bind=None, class_=None):
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


@pytest.fixture()
def handler_with_migrations(tmp_path, monkeypatch):
    # Create a temporary handler package with an empty process method.
    handler_pkg = tmp_path / 'tmp_azafea_handler'
    handler_pkg.mkdir()
    handler_pkg_init = handler_pkg / '__init__.py'
    handler_pkg_init.write_text('def process(*args, **kwargs): pass', 'utf-8')

    # Create the handler migrations directory.
    migrations_dir = handler_pkg / 'migrations'
    migrations_dir.mkdir()

    # Make the handler package available and return its path.
    monkeypatch.syspath_prepend(tmp_path)
    yield handler_pkg

    # Remove the handler package if it's been imported.
    sys.modules.pop(handler_pkg.name, None)
