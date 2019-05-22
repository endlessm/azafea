from typing import Mapping

import pytest

import toml

from chuleisi.config import Config


@pytest.fixture()
def make_config(tmp_path):
    config_file_path = tmp_path.joinpath('chuleisi.conf')

    def maker(d: Mapping) -> Config:
        with config_file_path.open('w') as f:
            toml.dump(d, f)

        return Config.from_file(str(config_file_path))

    return maker
