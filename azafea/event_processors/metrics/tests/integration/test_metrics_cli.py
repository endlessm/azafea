# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from datetime import datetime, timezone

from gi.repository import GLib

from azafea.tests.integration import IntegrationTest
from azafea.vendors import normalize_vendor


class TestMetrics(IntegrationTest):
    handler_module = 'azafea.event_processors.metrics.v2'

    def test_normalize_no_vendors(self, capfd):
        from azafea.event_processors.metrics.events import UpdaterBranchSelected

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(UpdaterBranchSelected)

        with self.db as dbsession:
            assert dbsession.query(UpdaterBranchSelected).count() == 0

        self.run_subcommand('test_normalize_no_vendors', 'normalize-vendors')

        with self.db as dbsession:
            assert dbsession.query(UpdaterBranchSelected).count() == 0

        capture = capfd.readouterr()
        assert 'No "updater branch selected" record in database' in capture.out

    def test_normalize_vendor(self):
        from azafea.event_processors.metrics.events import UpdaterBranchSelected
        from azafea.event_processors.metrics.request import Request

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(UpdaterBranchSelected)

        # Insert an event with a known bad vendor
        occured_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        bad_vendor = 'EnDlEsS'
        payload = GLib.Variant('mv', GLib.Variant('(sssb)', (
            'whatever, this gets replaced',
            'To Be Filled By O.E.M.',
            'os/eos/amd64/eos3',
            False
        )))

        with self.db as dbsession:
            request = Request(serialized=b'whatever', sha512='whatever', received_at=occured_at,
                              absolute_timestamp=1, relative_timestamp=2, machine_id='whatever',
                              send_number=0)
            dbsession.add(request)

            event = UpdaterBranchSelected(request_id=request.id, user_id=1000,
                                          occured_at=occured_at, payload=payload)

            # Manually denormalize the vendor
            event.hardware_vendor = bad_vendor

            dbsession.add(event)

        with self.db as dbsession:
            event = dbsession.query(UpdaterBranchSelected).one()
            assert event.hardware_vendor == bad_vendor

        # Normalize the event vendors
        self.run_subcommand('test_normalize_vendor', 'normalize-vendors')
        good_vendor = normalize_vendor(bad_vendor)

        with self.db as dbsession:
            event = dbsession.query(UpdaterBranchSelected).one()
            assert event.hardware_vendor == good_vendor

    def test_normalize_already_normalized_vendor(self):
        from azafea.event_processors.metrics.events import UpdaterBranchSelected
        from azafea.event_processors.metrics.request import Request

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(UpdaterBranchSelected)

        # Insert an event with a known normalized vendor
        occured_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        vendor = 'Endless'
        assert vendor == normalize_vendor(vendor)
        payload = GLib.Variant('mv', GLib.Variant('(sssb)', (
            vendor,
            'To Be Filled By O.E.M.',
            'os/eos/amd64/eos3',
            False
        )))

        with self.db as dbsession:
            request = Request(serialized=b'whatever', sha512='whatever', received_at=occured_at,
                              absolute_timestamp=1, relative_timestamp=2, machine_id='whatever',
                              send_number=0)
            dbsession.add(request)
            dbsession.add(UpdaterBranchSelected(request_id=request.id, user_id=1000,
                                                occured_at=occured_at, payload=payload))

        with self.db as dbsession:
            event = dbsession.query(UpdaterBranchSelected).one()
            assert event.hardware_vendor == vendor

        # Normalize the event vendors
        self.run_subcommand('test_normalize_already_normalized_vendor', 'normalize-vendors')

        with self.db as dbsession:
            event = dbsession.query(UpdaterBranchSelected).one()
            assert event.hardware_vendor == vendor
