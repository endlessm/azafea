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
from azafea.config import Config
from azafea.model import Db


class TestManageDb:
    def test_initdb(self, make_config_file):
        from .handler_module import Event

        config_file = make_config_file({
            'main': {'verbose': True},
            'postgresql': {'database': 'azafea-tests'},
            'queues': {'event': {'handler': 'azafea.tests.integration.managedb.handler_module'}},
        })
        config = Config.from_file(str(config_file))
        db = Db(config.postgresql.host, config.postgresql.port, config.postgresql.user,
                config.postgresql.password, config.postgresql.database)

        # Ensure there is no table at the start
        with pytest.raises(ProgrammingError) as exc_info:
            with db as dbsession:
                dbsession.query(Event).all()
        assert 'relation "managedb_event" does not exist' in str(exc_info.value)

        # Create the table
        args = cli.parse_args([
            '-c', str(config_file),
            'initdb',
        ])
        assert args.subcommand(args) == cli.ExitCode.OK

        # Ensure the table exists
        with db as dbsession:
            dbsession.query(Event).all()

        # Drop all tables to avoid side-effects between tests
        db.drop_all()

    def test_reinitdb(self, make_config_file):
        from .handler_module import Event

        config_file = make_config_file({
            'main': {'verbose': True},
            'postgresql': {'database': 'azafea-tests'},
            'queues': {'event': {'handler': 'azafea.tests.integration.managedb.handler_module'}},
        })
        config = Config.from_file(str(config_file))
        db = Db(config.postgresql.host, config.postgresql.port, config.postgresql.user,
                config.postgresql.password, config.postgresql.database)

        # Ensure there is no table at the start
        with pytest.raises(ProgrammingError) as exc_info:
            with db as dbsession:
                dbsession.query(Event).all()
        assert 'relation "managedb_event" does not exist' in str(exc_info.value)

        # Create the table
        args = cli.parse_args([
            '-c', str(config_file),
            'initdb',
        ])
        assert args.subcommand(args) == cli.ExitCode.OK

        # Add some events
        with db as dbsession:
            dbsession.add(Event(name='hi!'))

        # Ensure the element was inserted
        with db as dbsession:
            event = dbsession.query(Event).one()
            assert event.name == 'hi!'

        # Drop the table
        args = cli.parse_args([
            '-c', str(config_file),
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
            '-c', str(config_file),
            'initdb',
        ])
        assert args.subcommand(args) == cli.ExitCode.OK

        # Ensure the old events were cleared by the drop
        with db as dbsession:
            assert dbsession.query(Event).all() == []

        # Drop all tables to avoid side-effects between tests
        db.drop_all()
