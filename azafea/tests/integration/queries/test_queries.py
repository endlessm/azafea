# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from .. import IntegrationTest


class TestQuery(IntegrationTest):
    handler_module = 'azafea.tests.integration.queries.handler_module'

    def test_chunked_query(self):
        from .handler_module import Event

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Event)

        # Insert events
        with self.db as dbsession:
            for i in range(1, 61):
                dbsession.add(Event(name=f'name-{i}'))

        CHUNK_SIZE = 4

        # Now get them all with a chunked query
        with self.db as dbsession:
            query = dbsession.chunked_query(Event, chunk_size=CHUNK_SIZE)
            counted = 0

            for chunk_number, chunk in enumerate(query):
                for event_number, event in enumerate(chunk, start=1):
                    index = event_number + chunk_number * CHUNK_SIZE

                    # This works because the chunked query sorts by id
                    assert event.name == f'name-{index}'

                    counted += 1

        # We already checked we had all events from 1 to 60, let's ensure we have 60 in total
        assert counted == 60

    def test_chunked_query_descending(self):
        from .handler_module import Event

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Event)

        # Insert events
        with self.db as dbsession:
            for i in range(1, 61):
                dbsession.add(Event(name=f'name-{i}'))

        CHUNK_SIZE = 4

        # Now get them all with a chunked query
        with self.db as dbsession:
            query = dbsession.chunked_query(Event, chunk_size=CHUNK_SIZE)
            query = query.reverse_chunks()
            counted = 0

            for chunk_number, chunk in enumerate(query, start=1):
                for event_number, event in enumerate(chunk, start=1):
                    index = event_number + (60 - chunk_number * CHUNK_SIZE)

                    # This works because the chunked query sorts by id
                    assert event.name == f'name-{index}'

                    counted += 1

        # We already checked we had all events from 1 to 60, let's ensure we have 60 in total
        assert counted == 60
