# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from importlib import import_module
from pathlib import Path

from .. import IntegrationTest

TEST_DIR = Path(__file__).parent


class TestManageDb(IntegrationTest):
    handler_path = TEST_DIR / 'handler_module.py'

    def test_initdb(self):
        Event = import_module(self.handler_module).Event

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Event)

    def test_reinitdb(self):
        Event = import_module(self.handler_module).Event

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Event)

        # Add an event
        with self.db as dbsession:
            dbsession.add(Event(name='hi!'))

        # Ensure the event was inserted
        with self.db as dbsession:
            event = dbsession.query(Event).one()
            assert event.name == 'hi!'

        # Drop the table
        self.run_subcommand('dropdb')
        self.ensure_no_tables()

        # Recreate the table
        self.run_subcommand('initdb')
        self.ensure_tables(Event)

        # Ensure the old events were cleared by the drop
        with self.db as dbsession:
            assert dbsession.query(Event).all() == []
