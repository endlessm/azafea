# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from datetime import datetime, timezone, date

from gi.repository import GLib

from azafea.tests.integration import IntegrationTest


class TestMetrics(IntegrationTest):
    handler_module = 'azafea.event_processors.endless.metrics.v3'

    def test_replay_invalid_singular(self):
        from azafea.event_processors.endless.metrics.v3.model import (
            InvalidSingularEvent, Channel, UnknownSingularEvent)
        from azafea.event_processors.endless.metrics.v3.model import _base
        _base.IGNORED_EMPTY_PAYLOAD_ERRORS = ['9d03daad-f1ed-41a8-bc5a-6b532c075832']
        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(
            Channel, InvalidSingularEvent, UnknownSingularEvent)

        occured_at = datetime.now(tz=timezone.utc)
        image_id = 'eos-eos3.7-amd64-amd64.190419-225606.base'

        with self.db as dbsession:
            channel = Channel(
                received_at=occured_at,
                absolute_timestamp=1,
                relative_timestamp=2,
                image_id=image_id,
                site={},
                dual_boot=False,
                live=False,
                send_number=0
            )
            dbsession.add(channel)

            # -- Invalid singular events --------

            # Add an invalid singular event which will be replayed as a
            # LaunchedEquivalentExistingFlatpak
            dbsession.add(InvalidSingularEvent(
                channel=channel,
                event_id='00d7bc1e-ec93-4c53-ae78-a6b40450be4a',
                occured_at=occured_at,
                payload=GLib.Variant('mv', GLib.Variant(
                    '(sas)',
                    ('replacement_app_id', ['argv1', 'argv2'])
                )),
                error='discard',
                os_version='os_version',
            ))

            # Add an invalid singular event which will be unknown after the replay
            unknown_singular = GLib.Variant('mv', GLib.Variant('s', 'unknown'))
            dbsession.add(InvalidSingularEvent(
                channel=channel,
                event_id='ffffffff-ffff-ffff-ffff-ffffffffffff',
                occured_at=occured_at,
                payload=unknown_singular,
                error='unknown',
                os_version='os_version',
            ))

            # Add an invalid singular event which will be replayed as a
            # LaunchedEquivalentExistingFlatpak uptime event, but fail
            invalid_singular = GLib.Variant(
                'mv', GLib.Variant('as', ['invalid', 'payload'])
            )
            dbsession.add(InvalidSingularEvent(
                channel=channel,
                event_id='00d7bc1e-ec93-4c53-ae78-a6b40450be4a',
                occured_at=occured_at,
                payload=invalid_singular,
                error='invalid',
                os_version='os_version',
            ))

            # Add an invalid singular event which will be replayed as a
            # ParentalControlsBlockedFlatpakInstall uptime event, but fail
            invalid_singular_2 = GLib.Variant(
                'mv', None
            )
            dbsession.add(InvalidSingularEvent(
                channel=channel,
                event_id='9d03daad-f1ed-41a8-bc5a-6b532c075832',
                occured_at=occured_at,
                payload=invalid_singular_2,
                error='invalid',
                os_version='os_version',
            ))

            # Add an invalid singular event which will be ignored
            # event_id in IGNORED_EVENTS
            dbsession.add(InvalidSingularEvent(
                channel=channel,
                event_id='005096c4-9444-48c6-844b-6cb693c15235',
                occured_at=occured_at,
                payload=GLib.Variant('mv', None),
                error='discard',
                os_version='os_version',
            ))

        # Replay the invalid events
        self.run_subcommand('test_replay_invalid_singular', 'replay-invalid')

        with self.db as dbsession:
            channel = dbsession.query(Channel).one()

            # -- Singular events ----------------
            unknown = dbsession.query(UnknownSingularEvent).one()
            assert unknown.channel == channel
            assert unknown.occured_at == occured_at
            assert unknown.payload_data == unknown_singular.get_data_as_bytes().get_data()

            invalid = dbsession.query(InvalidSingularEvent).one()
            assert invalid.channel == channel
            assert invalid.occured_at == occured_at
            assert invalid.payload_data == invalid_singular.get_data_as_bytes().get_data()
            assert invalid.error == 'invalid'

    def test_replay_unknown_singular(self):
        from azafea.event_processors.endless.metrics.v3.model import (
            InvalidSingularEvent, Channel,
            UnknownSingularEvent, ParentalControlsEnabled
        )
        from azafea.event_processors.endless.metrics.v3.model import _base
        _base.IGNORED_EMPTY_PAYLOAD_ERRORS = ['9d03daad-f1ed-41a8-bc5a-6b532c075832']
        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(
            Channel, InvalidSingularEvent, UnknownSingularEvent, ParentalControlsEnabled,
        )

        occured_at = datetime.now(tz=timezone.utc)
        image_id = 'eos-eos3.7-amd64-amd64.190419-225606.base'

        with self.db as dbsession:
            channel = Channel(
                received_at=occured_at,
                absolute_timestamp=1,
                relative_timestamp=2,
                image_id=image_id,
                site={},
                dual_boot=False,
                live=False,
                send_number=0
            )
            dbsession.add(channel)
            # -- Unknown aggregate events -------

            # Add an unknown singular event which will be ignored after the replay
            dbsession.add(UnknownSingularEvent(
                channel=channel,
                event_id='7be59566-2b23-408a-acf6-91490fc1df1c',
                occured_at=occured_at,
                payload=GLib.Variant('mv', GLib.Variant('s', 'discard')),
                os_version='os_version'
            ))

            # Add an unknown singular event which will be replay as ParentalControlsEnabled
            dbsession.add(UnknownSingularEvent(
                channel=channel,
                event_id='c227a817-808c-4fcb-b797-21002d17b69a',
                occured_at=occured_at,
                payload=GLib.Variant('mv', GLib.Variant('b', True)),
                os_version='os_version'
            ))

            # Add an unknown singular event which will be replay as ParentalControlsEnabled
            # Will fail and add as InvalidSingularEvent
            dbsession.add(UnknownSingularEvent(
                channel=channel,
                event_id='c227a817-808c-4fcb-b797-21002d17b69a',
                occured_at=occured_at,
                payload=GLib.Variant('mv', GLib.Variant('(sb)', ('should be invalid', True))),
                os_version='os_version'
            ))

            # Add an unknown singular event which will be replay
            # as ParentalControlsBlockedFlatpakInstall
            # Will fail and add as InvalidSingularEvent
            dbsession.add(UnknownSingularEvent(
                channel=channel,
                event_id='9d03daad-f1ed-41a8-bc5a-6b532c075832',
                occured_at=occured_at,
                payload=GLib.Variant('mv', None),
                os_version='os_version',
            ))

        with self.db as dbsession:
            assert dbsession.query(Channel).count() == 1
            assert dbsession.query(UnknownSingularEvent).count() == 4

        # Replay the unknown events
        self.run_subcommand('test_replay_unknown_singular', 'replay-unknown')

        with self.db as dbsession:
            channel = dbsession.query(Channel).one()

            assert dbsession.query(UnknownSingularEvent).count() == 0
            assert dbsession.query(InvalidSingularEvent).count() == 1
            assert dbsession.query(ParentalControlsEnabled).count() == 1

    def test_replay_unknown_aggregate(self):
        from azafea.event_processors.endless.metrics.v3.model import (
            Channel, UnknownAggregateEvent
        )

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Channel, UnknownAggregateEvent)

        occured_at = datetime.now(tz=timezone.utc)
        image_id = 'eos-eos3.7-amd64-amd64.190419-225606.base'

        with self.db as dbsession:
            channel = Channel(
                received_at=occured_at,
                absolute_timestamp=1,
                relative_timestamp=2,
                image_id=image_id,
                site={},
                dual_boot=False,
                live=False,
                send_number=0
            )
            dbsession.add(channel)
            # -- Unknown aggregate events -------

            # Add an unknown singular event which will be ignored after the replay
            dbsession.add(UnknownAggregateEvent(
                channel=channel,
                event_id='91de63ea-c7b7-412c-93f3-6f3d9b2f864c',
                period_start=date(1970, 1, 1),
                period_start_str='2020-08-15',
                count=15,
                payload=GLib.Variant('mv', None),
                os_version='os_version'
            ))

            # Add an unknown singular event
            dbsession.add(UnknownAggregateEvent(
                channel=channel,
                event_id='a3826320-9192-446a-8886-e2129c0ce302',
                period_start=date(1970, 1, 1),
                count=15,
                period_start_str='2020-08-15',
                payload=GLib.Variant('mv', None),
                os_version='os_version'
            ))

        with self.db as dbsession:
            assert dbsession.query(Channel).count() == 1
            assert dbsession.query(UnknownAggregateEvent).count() == 2

        # Replay the unknown events
        self.run_subcommand('test_replay_unknown_aggregate', 'replay-unknown')

        with self.db as dbsession:
            channel = dbsession.query(Channel).one()
            assert dbsession.query(UnknownAggregateEvent).count() == 1

    def test_parse_old_images(self):
        from azafea.event_processors.endless.metrics.v3.model import Channel

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Channel)

        # Insert a channel without parsed image components
        image_id = 'eos-eos3.7-amd64-amd64.190419-225606.base'

        with self.db as dbsession:
            channel = Channel(image_id=image_id, site={}, dual_boot=False, live=False)
            channel.image_product = None
            channel.image_branch = None
            channel.image_arch = None
            channel.image_platform = None
            channel.image_timestamp = None
            channel.image_personality = None
            dbsession.add(channel)

        with self.db as dbsession:
            channel = dbsession.query(Channel).one()
            assert channel.image_id == image_id
            assert channel.image_product is None
            assert channel.image_branch is None
            assert channel.image_arch is None
            assert channel.image_platform is None
            assert channel.image_timestamp is None
            assert channel.image_personality is None

        # Parse the image for old channel records
        self.run_subcommand('test_parse_old_images', 'parse-old-images')

        with self.db as dbsession:
            machine = dbsession.query(Channel).one()
            assert machine.image_id == image_id
            assert machine.image_product == 'eos'
            assert machine.image_branch == 'eos3.7'
            assert machine.image_arch == 'amd64'
            assert machine.image_platform == 'amd64'
            assert machine.image_timestamp == datetime(2019, 4, 19, 22, 56, 6)
            assert machine.image_personality == 'base'

    def test_parse_old_images_skips_already_done(self, capfd):
        from azafea.event_processors.endless.metrics.v3.model import Channel

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Channel)

        # Insert a channel without parsed image components
        image_id = 'eos-eos3.7-amd64-amd64.190419-225606.base'

        with self.db as dbsession:
            dbsession.add(Channel(image_id=image_id, site={}, dual_boot=False, live=False))

        with self.db as dbsession:
            machine = dbsession.query(Channel).one()
            assert machine.image_id == image_id
            assert machine.image_product == 'eos'
            assert machine.image_branch == 'eos3.7'
            assert machine.image_arch == 'amd64'
            assert machine.image_platform == 'amd64'
            assert machine.image_timestamp == datetime(2019, 4, 19, 22, 56, 6)
            assert machine.image_personality == 'base'

        # Parse the image for old channel records
        self.run_subcommand('test_parse_old_images_skips_already_done', 'parse-old-images')

        with self.db as dbsession:
            machine = dbsession.query(Channel).one()
            assert machine.image_id == image_id
            assert machine.image_product == 'eos'
            assert machine.image_branch == 'eos3.7'
            assert machine.image_arch == 'amd64'
            assert machine.image_platform == 'amd64'
            assert machine.image_timestamp == datetime(2019, 4, 19, 22, 56, 6)
            assert machine.image_personality == 'base'

        capture = capfd.readouterr()
        assert 'No Channel records with unparsed image IDs' in capture.out
