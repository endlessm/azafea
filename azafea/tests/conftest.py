# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from pathlib import Path
from typing import Mapping

import pytest

import toml

from azafea.config import Config


def pytest_collection_modifyitems(items):
    for item in items:
        markers = [m for m in item.own_markers if m.name in ('flake8', 'mypy')]

        if markers:
            continue

        if item.nodeid.startswith('azafea/tests/integration/'):
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
