# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import pytest

from sqlalchemy.sql import text

from .. import IntegrationTest


class TestNullableBoolean(IntegrationTest):
    handler_module = 'azafea.tests.integration.nullableboolean.handler_module'

    @pytest.mark.parametrize('name, value', [
        pytest.param('true', True, id='true'),
        pytest.param('false', False, id='false'),
        pytest.param('unknown', None, id='unknown'),
    ])
    def test_nullableboolean(self, name, value):
        from .handler_module import Event

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Event)

        # Insert a value
        with self.db as dbsession:
            dbsession.add(Event(name=name, value=value))

        # Ensure the value is correct
        with self.db as dbsession:
            event = dbsession.query(Event).one()
            assert event.name == name
            assert event.value == value

            # Also Check the value in the DB, bypassing the ORM
            # Note: this only works because the param passed as name is what gets stored in the DB,
            # but that's just something done on purpose for this test
            result = dbsession.execute(text('SELECT value FROM nullableboolean_event'))
            assert result.rowcount == 1
            assert result.fetchone()[0] == name

    def test_query_filtered_on_none(self):
        from .handler_module import Event

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Event)

        # Insert a value
        with self.db as dbsession:
            dbsession.add(Event(name='hello', value=None))

        # Try filtering on the None value
        with self.db as dbsession:
            event = dbsession.query(Event).filter_by(value=None).one()
            assert event.name == 'hello'
