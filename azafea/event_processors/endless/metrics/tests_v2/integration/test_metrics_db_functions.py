# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from datetime import datetime, timezone

from gi.repository import GLib

import pytest

from sqlalchemy.sql.expression import func

from azafea.tests.integration import IntegrationTest


class TestMetrics(IntegrationTest):
    handler_module = 'azafea.event_processors.endless.metrics.v2'

    @pytest.fixture(autouse=True)
    def drop_functions(self):
        yield

        with self.db as dbsession:
            dbsession.execute('DROP FUNCTION get_image_product')
            dbsession.execute('DROP FUNCTION get_image_personality')

            # We have to do this explicitly because the model Base is imported long before we have
            # a chance to run the migratedb command
            dbsession.execute('DROP TABLE alembic_version')

    def test_get_image_product_personality(self):
        from azafea.event_processors.endless.metrics.v2.model import ImageVersion, Machine, Request

        self.run_subcommand('migratedb')
        self.ensure_tables(ImageVersion, Machine, Request)

        image_id = 'eosoem-eos3.7-amd64-amd64.190419-225606.base'
        occured_at = datetime.utcnow().replace(tzinfo=timezone.utc)

        # Add a request with an image version
        with self.db as dbsession:
            request = Request(sha512='whatever', received_at=occured_at, absolute_timestamp=1,
                              relative_timestamp=2, machine_id='machine', send_number=0)
            dbsession.add(request)

            dbsession.add(ImageVersion(request=request, user_id=1001, occured_at=occured_at,
                                       payload=GLib.Variant('mv', GLib.Variant('s', image_id))))

        # Ensure this machine has the right product/personality
        with self.db as dbsession:
            product = dbsession.query(func.get_image_product(Request.machine_id)).one()[0]
            assert product == 'eosoem'
            personality = dbsession.query(func.get_image_personality(Request.machine_id)).one()[0]
            assert personality == 'base'

    def test_get_image_product_personality_without_machine_mapping(self):
        from azafea.event_processors.endless.metrics.v2.model import ImageVersion, Machine, Request

        self.run_subcommand('migratedb')
        self.ensure_tables(ImageVersion, Machine, Request)

        occured_at = datetime.utcnow().replace(tzinfo=timezone.utc)

        # Add a request without an image version
        with self.db as dbsession:
            request = Request(sha512='whatever', received_at=occured_at, absolute_timestamp=1,
                              relative_timestamp=2, machine_id='machine', send_number=0)
            dbsession.add(request)

        # Ensure this machine has no product/personality
        with self.db as dbsession:
            product = dbsession.query(func.get_image_product(Request.machine_id)).one()[0]
            assert product is None
            personality = dbsession.query(func.get_image_personality(Request.machine_id)).one()[0]
            assert personality is None
