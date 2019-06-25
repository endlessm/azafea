# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# Azafea is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Azafea is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Azafea.  If not, see <http://www.gnu.org/licenses/>.


import pytest

from sqlalchemy.sql import text

from azafea import cli

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
        args = cli.parse_args([
            '-c', self.config_file,
            'initdb',
        ])
        assert args.subcommand(args) == cli.ExitCode.OK

        # Insert a True value
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

        # Drop all tables to avoid side-effects between tests
        self.db.drop_all()
