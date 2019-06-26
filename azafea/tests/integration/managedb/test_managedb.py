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


from azafea import cli

from .. import IntegrationTest


class TestManageDb(IntegrationTest):
    handler_module = 'azafea.tests.integration.managedb.handler_module'

    def test_initdb(self):
        from .handler_module import Event

        # Create the table
        args = cli.parse_args([
            '-c', self.config_file,
            'initdb',
        ])
        assert args.subcommand(args) == cli.ExitCode.OK

        # Ensure the table exists
        with self.db as dbsession:
            dbsession.query(Event).all()

    def test_reinitdb(self):
        from .handler_module import Event

        # Create the table
        args = cli.parse_args([
            '-c', self.config_file,
            'initdb',
        ])
        assert args.subcommand(args) == cli.ExitCode.OK

        # Add an event
        with self.db as dbsession:
            dbsession.add(Event(name='hi!'))

        # Ensure the event was inserted
        with self.db as dbsession:
            event = dbsession.query(Event).one()
            assert event.name == 'hi!'

        # Drop the table
        args = cli.parse_args([
            '-c', self.config_file,
            'dropdb'
        ])
        assert args.subcommand(args) == cli.ExitCode.OK

        # Ensure the table was dropped
        self.ensure_no_tables()

        # Recreate the table
        args = cli.parse_args([
            '-c', self.config_file,
            'initdb',
        ])
        assert args.subcommand(args) == cli.ExitCode.OK

        # Ensure the old events were cleared by the drop
        with self.db as dbsession:
            assert dbsession.query(Event).all() == []
