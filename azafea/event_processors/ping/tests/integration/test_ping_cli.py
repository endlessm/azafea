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


class TestPing(IntegrationTest):
    handler_module = 'azafea.event_processors.ping.v1'

    def test_normalize_no_vendors(self, capfd):
        from azafea.event_processors.ping.v1.handler import PingConfiguration

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(PingConfiguration)

        with self.db as dbsession:
            assert dbsession.query(PingConfiguration).count() == 0

        self.run_subcommand('test_normalize_no_vendors', 'normalize-vendors')

        with self.db as dbsession:
            assert dbsession.query(PingConfiguration).count() == 0

        capture = capfd.readouterr()
        assert 'No ping configuration record in database' in capture.out

    def test_normalize_existing_vendor(self):
        from azafea.event_processors.ping.v1.handler import PingConfiguration

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(PingConfiguration)

        # Insert a ping configuration with a known bad vendor
        created_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        bad_vendor = 'EnDlEsS'

        with self.db as dbsession:
            dbsession.add(PingConfiguration(image='image', product='product', dualboot=True,
                                            created_at=created_at, vendor=bad_vendor))

        with self.db as dbsession:
            ping_config = dbsession.query(PingConfiguration).one()
            assert ping_config.vendor == bad_vendor

        # Normalize the ping configuration vendors
        self.run_subcommand('test_normalize_existing_vendor', 'normalize-vendors')
        good_vendor = normalize_vendor(bad_vendor)

        with self.db as dbsession:
            ping_config = dbsession.query(PingConfiguration).one()
            assert ping_config.vendor == good_vendor

    def test_normalize_already_normalized_vendor(self):
        from azafea.event_processors.ping.v1.handler import PingConfiguration

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(PingConfiguration)

        # Insert a ping configuration with a known normalized vendor
        created_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        vendor = 'Endless'
        assert vendor == normalize_vendor(vendor)

        with self.db as dbsession:
            dbsession.add(PingConfiguration(image='image', product='product', dualboot=True,
                                            created_at=created_at, vendor=vendor))

        with self.db as dbsession:
            ping_config = dbsession.query(PingConfiguration).one()
            assert ping_config.vendor == vendor

        # Normalize the ping configuration vendors
        self.run_subcommand('test_normalize_already_normalized_vendor', 'normalize-vendors')

        with self.db as dbsession:
            ping_config = dbsession.query(PingConfiguration).one()
            assert ping_config.vendor == vendor

    def test_normalize_vendors_to_same_new_vendor(self):
        from azafea.event_processors.ping.v1.handler import Ping, PingConfiguration

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(PingConfiguration)

        # Insert a ping configuration with a known bad vendor, with a first ping
        created_at = datetime.utcnow().replace(tzinfo=timezone.utc)

        with self.db as dbsession:
            ping_config = PingConfiguration(image='image', product='product', dualboot=True,
                                            created_at=created_at, vendor='EnDlEsS')
            dbsession.add(ping_config)
            dbsession.add(Ping(config=ping_config, release='release', count=0,
                               created_at=created_at))

        # Insert another ping configuration with a known bad vendor which normalizes to the same
        # vendor as the previous one
        created_at = datetime.utcnow().replace(tzinfo=timezone.utc)

        with self.db as dbsession:
            ping_config = PingConfiguration(image='image', product='product', dualboot=True,
                                            created_at=created_at, vendor='eNdLeSs')
            dbsession.add(ping_config)
            dbsession.add(Ping(config=ping_config, release='release', count=0,
                               created_at=created_at))

        # Check what we just did
        with self.db as dbsession:
            configs = dbsession.query(PingConfiguration).order_by(PingConfiguration.created_at)
            assert configs.count() == 2

            configs = configs.all()
            assert configs[0].vendor == 'EnDlEsS'
            assert configs[1].vendor == 'eNdLeSs'
            kept_config_id = configs[0].id

            pings = dbsession.query(Ping).order_by(Ping.created_at)
            assert pings.count() == 2

            pings = pings.all()
            assert pings[0].config_id == configs[0].id
            assert pings[0].count == 0
            assert pings[1].config_id == configs[1].id
            assert pings[1].count == 0

        # Normalize the ping configuration vendors
        self.run_subcommand('test_normalize_vendors_to_same_new_vendor', 'normalize-vendors')

        with self.db as dbsession:
            config = dbsession.query(PingConfiguration).one()
            assert config.vendor == 'Endless'
            assert config.id == kept_config_id

            pings = dbsession.query(Ping).order_by(Ping.created_at)
            assert pings.count() == 2

            pings = pings.all()
            assert pings[0].config_id == kept_config_id
            assert pings[1].config_id == kept_config_id

    def test_normalize_vendor_with_conflict_and_pings(self):
        from azafea.event_processors.ping.v1.handler import Ping, PingConfiguration

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(PingConfiguration)

        # Insert a ping configuration with a known bad vendor, with a first ping
        created_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        bad_vendor = 'EnDlEsS'

        with self.db as dbsession:
            ping_config = PingConfiguration(image='image', product='product', dualboot=True,
                                            created_at=created_at, vendor=bad_vendor)
            dbsession.add(ping_config)
            dbsession.add(Ping(config=ping_config, release='release', count=0,
                               created_at=created_at))

        # Now insert a ping configuration with a known normalized vendor, with a second ping
        created_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        good_vendor = normalize_vendor(bad_vendor)

        with self.db as dbsession:
            ping_config = PingConfiguration(image='image', product='product', dualboot=True,
                                            created_at=created_at, vendor=good_vendor)
            dbsession.add(ping_config)
            dbsession.add(Ping(config=ping_config, release='release', count=1,
                               created_at=created_at))

        # Check what we just did
        with self.db as dbsession:
            configs = dbsession.query(PingConfiguration).order_by(PingConfiguration.created_at)
            assert configs.count() == 2

            configs = configs.all()
            assert configs[0].vendor == bad_vendor
            assert configs[1].vendor == good_vendor
            kept_config_id = configs[1].id

            pings = dbsession.query(Ping).order_by(Ping.created_at)
            assert pings.count() == 2

            pings = pings.all()
            assert pings[0].config_id == configs[0].id
            assert pings[0].count == 0
            assert pings[1].config_id == configs[1].id
            assert pings[1].count == 1

        # Normalize the ping configuration vendors
        self.run_subcommand('test_normalize_vendor_with_conflict_and_pings', 'normalize-vendors')

        with self.db as dbsession:
            config = dbsession.query(PingConfiguration).one()
            assert config.vendor == good_vendor
            assert config.id == kept_config_id

            pings = dbsession.query(Ping).order_by(Ping.created_at)
            assert pings.count() == 2

            pings = pings.all()
            assert pings[0].config_id == kept_config_id
            assert pings[0].count == 0
            assert pings[1].config_id == kept_config_id
            assert pings[1].count == 1
