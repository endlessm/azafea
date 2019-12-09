# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import os

from alembic.config import Config as AlembicConfig
from alembic.util import coerce_resource_to_filename

from azafea.config import Config
from ..model import Base


def get_alembic_config(config: Config) -> AlembicConfig:
    config_path = coerce_resource_to_filename('azafea.migrations:alembic.ini')
    alembic_config = AlembicConfig(config_path)
    alembic_config.attributes['Base'] = Base

    migration_dirs = (
        get_queue_migrations_path(queue_config.handler)
        for queue_config in config.queues.values()
    )
    migration_dirs = (d for d in migration_dirs if os.path.exists(d))
    alembic_config.set_main_option('version_locations', ' '.join(migration_dirs))

    return alembic_config


def get_queue_migrations_path(queue_handler: str) -> str:
    return coerce_resource_to_filename(f'{queue_handler}:migrations')
