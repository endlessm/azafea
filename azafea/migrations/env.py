# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


# type: ignore


from alembic import context


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    config = context.config
    context.configure(connection=config.attributes['connection'],
                      target_metadata=config.attributes['Base'].metadata)

    with context.begin_transaction():
        context.run_migrations()


run_migrations_online()
