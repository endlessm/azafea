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
            dbsession.add(Activation(image='eos-eos3.7-amd64-amd64.190419-225606.base',
                                     product='product', release='release', country='HK',
                                     created_at=created_at, vendor=bad_vendor))

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
            dbsession.add(Activation(image='eos-eos3.7-amd64-amd64.190419-225606.base',
                                     product='product', release='release', country='HK',
                                     created_at=created_at, vendor=vendor))

        with self.db as dbsession:
            activation = dbsession.query(Activation).one()
            assert activation.vendor == vendor

        # Normalize the activation vendors
        self.run_subcommand('test_normalize_already_normalized_vendor', 'normalize-vendors')

        with self.db as dbsession:
            activation = dbsession.query(Activation).one()
            assert activation.vendor == vendor

    def test_parse_old_images(self):
        from azafea.event_processors.endless.activation.v1.handler import Activation

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Activation)

        # Insert an activation without parsed image components
        image_id = 'eos-eos3.7-amd64-amd64.190419-225606.base'
        created_at = datetime.utcnow().replace(tzinfo=timezone.utc)

        with self.db as dbsession:
            dbsession.add(Activation(image=image_id, product='product', release='release',
                                     country='HK', created_at=created_at, vendor='vendor'))

        with self.db as dbsession:
            activation = dbsession.query(Activation).one()
            assert activation.image == image_id
            assert activation.image_product is None
            assert activation.image_branch is None
            assert activation.image_arch is None
            assert activation.image_platform is None
            assert activation.image_timestamp is None
            assert activation.image_personality is None

        # Parse the image for old activation records
        self.run_subcommand('test_parse_old_images', 'parse-old-images')

        with self.db as dbsession:
            activation = dbsession.query(Activation).one()
            assert activation.image == image_id
            assert activation.image_product == 'eos'
            assert activation.image_branch == 'eos3.7'
            assert activation.image_arch == 'amd64'
            assert activation.image_platform == 'amd64'
            assert activation.image_timestamp == datetime(2019, 4, 19, 22, 56, 6,
                                                          tzinfo=timezone.utc)
            assert activation.image_personality == 'base'

    def test_parse_old_images_skips_already_done(self, capfd):
        from azafea.event_processors.endless.activation.v1.handler import Activation

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Activation)

        # Insert an activation without parsed image components
        image_id = 'eos-eos3.7-amd64-amd64.190419-225606.base'
        created_at = datetime.utcnow().replace(tzinfo=timezone.utc)

        with self.db as dbsession:
            dbsession.add(Activation(image=image_id, image_product='eos', image_branch='eos3.7',
                                     image_arch='amd64', image_platform='amd64',
                                     image_timestamp=datetime(2019, 4, 19, 22, 56, 6,
                                                              tzinfo=timezone.utc),
                                     image_personality='base', product='product', release='release',
                                     country='HK', created_at=created_at, vendor='vendor'))

        with self.db as dbsession:
            activation = dbsession.query(Activation).one()
            assert activation.image == image_id
            assert activation.image_product == 'eos'
            assert activation.image_branch == 'eos3.7'
            assert activation.image_arch == 'amd64'
            assert activation.image_platform == 'amd64'
            assert activation.image_timestamp == datetime(2019, 4, 19, 22, 56, 6,
                                                          tzinfo=timezone.utc)
            assert activation.image_personality == 'base'

        # Parse the image for old activation records
        self.run_subcommand('test_parse_old_images_skips_already_done', 'parse-old-images')

        with self.db as dbsession:
            activation = dbsession.query(Activation).one()
            assert activation.image == image_id
            assert activation.image_product == 'eos'
            assert activation.image_branch == 'eos3.7'
            assert activation.image_arch == 'amd64'
            assert activation.image_platform == 'amd64'
            assert activation.image_timestamp == datetime(2019, 4, 19, 22, 56, 6,
                                                          tzinfo=timezone.utc)
            assert activation.image_personality == 'base'

        capture = capfd.readouterr()
        assert 'No activation record with unparsed image ids' in capture.out

    def test_parse_old_unknown_images(self, capfd):
        from azafea.event_processors.endless.activation.v1.handler import Activation

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Activation)

        # Insert an activation with an unknown image
        image_id = 'unknown'
        created_at = datetime.utcnow().replace(tzinfo=timezone.utc)

        with self.db as dbsession:
            dbsession.add(Activation(image=image_id, product='product', release='release',
                                     country='HK', created_at=created_at, vendor='vendor'))

        with self.db as dbsession:
            activation = dbsession.query(Activation).one()
            assert activation.image == image_id
            assert activation.image_product is None
            assert activation.image_branch is None
            assert activation.image_arch is None
            assert activation.image_platform is None
            assert activation.image_timestamp is None
            assert activation.image_personality is None

        # Parse the image for old activation records
        self.run_subcommand('test_parse_old_unknown_images', 'parse-old-images')

        with self.db as dbsession:
            activation = dbsession.query(Activation).one()
            assert activation.image == image_id
            assert activation.image_product is None
            assert activation.image_branch is None
            assert activation.image_arch is None
            assert activation.image_platform is None
            assert activation.image_timestamp is None
            assert activation.image_personality is None

        capture = capfd.readouterr()
        assert 'No activation record with unparsed image ids' in capture.out

    def test_transform_countries_alpha_3_to_2(self, capfd):
        from azafea.event_processors.endless.activation.v1.handler import Activation

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Activation)

        created_at = datetime.utcnow().replace(tzinfo=timezone.utc)

        with self.db as dbsession:
            activation = Activation(
                image='unknown', product='product', release='release', country='FR',
                created_at=created_at, vendor='vendor')
            dbsession.add(activation)

        with self.db as dbsession:
            # Bypass ORM country validation
            dbsession.execute("UPDATE activation_v1 SET country='FRA'")

        with self.db as dbsession:
            activation = dbsession.query(Activation).one()
            assert activation.country == 'FRA'

        # Parse the image for old activation records
        self.run_subcommand(
            'test_transform_countries_alpha_3_to_2',
            'transform-countries-alpha-3-to-2')

        with self.db as dbsession:
            activation = dbsession.query(Activation).one()
            assert activation.country == 'FR'

    def test_transform_countries_alpha_3_to_2_only_2(self, capfd):
        from azafea.event_processors.endless.activation.v1.handler import Activation

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Activation)

        created_at = datetime.utcnow().replace(tzinfo=timezone.utc)

        with self.db as dbsession:
            activation = Activation(
                image='unknown', product='product', release='release', country='FR',
                created_at=created_at, vendor='vendor')
            dbsession.add(activation)

        self.run_subcommand(
            'test_transform_countries_alpha_3_to_2_only_2',
            'transform-countries-alpha-3-to-2')

        with self.db as dbsession:
            activation = dbsession.query(Activation).one()
            assert activation.country == 'FR'

        capture = capfd.readouterr()
        assert 'No activation with alpha-3 country code found' in capture.out
