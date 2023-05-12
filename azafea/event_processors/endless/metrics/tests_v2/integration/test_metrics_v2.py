# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from datetime import datetime, timedelta, timezone
from hashlib import sha512
from uuid import UUID

from gi.repository import GLib

from azafea.tests.integration import IntegrationTest


class TestMetrics(IntegrationTest):
    handler_module = 'azafea.event_processors.endless.metrics.v2'

    def test_request(self):
        from azafea.event_processors.endless.metrics.v2.model import Request

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Request)

        # Build a request as it would have been sent to us
        now = datetime.now(tz=timezone.utc)
        machine_id = 'ffffffffffffffffffffffffffffffff'
        request = GLib.Variant(
            '(ixxaya(uayxmv)a(uayxxmv)a(uaya(xmv)))',
            (
                0,                                     # network send number
                2000000000,                            # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),     # request absolute timestamp
                bytes.fromhex(machine_id),
                [],                                    # singular events
                [],                                    # aggregate events
                []                                     # sequence events
            )
        )
        assert request.is_normal_form()
        request_body = request.get_data_as_bytes().get_data()

        received_at = now + timedelta(minutes=2)
        received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
        received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

        record = received_at_timestamp_bytes + request_body

        # Send the event request to the Redis queue
        self.redis.lpush('test_request', record)

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            request = dbsession.query(Request).one()

            assert request.send_number == 0
            assert request.machine_id == machine_id
            assert request.sha512 == sha512(request_body).hexdigest()
            assert request.received_at == received_at

    def test_duplicate_request(self):
        from azafea.event_processors.endless.metrics.v2.model import (
            Request, UnknownSingularEvent)

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Request)

        # Build a request as it would have been sent to us
        now = datetime.now(tz=timezone.utc)
        machine_id = 'ffffffffffffffffffffffffffffffff'
        request = GLib.Variant(
            '(ixxaya(uayxmv)a(uayxxmv)a(uaya(xmv)))',
            (
                0,                                     # network send number
                2000000000,                            # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),     # request absolute timestamp
                bytes.fromhex(machine_id),
                [                                      # singular events
                    (
                        1000,                          # user id
                        UUID('d3863909-8eff-43b6-9a33-ef7eda266195').bytes,
                        3000000000,                    # event relative timestamp (3 secs)
                        None,                          # empty payload
                    ),
                ],
                [],                                    # aggregate events
                []                                     # sequence events
            )
        )
        assert request.is_normal_form()
        request_body = request.get_data_as_bytes().get_data()

        received_at = now + timedelta(minutes=2)
        received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
        received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

        record = received_at_timestamp_bytes + request_body

        # Send the event request to the Redis queue, twice
        self.redis.lpush('test_duplicate_request', record)
        self.redis.lpush('test_duplicate_request', record)

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            request = dbsession.query(Request).one()

            assert request.send_number == 0
            assert request.machine_id == machine_id
            assert request.sha512 == sha512(request_body).hexdigest()
            assert request.received_at == received_at

            # Ensure we deduplicated the request and the events it contains
            assert dbsession.query(UnknownSingularEvent).count() == 1

    def test_invalid_request(self):
        from azafea.event_processors.endless.metrics.v2.model import Request

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Request)

        # Build an invalid request (GVariant not in its normal form)
        request = GLib.Variant.new_from_bytes(
            GLib.VariantType('(ixxaya(uayxmv)a(uayxxmv)a(uaya(xmv)))'),
            GLib.Bytes.new(b'\x00'),
            False)
        assert not request.is_normal_form()
        request_body = request.get_data_as_bytes().get_data()

        now = datetime.now(tz=timezone.utc)
        received_at = now + timedelta(minutes=2)
        received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
        received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

        record = received_at_timestamp_bytes + request_body

        # Send the event request to the Redis queue
        self.redis.lpush('test_invalid_request', record)

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure no record was inserted into the DB
        with self.db as dbsession:
            assert dbsession.query(Request).count() == 0

        # Ensure the request was pushed back into Redis
        assert self.redis.llen('errors-test_invalid_request') == 1
        assert self.redis.rpop('errors-test_invalid_request') == record

    def test_singular_events(self):
        from azafea.event_processors.endless.metrics.v2.model import (
            CacheIsCorrupt, CacheMetadataIsCorrupt, ControlCenterPanelOpened, CPUInfo,
            DiscoveryFeedClicked, DiscoveryFeedClosed, DiscoveryFeedOpened, DiskSpaceExtra,
            DiskSpaceSysroot, DualBootBooted, EndlessApplicationUnmaximized, EnteredDemoMode,
            ImageVersion, InvalidSingularEvent, UnknownSingularEvent,
            LaunchedEquivalentExistingFlatpak, LaunchedEquivalentInstallerForFlatpak,
            LaunchedExistingFlatpak, LaunchedInstallerForFlatpak, LinuxPackageOpened, LiveUsbBooted,
            Location, LocationLabel, Machine, MissingCodec, MonitorConnected, MonitorDisconnected,
            NetworkId, OSVersion, ProgramDumpedCore, RAMSize, Request, ShellAppAddedToDesktop,
            ShellAppRemovedFromDesktop, UnderscanEnabled, UpdaterBranchSelected, Uptime,
            WindowsAppOpened, WindowsLicenseTables,
        )

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(
            Request, Machine, InvalidSingularEvent, UnknownSingularEvent,
            CacheIsCorrupt, CacheMetadataIsCorrupt, ControlCenterPanelOpened, CPUInfo,
            DiscoveryFeedClicked, DiscoveryFeedClosed, DiscoveryFeedOpened, DiskSpaceExtra,
            DiskSpaceSysroot, DualBootBooted, EndlessApplicationUnmaximized, EnteredDemoMode,
            ImageVersion, LaunchedEquivalentExistingFlatpak, LaunchedEquivalentInstallerForFlatpak,
            LaunchedExistingFlatpak, LaunchedInstallerForFlatpak, LinuxPackageOpened, LiveUsbBooted,
            Location, LocationLabel, MissingCodec, MonitorConnected, MonitorDisconnected, NetworkId,
            OSVersion, ProgramDumpedCore, RAMSize, ShellAppAddedToDesktop,
            ShellAppRemovedFromDesktop, UnderscanEnabled, UpdaterBranchSelected, Uptime,
            WindowsAppOpened, WindowsLicenseTables,
        )

        # Build a request as it would have been sent to us
        now = datetime.now(tz=timezone.utc)
        machine_id = 'ffffffffffffffffffffffffffffffff'
        image_id = 'eos-eos3.7-amd64-amd64.190419-225606.base'
        user_id = 2000
        request = GLib.Variant(
            '(ixxaya(uayxmv)a(uayxxmv)a(uaya(xmv)))',
            (
                0,                                     # network send number
                2000000000,                            # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),     # request absolute timestamp
                bytes.fromhex(machine_id),
                [                                      # singular events
                    (
                        user_id,
                        UUID('d84b9a19-9353-73eb-70bf-f91a584abcbd').bytes,
                        1000000000,                    # event relative timestamp (1 sec)
                        None,                          # empty payload
                    ),
                    (
                        user_id,
                        UUID('f0e8a206-3bc2-405e-90d0-ef6fe6dd7edc').bytes,
                        2000000000,                    # event relative timestamp (2 secs)
                        None,                          # empty payload
                    ),
                    (
                        user_id,
                        UUID('3c5d59d2-6c3f-474b-95f4-ac6fcc192655').bytes,
                        28000000000,                   # event relative timestamp (28 secs)
                        GLib.Variant('s', 'privacy')
                    ),
                    (
                        user_id,
                        UUID('4a75488a-0d9a-4c38-8556-148f500edaf0').bytes,
                        5000000000,                    # event relative timestamp (5 secs)
                        GLib.Variant('a(sqd)', [
                            ('Intel(R) Core(TM) i7-5600U CPU @ 2.60GHz', 4, 2600.0),
                        ])
                    ),
                    (
                        user_id,
                        UUID('f2f31a64-2193-42b5-ae39-ca0b4d1f0691').bytes,
                        29000000000,                   # event relative timestamp (29 secs)
                        GLib.Variant('a{ss}', {
                            'app_id': 'org.gnome.Totem',
                            'content_type': 'knowledge_video',
                        })
                    ),
                    (
                        user_id,
                        UUID('e7932cbd-7c20-49eb-94e9-4bf075e0c0c0').bytes,
                        30000000000,                   # event relative timestamp (30 secs)
                        GLib.Variant('a{ss}', {
                            'closed_by': 'buttonclose',
                            'time_open': '123',
                        })
                    ),
                    (
                        user_id,
                        UUID('d54cbd8c-c977-4dac-ae72-535ad5633877').bytes,
                        31000000000,                   # event relative timestamp (31 secs)
                        GLib.Variant('a{ss}', {
                            'opened_by': 'shell_button',
                            'language': 'fr_FR.UTF-8',
                        })
                    ),
                    (
                        user_id,
                        UUID('da505554-4248-4a38-bb32-84ab58e45a6d').bytes,
                        6000000000,                    # event relative timestamp (6 secs)
                        GLib.Variant('(uuu)', (30, 10, 20))
                    ),
                    (
                        user_id,
                        UUID('5f58024f-3b99-47d3-a17f-1ec876acd97e').bytes,
                        7000000000,                    # event relative timestamp (7 secs)
                        GLib.Variant('(uuu)', (5, 2, 3))
                    ),
                    (
                        user_id,
                        UUID('16cfc671-5525-4a99-9eb9-4f6c074803a9').bytes,
                        8000000000,                    # event relative timestamp (8 secs)
                        None,                          # empty payload
                    ),
                    (
                        user_id,
                        UUID('2b5c044d-d819-4e2c-a3a6-c485c1ac371e').bytes,
                        32000000000,                   # event relative timestamp (32 secs)
                        GLib.Variant('s', 'org.gnome.Calendar')
                    ),
                    (
                        user_id,
                        UUID('c75af67f-cf2f-433d-a060-a670087d93a1').bytes,
                        36000000000,                   # event relative timestamp (36 secs)
                        None
                    ),
                    (
                        user_id,
                        UUID('6b1c1cfc-bc36-438c-0647-dacd5878f2b3').bytes,
                        9000000000,                    # event relative timestamp (9 secs)
                        GLib.Variant('s', image_id)
                    ),
                    (
                        user_id,
                        UUID('00d7bc1e-ec93-4c53-ae78-a6b40450be4a').bytes,
                        10000000000,                   # event relative timestamp (10 secs)
                        GLib.Variant('(sas)', ('org.glimpse_editor.Glimpse', ['photoshop.exe']))
                    ),
                    (
                        user_id,
                        UUID('7de69d43-5f6b-4bef-b5f3-a21295b79185').bytes,
                        11000000000,                   # event relative timestamp (11 secs)
                        GLib.Variant('(sas)', ('org.glimpse_editor.Glimpse', ['photoshop.exe']))
                    ),
                    (
                        user_id,
                        UUID('192f39dd-79b3-4497-99fa-9d8aea28760c').bytes,
                        12000000000,                   # event relative timestamp (12 secs)
                        GLib.Variant('(sas)', ('org.gnome.Calendar', ['gnome-calendar.deb']))
                    ),
                    (
                        user_id,
                        UUID('e98bf6d9-8511-44f9-a1bd-a1d0518934b9').bytes,
                        13000000000,                   # event relative timestamp (13 secs)
                        GLib.Variant('(sas)', ('org.gnome.Calendar', ['gnome-calendar.deb']))
                    ),
                    (
                        user_id,
                        UUID('0bba3340-52e3-41a2-854f-e6ed36621379').bytes,
                        17000000000,                   # event relative timestamp (17 secs)
                        GLib.Variant('as', ['gnome-calendar.deb'])
                    ),
                    (
                        user_id,
                        UUID('56be0b38-e47b-4578-9599-00ff9bda54bb').bytes,
                        3000000000,                    # event relative timestamp (3 secs)
                        None,                          # empty payload
                    ),
                    (
                        user_id,
                        UUID('abe7af92-6704-4d34-93cf-8f1b46eb09b8').bytes,
                        34000000000,                   # event relative timestamp (34 secs)
                        GLib.Variant('(ddbdd)', (5.4, 6.5, False, 7.6, 8.7))
                    ),
                    (
                        user_id,
                        UUID('abe7af92-6704-4d34-93cf-8f1b46eb09b8').bytes,
                        33000000000,                   # event relative timestamp (33 secs)
                        GLib.Variant('(ddbdd)', (1.0, 2.1, True, 3.2, 4.3))
                    ),
                    (
                        user_id,
                        UUID('eb0302d8-62e7-274b-365f-cd4e59103983').bytes,
                        35000000000,                   # event relative timestamp (35 secs)
                        GLib.Variant('a{ss}',
                                     {'city': 'City', 'state': 'State', 'facility': 'Facility'})
                    ),
                    (
                        user_id,
                        UUID('74ceec37-1f66-486e-99b0-d39b23daa113').bytes,
                        18000000000,                   # event relative timestamp (18 secs)
                        GLib.Variant('(ssssa{sv})', (
                            '1.16.0',
                            'Videos',
                            'decoder',
                            'audio/mp3',
                            {
                                "mpegaudioversion": GLib.Variant('i', 1),
                                "mpegversion": GLib.Variant('i', 1),
                                "layer": GLib.Variant('u', 3),
                            },
                        ))
                    ),
                    (
                        user_id,
                        UUID('fa82f422-a685-46e4-91a7-7b7bfb5b289f').bytes,
                        15000000000,                   # event relative timestamp (15 secs)
                        GLib.Variant('(ssssiiay)', (
                            'Samsung Electric Company 22',
                            'SAM',
                            'S22E450',
                            'serial number ignored',
                            500,
                            350,
                            b'edid data'
                        ))
                    ),
                    (
                        user_id,
                        UUID('5e8c3f40-22a2-4d5d-82f3-e3bf927b5b74').bytes,
                        14000000000,                   # event relative timestamp (14 secs)
                        GLib.Variant('(ssssiiay)', (
                            'Samsung Electric Company 22',
                            'SAM',
                            'S22E450',
                            'serial number ignored',
                            500,
                            350,
                            b'edid data'
                        ))
                    ),
                    (
                        user_id,
                        UUID('38eb48f8-e131-9b57-77c6-35e0590c82fd').bytes,
                        19000000000,                   # event relative timestamp (19 secs)
                        GLib.Variant('u', 123456)
                    ),
                    (
                        user_id,
                        UUID('1fa16a31-9225-467e-8502-e31806e9b4eb').bytes,
                        16000000000,                   # event relative timestamp (16 secs)
                        GLib.Variant('(sss)', ('Endless', '3.5.3', 'obsolete and ignored'))
                    ),
                    (
                        user_id,
                        UUID('ed57b607-4a56-47f1-b1e4-5dc3e74335ec').bytes,
                        21000000000,                   # event relative timestamp (21 secs)
                        GLib.Variant('a{sv}', {
                            'binary': GLib.Variant('s', '/app/bin/evolution'),
                            'signal': GLib.Variant('u', 11),
                        })
                    ),
                    (
                        user_id,
                        UUID('aee94585-07a2-4483-a090-25abda650b12').bytes,
                        22000000000,                   # event relative timestamp (22 secs)
                        GLib.Variant('u', 32000)
                    ),
                    (
                        user_id,
                        UUID('51640a4e-79aa-47ac-b7e2-d3106a06e129').bytes,
                        23000000000,                   # event relative timestamp (23 secs)
                        GLib.Variant('s', 'org.gnome.Calendar')
                    ),
                    (
                        user_id,
                        UUID('683b40a7-cac0-4f9a-994c-4b274693a0a0').bytes,
                        24000000000,                   # event relative timestamp (24 secs)
                        GLib.Variant('s', 'org.gnome.Evolution')
                    ),
                    (
                        user_id,
                        UUID('304662c0-fdce-46b8-aa39-d1beb097efcd').bytes,
                        36000000000,                   # event relative timestamp (36 secs)
                        None
                    ),
                    (
                        user_id,
                        UUID('99f48aac-b5a0-426d-95f4-18af7d081c4e').bytes,
                        25000000000,                   # event relative timestamp (25 secs)
                        GLib.Variant('(sssb)', (
                            'Asustek Computer Inc.',
                            'To Be Filled By O.E.M.',
                            'os/eos/amd64/eos3',
                            False
                        ))
                    ),
                    (
                        user_id,
                        UUID('9af2cc74-d6dd-423f-ac44-600a6eee2d96').bytes,
                        4000000000,                    # event relative timestamp (4 secs)
                        # Pack uptime payload into 2 levels of variants, that's how we receive them
                        GLib.Variant('v', GLib.Variant('(xx)', (2, 1))),
                    ),
                    (
                        user_id,
                        UUID('cf09194a-3090-4782-ab03-87b2f1515aed').bytes,
                        26000000000,                   # event relative timestamp (26 secs)
                        GLib.Variant('as', ['photoshop.exe'])
                    ),
                    (
                        user_id,
                        UUID('ef74310f-7c7e-ca05-0e56-3e495973070a').bytes,
                        27000000000,                   # event relative timestamp (27 secs)
                        GLib.Variant('u', 0)
                    ),
                ],
                [],                                    # aggregate events
                []                                     # sequence events
            )
        )
        assert request.is_normal_form()
        request_body = request.get_data_as_bytes().get_data()

        received_at = now + timedelta(minutes=2)
        received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
        received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

        record = received_at_timestamp_bytes + request_body

        # Send the event request to the Redis queue
        self.redis.lpush('test_singular_events', record)

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            request = dbsession.query(Request).one()
            assert request.send_number == 0
            assert request.machine_id == machine_id

            machine = dbsession.query(Machine).one()
            assert machine.machine_id == machine_id
            assert machine.image_id == image_id
            assert machine.image_product == 'eos'
            assert machine.image_branch == 'eos3.7'
            assert machine.image_arch == 'amd64'
            assert machine.image_platform == 'amd64'
            assert machine.image_timestamp == datetime(2019, 4, 19, 22, 56, 6, tzinfo=timezone.utc)
            assert machine.image_personality == 'base'

            corrupted_cache = dbsession.query(CacheIsCorrupt).one()
            assert corrupted_cache.request_id == request.id
            assert corrupted_cache.user_id == user_id
            assert corrupted_cache.occured_at == now - timedelta(seconds=2) + timedelta(seconds=1)

            corrupted_meta = dbsession.query(CacheMetadataIsCorrupt).one()
            assert corrupted_meta.request_id == request.id
            assert corrupted_meta.user_id == user_id
            assert corrupted_meta.occured_at == now - timedelta(seconds=2) + timedelta(seconds=2)

            panel = dbsession.query(ControlCenterPanelOpened).one()
            assert panel.request_id == request.id
            assert panel.user_id == user_id
            assert panel.occured_at == now - timedelta(seconds=2) + timedelta(seconds=28)
            assert panel.name == 'privacy'

            cpu_info = dbsession.query(CPUInfo).one()
            assert cpu_info.request_id == request.id
            assert cpu_info.user_id == user_id
            assert cpu_info.occured_at == now - timedelta(seconds=2) + timedelta(seconds=5)
            assert cpu_info.info == [{
                'model': 'Intel(R) Core(TM) i7-5600U CPU @ 2.60GHz',
                'cores': 4,
                'max_frequency': 2600.0,
            }]

            feed = dbsession.query(DiscoveryFeedClicked).one()
            assert feed.request_id == request.id
            assert feed.user_id == user_id
            assert feed.occured_at == now - timedelta(seconds=2) + timedelta(seconds=29)
            assert feed.info == {
                'app_id': 'org.gnome.Totem',
                'content_type': 'knowledge_video',
            }

            feed = dbsession.query(DiscoveryFeedClosed).one()
            assert feed.request_id == request.id
            assert feed.user_id == user_id
            assert feed.occured_at == now - timedelta(seconds=2) + timedelta(seconds=30)
            assert feed.info == {
                'closed_by': 'buttonclose',
                'time_open': '123',
            }

            feed = dbsession.query(DiscoveryFeedOpened).one()
            assert feed.request_id == request.id
            assert feed.user_id == user_id
            assert feed.occured_at == now - timedelta(seconds=2) + timedelta(seconds=31)
            assert feed.info == {
                'opened_by': 'shell_button',
                'language': 'fr_FR.UTF-8',
            }

            extra_space = dbsession.query(DiskSpaceExtra).one()
            assert extra_space.request_id == request.id
            assert extra_space.user_id == user_id
            assert extra_space.occured_at == now - timedelta(seconds=2) + timedelta(seconds=6)
            assert extra_space.total == 30
            assert extra_space.used == 10
            assert extra_space.free == 20

            root_space = dbsession.query(DiskSpaceSysroot).one()
            assert root_space.request_id == request.id
            assert root_space.user_id == user_id
            assert root_space.occured_at == now - timedelta(seconds=2) + timedelta(seconds=7)
            assert root_space.total == 5
            assert root_space.used == 2
            assert root_space.free == 3

            dual_boot = dbsession.query(DualBootBooted).one()
            assert dual_boot.request_id == request.id
            assert dual_boot.user_id == user_id
            assert dual_boot.occured_at == now - timedelta(seconds=2) + timedelta(seconds=8)

            unmaximized = dbsession.query(EndlessApplicationUnmaximized).one()
            assert unmaximized.request_id == request.id
            assert unmaximized.user_id == user_id
            assert unmaximized.occured_at == now - timedelta(seconds=2) + timedelta(seconds=32)
            assert unmaximized.app_id == 'org.gnome.Calendar'

            demo = dbsession.query(EnteredDemoMode).one()
            assert demo.request_id == request.id
            assert demo.user_id == user_id
            assert demo.occured_at == now - timedelta(seconds=2) + timedelta(seconds=36)

            image = dbsession.query(ImageVersion).one()
            assert image.request_id == request.id
            assert image.user_id == user_id
            assert image.occured_at == now - timedelta(seconds=2) + timedelta(seconds=9)
            assert image.image_id == image_id

            equivalent = dbsession.query(LaunchedEquivalentExistingFlatpak).one()
            assert equivalent.request_id == request.id
            assert equivalent.user_id == user_id
            assert equivalent.occured_at == now - timedelta(seconds=2) + timedelta(seconds=10)
            assert equivalent.replacement_app_id == 'org.glimpse_editor.Glimpse'
            assert equivalent.argv == ['photoshop.exe']

            equivalent = dbsession.query(LaunchedEquivalentInstallerForFlatpak).one()
            assert equivalent.request_id == request.id
            assert equivalent.user_id == user_id
            assert equivalent.occured_at == now - timedelta(seconds=2) + timedelta(seconds=11)
            assert equivalent.replacement_app_id == 'org.glimpse_editor.Glimpse'
            assert equivalent.argv == ['photoshop.exe']

            existing = dbsession.query(LaunchedExistingFlatpak).one()
            assert existing.request_id == request.id
            assert existing.user_id == user_id
            assert existing.occured_at == now - timedelta(seconds=2) + timedelta(seconds=12)
            assert existing.replacement_app_id == 'org.gnome.Calendar'
            assert existing.argv == ['gnome-calendar.deb']

            installer = dbsession.query(LaunchedInstallerForFlatpak).one()
            assert installer.request_id == request.id
            assert installer.user_id == user_id
            assert installer.occured_at == now - timedelta(seconds=2) + timedelta(seconds=13)
            assert installer.replacement_app_id == 'org.gnome.Calendar'
            assert installer.argv == ['gnome-calendar.deb']

            package = dbsession.query(LinuxPackageOpened).one()
            assert package.request_id == request.id
            assert package.user_id == user_id
            assert package.occured_at == now - timedelta(seconds=2) + timedelta(seconds=17)
            assert package.argv == ['gnome-calendar.deb']

            live_boot = dbsession.query(LiveUsbBooted).one()
            assert live_boot.request_id == request.id
            assert live_boot.user_id == user_id
            assert live_boot.occured_at == now - timedelta(seconds=2) + timedelta(seconds=3)

            locations = dbsession.query(Location).order_by(Location.altitude).all()

            location = locations[0]
            assert location.request_id == request.id
            assert location.user_id == user_id
            assert location.occured_at == now - timedelta(seconds=2) + timedelta(seconds=33)
            assert location.latitude == 1.0
            assert location.longitude == 2.1
            assert location.altitude == 3.2
            assert location.accuracy == 4.3

            location = locations[1]
            assert location.request_id == request.id
            assert location.user_id == user_id
            assert location.occured_at == now - timedelta(seconds=2) + timedelta(seconds=34)
            assert location.latitude == 5.4
            assert location.longitude == 6.5
            assert location.altitude is None
            assert location.accuracy == 8.7

            location = dbsession.query(LocationLabel).one()
            assert location.request_id == request.id
            assert location.user_id == user_id
            assert location.occured_at == now - timedelta(seconds=2) + timedelta(seconds=35)
            assert location.info == {'facility': 'Facility', 'city': 'City', 'state': 'State'}

            codec = dbsession.query(MissingCodec).one()
            assert codec.request_id == request.id
            assert codec.user_id == user_id
            assert codec.occured_at == now - timedelta(seconds=2) + timedelta(seconds=18)
            assert codec.gstreamer_version == '1.16.0'
            assert codec.app_name == 'Videos'
            assert codec.type == 'decoder'
            assert codec.name == 'audio/mp3'
            assert codec.extra_info == {
                "mpegaudioversion": 1,
                "mpegversion": 1,
                "layer": 3,
            }

            monitor = dbsession.query(MonitorConnected).one()
            assert monitor.request_id == request.id
            assert monitor.user_id == user_id
            assert monitor.occured_at == now - timedelta(seconds=2) + timedelta(seconds=15)
            assert monitor.display_name == 'Samsung Electric Company 22'
            assert monitor.display_vendor == 'SAM'
            assert monitor.display_product == 'S22E450'
            assert monitor.display_width == 500
            assert monitor.display_height == 350
            assert monitor.edid == b'edid data'

            monitor = dbsession.query(MonitorDisconnected).one()
            assert monitor.request_id == request.id
            assert monitor.user_id == user_id
            assert monitor.occured_at == now - timedelta(seconds=2) + timedelta(seconds=14)
            assert monitor.display_name == 'Samsung Electric Company 22'
            assert monitor.display_vendor == 'SAM'
            assert monitor.display_product == 'S22E450'
            assert monitor.display_width == 500
            assert monitor.display_height == 350
            assert monitor.edid == b'edid data'

            network = dbsession.query(NetworkId).one()
            assert network.request_id == request.id
            assert network.user_id == user_id
            assert network.occured_at == now - timedelta(seconds=2) + timedelta(seconds=19)
            assert network.network_id == 123456

            os = dbsession.query(OSVersion).one()
            assert os.request_id == request.id
            assert os.user_id == user_id
            assert os.occured_at == now - timedelta(seconds=2) + timedelta(seconds=16)
            assert os.version == '3.5.3'

            crash = dbsession.query(ProgramDumpedCore).one()
            assert crash.request_id == request.id
            assert crash.user_id == user_id
            assert crash.occured_at == now - timedelta(seconds=2) + timedelta(seconds=21)
            assert crash.info == {'binary': '/app/bin/evolution', 'signal': 11}

            ram = dbsession.query(RAMSize).one()
            assert ram.request_id == request.id
            assert ram.user_id == user_id
            assert ram.occured_at == now - timedelta(seconds=2) + timedelta(seconds=22)
            assert ram.total == 32000

            app_added = dbsession.query(ShellAppAddedToDesktop).one()
            assert app_added.request_id == request.id
            assert app_added.user_id == user_id
            assert app_added.occured_at == now - timedelta(seconds=2) + timedelta(seconds=23)
            assert app_added.app_id == 'org.gnome.Calendar'

            app_removed = dbsession.query(ShellAppRemovedFromDesktop).one()
            assert app_removed.request_id == request.id
            assert app_removed.user_id == user_id
            assert app_removed.occured_at == now - timedelta(seconds=2) + timedelta(seconds=24)
            assert app_removed.app_id == 'org.gnome.Evolution'

            underscan = dbsession.query(UnderscanEnabled).one()
            assert underscan.request_id == request.id
            assert underscan.user_id == user_id
            assert underscan.occured_at == now - timedelta(seconds=2) + timedelta(seconds=36)

            branch = dbsession.query(UpdaterBranchSelected).one()
            assert branch.request_id == request.id
            assert branch.user_id == user_id
            assert branch.occured_at == now - timedelta(seconds=2) + timedelta(seconds=25)
            assert branch.hardware_vendor == 'ASUS'
            assert branch.hardware_product == 'To Be Filled By O.E.M.'
            assert branch.ostree_branch == 'os/eos/amd64/eos3'
            assert not branch.on_hold

            uptime = dbsession.query(Uptime).one()
            assert uptime.request_id == request.id
            assert uptime.user_id == user_id
            assert uptime.occured_at == now - timedelta(seconds=2) + timedelta(seconds=4)
            assert uptime.accumulated_uptime == 2
            assert uptime.number_of_boots == 1

            windows_app = dbsession.query(WindowsAppOpened).one()
            assert windows_app.request_id == request.id
            assert windows_app.user_id == user_id
            assert windows_app.occured_at == now - timedelta(seconds=2) + timedelta(seconds=26)
            assert windows_app.argv == ['photoshop.exe']

            windows_tables = dbsession.query(WindowsLicenseTables).one()
            assert windows_tables.request_id == request.id
            assert windows_tables.user_id == user_id
            assert windows_tables.occured_at == now - timedelta(seconds=2) + timedelta(seconds=27)
            assert windows_tables.tables == 0

            assert dbsession.query(InvalidSingularEvent).count() == 0
            assert dbsession.query(UnknownSingularEvent).count() == 0

    def test_no_payload_singular_event_with_payload(self, capfd):
        from azafea.event_processors.endless.metrics.v2.model import LiveUsbBooted, Request

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Request, LiveUsbBooted)

        # Build a request as it would have been sent to us
        now = datetime.now(tz=timezone.utc)
        machine_id = 'ffffffffffffffffffffffffffffffff'
        user_id = 2000
        request = GLib.Variant(
            '(ixxaya(uayxmv)a(uayxxmv)a(uaya(xmv)))',
            (
                0,                                     # network send number
                2000000000,                            # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),     # request absolute timestamp
                bytes.fromhex(machine_id),
                [                                      # singular events
                    (
                        user_id,
                        UUID('56be0b38-e47b-4578-9599-00ff9bda54bb').bytes,
                        3000000000,                    # event relative timestamp (3 secs)
                        GLib.Variant('x', 2),          # non-empty payload, expected empty
                    ),
                ],
                [],                                    # aggregate events
                []                                     # sequence events
            )
        )
        assert request.is_normal_form()
        request_body = request.get_data_as_bytes().get_data()

        received_at = now + timedelta(minutes=2)
        received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
        received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

        record = received_at_timestamp_bytes + request_body

        # Send the event request to the Redis queue
        self.redis.lpush('test_no_payload_singular_event_with_payload', record)

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            request = dbsession.query(Request).one()
            assert request.send_number == 0
            assert request.machine_id == machine_id

            live_boot = dbsession.query(LiveUsbBooted).one()
            assert live_boot.request_id == request.id
            assert live_boot.user_id == user_id
            assert live_boot.occured_at == now - timedelta(seconds=2) + timedelta(seconds=3)

        capture = capfd.readouterr()
        assert ('Metric event 56be0b38-e47b-4578-9599-00ff9bda54bb takes no payload, but got '
                '<int64 2>') in capture.err

    def test_insert_machine_image_id(self):
        from azafea.event_processors.endless.metrics.v2.model import ImageVersion, Machine, Request

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Request, Machine, ImageVersion)

        # Build a request as it would have been sent to us
        now = datetime.now(tz=timezone.utc)
        machine_id = 'ffffffffffffffffffffffffffffffff'
        image_id = 'eosoem-eos3.7-amd64-amd64.190419-225606.base'
        user_id = 2000
        request = GLib.Variant(
            '(ixxaya(uayxmv)a(uayxxmv)a(uaya(xmv)))',
            (
                0,                                     # network send number
                2000000000,                            # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),     # request absolute timestamp
                bytes.fromhex(machine_id),
                [                                      # singular events
                    (
                        user_id,
                        UUID('6b1c1cfc-bc36-438c-0647-dacd5878f2b3').bytes,
                        1000000000,                    # event relative timestamp (1 secs)
                        GLib.Variant('s', image_id)
                    ),
                ],
                [],                                    # aggregate events
                []                                     # sequence events
            )
        )
        assert request.is_normal_form()
        request_body = request.get_data_as_bytes().get_data()

        received_at = now + timedelta(minutes=2)
        received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
        received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

        record = received_at_timestamp_bytes + request_body

        # Send the event request to the Redis queue
        self.redis.lpush('test_insert_machine_image_id', record)

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            request = dbsession.query(Request).one()

            image = dbsession.query(ImageVersion).one()
            assert image.request_id == request.id
            assert image.image_id == image_id

            machine = dbsession.query(Machine).one()
            assert machine.machine_id == request.machine_id
            assert machine.image_id == image_id
            assert machine.dualboot is False
            assert machine.live is False
            assert machine.demo is False

    def test_insert_machine_invalid_image_id(self, capfd):
        from azafea.event_processors.endless.metrics.v2.model import ImageVersion, Machine, Request

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Request, Machine, ImageVersion)

        # Build a request as it would have been sent to us
        now = datetime.now(tz=timezone.utc)
        machine_id = 'ffffffffffffffffffffffffffffffff'
        image_id = 'image'
        user_id = 2000
        request = GLib.Variant(
            '(ixxaya(uayxmv)a(uayxxmv)a(uaya(xmv)))',
            (
                0,                                     # network send number
                2000000000,                            # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),     # request absolute timestamp
                bytes.fromhex(machine_id),
                [                                      # singular events
                    (
                        user_id,
                        UUID('6b1c1cfc-bc36-438c-0647-dacd5878f2b3').bytes,
                        1000000000,                    # event relative timestamp (1 secs)
                        GLib.Variant('s', image_id)
                    ),
                ],
                [],                                    # aggregate events
                []                                     # sequence events
            )
        )
        assert request.is_normal_form()
        request_body = request.get_data_as_bytes().get_data()

        received_at = now + timedelta(minutes=2)
        received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
        received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

        record = received_at_timestamp_bytes + request_body

        # Send the event request to the Redis queue
        self.redis.lpush('test_insert_machine_invalid_image_id', record)

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            assert dbsession.query(Request).order_by(Request.id).count() == 0
            assert dbsession.query(Machine).order_by(Machine.id).count() == 0
            assert dbsession.query(ImageVersion).order_by(ImageVersion.id).count() == 0

        capture = capfd.readouterr()
        assert f'Invalid image id {image_id!r}: Did not match the expected format' in capture.err

    def test_insert_machine_demo(self):
        from azafea.event_processors.endless.metrics.v2.model import (
            EnteredDemoMode, Machine, Request)

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Request, Machine, EnteredDemoMode)

        # Build a request as it would have been sent to us
        now = datetime.now(tz=timezone.utc)
        machine_id = 'ffffffffffffffffffffffffffffffff'
        request = GLib.Variant(
            '(ixxaya(uayxmv)a(uayxxmv)a(uaya(xmv)))',
            (
                0,                                     # network send number
                2000000000,                            # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),     # request absolute timestamp
                bytes.fromhex(machine_id),
                [                                      # singular events
                    (
                        1001,
                        UUID('c75af67f-cf2f-433d-a060-a670087d93a1').bytes,
                        2000000000,                    # event relative timestamp (2 secs)
                        None
                    ),
                ],
                [],                                    # aggregate events
                []                                     # sequence events
            )
        )
        assert request.is_normal_form()
        request_body = request.get_data_as_bytes().get_data()

        received_at = now + timedelta(minutes=2)
        received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
        received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

        record = received_at_timestamp_bytes + request_body

        # Send the event request to the Redis queue
        self.redis.lpush('test_insert_machine_demo', record)

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            request = dbsession.query(Request).one()

            demo = dbsession.query(EnteredDemoMode).one()
            assert demo.request_id == request.id

            machine = dbsession.query(Machine).one()
            assert machine.machine_id == request.machine_id
            assert machine.image_id is None
            assert machine.dualboot is False
            assert machine.live is False
            assert machine.demo is True

    def test_insert_machine_dualboot(self):
        from azafea.event_processors.endless.metrics.v2.model import (
            DualBootBooted, Machine, Request)

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Request, Machine, DualBootBooted)

        # Build a request as it would have been sent to us
        now = datetime.now(tz=timezone.utc)
        machine_id = 'ffffffffffffffffffffffffffffffff'
        request = GLib.Variant(
            '(ixxaya(uayxmv)a(uayxxmv)a(uaya(xmv)))',
            (
                0,                                     # network send number
                2000000000,                            # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),     # request absolute timestamp
                bytes.fromhex(machine_id),
                [                                      # singular events
                    (
                        1001,
                        UUID('16cfc671-5525-4a99-9eb9-4f6c074803a9').bytes,
                        2000000000,                    # event relative timestamp (2 secs)
                        None
                    ),
                ],
                [],                                    # aggregate events
                []                                     # sequence events
            )
        )
        assert request.is_normal_form()
        request_body = request.get_data_as_bytes().get_data()

        received_at = now + timedelta(minutes=2)
        received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
        received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

        record = received_at_timestamp_bytes + request_body

        # Send the event request to the Redis queue
        self.redis.lpush('test_insert_machine_dualboot', record)

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            request = dbsession.query(Request).one()

            dualboot = dbsession.query(DualBootBooted).one()
            assert dualboot.request_id == request.id

            machine = dbsession.query(Machine).one()
            assert machine.machine_id == request.machine_id
            assert machine.image_id is None
            assert machine.dualboot is True
            assert machine.live is False
            assert machine.demo is False

    def test_insert_machine_live(self):
        from azafea.event_processors.endless.metrics.v2.model import (
            LiveUsbBooted, Machine, Request)

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Request, Machine, LiveUsbBooted)

        # Build a request as it would have been sent to us
        now = datetime.now(tz=timezone.utc)
        machine_id = 'ffffffffffffffffffffffffffffffff'
        request = GLib.Variant(
            '(ixxaya(uayxmv)a(uayxxmv)a(uaya(xmv)))',
            (
                0,                                     # network send number
                2000000000,                            # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),     # request absolute timestamp
                bytes.fromhex(machine_id),
                [                                      # singular events
                    (
                        1001,
                        UUID('56be0b38-e47b-4578-9599-00ff9bda54bb').bytes,
                        2000000000,                    # event relative timestamp (2 secs)
                        None
                    ),
                ],
                [],                                    # aggregate events
                []                                     # sequence events
            )
        )
        assert request.is_normal_form()
        request_body = request.get_data_as_bytes().get_data()

        received_at = now + timedelta(minutes=2)
        received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
        received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

        record = received_at_timestamp_bytes + request_body

        # Send the event request to the Redis queue
        self.redis.lpush('test_insert_machine_live', record)

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            request = dbsession.query(Request).one()

            live = dbsession.query(LiveUsbBooted).one()
            assert live.request_id == request.id

            machine = dbsession.query(Machine).one()
            assert machine.machine_id == request.machine_id
            assert machine.image_id is None
            assert machine.dualboot is False
            assert machine.live is True
            assert machine.demo is False

    def test_upsert_machine_image_id_then_dualboot(self):
        from azafea.event_processors.endless.metrics.v2.model import (
            DualBootBooted, ImageVersion, Machine, Request)

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Request, Machine, DualBootBooted, ImageVersion)

        # Build a request as it would have been sent to us
        now = datetime.now(tz=timezone.utc)
        machine_id = 'ffffffffffffffffffffffffffffffff'
        image_id = 'eosoem-eos3.7-amd64-amd64.190419-225606.base'
        user_id = 2000
        request = GLib.Variant(
            '(ixxaya(uayxmv)a(uayxxmv)a(uaya(xmv)))',
            (
                0,                                     # network send number
                2000000000,                            # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),     # request absolute timestamp
                bytes.fromhex(machine_id),
                [                                      # singular events
                    (
                        user_id,
                        UUID('6b1c1cfc-bc36-438c-0647-dacd5878f2b3').bytes,
                        1000000000,                    # event relative timestamp (1 secs)
                        GLib.Variant('s', image_id)
                    ),
                ],
                [],                                    # aggregate events
                []                                     # sequence events
            )
        )
        assert request.is_normal_form()
        request_body = request.get_data_as_bytes().get_data()

        received_at = now + timedelta(minutes=2)
        received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
        received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

        record = received_at_timestamp_bytes + request_body

        # Send the event request to the Redis queue
        self.redis.lpush('test_upsert_machine_image_id_then_dualboot', record)

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            request = dbsession.query(Request).one()

            image = dbsession.query(ImageVersion).one()
            assert image.request_id == request.id
            assert image.image_id == image_id

            machine = dbsession.query(Machine).one()
            assert machine.machine_id == request.machine_id
            assert machine.image_id == image_id
            assert machine.dualboot is False
            assert machine.live is False

        # Build a request as it would have been sent to us
        now = datetime.now(tz=timezone.utc)
        machine_id = 'ffffffffffffffffffffffffffffffff'
        request = GLib.Variant(
            '(ixxaya(uayxmv)a(uayxxmv)a(uaya(xmv)))',
            (
                0,                                     # network send number
                2000000000,                            # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),     # request absolute timestamp
                bytes.fromhex(machine_id),
                [                                      # singular events
                    (
                        1001,
                        UUID('16cfc671-5525-4a99-9eb9-4f6c074803a9').bytes,
                        2000000000,                    # event relative timestamp (2 secs)
                        None
                    ),
                ],
                [],                                    # aggregate events
                []                                     # sequence events
            )
        )
        assert request.is_normal_form()
        request_body = request.get_data_as_bytes().get_data()

        received_at = now + timedelta(minutes=2)
        received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
        received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

        record = received_at_timestamp_bytes + request_body

        # Send the event request to the Redis queue
        self.redis.lpush('test_upsert_machine_image_id_then_dualboot', record)

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            request = dbsession.query(Request).order_by(Request.received_at.desc()).first()

            dualboot = dbsession.query(DualBootBooted).one()
            assert dualboot.request_id == request.id

            machine = dbsession.query(Machine).one()
            assert machine.machine_id == request.machine_id
            assert machine.image_id == image_id
            assert machine.dualboot is True
            assert machine.live is False

    def test_upsert_machine_live_then_image_id(self):
        from azafea.event_processors.endless.metrics.v2.model import (
            ImageVersion, LiveUsbBooted, Machine, Request)

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Request, Machine, ImageVersion, LiveUsbBooted)

        # Build a request as it would have been sent to us
        now = datetime.now(tz=timezone.utc)
        machine_id = 'ffffffffffffffffffffffffffffffff'
        request = GLib.Variant(
            '(ixxaya(uayxmv)a(uayxxmv)a(uaya(xmv)))',
            (
                0,                                     # network send number
                2000000000,                            # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),     # request absolute timestamp
                bytes.fromhex(machine_id),
                [                                      # singular events
                    (
                        1001,
                        UUID('56be0b38-e47b-4578-9599-00ff9bda54bb').bytes,
                        2000000000,                    # event relative timestamp (2 secs)
                        None
                    ),
                ],
                [],                                    # aggregate events
                []                                     # sequence events
            )
        )
        assert request.is_normal_form()
        request_body = request.get_data_as_bytes().get_data()

        received_at = now + timedelta(minutes=2)
        received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
        received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

        record = received_at_timestamp_bytes + request_body

        # Send the event request to the Redis queue
        self.redis.lpush('test_upsert_machine_live_then_image_id', record)

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            request = dbsession.query(Request).one()

            live = dbsession.query(LiveUsbBooted).one()
            assert live.request_id == request.id

            machine = dbsession.query(Machine).one()
            assert machine.machine_id == request.machine_id
            assert machine.image_id is None
            assert machine.dualboot is False
            assert machine.live is True

        # Build a request as it would have been sent to us
        now = datetime.now(tz=timezone.utc)
        machine_id = 'ffffffffffffffffffffffffffffffff'
        image_id = 'eosoem-eos3.7-amd64-amd64.190419-225606.base'
        user_id = 2000
        request = GLib.Variant(
            '(ixxaya(uayxmv)a(uayxxmv)a(uaya(xmv)))',
            (
                0,                                     # network send number
                2000000000,                            # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),     # request absolute timestamp
                bytes.fromhex(machine_id),
                [                                      # singular events
                    (
                        user_id,
                        UUID('6b1c1cfc-bc36-438c-0647-dacd5878f2b3').bytes,
                        1000000000,                    # event relative timestamp (1 secs)
                        GLib.Variant('s', image_id)
                    ),
                ],
                [],                                    # aggregate events
                []                                     # sequence events
            )
        )
        assert request.is_normal_form()
        request_body = request.get_data_as_bytes().get_data()

        received_at = now + timedelta(minutes=2)
        received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
        received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

        record = received_at_timestamp_bytes + request_body

        # Send the event request to the Redis queue
        self.redis.lpush('test_upsert_machine_live_then_image_id', record)

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            request = dbsession.query(Request).order_by(Request.received_at.desc()).first()

            image = dbsession.query(ImageVersion).one()
            assert image.request_id == request.id
            assert image.image_id == image_id

            machine = dbsession.query(Machine).one()
            assert machine.machine_id == request.machine_id
            assert machine.image_id == image_id
            assert machine.dualboot is False
            assert machine.live is True

    def test_upsert_machine_location_then_image_id(self):
        from azafea.event_processors.endless.metrics.v2.model import (
            ImageVersion, LocationLabel, Machine, Request)

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Request, Machine, ImageVersion, LocationLabel)

        # Build a request as it would have been sent to us
        now = datetime.now(tz=timezone.utc)
        machine_id = 'ffffffffffffffffffffffffffffffff'
        request = GLib.Variant(
            '(ixxaya(uayxmv)a(uayxxmv)a(uaya(xmv)))',
            (
                0,                                     # network send number
                2000000000,                            # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),     # request absolute timestamp
                bytes.fromhex(machine_id),
                [                                      # singular events
                    (
                        1001,
                        UUID('eb0302d8-62e7-274b-365f-cd4e59103983').bytes,
                        2000000000,                    # event relative timestamp (2 secs)
                        GLib.Variant('a{ss}', {
                            'city': 'City', 'state': 'State', 'facility': 'Facility'})
                    ),
                ],
                [],                                    # aggregate events
                []                                     # sequence events
            )
        )
        assert request.is_normal_form()
        request_body = request.get_data_as_bytes().get_data()

        received_at = now + timedelta(minutes=2)
        received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
        received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

        record = received_at_timestamp_bytes + request_body

        # Send the event request to the Redis queue
        self.redis.lpush('test_upsert_machine_location_then_image_id', record)

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            request = dbsession.query(Request).one()

            location = dbsession.query(LocationLabel).one()
            assert location.request_id == request.id

            machine = dbsession.query(Machine).one()
            assert machine.machine_id == request.machine_id
            assert machine.image_id is None
            assert machine.location == {'city': 'City', 'state': 'State', 'facility': 'Facility'}
            assert machine.location_city == 'City'
            assert machine.location_state == 'State'
            assert machine.location_facility == 'Facility'

        # Build a request as it would have been sent to us
        now = datetime.now(tz=timezone.utc)
        machine_id = 'ffffffffffffffffffffffffffffffff'
        image_id = 'eosoem-eos3.7-amd64-amd64.190419-225606.base'
        user_id = 2000
        request = GLib.Variant(
            '(ixxaya(uayxmv)a(uayxxmv)a(uaya(xmv)))',
            (
                0,                                     # network send number
                2000000000,                            # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),     # request absolute timestamp
                bytes.fromhex(machine_id),
                [                                      # singular events
                    (
                        user_id,
                        UUID('6b1c1cfc-bc36-438c-0647-dacd5878f2b3').bytes,
                        1000000000,                    # event relative timestamp (1 secs)
                        GLib.Variant('s', image_id)
                    ),
                ],
                [],                                    # aggregate events
                []                                     # sequence events
            )
        )
        assert request.is_normal_form()
        request_body = request.get_data_as_bytes().get_data()

        received_at = now + timedelta(minutes=2)
        received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
        received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

        record = received_at_timestamp_bytes + request_body

        # Send the event request to the Redis queue
        self.redis.lpush('test_upsert_machine_location_then_image_id', record)

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            request = dbsession.query(Request).order_by(Request.received_at.desc()).first()

            image = dbsession.query(ImageVersion).one()
            assert image.request_id == request.id
            assert image.image_id == image_id

            machine = dbsession.query(Machine).one()
            assert machine.machine_id == request.machine_id
            assert machine.image_id == image_id
            assert machine.location == {'city': 'City', 'state': 'State', 'facility': 'Facility'}
            assert machine.location_city == 'City'
            assert machine.location_state == 'State'
            assert machine.location_facility == 'Facility'

    def test_upsert_machine_location_unknown_keys(self):
        from azafea.event_processors.endless.metrics.v2.model import (
            ImageVersion, LocationLabel, Machine, Request)

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Request, Machine, ImageVersion, LocationLabel)

        # Build a request as it would have been sent to us
        now = datetime.now(tz=timezone.utc)
        machine_id = 'ffffffffffffffffffffffffffffffff'
        request = GLib.Variant(
            '(ixxaya(uayxmv)a(uayxxmv)a(uaya(xmv)))',
            (
                0,                                     # network send number
                2000000000,                            # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),     # request absolute timestamp
                bytes.fromhex(machine_id),
                [                                      # singular events
                    (
                        1001,
                        UUID('eb0302d8-62e7-274b-365f-cd4e59103983').bytes,
                        2000000000,                    # event relative timestamp (2 secs)
                        GLib.Variant('a{ss}', {
                            'city': 'City', 'state': 'State', 'unknown': 'Unknown'})
                    ),
                ],
                [],                                    # aggregate events
                []                                     # sequence events
            )
        )
        assert request.is_normal_form()
        request_body = request.get_data_as_bytes().get_data()

        received_at = now + timedelta(minutes=2)
        received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
        received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

        record = received_at_timestamp_bytes + request_body

        # Send the event request to the Redis queue
        self.redis.lpush('test_upsert_machine_location_unknown_keys', record)

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            request = dbsession.query(Request).one()

            location = dbsession.query(LocationLabel).one()
            assert location.request_id == request.id

            machine = dbsession.query(Machine).one()
            assert machine.machine_id == request.machine_id
            assert machine.image_id is None
            assert machine.location == {'city': 'City', 'state': 'State', 'unknown': 'Unknown'}
            assert machine.location_city == 'City'
            assert machine.location_state == 'State'

    def test_upsert_machine_all_at_once(self):
        from azafea.event_processors.endless.metrics.v2.model import (
            DualBootBooted, EnteredDemoMode, ImageVersion, LiveUsbBooted, Machine, Request)

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Request, Machine, DualBootBooted, EnteredDemoMode, ImageVersion,
                           LiveUsbBooted)

        # Build a request as it would have been sent to us
        now = datetime.now(tz=timezone.utc)
        machine_id = 'ffffffffffffffffffffffffffffffff'
        image_id = 'eosoem-eos3.7-amd64-amd64.190419-225606.base'
        user_id = 2000
        request = GLib.Variant(
            '(ixxaya(uayxmv)a(uayxxmv)a(uaya(xmv)))',
            (
                0,                                     # network send number
                2000000000,                            # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),     # request absolute timestamp
                bytes.fromhex(machine_id),
                [                                      # singular events
                    (
                        user_id,
                        UUID('6b1c1cfc-bc36-438c-0647-dacd5878f2b3').bytes,
                        1000000000,                    # event relative timestamp (1 secs)
                        GLib.Variant('s', image_id)
                    ),
                    (
                        1001,
                        UUID('16cfc671-5525-4a99-9eb9-4f6c074803a9').bytes,
                        2000000000,                    # event relative timestamp (2 secs)
                        None
                    ),
                    (
                        1001,
                        UUID('56be0b38-e47b-4578-9599-00ff9bda54bb').bytes,
                        2000000000,                    # event relative timestamp (3 secs)
                        None
                    ),
                    (
                        1001,
                        UUID('c75af67f-cf2f-433d-a060-a670087d93a1').bytes,
                        2000000000,                    # event relative timestamp (4 secs)
                        None
                    ),
                ],
                [],                                    # aggregate events
                []                                     # sequence events
            )
        )
        assert request.is_normal_form()
        request_body = request.get_data_as_bytes().get_data()

        received_at = now + timedelta(minutes=2)
        received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
        received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

        record = received_at_timestamp_bytes + request_body

        # Send the event request to the Redis queue
        self.redis.lpush('test_upsert_machine_all_at_once', record)

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            request = dbsession.query(Request).one()

            live = dbsession.query(LiveUsbBooted).one()
            assert live.request_id == request.id

            machine = dbsession.query(Machine).one()
            assert machine.machine_id == request.machine_id
            assert machine.image_id == image_id
            assert machine.dualboot is True
            assert machine.live is True
            assert machine.demo is True

    def test_upsert_multiple_machines(self):
        from azafea.event_processors.endless.metrics.v2.model import (
            DualBootBooted, EnteredDemoMode, ImageVersion, LiveUsbBooted, Machine, Request)

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Request, Machine, DualBootBooted, EnteredDemoMode, ImageVersion,
                           LiveUsbBooted)

        # Build a request as it would have been sent to us, with an image version event
        now = datetime.now(tz=timezone.utc)
        machine_id_1 = 'ffffffffffffffffffffffffffffffff'
        image_id_1 = 'eosoem-eos3.7-amd64-amd64.190419-225606.base'
        user_id = 2000
        request = GLib.Variant(
            '(ixxaya(uayxmv)a(uayxxmv)a(uaya(xmv)))',
            (
                0,                                     # network send number
                2000000000,                            # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),     # request absolute timestamp
                bytes.fromhex(machine_id_1),
                [                                      # singular events
                    (
                        user_id,
                        UUID('6b1c1cfc-bc36-438c-0647-dacd5878f2b3').bytes,
                        1000000000,                    # event relative timestamp (1 secs)
                        GLib.Variant('s', image_id_1)
                    ),
                ],
                [],                                    # aggregate events
                []                                     # sequence events
            )
        )
        assert request.is_normal_form()
        request_body = request.get_data_as_bytes().get_data()

        received_at = now + timedelta(minutes=1)
        received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
        received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

        record = received_at_timestamp_bytes + request_body

        # Send the event request to the Redis queue
        self.redis.lpush('test_upsert_multiple_machines', record)

        # Build a request as it would have been sent to us, with an image version and a live events
        user_id = 2000
        request = GLib.Variant(
            '(ixxaya(uayxmv)a(uayxxmv)a(uaya(xmv)))',
            (
                0,                                     # network send number
                2000000000,                            # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),     # request absolute timestamp
                bytes.fromhex(machine_id_1),
                [                                      # singular events
                    (
                        user_id,
                        UUID('6b1c1cfc-bc36-438c-0647-dacd5878f2b3').bytes,
                        3000000000,                    # event relative timestamp (3 secs)
                        GLib.Variant('s', image_id_1)
                    ),
                    (
                        user_id,
                        UUID('56be0b38-e47b-4578-9599-00ff9bda54bb').bytes,
                        2000000000,                    # event relative timestamp (2 secs)
                        None
                    ),
                ],
                [],                                    # aggregate events
                []                                     # sequence events
            )
        )
        assert request.is_normal_form()
        request_body = request.get_data_as_bytes().get_data()

        received_at = now + timedelta(minutes=2)
        received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
        received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

        record = received_at_timestamp_bytes + request_body

        # Send the event request to the Redis queue
        self.redis.lpush('test_upsert_multiple_machines', record)

        # Build a request as it would have been sent to us, with a dualboot event
        machine_id_2 = '00000000000000000000000000000000'
        user_id = 2000
        request = GLib.Variant(
            '(ixxaya(uayxmv)a(uayxxmv)a(uaya(xmv)))',
            (
                0,                                     # network send number
                2000000000,                            # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),     # request absolute timestamp
                bytes.fromhex(machine_id_2),
                [                                      # singular events
                    (
                        user_id,
                        UUID('16cfc671-5525-4a99-9eb9-4f6c074803a9').bytes,
                        2000000000,                    # event relative timestamp (2 secs)
                        None
                    ),
                ],
                [],                                    # aggregate events
                []                                     # sequence events
            )
        )
        assert request.is_normal_form()
        request_body = request.get_data_as_bytes().get_data()

        received_at = now + timedelta(minutes=3)
        received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
        received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

        record = received_at_timestamp_bytes + request_body

        # Send the event request to the Redis queue
        self.redis.lpush('test_upsert_multiple_machines', record)

        # Build a request as it would have been sent to us, with a demo mode event
        user_id = 2000
        request = GLib.Variant(
            '(ixxaya(uayxmv)a(uayxxmv)a(uaya(xmv)))',
            (
                0,                                     # network send number
                2000000000,                            # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),     # request absolute timestamp
                bytes.fromhex(machine_id_2),
                [                                      # singular events
                    (
                        user_id,
                        UUID('c75af67f-cf2f-433d-a060-a670087d93a1').bytes,
                        2000000000,                    # event relative timestamp (2 secs)
                        None
                    ),
                ],
                [],                                    # aggregate events
                []                                     # sequence events
            )
        )
        assert request.is_normal_form()
        request_body = request.get_data_as_bytes().get_data()

        received_at = now + timedelta(minutes=3)
        received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
        received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

        record = received_at_timestamp_bytes + request_body

        # Send the event request to the Redis queue
        self.redis.lpush('test_upsert_multiple_machines', record)

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            requests = dbsession.query(Request).order_by(Request.received_at).all()
            assert len(requests) == 4
            assert requests[0].machine_id == machine_id_1
            assert requests[1].machine_id == machine_id_1
            assert requests[2].machine_id == machine_id_2
            assert requests[3].machine_id == machine_id_2

            machines = dbsession.query(Machine).order_by(Machine.id).all()
            assert len(machines) == 2
            assert machines[0].machine_id == machine_id_1
            assert machines[0].image_id == image_id_1
            assert machines[0].dualboot is False
            assert machines[0].live is True
            assert machines[0].demo is False
            assert machines[1].machine_id == machine_id_2
            assert machines[1].image_id is None
            assert machines[1].dualboot is True
            assert machines[1].live is False
            assert machines[1].demo is True

            assert dbsession.query(DualBootBooted).count() == 1
            assert dbsession.query(EnteredDemoMode).count() == 1
            assert dbsession.query(ImageVersion).count() == 2
            assert dbsession.query(LiveUsbBooted).count() == 1

    def test_deduplicate_dualboots(self):
        from azafea.event_processors.endless.metrics.v2.model import DualBootBooted, Request

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Request, DualBootBooted)

        # Build a request as it would have been sent to us
        now = datetime.now(tz=timezone.utc)
        machine_id = 'ffffffffffffffffffffffffffffffff'
        request = GLib.Variant(
            '(ixxaya(uayxmv)a(uayxxmv)a(uaya(xmv)))',
            (
                0,                                     # network send number
                2000000000,                            # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),     # request absolute timestamp
                bytes.fromhex(machine_id),
                [                                      # singular events
                    (
                        1001,
                        UUID('16cfc671-5525-4a99-9eb9-4f6c074803a9').bytes,
                        1000000000,                    # event relative timestamp (1 secs)
                        None
                    ),
                    (
                        1002,
                        UUID('16cfc671-5525-4a99-9eb9-4f6c074803a9').bytes,
                        2000000000,                    # event relative timestamp (2 secs)
                        None
                    ),
                ],
                [],                                    # aggregate events
                []                                     # sequence events
            )
        )
        assert request.is_normal_form()
        request_body = request.get_data_as_bytes().get_data()

        received_at = now + timedelta(minutes=2)
        received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
        received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

        record = received_at_timestamp_bytes + request_body

        # Send the event request to the Redis queue
        self.redis.lpush('test_deduplicate_dualboots', record)

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            assert dbsession.query(Request).order_by(Request.id).count() == 1

            dualboot = dbsession.query(DualBootBooted).one()
            assert dualboot.user_id == 1001

    def test_deduplicate_image_versions(self):
        from azafea.event_processors.endless.metrics.v2.model import ImageVersion, Request

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Request, ImageVersion)

        # Build a request as it would have been sent to us
        now = datetime.now(tz=timezone.utc)
        machine_id = 'ffffffffffffffffffffffffffffffff'
        image_id = 'eosoem-eos3.7-amd64-amd64.190419-225606.base'
        request = GLib.Variant(
            '(ixxaya(uayxmv)a(uayxxmv)a(uaya(xmv)))',
            (
                0,                                     # network send number
                2000000000,                            # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),     # request absolute timestamp
                bytes.fromhex(machine_id),
                [                                      # singular events
                    (
                        1001,
                        UUID('6b1c1cfc-bc36-438c-0647-dacd5878f2b3').bytes,
                        1000000000,                    # event relative timestamp (1 secs)
                        GLib.Variant('s', image_id)
                    ),
                    (
                        1002,
                        UUID('6b1c1cfc-bc36-438c-0647-dacd5878f2b3').bytes,
                        2000000000,                    # event relative timestamp (2 secs)
                        GLib.Variant('s', image_id)
                    ),
                ],
                [],                                    # aggregate events
                []                                     # sequence events
            )
        )
        assert request.is_normal_form()
        request_body = request.get_data_as_bytes().get_data()

        received_at = now + timedelta(minutes=2)
        received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
        received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

        record = received_at_timestamp_bytes + request_body

        # Send the event request to the Redis queue
        self.redis.lpush('test_deduplicate_image_versions', record)

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            assert dbsession.query(Request).order_by(Request.id).count() == 1

            image = dbsession.query(ImageVersion).order_by(ImageVersion.id).one()
            assert image.user_id == 1001

    def test_deduplicate_live_usb_booted(self):
        from azafea.event_processors.endless.metrics.v2.model import LiveUsbBooted, Request

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Request, LiveUsbBooted)

        # Build a request as it would have been sent to us
        now = datetime.now(tz=timezone.utc)
        machine_id = 'ffffffffffffffffffffffffffffffff'
        request = GLib.Variant(
            '(ixxaya(uayxmv)a(uayxxmv)a(uaya(xmv)))',
            (
                0,                                     # network send number
                2000000000,                            # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),     # request absolute timestamp
                bytes.fromhex(machine_id),
                [                                      # singular events
                    (
                        1001,
                        UUID('56be0b38-e47b-4578-9599-00ff9bda54bb').bytes,
                        1000000000,                    # event relative timestamp (1 secs)
                        None
                    ),
                    (
                        1002,
                        UUID('56be0b38-e47b-4578-9599-00ff9bda54bb').bytes,
                        2000000000,                    # event relative timestamp (2 secs)
                        None
                    ),
                ],
                [],                                    # aggregate events
                []                                     # sequence events
            )
        )
        assert request.is_normal_form()
        request_body = request.get_data_as_bytes().get_data()

        received_at = now + timedelta(minutes=2)
        received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
        received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

        record = received_at_timestamp_bytes + request_body

        # Send the event request to the Redis queue
        self.redis.lpush('test_deduplicate_live_usb_booted', record)

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            assert dbsession.query(Request).order_by(Request.id).count() == 1

            live = dbsession.query(LiveUsbBooted).one()
            assert live.user_id == 1001

    def test_deduplicate_multiple_events_per_request(self):
        # This test is a bit different from the others, because it does not push a request to Redis
        # for Azafea to process, it operates directly on the model.
        #
        # This is because the goal here is to test what happens when we process multiple metrics
        # requests in a single database transaction, but Azafea (currently) always opens a new
        # database transaction for each request.

        from azafea.event_processors.endless.metrics.v2.model import (
            DualBootBooted, ImageVersion, LiveUsbBooted, Request)

        self.run_subcommand('initdb')
        self.ensure_tables(Request, DualBootBooted, ImageVersion, LiveUsbBooted)

        occured_at = datetime.now(tz=timezone.utc)

        with self.db as dbsession:
            # Add a first request with 1 dualboot, 2 image version and 3 live usb events
            request = Request(sha512='whatever', received_at=occured_at,
                              absolute_timestamp=1, relative_timestamp=2, machine_id='machine1',
                              send_number=0)
            dbsession.add(request)

            image_id_1 = 'eos-eos3.6-amd64-amd64.190619-225606.base'
            dbsession.add(DualBootBooted(request=request, user_id=1001, occured_at=occured_at,
                                         payload=GLib.Variant('mv', None)))
            dbsession.add(ImageVersion(request=request, user_id=1001, occured_at=occured_at,
                                       payload=GLib.Variant('mv', GLib.Variant('s', image_id_1))))
            dbsession.add(ImageVersion(request=request, user_id=1002, occured_at=occured_at,
                                       payload=GLib.Variant('mv', GLib.Variant('s', image_id_1))))
            dbsession.add(LiveUsbBooted(request=request, user_id=1001, occured_at=occured_at,
                                        payload=GLib.Variant('mv', None)))
            dbsession.add(LiveUsbBooted(request=request, user_id=1002, occured_at=occured_at,
                                        payload=GLib.Variant('mv', None)))
            dbsession.add(LiveUsbBooted(request=request, user_id=1003, occured_at=occured_at,
                                        payload=GLib.Variant('mv', None)))

            # Add a second request with 1 dualboot, 2 image version and 3 live usb events
            request = Request(sha512='whatever2', received_at=occured_at,
                              absolute_timestamp=1, relative_timestamp=2, machine_id='machine2',
                              send_number=0)
            dbsession.add(request)

            image_id_2 = 'eos-eos3.7-amd64-amd64.191019-225606.base'
            dbsession.add(DualBootBooted(request=request, user_id=2001, occured_at=occured_at,
                                         payload=GLib.Variant('mv', None)))
            dbsession.add(ImageVersion(request=request, user_id=2001, occured_at=occured_at,
                                       payload=GLib.Variant('mv', GLib.Variant('s', image_id_2))))
            dbsession.add(ImageVersion(request=request, user_id=2002, occured_at=occured_at,
                                       payload=GLib.Variant('mv', GLib.Variant('s', image_id_2))))
            dbsession.add(LiveUsbBooted(request=request, user_id=2001, occured_at=occured_at,
                                        payload=GLib.Variant('mv', None)))
            dbsession.add(LiveUsbBooted(request=request, user_id=2002, occured_at=occured_at,
                                        payload=GLib.Variant('mv', None)))
            dbsession.add(LiveUsbBooted(request=request, user_id=2003, occured_at=occured_at,
                                        payload=GLib.Variant('mv', None)))

        with self.db as dbsession:
            requests = dbsession.query(Request).order_by(Request.id).all()
            assert len(requests) == 2

            dualboots = dbsession.query(DualBootBooted).order_by(DualBootBooted.request_id).all()
            assert len(dualboots) == 2
            assert dualboots[0].request_id == requests[0].id
            assert dualboots[0].user_id == 1001
            assert dualboots[1].request_id == requests[1].id
            assert dualboots[1].user_id == 2001

            images = dbsession.query(ImageVersion).order_by(ImageVersion.request_id).all()
            assert len(images) == 2
            assert images[0].image_id == image_id_1
            assert images[0].request_id == requests[0].id
            assert images[0].user_id == 1001
            assert images[1].image_id == image_id_2
            assert images[1].request_id == requests[1].id
            assert images[1].user_id == 2001

            live_usbs = dbsession.query(LiveUsbBooted).order_by(LiveUsbBooted.request_id).all()
            assert len(live_usbs) == 2
            assert live_usbs[0].request_id == requests[0].id
            assert live_usbs[0].user_id == 1001
            assert live_usbs[1].request_id == requests[1].id
            assert live_usbs[1].user_id == 2001

    def test_unknown_singular_events(self):
        from azafea.event_processors.endless.metrics.v2.model import Request, UnknownSingularEvent

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Request, UnknownSingularEvent)

        # Build a request as it would have been sent to us
        now = datetime.now(tz=timezone.utc)
        machine_id = 'ffffffffffffffffffffffffffffffff'
        user_id = 2000
        event_id = UUID('d3863909-8eff-43b6-9a33-ef7eda266195')
        request = GLib.Variant(
            '(ixxaya(uayxmv)a(uayxxmv)a(uaya(xmv)))',
            (
                0,                                     # network send number
                2000000000,                            # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),     # request absolute timestamp
                bytes.fromhex(machine_id),
                [                                      # singular events
                    (
                        user_id,
                        event_id.bytes,
                        3000000000,                    # event relative timestamp (3 secs)
                        None,                          # empty payload
                    ),
                    (
                        user_id,
                        event_id.bytes,
                        4000000000,                    # event relative timestamp (4 secs)
                        GLib.Variant('(xx)', (1, 2)),  # Non empty payload
                    ),
                ],
                [],                                    # aggregate events
                []                                     # sequence events
            )
        )
        assert request.is_normal_form()
        request_body = request.get_data_as_bytes().get_data()

        received_at = now + timedelta(minutes=2)
        received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
        received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

        record = received_at_timestamp_bytes + request_body

        # Send the event request to the Redis queue
        self.redis.lpush('test_unknown_singular_events', record)

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            request = dbsession.query(Request).one()
            assert request.send_number == 0
            assert request.machine_id == machine_id

            events = dbsession.query(UnknownSingularEvent).order_by(UnknownSingularEvent.occured_at)
            assert events.count() == 2

            events = events.all()

            event = events[0]
            assert event.request_id == request.id
            assert event.user_id == user_id
            assert event.occured_at == now - timedelta(seconds=2) + timedelta(seconds=3)
            assert event.event_id == event_id
            assert event.payload_data == b''

            event = events[1]
            assert event.request_id == request.id
            assert event.user_id == user_id
            assert event.occured_at == now - timedelta(seconds=2) + timedelta(seconds=4)
            assert event.event_id == event_id
            assert GLib.Variant.new_from_bytes(GLib.VariantType('mv'),
                                               GLib.Bytes.new(event.payload_data),
                                               False).unpack() == (1, 2)

    def test_invalid_singular_event_payload(self, capfd):
        from azafea.event_processors.endless.metrics.v2.model import (
            InvalidSingularEvent, Request, Uptime)

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Request, Uptime, InvalidSingularEvent)

        # Build a request as it would have been sent to us
        now = datetime.now(tz=timezone.utc)
        machine_id = 'ffffffffffffffffffffffffffffffff'
        user_id = 2000
        event_id = UUID('aee94585-07a2-4483-a090-25abda650b12')
        request = GLib.Variant(
            '(ixxaya(uayxmv)a(uayxxmv)a(uaya(xmv)))',
            (
                0,                                     # network send number
                2000000000,                            # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),     # request absolute timestamp
                bytes.fromhex(machine_id),
                [                                      # singular events
                    (
                        user_id,
                        event_id.bytes,
                        3000000000,                    # event relative timestamp (3 secs)
                        None,                          # empty payload, expected '(xx)'
                    ),
                    (
                        user_id,
                        event_id.bytes,
                        4000000000,                    # event relative timestamp (3 secs)
                        GLib.Variant('s', 'Up!'),      # 's' payload, expected '(xx)'
                    ),
                ],
                [],                                    # aggregate events
                []                                     # sequence events
            )
        )
        assert request.is_normal_form()
        request_body = request.get_data_as_bytes().get_data()

        received_at = now + timedelta(minutes=2)
        received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
        received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

        record = received_at_timestamp_bytes + request_body

        # Send the event request to the Redis queue
        self.redis.lpush('test_invalid_singular_event_payload', record)

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            request = dbsession.query(Request).one()
            assert request.send_number == 0
            assert request.machine_id == machine_id

            assert dbsession.query(Uptime).count() == 0

            events = dbsession.query(InvalidSingularEvent).order_by(InvalidSingularEvent.occured_at)
            assert events.count() == 2

            events = events.all()

            event = events[0]
            assert event.request_id == request.id
            assert event.user_id == user_id
            assert event.occured_at == now - timedelta(seconds=2) + timedelta(seconds=3)
            assert event.event_id == event_id
            assert event.payload_data == b''
            assert event.error == (
                'Metric event aee94585-07a2-4483-a090-25abda650b12 needs a u payload, '
                'but got none')

            event = events[1]
            assert event.request_id == request.id
            assert event.user_id == user_id
            assert event.occured_at == now - timedelta(seconds=2) + timedelta(seconds=4)
            assert event.event_id == event_id
            assert GLib.Variant.new_from_bytes(GLib.VariantType('mv'),
                                               GLib.Bytes.new(event.payload_data),
                                               False).unpack() == 'Up!'
            assert event.error == (
                'Metric event aee94585-07a2-4483-a090-25abda650b12 needs a u payload, '
                "but got 'Up!' (s)")

        capture = capfd.readouterr()
        assert 'An error occured while processing the event:' in capture.err
        assert ('Metric event aee94585-07a2-4483-a090-25abda650b12 needs a u payload, '
                'but got none') in capture.err
        assert ('Metric event aee94585-07a2-4483-a090-25abda650b12 needs a u payload, '
                "but got 'Up!' (s)") in capture.err

    def test_unknown_aggregate_events(self):
        from azafea.event_processors.endless.metrics.v2.model import (
            Request, UnknownAggregateEvent)

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Request, UnknownAggregateEvent)

        # Build a request as it would have been sent to us
        now = datetime.now(tz=timezone.utc)
        machine_id = 'ffffffffffffffffffffffffffffffff'
        user_id = 2000
        event_id = UUID('d3863909-8eff-43b6-9a33-ef7eda266195')
        request = GLib.Variant(
            '(ixxaya(uayxmv)a(uayxxmv)a(uaya(xmv)))',
            (
                0,                                     # network send number
                2000000000,                            # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),     # request absolute timestamp
                bytes.fromhex(machine_id),
                [],                                    # singular events
                [                                      # aggregate events
                    (
                        user_id,
                        event_id.bytes,
                        0,                             # count
                        3000000000,                    # event relative timestamp (3 secs)
                        None,                          # empty payload
                    ),
                    (
                        user_id,
                        event_id.bytes,
                        10,                            # count
                        4000000000,                    # event relative timestamp (4 secs)
                        GLib.Variant('(xx)', (1, 2)),  # Non empty payload
                    ),
                ],
                []                                     # sequence events
            )
        )
        assert request.is_normal_form()
        request_body = request.get_data_as_bytes().get_data()

        received_at = now + timedelta(minutes=2)
        received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
        received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

        record = received_at_timestamp_bytes + request_body

        # Send the event request to the Redis queue
        self.redis.lpush('test_unknown_aggregate_events', record)

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            request = dbsession.query(Request).one()
            assert request.send_number == 0
            assert request.machine_id == machine_id

            events = dbsession.query(UnknownAggregateEvent) \
                              .order_by(UnknownAggregateEvent.occured_at)
            assert events.count() == 2

            events = events.all()

            event = events[0]
            assert event.request_id == request.id
            assert event.user_id == user_id
            assert event.occured_at == now - timedelta(seconds=2) + timedelta(seconds=3)
            assert event.count == 0
            assert event.event_id == event_id
            assert event.payload_data == b''

            event = events[1]
            assert event.request_id == request.id
            assert event.user_id == user_id
            assert event.occured_at == now - timedelta(seconds=2) + timedelta(seconds=4)
            assert event.count == 10
            assert event.event_id == event_id
            assert GLib.Variant.new_from_bytes(GLib.VariantType('mv'),
                                               GLib.Bytes.new(event.payload_data),
                                               False).unpack() == (1, 2)

    def test_sequence_events(self):
        from azafea.event_processors.endless.metrics.v2.model import (
            Request, ShellAppIsOpen, UserIsLoggedIn)

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Request, ShellAppIsOpen)

        # Build a request as it would have been sent to us
        now = datetime.now(tz=timezone.utc)
        machine_id = 'ffffffffffffffffffffffffffffffff'
        user_id = 2000
        request = GLib.Variant(
            '(ixxaya(uayxmv)a(uayxxmv)a(uaya(xmv)))',
            (
                0,                                  # network send number
                2000000000,                         # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),  # request absolute timestamp
                bytes.fromhex(machine_id),
                [],                                 # singular events
                [],                                 # aggregate events
                [                                   # sequence events
                    (
                        user_id,
                        UUID('b5e11a3d-13f8-4219-84fd-c9ba0bf3d1f0').bytes,
                        [                           # events in the sequence
                            (
                                3000000000,         # event relative timestamp (3 secs)
                                GLib.Variant('s',   # app id
                                             'org.gnome.Podcasts'),
                            ),
                            (
                                120000000000,       # event relative timestamp (2 mins)
                                None,               # no payload on stop event
                            ),
                        ]
                    ),
                    (
                        user_id,
                        UUID('b5e11a3d-13f8-4219-84fd-c9ba0bf3d1f0').bytes,
                        [                           # events in the sequence
                            (
                                4000000000,         # event relative timestamp (4 secs)
                                GLib.Variant('s',   # app id
                                             'org.gnome.Fractal'),
                            ),
                            (
                                3600000000000,      # event relative timestamp (1 hour)
                                None,               # no payload on stop event
                            ),
                        ]
                    ),
                    (
                        0,
                        UUID('add052be-7b2a-4959-81a5-a7f45062ee98').bytes,
                        [
                            (
                                2000000000,         # event relative timestamp (5 secs)
                                GLib.Variant('u', user_id),
                            ),
                            (
                                3610000000000,      # event relative timestamp (1 hour 10 secs)
                                None,
                            ),
                        ]
                    ),
                ]
            )
        )
        assert request.is_normal_form()
        request_body = request.get_data_as_bytes().get_data()

        received_at = now + timedelta(minutes=2)
        received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
        received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

        record = received_at_timestamp_bytes + request_body

        # Send the event request to the Redis queue
        self.redis.lpush('test_sequence_events', record)

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            request = dbsession.query(Request).one()
            assert request.send_number == 0
            assert request.machine_id == machine_id

            events = dbsession.query(ShellAppIsOpen).order_by(ShellAppIsOpen.started_at)
            assert events.count() == 2

            events = events.all()

            podcasts = events[0]
            assert podcasts.request_id == request.id
            assert podcasts.user_id == user_id
            assert podcasts.started_at == now - timedelta(seconds=2) + timedelta(seconds=3)
            assert podcasts.stopped_at == now - timedelta(seconds=2) + timedelta(minutes=2)
            assert podcasts.app_id == 'org.gnome.Podcasts'

            fractal = events[1]
            assert fractal.request_id == request.id
            assert fractal.user_id == user_id
            assert fractal.started_at == now - timedelta(seconds=2) + timedelta(seconds=4)
            assert fractal.stopped_at == now - timedelta(seconds=2) + timedelta(hours=1)
            assert fractal.app_id == 'org.gnome.Fractal'

            logged_in = dbsession.query(UserIsLoggedIn).one()
            assert logged_in.request_id == request.id
            assert logged_in.user_id == 0
            assert logged_in.started_at == now - timedelta(seconds=2) + timedelta(seconds=2)
            assert logged_in.stopped_at == now - timedelta(seconds=2) + timedelta(hours=1,
                                                                                  seconds=10)
            assert logged_in.logged_in_user_id == user_id

    def test_unknown_sequence(self):
        from azafea.event_processors.endless.metrics.v2.model import Request, UnknownSequence

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Request, UnknownSequence)

        # Build a request as it would have been sent to us
        now = datetime.now(tz=timezone.utc)
        machine_id = 'ffffffffffffffffffffffffffffffff'
        user_id = 2000
        event_id = UUID('d3863909-8eff-43b6-9a33-ef7eda266195')
        request = GLib.Variant(
            '(ixxaya(uayxmv)a(uayxxmv)a(uaya(xmv)))',
            (
                0,                                         # network send number
                2000000000,                                # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),         # request absolute timestamp
                bytes.fromhex(machine_id),
                [],                                        # singular events
                [],                                        # aggregate events
                [                                          # sequence events
                    (
                        user_id,
                        event_id.bytes,
                        [                                  # events in the sequence
                            (
                                3000000000,                # event relative timestamp (3 secs)
                                GLib.Variant('s', 'foo'),  # app id
                            ),
                            (
                                60000000000,               # event relative timestamp (1 min)
                                None,                      # no payload on progress event
                            ),
                            (
                                120000000000,              # event relative timestamp (2 mins)
                                None,                      # no payload on progress event
                            ),
                            (
                                180000000000,              # event relative timestamp (3 mins)
                                None,                      # no payload on stop event
                            ),
                        ]
                    ),
                ]
            )
        )
        assert request.is_normal_form()
        request_body = request.get_data_as_bytes().get_data()

        received_at = now + timedelta(minutes=2)
        received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
        received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

        record = received_at_timestamp_bytes + request_body

        # Send the event request to the Redis queue
        self.redis.lpush('test_unknown_sequence', record)

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            request = dbsession.query(Request).one()
            assert request.send_number == 0
            assert request.machine_id == machine_id

            sequence = dbsession.query(UnknownSequence).one()
            assert sequence.request_id == request.id
            assert sequence.user_id == user_id
            assert GLib.Variant.new_from_bytes(GLib.VariantType('a(xmv)'),
                                               GLib.Bytes.new(sequence.payload_data),
                                               False).unpack() == [(3000000000, 'foo'),
                                                                   (60000000000, None),
                                                                   (120000000000, None),
                                                                   (180000000000, None)]

    def test_invalid_sequence(self, capfd):
        from azafea.event_processors.endless.metrics.v2.model import Request, InvalidSequence

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Request, InvalidSequence)

        # Build a request as it would have been sent to us
        now = datetime.now(tz=timezone.utc)
        machine_id = 'ffffffffffffffffffffffffffffffff'
        user_id = 2000
        event_id = UUID('b5e11a3d-13f8-4219-84fd-c9ba0bf3d1f0')
        request = GLib.Variant(
            '(ixxaya(uayxmv)a(uayxxmv)a(uaya(xmv)))',
            (
                0,                                         # network send number
                2000000000,                                # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),         # request absolute timestamp
                bytes.fromhex(machine_id),
                [],                                        # singular events
                [],                                        # aggregate events
                [                                          # sequence events
                    (
                        user_id,
                        event_id.bytes,
                        [                                  # INVALID: a single event in the sequence
                            (
                                3000000000,                # event relative timestamp (3 secs)
                                GLib.Variant('s', 'foo'),  # app id
                            )
                        ]
                    ),
                    (
                        user_id,
                        event_id.bytes,
                        [                                  # events in the sequence
                            (
                                3000000000,                # event relative timestamp (3 secs)
                                GLib.Variant('u', 42),     # INVALID: Should be an app id ('s')
                            ),
                            (
                                120000000000,              # event relative timestamp (2 mins)
                                None,                      # no payload on stop event
                            ),
                        ]
                    ),
                ]
            )
        )

        assert request.is_normal_form()
        request_body = request.get_data_as_bytes().get_data()

        received_at = now + timedelta(minutes=2)
        received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
        received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

        record = received_at_timestamp_bytes + request_body

        # Send the event request to the Redis queue
        self.redis.lpush('test_invalid_sequence', record)

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            request = dbsession.query(Request).one()
            assert request.send_number == 0
            assert request.machine_id == machine_id

            sequences = dbsession.query(InvalidSequence).order_by(InvalidSequence.event_id)
            assert sequences.count() == 2

            sequences = sequences.all()

            sequence = sequences[0]
            assert sequence.request_id == request.id
            assert sequence.user_id == user_id
            assert GLib.Variant.new_from_bytes(GLib.VariantType('a(xmv)'),
                                               GLib.Bytes.new(sequence.payload_data),
                                               False).unpack() == [(3000000000, 'foo')]

            sequence = sequences[1]
            assert sequence.request_id == request.id
            assert sequence.user_id == user_id
            assert GLib.Variant.new_from_bytes(GLib.VariantType('a(xmv)'),
                                               GLib.Bytes.new(sequence.payload_data),
                                               False).unpack() == [(3000000000, 42),
                                                                   (120000000000, None)]
            assert sequence.error == (
                'Metric event b5e11a3d-13f8-4219-84fd-c9ba0bf3d1f0 needs a s payload, '
                "but got uint32 42 (u)")

        capture = capfd.readouterr()
        assert 'An error occured while processing the sequence:' in capture.err
        assert ('Metric event b5e11a3d-13f8-4219-84fd-c9ba0bf3d1f0 needs a s payload, '
                "but got uint32 42 (u)") in capture.err

    def test_ignored_events(self):
        from azafea.event_processors.endless.metrics.v2.model import (
            Request, UnknownAggregateEvent, UnknownSequence, UnknownSingularEvent)

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Request)

        # Build a request as it would have been sent to us
        now = datetime.now(tz=timezone.utc)
        machine_id = 'ffffffffffffffffffffffffffffffff'
        user_id = 2000
        request = GLib.Variant(
            '(ixxaya(uayxmv)a(uayxxmv)a(uaya(xmv)))',
            (
                0,                                         # network send number
                2000000000,                                # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),         # request absolute timestamp
                bytes.fromhex(machine_id),
                [                                          # singular events
                    (
                        user_id,
                        UUID('566adb36-7701-4067-a971-a398312c2874').bytes,
                        1000000000,                        # event relative timestamp (1 sec)
                        None,                              # empty payload
                    ),
                ],
                [                                          # aggregate events
                    (
                        user_id,
                        UUID('9a0cf836-12cd-4887-95d8-e48ccdf6e552').bytes,
                        10,                                # count
                        2000000000,                        # event relative timestamp (2 secs)
                        None,
                    ),
                ],
                [                                          # sequence events
                    (
                        user_id,
                        UUID('ab839fd2-a927-456c-8c18-f1136722666b').bytes,
                        [                                  # events in the sequence
                            (
                                3000000000,                # event relative timestamp (3 secs)
                                GLib.Variant('u', 42),
                            ),
                            (
                                120000000000,              # event relative timestamp (2 mins)
                                None,
                            ),
                        ]
                    ),
                ]
            )
        )

        assert request.is_normal_form()
        request_body = request.get_data_as_bytes().get_data()

        received_at = now + timedelta(minutes=2)
        received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
        received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

        record = received_at_timestamp_bytes + request_body

        # Send the event request to the Redis queue
        self.redis.lpush('test_ignored_events', record)

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            request = dbsession.query(Request).one()
            assert request.send_number == 0
            assert request.machine_id == machine_id

            assert dbsession.query(UnknownAggregateEvent).count() == 0
            assert dbsession.query(UnknownSingularEvent).count() == 0
            assert dbsession.query(UnknownSequence).count() == 0

    def test_ignored_empty_payload_errors(self):
        from azafea.event_processors.endless.metrics.v2.model import (
            InvalidSequence, InvalidSingularEvent, Request, Uptime, UserIsLoggedIn)

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Request)

        # Build a request as it would have been sent to us
        now = datetime.now(tz=timezone.utc)
        machine_id = 'ffffffffffffffffffffffffffffffff'
        user_id = 2000
        request = GLib.Variant(
            '(ixxaya(uayxmv)a(uayxxmv)a(uaya(xmv)))',
            (
                0,                                         # network send number
                2000000000,                                # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),         # request absolute timestamp
                bytes.fromhex(machine_id),
                [                                          # singular events
                    (
                        user_id,
                        UUID('9af2cc74-d6dd-423f-ac44-600a6eee2d96').bytes,
                        1000000000,                        # event relative timestamp (1 sec)
                        None,                              # empty payload
                    ),
                ],
                [],                                        # aggregate events
                [                                          # sequence events
                    (
                        user_id,
                        UUID('add052be-7b2a-4959-81a5-a7f45062ee98').bytes,
                        [                                  # events in the sequence
                            (
                                3000000000,                # event relative timestamp (3 secs)
                                None,                      # INVALID: the payload should be a 'u'
                            ),
                            (
                                120000000000,              # event relative timestamp (2 mins)
                                None,
                            ),
                        ]
                    ),
                ]
            )
        )

        assert request.is_normal_form()
        request_body = request.get_data_as_bytes().get_data()

        received_at = now + timedelta(minutes=2)
        received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
        received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

        record = received_at_timestamp_bytes + request_body

        # Send the event request to the Redis queue
        self.redis.lpush('test_ignored_empty_payload_errors', record)

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            request = dbsession.query(Request).one()
            assert request.send_number == 0
            assert request.machine_id == machine_id

            assert dbsession.query(InvalidSingularEvent).count() == 0
            assert dbsession.query(Uptime).count() == 0

            assert dbsession.query(InvalidSequence).count() == 0
            assert dbsession.query(UserIsLoggedIn).count() == 0
