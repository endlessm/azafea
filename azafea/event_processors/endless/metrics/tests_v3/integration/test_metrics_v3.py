# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from datetime import datetime, timedelta, timezone, date
from hashlib import sha512
from uuid import UUID

from gi.repository import GLib

from azafea.tests.integration import IntegrationTest


class TestMetrics(IntegrationTest):
    handler_module = 'azafea.event_processors.endless.metrics.v3'

    def test_request(self):
        from azafea.event_processors.endless.metrics.v3.model import Channel, Request

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Channel, Request)

        # Build a request as it would have been sent to us
        now = datetime.now(tz=timezone.utc)
        absolute_timestamp = int(now.timestamp() * 1000000000)
        request = GLib.Variant(
            '(xxsa{ss}ya(aysxmv)a(ayssumv))',
            (
                2000000,   # request relative timestamp (2 secs)
                absolute_timestamp,  # Absolute timestamp
                'image_id',
                {},
                2,
                [],                                    # singular events
                []                                     # aggregate events
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
            channel = dbsession.query(Channel).one()
            assert channel.image_id == 'image_id'

            request = dbsession.query(Request).one()
            assert request.channel_id == channel.id
            assert request.received_at == received_at
            assert request.sha512 == sha512(request_body).hexdigest()
            assert request.relative_timestamp == 2000000
            assert request.absolute_timestamp == absolute_timestamp

    def test_invalid_request(self):
        from azafea.event_processors.endless.metrics.v3.model import Channel

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Channel)

        # Build an invalid request (GVariant not in its normal form)
        request = GLib.Variant.new_from_bytes(
            GLib.VariantType('(ixxaya(uayxmv)a(uayxmv)a(uaya(xmv)))'),
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
            assert dbsession.query(Channel).count() == 0

        # Ensure the request was pushed back into Redis
        assert self.redis.llen('errors-test_invalid_request') == 1
        assert self.redis.rpop('errors-test_invalid_request') == record

    def test_channel_not_duplicate(self):
        from azafea.event_processors.endless.metrics.v3.model import Channel

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Channel)

        # Build a request as it would have been sent to us
        now = datetime.now(tz=timezone.utc)
        request = GLib.Variant(
            '(xxsa{ss}ya(aysxmv)a(ayssumv))',
            (
                2000000,   # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),  # Absolute timestamp
                'image_id',
                {},
                2,
                [],                                    # singular events
                []                                     # aggregate events
            )
        )
        request_2 = GLib.Variant(
            '(xxsa{ss}ya(aysxmv)a(ayssumv))',
            (
                2000300,   # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),  # Absolute timestamp
                'image_id',
                {},
                2,
                [],                                    # singular events
                []                                     # aggregate events
            )
        )
        assert request.is_normal_form()
        request_body = request.get_data_as_bytes().get_data()
        request_body_2 = request_2.get_data_as_bytes().get_data()

        received_at = now + timedelta(minutes=2)
        received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
        received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

        record = received_at_timestamp_bytes + request_body
        record_2 = received_at_timestamp_bytes + request_body_2

        # Send the event request to the Redis queue
        self.redis.lpush('test_channel_not_duplicate', record)
        self.redis.lpush('test_channel_not_duplicate', record_2)

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            channel = dbsession.query(Channel).one()
            assert channel.image_id == 'image_id'

    def test_singular_events(self):
        from azafea.event_processors.endless.metrics.v3.model import (
            Channel, InvalidSingularEvent, UnknownSingularEvent, StartupFinished,
            LaunchedEquivalentExistingFlatpak, LaunchedEquivalentInstallerForFlatpak,
            LaunchedExistingFlatpak, LaunchedInstallerForFlatpak, LinuxPackageOpened,
            ParentalControlsBlockedFlatpakInstall, ParentalControlsBlockedFlatpakRun,
            ProgramDumpedCore, UpdaterFailure, ParentalControlsEnabled,
            ParentalControlsChanged, WindowsAppOpened, ComputerInformation
        )
        from azafea.event_processors.endless.metrics.v3.model import _base
        _base.IGNORED_EMPTY_PAYLOAD_ERRORS = ['9d03daad-f1ed-41a8-bc5a-6b532c075832']

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(
            Channel, InvalidSingularEvent, UnknownSingularEvent, StartupFinished,
            LaunchedEquivalentExistingFlatpak, LaunchedEquivalentInstallerForFlatpak,
            LaunchedExistingFlatpak, LaunchedInstallerForFlatpak, LinuxPackageOpened,
            ParentalControlsBlockedFlatpakInstall, ParentalControlsBlockedFlatpakRun,
            ProgramDumpedCore, UpdaterFailure, ParentalControlsEnabled,
            ParentalControlsChanged, WindowsAppOpened, ComputerInformation
        )

        # Build a request as it would have been sent to us
        now = datetime.now(tz=timezone.utc)
        image_id = 'eos-eos3.7-amd64-amd64.190419-225606.base'
        request = GLib.Variant(
            '(xxsa{ss}ya(aysxmv)a(ayssumv))',
            (
                2000000,   # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),  # Absolute timestamp
                image_id,
                {},
                2,
                [                         # singular events
                    (
                        UUID('bf7e8aed-2932-455c-a28e-d407cfd5aaba').bytes,
                        'os_version',
                        100,
                        GLib.Variant(
                            '(tttttt)',
                            (1000000, 1000000, 1000000, 1000000, 1000000, 1000000,)
                        )
                    ),
                    (
                        UUID('00d7bc1e-ec93-4c53-ae78-a6b40450be4a').bytes,
                        'os_version',
                        100,
                        GLib.Variant(
                            '(sas)',
                            ('replacement_app_id', ['argv1', 'argv2'])
                        )
                    ),
                    (
                        UUID('7de69d43-5f6b-4bef-b5f3-a21295b79185').bytes,
                        'os_version',
                        100,
                        GLib.Variant(
                            '(sas)',
                            ('replacement_app_id', ['argv1', 'argv2'])
                        )
                    ),
                    (
                        UUID('192f39dd-79b3-4497-99fa-9d8aea28760c').bytes,
                        'os_version',
                        100,
                        GLib.Variant(
                            '(sas)',
                            ('replacement_app_id', ['argv1', 'argv2'])
                        )
                    ),
                    (
                        UUID('e98bf6d9-8511-44f9-a1bd-a1d0518934b9').bytes,
                        'os_version',
                        100,
                        GLib.Variant(
                            '(sas)',
                            ('replacement_app_id', ['argv1', 'argv2'])
                        )
                    ),
                    (
                        UUID('0bba3340-52e3-41a2-854f-e6ed36621379').bytes,
                        'os_version',
                        100,
                        GLib.Variant(
                            'as',
                            ['argv1', 'argv2']
                        )
                    ),
                    (
                        UUID('9d03daad-f1ed-41a8-bc5a-6b532c075832').bytes,
                        'os_version',
                        100,
                        GLib.Variant(
                            's', 'app'
                        )
                    ),
                    # Test not register it if empty payload
                    (
                        UUID('9d03daad-f1ed-41a8-bc5a-6b532c075832').bytes,
                        'os_version',
                        100,
                        None
                    ),
                    (
                        UUID('afca2515-e9ce-43aa-b355-7663c770b4b6').bytes,
                        'os_version',
                        100,
                        GLib.Variant(
                            's', 'app'
                        )
                    ),
                    (
                        UUID('ed57b607-4a56-47f1-b1e4-5dc3e74335ec').bytes,
                        'os_version',
                        100,
                        GLib.Variant(
                            'a{sv}',
                            {
                                'binary': GLib.Variant('s', '/app/bin/evolution'),
                                'signal': GLib.Variant('u', 11),
                            }
                        )
                    ),
                    (
                        UUID('927d0f61-4890-4912-a513-b2cb0205908f').bytes,
                        'os_version',
                        100,
                        GLib.Variant(
                            '(ss)',
                            ('component', 'error_message')
                        )
                    ),
                    (
                        UUID('c227a817-808c-4fcb-b797-21002d17b69a').bytes,
                        'os_version',
                        100,
                        GLib.Variant(
                            'b',
                            True
                        )
                    ),
                    (
                        UUID('449ec188-cb7b-45d3-a0ed-291d943b9aa6').bytes,
                        'os_version',
                        100,
                        GLib.Variant(
                            'a{sv}',
                            {
                                'AppFilter': GLib.Variant(
                                    '(bas)', (True, ['app_filter_1', 'app_filter_2'])
                                ),
                                'OarsFilter': GLib.Variant(
                                    '(sa{ss})',
                                    (
                                        'oars-1.0',
                                        {'oars_filter_1': 'mild', 'oars_filter_2': 'moderate'}
                                    )
                                ),
                                'AllowUserInstallation': GLib.Variant('b', True),
                                'AllowSystemInstallation': GLib.Variant('b', True),
                                'IsAdministrator': GLib.Variant('b', True),
                                'IsInitialSetup': GLib.Variant('b', True),

                            }
                        )
                    ),
                    (
                        UUID('cf09194a-3090-4782-ab03-87b2f1515aed').bytes,
                        'os_version',
                        100,
                        GLib.Variant(
                            'as',
                            ['argv1', 'argv2']
                        )
                    ),
                    (
                        UUID('81f303aa-448d-443d-97f9-8d8a9169321c').bytes,
                        'os_version',
                        100,
                        GLib.Variant(
                            '(uuuua(sqd))',
                            (
                                40000,
                                50000,
                                6000,
                                600000,
                                [('model_1', 8, 14.5), ('model_2', 8, 14.5)]
                            )
                        )
                    )
                ],
                [],                       # aggregate events
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
            channel = dbsession.query(Channel).one()
            assert channel.image_id == image_id
            assert not channel.dual_boot
            assert channel.live
            assert channel.site == {}

            startup_finished = dbsession.query(StartupFinished).one()
            assert startup_finished.os_version == 'os_version'
            assert startup_finished.firmware == 1000000
            assert startup_finished.loader == 1000000
            assert startup_finished.kernel == 1000000
            assert startup_finished.initrd == 1000000
            assert startup_finished.userspace == 1000000
            assert startup_finished.total == 1000000

            launched_equivalent_existing_flatpak = dbsession.query(
                LaunchedEquivalentExistingFlatpak
            ).one()
            assert launched_equivalent_existing_flatpak.os_version == 'os_version'
            assert launched_equivalent_existing_flatpak.replacement_app_id == 'replacement_app_id'
            assert launched_equivalent_existing_flatpak.argv == ['argv1', 'argv2']

            launched_equivalent_installer_flatpak = dbsession.query(
                LaunchedEquivalentInstallerForFlatpak
            ).one()
            assert launched_equivalent_installer_flatpak.os_version == 'os_version'
            assert launched_equivalent_installer_flatpak.replacement_app_id == 'replacement_app_id'
            assert launched_equivalent_installer_flatpak.argv == ['argv1', 'argv2']

            launched_existing_flatpak = dbsession.query(
                LaunchedExistingFlatpak
            ).one()
            assert launched_existing_flatpak.os_version == 'os_version'
            assert launched_existing_flatpak.replacement_app_id == 'replacement_app_id'
            assert launched_existing_flatpak.argv == ['argv1', 'argv2']

            launched_installer_flatpak = dbsession.query(
                LaunchedInstallerForFlatpak
            ).one()
            assert launched_installer_flatpak.os_version == 'os_version'
            assert launched_installer_flatpak.replacement_app_id == 'replacement_app_id'
            assert launched_installer_flatpak.argv == ['argv1', 'argv2']

            linux_package_opened = dbsession.query(
                LinuxPackageOpened
            ).one()
            assert linux_package_opened.os_version == 'os_version'
            assert linux_package_opened.argv == ['argv1', 'argv2']

            parental_controls_blocked_flatpak_install = dbsession.query(
                ParentalControlsBlockedFlatpakInstall
            ).one()
            assert parental_controls_blocked_flatpak_install.os_version == 'os_version'
            assert parental_controls_blocked_flatpak_install.app == 'app'

            parental_controls_blocked_flatpak_run = dbsession.query(
                ParentalControlsBlockedFlatpakRun
            ).one()
            assert parental_controls_blocked_flatpak_run.os_version == 'os_version'
            assert parental_controls_blocked_flatpak_run.app == 'app'

            program_dumped_core = dbsession.query(ProgramDumpedCore).one()
            assert program_dumped_core.os_version == 'os_version'
            assert program_dumped_core.info == {
                'binary': '/app/bin/evolution',
                'signal': 11,
            }

            updater_failure = dbsession.query(UpdaterFailure).one()
            assert updater_failure.os_version == 'os_version'
            assert updater_failure.component == 'component'
            assert updater_failure.error_message == 'error_message'

            parental_controls_enabled = dbsession.query(ParentalControlsEnabled).one()
            assert parental_controls_enabled.os_version == 'os_version'
            assert parental_controls_enabled.enabled

            parental_controls_changed = dbsession.query(ParentalControlsChanged).one()
            assert parental_controls_changed.os_version == 'os_version'
            assert parental_controls_changed.app_filter_is_whitelist
            assert parental_controls_changed.app_filter == ['app_filter_1', 'app_filter_2']
            assert parental_controls_changed.oars_filter == {
                'oars_filter_1': 'mild',
                'oars_filter_2': 'moderate',
            }
            assert parental_controls_changed.allow_user_installation
            assert parental_controls_changed.allow_system_installation
            assert parental_controls_changed.is_administrator
            assert parental_controls_changed.is_initial_setup

            windows_app_opened = dbsession.query(
                WindowsAppOpened
            ).one()
            assert windows_app_opened.os_version == 'os_version'
            assert windows_app_opened.argv == ['argv1', 'argv2']

            computer_information = dbsession.query(
                ComputerInformation
            ).one()
            assert computer_information.os_version == 'os_version'
            assert computer_information.total_ram == 40000
            assert computer_information.total_disk == 50000
            assert computer_information.used_disk == 6000
            assert computer_information.free_disk == 600000
            assert computer_information.info == [
                {'model': 'model_1', 'cores': 8, 'max_frequency': 14.5},
                {'model': 'model_2', 'cores': 8, 'max_frequency': 14.5}
            ]

            assert dbsession.query(InvalidSingularEvent).count() == 0
            assert dbsession.query(UnknownSingularEvent).count() == 0

    def test_aggregate_events(self):
        from azafea.event_processors.endless.metrics.v3.model import (
            Channel, DailyAppUsage, MonthlyAppUsage, DailyUsers,
            MonthlyUsers, DailySessionTime, MonthlySessionTime
        )
        from azafea.event_processors.endless.metrics.v3.model import _base
        _base.IGNORED_EMPTY_PAYLOAD_ERRORS = ['49d0451a-f706-4f50-81d2-70cc0ec923a4']
        self.run_subcommand('initdb')
        self.ensure_tables(
            Channel, DailyAppUsage, MonthlyAppUsage, DailyUsers,
            MonthlyUsers, DailySessionTime, MonthlySessionTime
        )
        now = datetime.now(tz=timezone.utc)
        image_id = 'eos-eos3.7-amd64-amd64.190419-225606.base'

        request = GLib.Variant(
            '(xxsa{ss}ya(aysxmv)a(ayssumv))',
            (
                2000000,   # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),  # Absolute timestamp
                image_id,
                {},
                2,
                [],                         # singular events
                [                           # aggregate events
                    (
                        UUID('49d0451a-f706-4f50-81d2-70cc0ec923a4').bytes,
                        'os_version',
                        '2020-06-15',
                        1000,
                        GLib.Variant('s', 'app_id')
                    ),
                    # test ignore empty payload
                    (
                        UUID('49d0451a-f706-4f50-81d2-70cc0ec923a4').bytes,
                        'os_version',
                        '2020-06-15',
                        1000,
                        None
                    ),
                    (
                        UUID('f2839256-ccbf-45ec-a5b0-fdc99c3f0a2b').bytes,
                        'os_version',
                        '2020-06-15',
                        1000,
                        GLib.Variant('s', 'app_id')
                    ),
                    (
                        UUID('a3826320-9192-446a-8886-e2129c0ce302').bytes,
                        'os_version',
                        '2020-06-15',
                        1000,
                        None,
                    ),
                    (
                        UUID('86cacd30-e1c0-4c66-8f1e-99fdb4c3546f').bytes,
                        'os_version',
                        '2020-06-15',
                        1000,
                        None,
                    ),
                    (
                        UUID('5dc0b53c-93f9-4df0-ad6f-bd25e9fe638f').bytes,
                        'os_version',
                        '2020-06-15',
                        1000,
                        None,
                    ),
                    (
                        UUID('8023ae8e-f0c7-4fee-bc00-2d6b28061fce').bytes,
                        'os_version',
                        '2020-06-15',
                        1000,
                        None,
                    ),
                ],
            )
        )
        assert request.is_normal_form()
        request_body = request.get_data_as_bytes().get_data()

        received_at = now + timedelta(minutes=2)
        received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
        received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

        record = received_at_timestamp_bytes + request_body

        self.redis.lpush('test_aggregate_events', record)

        # Run Azafea so it processes the event
        self.run_azafea()

        with self.db as dbsession:
            channel = dbsession.query(Channel).one()
            assert channel.image_id == image_id
            assert not channel.dual_boot
            assert channel.live
            assert channel.site == {}

            daily_app_usage = dbsession.query(DailyAppUsage).one()
            assert daily_app_usage.channel_id == channel.id
            assert daily_app_usage.count == 1000
            assert daily_app_usage.period_start.isoformat() == '2020-06-15'
            assert daily_app_usage.app_id == 'app_id'

            monthly_app_usage = dbsession.query(MonthlyAppUsage).one()
            assert monthly_app_usage.channel_id == channel.id
            assert monthly_app_usage.count == 1000
            assert monthly_app_usage.period_start.isoformat() == '2020-06-15'
            assert monthly_app_usage.app_id == 'app_id'

            daily_users = dbsession.query(DailyUsers).one()
            assert daily_users.channel_id == channel.id
            assert daily_users.count == 1000
            assert daily_users.period_start.isoformat() == '2020-06-15'

            monthly_users = dbsession.query(MonthlyUsers).one()
            assert monthly_users.channel_id == channel.id
            assert monthly_users.count == 1000
            assert monthly_users.period_start.isoformat() == '2020-06-15'

            daily_session_time = dbsession.query(DailySessionTime).one()
            assert daily_session_time.channel_id == channel.id
            assert daily_session_time.count == 1000
            assert daily_session_time.period_start.isoformat() == '2020-06-15'
            monthly_session_time = dbsession.query(MonthlySessionTime).one()
            assert monthly_session_time.channel_id == channel.id
            assert monthly_session_time.count == 1000
            assert monthly_session_time.period_start.isoformat() == '2020-06-15'

    def test_ignored_event(self):
        from azafea.event_processors.endless.metrics.v3.model import (
            Channel, InvalidSingularEvent, UnknownSingularEvent,
            InvalidAggregateEvent, UnknownAggregateEvent, StartupFinished,
            LaunchedEquivalentExistingFlatpak, LaunchedEquivalentInstallerForFlatpak,
            LaunchedExistingFlatpak, LaunchedInstallerForFlatpak, LinuxPackageOpened,
            ParentalControlsBlockedFlatpakInstall, ParentalControlsBlockedFlatpakRun,
            ProgramDumpedCore, UpdaterFailure, ParentalControlsEnabled,
            ParentalControlsChanged, WindowsAppOpened, DailyAppUsage, MonthlyAppUsage,
            DailyUsers, MonthlyUsers, DailySessionTime, MonthlySessionTime
        )
        self.run_subcommand('initdb')
        self.ensure_tables(
            Channel, InvalidSingularEvent, UnknownSingularEvent,
            InvalidAggregateEvent, UnknownAggregateEvent, StartupFinished,
            LaunchedEquivalentExistingFlatpak, LaunchedEquivalentInstallerForFlatpak,
            LaunchedExistingFlatpak, LaunchedInstallerForFlatpak, LinuxPackageOpened,
            ParentalControlsBlockedFlatpakInstall, ParentalControlsBlockedFlatpakRun,
            ProgramDumpedCore, UpdaterFailure, ParentalControlsEnabled,
            ParentalControlsChanged, WindowsAppOpened, DailyAppUsage, MonthlyAppUsage,
            DailyUsers, MonthlyUsers, DailySessionTime, MonthlySessionTime
        )
        now = datetime.now(tz=timezone.utc)
        image_id = 'eos-eos3.7-amd64-amd64.190419-225606.base'

        request = GLib.Variant(
            '(xxsa{ss}ya(aysxmv)a(ayssumv))',
            (
                2000000,   # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),  # Absolute timestamp
                image_id,
                {},
                2,
                [                           # singular events
                    (
                        UUID('005096c4-9444-48c6-844b-6cb693c15235').bytes,
                        'os_version',
                        100,
                        GLib.Variant(
                            '(sas)',
                            ('replacement_app_id', ['argv1', 'argv2'])
                        )
                    ),
                ],
                [                           # aggregate events
                    (
                        UUID('337fa66d-5163-46ae-ab20-dc605b5d7307').bytes,
                        'os_version',
                        '2020-06-15',
                        1000,
                        GLib.Variant('s', 'app_id')
                    ),
                ],
            )
        )
        assert request.is_normal_form()
        request_body = request.get_data_as_bytes().get_data()

        received_at = now + timedelta(minutes=2)
        received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
        received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

        record = received_at_timestamp_bytes + request_body

        self.redis.lpush('test_ignored_event', record)

        # Run Azafea so it processes the event
        self.run_azafea()

        with self.db as dbsession:
            assert dbsession.query(Channel).count() == 1

            assert dbsession.query(InvalidSingularEvent).count() == 0
            assert dbsession.query(UnknownSingularEvent).count() == 0
            assert dbsession.query(InvalidAggregateEvent).count() == 0
            assert dbsession.query(UnknownAggregateEvent).count() == 0
            assert dbsession.query(StartupFinished).count() == 0
            assert dbsession.query(InvalidSingularEvent).count() == 0
            assert dbsession.query(LaunchedEquivalentExistingFlatpak).count() == 0
            assert dbsession.query(LaunchedEquivalentInstallerForFlatpak).count() == 0
            assert dbsession.query(LaunchedExistingFlatpak).count() == 0
            assert dbsession.query(LaunchedInstallerForFlatpak).count() == 0
            assert dbsession.query(LinuxPackageOpened).count() == 0
            assert dbsession.query(ParentalControlsBlockedFlatpakInstall).count() == 0
            assert dbsession.query(ParentalControlsBlockedFlatpakRun).count() == 0
            assert dbsession.query(ProgramDumpedCore).count() == 0
            assert dbsession.query(UpdaterFailure).count() == 0
            assert dbsession.query(ParentalControlsEnabled).count() == 0
            assert dbsession.query(ParentalControlsChanged).count() == 0
            assert dbsession.query(WindowsAppOpened).count() == 0
            assert dbsession.query(DailyAppUsage).count() == 0
            assert dbsession.query(MonthlyAppUsage).count() == 0
            assert dbsession.query(DailyUsers).count() == 0
            assert dbsession.query(MonthlyUsers).count() == 0
            assert dbsession.query(DailySessionTime).count() == 0
            assert dbsession.query(MonthlySessionTime).count() == 0

    def test_unknown_singular_events(self):
        from azafea.event_processors.endless.metrics.v3.model import (
            Channel, UnknownSingularEvent
        )

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Channel, UnknownSingularEvent)

        # Build a request as it would have been sent to us
        now = datetime.now(tz=timezone.utc)
        image_id = 'eos-eos3.7-amd64-amd64.190419-225606.base'
        event_id = UUID('d3863909-8eff-43b6-9a33-ef7eda266195')
        request = GLib.Variant(
            '(xxsa{ss}ya(aysxmv)a(ayssumv))',
            (
                2000000,   # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),  # Absolute timestamp
                image_id,
                {},
                2,
                [                                      # singular events
                    (
                        event_id.bytes,
                        'os_version',
                        3000000000,                    # event relative timestamp (3 secs)
                        None,                          # empty payload
                    ),
                    (
                        event_id.bytes,
                        'os_version',
                        4000000000,                    # event relative timestamp (4 secs)
                        GLib.Variant('(xx)', (1, 2)),  # Non empty payload
                    ),
                ],
                [],                                   # aggregate events
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
            channel = dbsession.query(Channel).one()

            events = dbsession.query(UnknownSingularEvent).order_by(UnknownSingularEvent.occured_at)
            assert events.count() == 2

            events = events.all()

            event = events[0]
            assert event.channel == channel
            assert event.event_id == event_id
            assert event.payload_data == b''

            event = events[1]
            assert event.channel_id == channel.id
            assert event.event_id == event_id
            assert GLib.Variant.new_from_bytes(GLib.VariantType('mv'),
                                               GLib.Bytes.new(event.payload_data),
                                               False).unpack() == (1, 2)

    def test_invalid_singular_event_payload(self, capfd):
        from azafea.event_processors.endless.metrics.v3.model import (
            InvalidSingularEvent, Channel)

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Channel, InvalidSingularEvent)

        # Build a request as it would have been sent to us
        now = datetime.now(tz=timezone.utc)
        image_id = 'eos-eos3.7-amd64-amd64.190419-225606.base'
        event_id = UUID('00d7bc1e-ec93-4c53-ae78-a6b40450be4a')
        request = GLib.Variant(
            '(xxsa{ss}ya(aysxmv)a(ayssumv))',
            (
                2000000,   # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),  # Absolute timestamp
                image_id,
                {},
                2,
                [                                      # singular events
                    (
                        event_id.bytes,
                        'os_version',
                        3000000000,                    # event relative timestamp (3 secs)
                        None,                          # empty payload, expected '(xx)'
                    ),
                    (
                        event_id.bytes,
                        'os_version',
                        4000000000,                    # event relative timestamp (3 secs)
                        GLib.Variant('s', 'Up!'),      # 's' payload, expected '(xx)'
                    ),
                ],
                [],                                    # aggregate events
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
            channel = dbsession.query(Channel).one()

            events = dbsession.query(InvalidSingularEvent).order_by(InvalidSingularEvent.occured_at)
            assert events.count() == 2

            events = events.all()

            event = events[0]
            assert event.channel_id == channel.id
            assert event.event_id == event_id
            assert event.payload_data == b''
            assert event.error == (
                'Metric event 00d7bc1e-ec93-4c53-ae78-a6b40450be4a needs a (sas) payload, '
                'but got none')

            event = events[1]
            assert event.channel_id == channel.id
            assert event.event_id == event_id
            assert GLib.Variant.new_from_bytes(GLib.VariantType('mv'),
                                               GLib.Bytes.new(event.payload_data),
                                               False).unpack() == 'Up!'
            assert event.error == (
                'Metric event 00d7bc1e-ec93-4c53-ae78-a6b40450be4a needs a (sas) payload, '
                "but got 'Up!' (s)")

        capture = capfd.readouterr()
        assert 'An error occured while processing the event:' in capture.err
        assert ('Metric event 00d7bc1e-ec93-4c53-ae78-a6b40450be4a needs a (sas) payload, '
                'but got none') in capture.err
        assert ('Metric event 00d7bc1e-ec93-4c53-ae78-a6b40450be4a needs a (sas) payload, '
                "but got 'Up!' (s)") in capture.err

    def test_invalid_aggregate_event_payload(self, capfd):
        from azafea.event_processors.endless.metrics.v3.model import (
            InvalidAggregateEvent, Channel)

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Channel, InvalidAggregateEvent)

        # Build a request as it would have been sent to us
        now = datetime.now(tz=timezone.utc)
        image_id = 'eos-eos3.7-amd64-amd64.190419-225606.base'
        event_id = UUID('49d0451a-f706-4f50-81d2-70cc0ec923a4')
        request = GLib.Variant(
            '(xxsa{ss}ya(aysxmv)a(ayssumv))',
            (
                2000000,   # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),  # Absolute timestamp
                image_id,
                {},
                2,
                [],                                  # singular events
                [                                    # aggregate events
                    (
                        event_id.bytes,
                        'os_version',
                        '2020-06-15',
                        1000,
                        GLib.Variant('(ss)', ('str_1', 'str_2'))
                    ),
                    (
                        event_id.bytes,
                        'os_version',
                        '2020-06-15',
                        1000,
                        None,
                    ),
                ],
            )
        )
        assert request.is_normal_form()
        request_body = request.get_data_as_bytes().get_data()

        received_at = now + timedelta(minutes=2)
        received_at_timestamp = int(received_at.timestamp() * 1000000)  # timestamp as microseconds
        received_at_timestamp_bytes = received_at_timestamp.to_bytes(8, 'little')

        record = received_at_timestamp_bytes + request_body

        # Send the event request to the Redis queue
        self.redis.lpush('test_invalid_aggregate_event_payload', record)

        # Run Azafea so it processes the event
        self.run_azafea()

        # Ensure the record was inserted into the DB
        with self.db as dbsession:
            channel = dbsession.query(Channel).one()

            events = dbsession.query(
                InvalidAggregateEvent
            )
            assert events.count() == 2

            events = events.all()

            event = events[0]
            assert event.channel_id == channel.id
            assert event.event_id == event_id
            assert GLib.Variant.new_from_bytes(
                GLib.VariantType('(ayssumv)'), GLib.Bytes.new(event.payload_data), False
            ).get_child_value(4).unpack() == ('str_1', 'str_2')
            assert event.period_start == date(1970, 1, 1)
            assert event.error == (
                'Metric event 49d0451a-f706-4f50-81d2-70cc0ec923a4 needs a s payload, '
                'but got (\'str_1\', \'str_2\') ((ss))'
            )

            event = events[1]
            assert event.channel_id == channel.id
            assert event.event_id == event_id
            assert GLib.Variant.new_from_bytes(
                GLib.VariantType('(ayssumv)'), GLib.Bytes.new(event.payload_data), False
            ).get_child_value(4).unpack() is None
            assert event.period_start == date(1970, 1, 1)
            assert event.error == (
                'Metric event 49d0451a-f706-4f50-81d2-70cc0ec923a4 needs a s payload, '
                "but got none")

        capture = capfd.readouterr()
        assert 'An error occured while processing the event:' in capture.err
        assert ('Metric event 49d0451a-f706-4f50-81d2-70cc0ec923a4 needs a s payload, '
                'but got none') in capture.err
        assert ('Metric event 49d0451a-f706-4f50-81d2-70cc0ec923a4 needs a s payload, '
                "but got (\'str_1\', \'str_2\') ((ss))") in capture.err

    def test_unknown_aggregate_events(self):
        from azafea.event_processors.endless.metrics.v3.model import (
            UnknownAggregateEvent, Channel
        )

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(UnknownAggregateEvent, Channel)

        # Build a request as it would have been sent to us
        now = datetime.now(tz=timezone.utc)
        image_id = 'eos-eos3.7-amd64-amd64.190419-225606.base'
        event_id = UUID('d3863909-8eff-43b6-9a33-ef7eda266195')
        request = GLib.Variant(
            '(xxsa{ss}ya(aysxmv)a(ayssumv))',
            (
                2000000,   # request relative timestamp (2 secs)
                int(now.timestamp() * 1000000000),  # Absolute timestamp
                image_id,
                {},
                2,
                [],                                    # singular events
                [                                      # aggregate events
                    (
                        event_id.bytes,
                        'os_version',
                        '2020-06-15',
                        2,
                        None,                          # empty payload
                    ),
                    (
                        event_id.bytes,
                        'os_version',
                        '2020-06-15',
                        10,
                        GLib.Variant('(xx)', (1, 2)),  # Non empty payload
                    ),
                ],
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
            channel = dbsession.query(Channel).one()

            events = dbsession.query(UnknownAggregateEvent) \
                              .order_by(UnknownAggregateEvent.period_start)
            assert events.count() == 2

            events = events.all()

            event = events[0]
            assert event.channel_id == channel.id
            assert event.count == 2
            assert event.event_id == event_id
            assert GLib.Variant.new_from_bytes(
                GLib.VariantType('(ayssumv)'), GLib.Bytes.new(event.payload_data), False
            ).get_child_value(4).unpack() is None
            assert event.period_start == date(1970, 1, 1)

            event = events[1]
            assert event.channel_id == channel.id
            assert event.count == 10
            assert event.event_id == event_id
            assert event.period_start == date(1970, 1, 1)
            assert GLib.Variant.new_from_bytes(
                GLib.VariantType('(ayssumv)'), GLib.Bytes.new(event.payload_data), False
            ).get_child_value(4).unpack() == (1, 2)
