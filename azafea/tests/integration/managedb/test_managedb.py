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

from sqlalchemy.exc import ProgrammingError

from azafea import cli
from azafea.model import Db

from .. import IntegrationTest


class TestManageDb(IntegrationTest):
    handler_module = 'azafea.tests.integration.managedb.handler_module'

    def test_initdb(self):
        from .handler_module import Event

        db = Db(self.config.postgresql.host, self.config.postgresql.port,
                self.config.postgresql.user, self.config.postgresql.password,
                self.config.postgresql.database)

        # Ensure there is no table at the start
        with pytest.raises(ProgrammingError) as exc_info:
            with db as dbsession:
                dbsession.query(Event).all()
        assert 'relation "managedb_event" does not exist' in str(exc_info.value)

        # Create the table
        args = cli.parse_args([
            '-c', self.config_file,
            'initdb',
        ])
        assert args.subcommand(args) == cli.ExitCode.OK

        # Ensure the table exists
        with db as dbsession:
            dbsession.query(Event).all()

        # Drop all tables to avoid side-effects between tests
        db.drop_all()

    def test_reinitdb(self):
        from .handler_module import Event

        db = Db(self.config.postgresql.host, self.config.postgresql.port,
                self.config.postgresql.user, self.config.postgresql.password,
                self.config.postgresql.database)

        # Ensure there is no table at the start
        with pytest.raises(ProgrammingError) as exc_info:
            with db as dbsession:
                dbsession.query(Event).all()
        assert 'relation "managedb_event" does not exist' in str(exc_info.value)

        # Create the table
        args = cli.parse_args([
            '-c', self.config_file,
            'initdb',
        ])
        assert args.subcommand(args) == cli.ExitCode.OK

        # Add an event
        with db as dbsession:
            dbsession.add(Event(name='hi!'))

        # Ensure the event was inserted
        with db as dbsession:
            event = dbsession.query(Event).one()
            assert event.name == 'hi!'

        # Drop the table
        args = cli.parse_args([
            '-c', self.config_file,
            'dropdb'
        ])
        assert args.subcommand(args) == cli.ExitCode.OK

        # Ensure the table was dropped
        with pytest.raises(ProgrammingError) as exc_info:
            with db as dbsession:
                dbsession.query(Event).all()
        assert 'relation "managedb_event" does not exist' in str(exc_info.value)

        # Recreate the table
        args = cli.parse_args([
            '-c', self.config_file,
            'initdb',
        ])
        assert args.subcommand(args) == cli.ExitCode.OK

        # Ensure the old events were cleared by the drop
        with db as dbsession:
            assert dbsession.query(Event).all() == []

        # Drop all tables to avoid side-effects between tests
        db.drop_all()
