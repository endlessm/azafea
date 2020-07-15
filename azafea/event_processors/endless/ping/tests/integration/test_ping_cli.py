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
    handler_module = 'azafea.event_processors.endless.ping.v1'

    def test_normalize_no_vendors(self, capfd):
        from azafea.event_processors.endless.ping.v1.handler import PingConfiguration

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
        from azafea.event_processors.endless.ping.v1.handler import PingConfiguration

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(PingConfiguration)

        # Insert a ping configuration with a known bad vendor
        created_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        bad_vendor = 'EnDlEsS'

        with self.db as dbsession:
            dbsession.add(PingConfiguration(image='eos-eos3.7-amd64-amd64.190419-225606.base',
                                            product='product', dualboot=True, created_at=created_at,
                                            vendor=bad_vendor))

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
        from azafea.event_processors.endless.ping.v1.handler import PingConfiguration

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(PingConfiguration)

        # Insert a ping configuration with a known normalized vendor
        created_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        vendor = 'Endless'
        assert vendor == normalize_vendor(vendor)

        with self.db as dbsession:
            dbsession.add(PingConfiguration(image='eos-eos3.7-amd64-amd64.190419-225606.base',
                                            product='product', dualboot=True, created_at=created_at,
                                            vendor=vendor))

        with self.db as dbsession:
            ping_config = dbsession.query(PingConfiguration).one()
            assert ping_config.vendor == vendor

        # Normalize the ping configuration vendors
        self.run_subcommand('test_normalize_already_normalized_vendor', 'normalize-vendors')

        with self.db as dbsession:
            ping_config = dbsession.query(PingConfiguration).one()
            assert ping_config.vendor == vendor

    def test_normalize_vendors_to_same_new_vendor(self):
        from azafea.event_processors.endless.ping.v1.handler import Ping, PingConfiguration

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(PingConfiguration)

        # Insert a ping configuration with a known bad vendor, with a first ping
        created_at = datetime.utcnow().replace(tzinfo=timezone.utc)

        with self.db as dbsession:
            ping_config = PingConfiguration(image='eos-eos3.7-amd64-amd64.190419-225606.base',
                                            product='product', dualboot=True, created_at=created_at,
                                            vendor='EnDlEsS')
            dbsession.add(ping_config)
            dbsession.add(Ping(config=ping_config, release='release', count=0,
                               created_at=created_at))

        # Insert another ping configuration with a known bad vendor which normalizes to the same
        # vendor as the previous one
        created_at = datetime.utcnow().replace(tzinfo=timezone.utc)

        with self.db as dbsession:
            ping_config = PingConfiguration(image='eos-eos3.7-amd64-amd64.190419-225606.base',
                                            product='product', dualboot=True, created_at=created_at,
                                            vendor='eNdLeSs')
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
        from azafea.event_processors.endless.ping.v1.handler import Ping, PingConfiguration

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(PingConfiguration)

        # Insert a ping configuration with a known bad vendor, with a first ping
        created_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        bad_vendor = 'EnDlEsS'

        with self.db as dbsession:
            ping_config = PingConfiguration(image='eos-eos3.7-amd64-amd64.190419-225606.base',
                                            product='product', dualboot=True, created_at=created_at,
                                            vendor=bad_vendor)
            dbsession.add(ping_config)
            dbsession.add(Ping(config=ping_config, release='release', count=0,
                               created_at=created_at))

        # Now insert a ping configuration with a known normalized vendor, with a second ping
        created_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        good_vendor = normalize_vendor(bad_vendor)

        with self.db as dbsession:
            ping_config = PingConfiguration(image='eos-eos3.7-amd64-amd64.190419-225606.base',
                                            product='product', dualboot=True, created_at=created_at,
                                            vendor=good_vendor)
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

    def test_parse_old_images(self):
        from azafea.event_processors.endless.ping.v1.handler import PingConfiguration

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(PingConfiguration)

        # Insert a ping configuration without parsed image components
        image_id = 'eos-eos3.7-amd64-amd64.190419-225606.base'
        created_at = datetime.utcnow().replace(tzinfo=timezone.utc)

        with self.db as dbsession:
            dbsession.add(PingConfiguration(image=image_id, product='product', release='release',
                                            dualboot=True, created_at=created_at, vendor='vendor'))

        with self.db as dbsession:
            config = dbsession.query(PingConfiguration).one()
            assert config.image == image_id
            assert config.image_product is None
            assert config.image_branch is None
            assert config.image_arch is None
            assert config.image_platform is None
            assert config.image_timestamp is None
            assert config.image_personality is None

        # Parse the image for old ping configuration records
        self.run_subcommand('test_parse_old_images', 'parse-old-images')

        with self.db as dbsession:
            config = dbsession.query(PingConfiguration).one()
            assert config.image == image_id
            assert config.image_product == 'eos'
            assert config.image_branch == 'eos3.7'
            assert config.image_arch == 'amd64'
            assert config.image_platform == 'amd64'
            assert config.image_timestamp == datetime(2019, 4, 19, 22, 56, 6, tzinfo=timezone.utc)
            assert config.image_personality == 'base'

    def test_parse_old_images_skips_already_done(self, capfd):
        from azafea.event_processors.endless.ping.v1.handler import PingConfiguration

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(PingConfiguration)

        # Insert a ping configuration without parsed image components
        image_id = 'eos-eos3.7-amd64-amd64.190419-225606.base'
        created_at = datetime.utcnow().replace(tzinfo=timezone.utc)

        with self.db as dbsession:
            dbsession.add(PingConfiguration(image=image_id, image_product='eos',
                                            image_branch='eos3.7', image_arch='amd64',
                                            image_platform='amd64',
                                            image_timestamp=datetime(2019, 4, 19, 22, 56, 6,
                                                                     tzinfo=timezone.utc),
                                            image_personality='base', product='product',
                                            release='release', dualboot=True, created_at=created_at,
                                            vendor='vendor'))

        with self.db as dbsession:
            config = dbsession.query(PingConfiguration).one()
            assert config.image == image_id
            assert config.image_product == 'eos'
            assert config.image_branch == 'eos3.7'
            assert config.image_arch == 'amd64'
            assert config.image_platform == 'amd64'
            assert config.image_timestamp == datetime(2019, 4, 19, 22, 56, 6, tzinfo=timezone.utc)
            assert config.image_personality == 'base'

        # Parse the image for old ping configuration records
        self.run_subcommand('test_parse_old_images_skips_already_done', 'parse-old-images')

        with self.db as dbsession:
            config = dbsession.query(PingConfiguration).one()
            assert config.image == image_id
            assert config.image_product == 'eos'
            assert config.image_branch == 'eos3.7'
            assert config.image_arch == 'amd64'
            assert config.image_platform == 'amd64'
            assert config.image_timestamp == datetime(2019, 4, 19, 22, 56, 6, tzinfo=timezone.utc)
            assert config.image_personality == 'base'

        capture = capfd.readouterr()
        assert 'No ping record with unparsed image ids' in capture.out

    def test_parse_old_unknown_images(self, capfd):
        from azafea.event_processors.endless.ping.v1.handler import PingConfiguration

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(PingConfiguration)

        # Insert a ping configuration without parsed image components
        image_id = 'unknown'
        created_at = datetime.utcnow().replace(tzinfo=timezone.utc)

        with self.db as dbsession:
            dbsession.add(PingConfiguration(image=image_id, product='product', release='release',
                                            dualboot=True, created_at=created_at, vendor='vendor'))

        with self.db as dbsession:
            config = dbsession.query(PingConfiguration).one()
            assert config.image == image_id
            assert config.image_product is None
            assert config.image_branch is None
            assert config.image_arch is None
            assert config.image_platform is None
            assert config.image_timestamp is None
            assert config.image_personality is None

        # Parse the image for old ping configuration records
        self.run_subcommand('test_parse_old_unknown_images', 'parse-old-images')

        with self.db as dbsession:
            config = dbsession.query(PingConfiguration).one()
            assert config.image == image_id
            assert config.image_product is None
            assert config.image_branch is None
            assert config.image_arch is None
            assert config.image_platform is None
            assert config.image_timestamp is None
            assert config.image_personality is None

        capture = capfd.readouterr()
        assert 'No ping record with unparsed image ids' in capture.out

    def test_transform_countries_alpha_3_to_2(self, capfd):
        from azafea.event_processors.endless.ping.v1.handler import Ping, PingConfiguration

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Ping)

        created_at = datetime.utcnow().replace(tzinfo=timezone.utc)

        with self.db as dbsession:
            ping_config = PingConfiguration(image='eos-eos3.7-amd64-amd64.190419-225606.base',
                                            product='product', dualboot=True, created_at=created_at,
                                            vendor='EnDlEsS')
            dbsession.add(ping_config)
            dbsession.add(Ping(config=ping_config, release='release', count=0,
                               created_at=created_at, country='FR'))

        with self.db as dbsession:
            # Bypass ORM country validation
            dbsession.execute("UPDATE ping_v1 SET country='FRA'")

        with self.db as dbsession:
            ping = dbsession.query(Ping).one()
            assert ping.country == 'FRA'

        self.run_subcommand(
            'test_transform_countries_alpha_3_to_2',
            'transform-countries-alpha-3-to-2')

        with self.db as dbsession:
            ping = dbsession.query(Ping).one()
            assert ping.country == 'FR'

    def test_transform_countries_alpha_3_to_2_only_2(self, capfd):
        from azafea.event_processors.endless.ping.v1.handler import Ping, PingConfiguration

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Ping)

        created_at = datetime.utcnow().replace(tzinfo=timezone.utc)

        with self.db as dbsession:
            ping_config = PingConfiguration(image='eos-eos3.7-amd64-amd64.190419-225606.base',
                                            product='product', dualboot=True, created_at=created_at,
                                            vendor='EnDlEsS')
            dbsession.add(ping_config)
            dbsession.add(Ping(config=ping_config, release='release', count=0,
                               created_at=created_at, country='FR'))

        self.run_subcommand(
            'test_transform_countries_alpha_3_to_2_only_2',
            'transform-countries-alpha-3-to-2')

        with self.db as dbsession:
            ping = dbsession.query(Ping).one()
            assert ping.country == 'FR'

        capture = capfd.readouterr()
        assert 'No ping with alpha-3 country code found' in capture.out
