# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import os

import azafea
from azafea.migrations.utils import get_alembic_config, get_queue_migrations_path


def test_get_alembic_config(monkeypatch, handler_with_migrations, make_config):
    def mock_get_callable(module_name, callable_name):
        return lambda *args, **kwargs: None

    with monkeypatch.context() as m:
        m.setattr(azafea.config, 'get_callable', mock_get_callable)
        config = make_config({
            'queues': {
                'some-queue': {'handler': 'azafea'},
                'other-queue': {'handler': handler_with_migrations.name},
            },
        })

    alembic_config = get_alembic_config(config)

    assert alembic_config.get_main_option('version_locations') == ' '.join([
        os.path.join(os.getcwd(), 'azafea', 'migrations'),
        str(handler_with_migrations / 'migrations'),
    ])


def test_get_alembic_config_no_queue(handler_with_migrations, make_config):
    config = make_config({})
    alembic_config = get_alembic_config(config)

    assert alembic_config.get_main_option('version_locations') == ''


def test_get_queue_migrations_path():
    root = os.getcwd()

    path = get_queue_migrations_path('azafea')
    assert path == os.path.join(root, 'azafea/migrations')
