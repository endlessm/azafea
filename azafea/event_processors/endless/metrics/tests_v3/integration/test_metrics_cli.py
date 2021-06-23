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

        occured_at = datetime.utcnow().replace(tzinfo=timezone.utc)
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
                absolute_timestamp=1,
                relative_timestamp=2,
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
                absolute_timestamp=1,
                relative_timestamp=2,
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
                absolute_timestamp=1,
                relative_timestamp=2,
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
                absolute_timestamp=1,
                relative_timestamp=2,
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
                absolute_timestamp=1,
                relative_timestamp=2,
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

        occured_at = datetime.utcnow().replace(tzinfo=timezone.utc)
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
                channel=channel, event_id='7be59566-2b23-408a-acf6-91490fc1df1c',
                absolute_timestamp=1, relative_timestamp=2, occured_at=occured_at,
                payload=GLib.Variant('mv', GLib.Variant('s', 'discard')), os_version='os_version'
            ))

            # Add an unknown singular event which will be replay as ParentalControlsEnabled
            dbsession.add(UnknownSingularEvent(
                channel=channel, event_id='c227a817-808c-4fcb-b797-21002d17b69a',
                absolute_timestamp=1, relative_timestamp=2, occured_at=occured_at,
                payload=GLib.Variant('mv', GLib.Variant('b', True)), os_version='os_version'
            ))

            # Add an unknown singular event which will be replay as ParentalControlsEnabled
            # Will fail and add as InvalidSingularEvent
            dbsession.add(UnknownSingularEvent(
                channel=channel, event_id='c227a817-808c-4fcb-b797-21002d17b69a',
                absolute_timestamp=1, relative_timestamp=2, occured_at=occured_at,
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
                absolute_timestamp=1,
                relative_timestamp=2,
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
