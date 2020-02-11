# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from datetime import datetime, timezone

from azafea.tests.integration import IntegrationTest
from azafea.vendors import normalize_vendor


class TestActivation(IntegrationTest):
    handler_module = 'azafea.event_processors.endless.activation.v1'

    def test_normalize_no_vendors(self, capfd):
        from azafea.event_processors.endless.activation.v1.handler import Activation

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Activation)

        with self.db as dbsession:
            assert dbsession.query(Activation).count() == 0

        self.run_subcommand('test_normalize_no_vendors', 'normalize-vendors')

        with self.db as dbsession:
            assert dbsession.query(Activation).count() == 0

        capture = capfd.readouterr()
        assert 'No activation record in database' in capture.out

    def test_normalize_existing_vendor(self):
        from azafea.event_processors.endless.activation.v1.handler import Activation

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Activation)

        # Insert an activation with a known bad vendor
        created_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        bad_vendor = 'EnDlEsS'

        with self.db as dbsession:
            dbsession.add(Activation(image='image', product='product', release='release',
                                     country='HKG', created_at=created_at, vendor=bad_vendor))

        with self.db as dbsession:
            activation = dbsession.query(Activation).one()
            assert activation.vendor == bad_vendor

        # Normalize the activation vendors
        self.run_subcommand('test_normalize_existing_vendor', 'normalize-vendors')
        good_vendor = normalize_vendor(bad_vendor)

        with self.db as dbsession:
            activation = dbsession.query(Activation).one()
            assert activation.vendor == good_vendor

    def test_normalize_already_normalized_vendor(self):
        from azafea.event_processors.endless.activation.v1.handler import Activation

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Activation)

        # Insert an activation with a known normalized vendor
        created_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        vendor = 'Endless'
        assert vendor == normalize_vendor(vendor)

        with self.db as dbsession:
            dbsession.add(Activation(image='image', product='product', release='release',
                                     country='HKG', created_at=created_at, vendor=vendor))

        with self.db as dbsession:
            activation = dbsession.query(Activation).one()
            assert activation.vendor == vendor

        # Normalize the activation vendors
        self.run_subcommand('test_normalize_already_normalized_vendor', 'normalize-vendors')

        with self.db as dbsession:
            activation = dbsession.query(Activation).one()
            assert activation.vendor == vendor
