# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from datetime import datetime, timedelta, timezone

from gi.repository import GLib

from azafea.tests.integration import IntegrationTest
from azafea.vendors import normalize_vendor


class TestMetrics(IntegrationTest):
    handler_module = 'azafea.event_processors.endless.metrics.v3'

    def test_dedupe_no_dualboots(self, capfd):
        from azafea.event_processors.endless.metrics.v3.model import DualBootBooted

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(DualBootBooted)

        with self.db as dbsession:
            assert dbsession.query(DualBootBooted).count() == 0

        self.run_subcommand('test_dedupe_no_dualboots', 'dedupe-dual-boots')

        with self.db as dbsession:
            assert dbsession.query(DualBootBooted).count() == 0

        capture = capfd.readouterr()
        assert 'No metrics requests with deduplicate dual boot events found' in capture.out

    def test_dedupe_dualboots(self):
        from azafea.event_processors.endless.metrics.v3.model import DualBootBooted, Request

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Request, DualBootBooted)

        occured_at = datetime.utcnow().replace(tzinfo=timezone.utc)

        with self.db as dbsession:
            dbsession.add(Request(sha512='sha512-1', received_at=occured_at,
                                  absolute_timestamp=1, relative_timestamp=2, machine_id='machine1',
                                  send_number=0))
            dbsession.add(Request(sha512='sha512-2', received_at=occured_at,
                                  absolute_timestamp=3, relative_timestamp=4, machine_id='machine2',
                                  send_number=0))
            dbsession.add(Request(sha512='sha512-3', received_at=occured_at,
                                  absolute_timestamp=5, relative_timestamp=6, machine_id='machine3',
                                  send_number=0))

        # Insert multiple dual boot events.
        #
        # We have to do it this way because adding them all in the same session would get them
        # deduplicated before we ever had a chance to run the command.

        for i in range(9):
            with self.db as dbsession:
                request = dbsession.query(Request).order_by(Request.id).all()[i % 3]
                dbsession.add(DualBootBooted(request=request, user_id=i, occured_at=occured_at,
                                             payload=GLib.Variant('mv', None)))

        with self.db as dbsession:
            req1, req2, req3 = dbsession.query(Request).order_by(Request.id).all()
            assert dbsession.query(DualBootBooted).filter_by(request_id=req1.id).count() == 3
            assert dbsession.query(DualBootBooted).filter_by(request_id=req2.id).count() == 3
            assert dbsession.query(DualBootBooted).filter_by(request_id=req3.id).count() == 3

        # Run the deduplication
        self.run_subcommand('test_dedupe_dualboots', 'dedupe-dual-boots', '--chunk-size=5')

        # Verify again after the deduplication
        with self.db as dbsession:
            req1, req2, req3 = dbsession.query(Request).order_by(Request.id).all()
            assert dbsession.query(DualBootBooted).filter_by(request_id=req1.id).one().user_id == 0
            assert dbsession.query(DualBootBooted).filter_by(request_id=req2.id).one().user_id == 1
            assert dbsession.query(DualBootBooted).filter_by(request_id=req3.id).one().user_id == 2

    def test_dedupe_no_image_versions(self, capfd):
        from azafea.event_processors.endless.metrics.v3.model import ImageVersion

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(ImageVersion)

        with self.db as dbsession:
            assert dbsession.query(ImageVersion).count() == 0

        self.run_subcommand('test_dedupe_no_image_versions', 'dedupe-image-versions')

        with self.db as dbsession:
            assert dbsession.query(ImageVersion).count() == 0

        capture = capfd.readouterr()
        assert 'No metrics requests with deduplicate image versions found' in capture.out

    def test_dedupe_image_versions(self):
        from azafea.event_processors.endless.metrics.v3.model import ImageVersion, Request

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Request, ImageVersion)

        occured_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        image_id = 'eos-eos3.7-amd64-amd64.190419-225606.base'

        with self.db as dbsession:
            dbsession.add(Request(sha512='sha512-1', received_at=occured_at,
                                  absolute_timestamp=1, relative_timestamp=2, machine_id='machine1',
                                  send_number=0))
            dbsession.add(Request(sha512='sha512-2', received_at=occured_at,
                                  absolute_timestamp=3, relative_timestamp=4, machine_id='machine2',
                                  send_number=0))
            dbsession.add(Request(sha512='sha512-3', received_at=occured_at,
                                  absolute_timestamp=5, relative_timestamp=6, machine_id='machine3',
                                  send_number=0))

        # Insert multiple image version events.
        #
        # We have to do it this way because adding them all in the same session would get them
        # deduplicated before we ever had a chance to run the command.

        for i in range(9):
            with self.db as dbsession:
                request = dbsession.query(Request).order_by(Request.id).all()[i % 3]
                dbsession.add(ImageVersion(request=request, user_id=i, occured_at=occured_at,
                                           payload=GLib.Variant('mv', GLib.Variant('s', image_id))))

        with self.db as dbsession:
            req1, req2, req3 = dbsession.query(Request).order_by(Request.id).all()
            assert dbsession.query(ImageVersion).filter_by(request_id=req1.id).count() == 3
            assert dbsession.query(ImageVersion).filter_by(request_id=req2.id).count() == 3
            assert dbsession.query(ImageVersion).filter_by(request_id=req3.id).count() == 3

        # Run the deduplication
        self.run_subcommand('test_dedupe_image_versions', 'dedupe-image-versions', '--chunk-size=5')

        # Verify again after the deduplication
        with self.db as dbsession:
            req1, req2, req3 = dbsession.query(Request).order_by(Request.id).all()
            assert dbsession.query(ImageVersion).filter_by(request_id=req1.id).one().user_id == 0
            assert dbsession.query(ImageVersion).filter_by(request_id=req2.id).one().user_id == 1
            assert dbsession.query(ImageVersion).filter_by(request_id=req3.id).one().user_id == 2

    def test_dedupe_no_live_usbs(self, capfd):
        from azafea.event_processors.endless.metrics.v3.model import LiveUsbBooted

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(LiveUsbBooted)

        with self.db as dbsession:
            assert dbsession.query(LiveUsbBooted).count() == 0

        self.run_subcommand('test_dedupe_no_live_usbs', 'dedupe-live-usbs')

        with self.db as dbsession:
            assert dbsession.query(LiveUsbBooted).count() == 0

        capture = capfd.readouterr()
        assert 'No metrics requests with deduplicate live usb events found' in capture.out

    def test_dedupe_live_usbs(self):
        from azafea.event_processors.endless.metrics.v3.model import LiveUsbBooted, Request

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Request, LiveUsbBooted)

        occured_at = datetime.utcnow().replace(tzinfo=timezone.utc)

        with self.db as dbsession:
            dbsession.add(Request(sha512='sha512-1', received_at=occured_at,
                                  absolute_timestamp=1, relative_timestamp=2, machine_id='machine1',
                                  send_number=0))
            dbsession.add(Request(sha512='sha512-2', received_at=occured_at,
                                  absolute_timestamp=3, relative_timestamp=4, machine_id='machine2',
                                  send_number=0))
            dbsession.add(Request(sha512='sha512-3', received_at=occured_at,
                                  absolute_timestamp=5, relative_timestamp=6, machine_id='machine3',
                                  send_number=0))

        # Insert multiple live usb events.
        #
        # We have to do it this way because adding them all in the same session would get them
        # deduplicated before we ever had a chance to run the command.

        for i in range(9):
            with self.db as dbsession:
                request = dbsession.query(Request).order_by(Request.id).all()[i % 3]
                dbsession.add(LiveUsbBooted(request=request, user_id=i, occured_at=occured_at,
                                            payload=GLib.Variant('mv', None)))

        with self.db as dbsession:
            req1, req2, req3 = dbsession.query(Request).order_by(Request.id).all()
            assert dbsession.query(LiveUsbBooted).filter_by(request_id=req1.id).count() == 3
            assert dbsession.query(LiveUsbBooted).filter_by(request_id=req2.id).count() == 3
            assert dbsession.query(LiveUsbBooted).filter_by(request_id=req3.id).count() == 3

        # Run the deduplication
        self.run_subcommand('test_dedupe_live_usbs', 'dedupe-live-usbs', '--chunk-size=5')

        # Verify again after the deduplication
        with self.db as dbsession:
            req1, req2, req3 = dbsession.query(Request).order_by(Request.id).all()
            assert dbsession.query(LiveUsbBooted).filter_by(request_id=req1.id).one().user_id == 0
            assert dbsession.query(LiveUsbBooted).filter_by(request_id=req2.id).one().user_id == 1
            assert dbsession.query(LiveUsbBooted).filter_by(request_id=req3.id).one().user_id == 2

    def test_normalize_no_vendors(self, capfd):
        from azafea.event_processors.endless.metrics.v3.model import UpdaterBranchSelected

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
        from azafea.event_processors.endless.metrics.v3.model import (
            UpdaterBranchSelected, Request)

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Request, UpdaterBranchSelected)

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
            request = Request(sha512='whatever', received_at=occured_at,
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
        from azafea.event_processors.endless.metrics.v3.model import (
            UpdaterBranchSelected, Request)

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Request, UpdaterBranchSelected)

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
            request = Request(sha512='whatever', received_at=occured_at,
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

    def test_replay_machine_dualboots(self):
        from azafea.event_processors.endless.metrics.v3.model import (
            DualBootBooted, Machine, Request)

        self.run_subcommand('initdb')
        self.ensure_tables(DualBootBooted, Machine, Request)

        occured_at = datetime.utcnow().replace(tzinfo=timezone.utc)

        with self.db as dbsession:
            request = Request(sha512='whatever', received_at=occured_at,
                              absolute_timestamp=1, relative_timestamp=2, machine_id='machine1',
                              send_number=0)
            dbsession.add(request)

            request = Request(sha512='whatever2', received_at=occured_at,
                              absolute_timestamp=1, relative_timestamp=2, machine_id='machine2',
                              send_number=0)
            dbsession.add(request)
            dbsession.add(DualBootBooted(request=request, user_id=1001, occured_at=occured_at,
                                         payload=GLib.Variant('mv', None)))

            request = Request(sha512='whatever3', received_at=occured_at,
                              absolute_timestamp=1, relative_timestamp=2, machine_id='machine3',
                              send_number=0)
            dbsession.add(request)
            dbsession.add(DualBootBooted(request=request, user_id=1001, occured_at=occured_at,
                                         payload=GLib.Variant('mv', None)))

        # Pretend these events had been received before we created the Machine model by simply
        # removing them
        with self.db as dbsession:
            dbsession.query(Machine).delete()

        with self.db as dbsession:
            assert dbsession.query(Request).count() == 3
            assert dbsession.query(DualBootBooted).count() == 2
            assert dbsession.query(Machine).count() == 0

        # The machine2 has sent a new event after creating the Machine model, but before running
        # the replay command
        with self.db as dbsession:
            request = Request(sha512='whatever4', received_at=occured_at,
                              absolute_timestamp=1, relative_timestamp=2, machine_id='machine2',
                              send_number=0)
            dbsession.add(request)
            dbsession.add(DualBootBooted(request=request, user_id=1001, occured_at=occured_at,
                                         payload=GLib.Variant('mv', None)))

        with self.db as dbsession:
            assert dbsession.query(Request).count() == 4
            assert dbsession.query(DualBootBooted).count() == 3
            assert dbsession.query(Machine).count() == 1
            assert dbsession.query(Machine).one().machine_id == 'machine2'

        # Replay the image version events
        self.run_subcommand('test_replay_machine_dualboots', 'replay-machine-dual-boots',
                            '--chunk-size=2')

        with self.db as dbsession:
            assert dbsession.query(Request).count() == 4
            assert dbsession.query(DualBootBooted).count() == 3
            assert dbsession.query(Machine).count() == 2

            machines = dbsession.query(Machine).order_by(Machine.machine_id).all()

            machine = machines[0]
            assert machine.machine_id == 'machine2'
            assert machine.dualboot is True

            machine = machines[1]
            assert machine.machine_id == 'machine3'
            assert machine.dualboot is True

    def test_replay_machine_images(self):
        from azafea.event_processors.endless.metrics.v3.model import (
            ImageVersion, Machine, Request)

        self.run_subcommand('initdb')
        self.ensure_tables(ImageVersion, Machine, Request)

        occured_at = datetime.utcnow().replace(tzinfo=timezone.utc)

        with self.db as dbsession:
            request = Request(sha512='whatever', received_at=occured_at,
                              absolute_timestamp=1, relative_timestamp=2, machine_id='machine1',
                              send_number=0)
            dbsession.add(request)

            image_id_1 = 'eos-eos3.6-amd64-amd64.190619-225606.base'
            dbsession.add(ImageVersion(request=request, user_id=1001, occured_at=occured_at,
                                       payload=GLib.Variant('mv', GLib.Variant('s', image_id_1))))

            request = Request(sha512='whatever2', received_at=occured_at,
                              absolute_timestamp=1, relative_timestamp=2, machine_id='machine2',
                              send_number=0)
            dbsession.add(request)

            image_id_2 = 'eos-eos3.7-amd64-amd64.191019-225606.base'
            dbsession.add(ImageVersion(request=request, user_id=1001, occured_at=occured_at,
                                       payload=GLib.Variant('mv', GLib.Variant('s', image_id_2))))

        # Pretend these events had been received before we created the Machine model by simply
        # removing them
        with self.db as dbsession:
            dbsession.query(Machine).delete()

        with self.db as dbsession:
            assert dbsession.query(Request).count() == 2
            assert dbsession.query(ImageVersion).count() == 2
            assert dbsession.query(Machine).count() == 0

        # The machine1 has sent a new event after creating the Machine model, but before running
        # the replay command
        with self.db as dbsession:
            request = Request(sha512='whatever3', received_at=occured_at,
                              absolute_timestamp=1, relative_timestamp=2, machine_id='machine1',
                              send_number=0)
            dbsession.add(request)

            dbsession.add(ImageVersion(request=request, user_id=1001, occured_at=occured_at,
                                       payload=GLib.Variant('mv', GLib.Variant('s', image_id_1))))

        with self.db as dbsession:
            assert dbsession.query(Request).count() == 3
            assert dbsession.query(ImageVersion).count() == 3
            assert dbsession.query(Machine).count() == 1
            assert dbsession.query(Machine).one().machine_id == 'machine1'

        # Replay the image version events
        self.run_subcommand('test_replay_machine_images', 'replay-machine-images', '--chunk-size=2')

        with self.db as dbsession:
            assert dbsession.query(Request).count() == 3
            assert dbsession.query(ImageVersion).count() == 3
            assert dbsession.query(Machine).count() == 2

            machines = dbsession.query(Machine).order_by(Machine.machine_id).all()

            machine = machines[0]
            assert machine.machine_id == 'machine1'
            assert machine.image_id == image_id_1

            machine = machines[1]
            assert machine.machine_id == 'machine2'
            assert machine.image_id == image_id_2

    def test_replay_machine_live_usbs(self):
        from azafea.event_processors.endless.metrics.v3.model import (
            LiveUsbBooted, Machine, Request)

        self.run_subcommand('initdb')
        self.ensure_tables(LiveUsbBooted, Machine, Request)

        occured_at = datetime.utcnow().replace(tzinfo=timezone.utc)

        with self.db as dbsession:
            request = Request(sha512='whatever', received_at=occured_at,
                              absolute_timestamp=1, relative_timestamp=2, machine_id='machine1',
                              send_number=0)
            dbsession.add(request)

            request = Request(sha512='whatever2', received_at=occured_at,
                              absolute_timestamp=1, relative_timestamp=2, machine_id='machine2',
                              send_number=0)
            dbsession.add(request)
            dbsession.add(LiveUsbBooted(request=request, user_id=1001, occured_at=occured_at,
                                        payload=GLib.Variant('mv', None)))

            request = Request(sha512='whatever3', received_at=occured_at,
                              absolute_timestamp=1, relative_timestamp=2, machine_id='machine3',
                              send_number=0)
            dbsession.add(request)
            dbsession.add(LiveUsbBooted(request=request, user_id=1001, occured_at=occured_at,
                                        payload=GLib.Variant('mv', None)))

        # Pretend these events had been received before we created the Machine model by simply
        # removing them
        with self.db as dbsession:
            dbsession.query(Machine).delete()

        with self.db as dbsession:
            assert dbsession.query(Request).count() == 3
            assert dbsession.query(LiveUsbBooted).count() == 2
            assert dbsession.query(Machine).count() == 0

        # The machine2 has sent a new event after creating the Machine model, but before running
        # the replay command
        with self.db as dbsession:
            request = Request(sha512='whatever4', received_at=occured_at,
                              absolute_timestamp=1, relative_timestamp=2, machine_id='machine2',
                              send_number=0)
            dbsession.add(request)
            dbsession.add(LiveUsbBooted(request=request, user_id=1001, occured_at=occured_at,
                                        payload=GLib.Variant('mv', None)))

        with self.db as dbsession:
            assert dbsession.query(Request).count() == 4
            assert dbsession.query(LiveUsbBooted).count() == 3
            assert dbsession.query(Machine).count() == 1
            assert dbsession.query(Machine).one().machine_id == 'machine2'

        # Replay the image version events
        self.run_subcommand('test_replay_machine_live_usbs', 'replay-machine-live-usbs',
                            '--chunk-size=2')

        with self.db as dbsession:
            assert dbsession.query(Request).count() == 4
            assert dbsession.query(LiveUsbBooted).count() == 3
            assert dbsession.query(Machine).count() == 2

            machines = dbsession.query(Machine).order_by(Machine.machine_id).all()

            machine = machines[0]
            assert machine.machine_id == 'machine2'
            assert machine.live is True

            machine = machines[1]
            assert machine.machine_id == 'machine3'
            assert machine.live is True

    def test_replay_invalid(self):
        from azafea.event_processors.endless.metrics.v3.model import (
            InvalidSingularEvent, Request, ShellAppIsOpen, UnknownSingularEvent, Uptime)

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(
            Request, ShellAppIsOpen, Uptime, InvalidSingularEvent, UnknownSingularEvent)

        occured_at = datetime.utcnow().replace(tzinfo=timezone.utc)

        with self.db as dbsession:
            request = Request(sha512='whatever', received_at=occured_at,
                              absolute_timestamp=1, relative_timestamp=2, machine_id='whatever',
                              send_number=0)
            dbsession.add(request)

            # -- Invalid singular events --------

            # Add an invalid singular event which will be ignored after the replay
            dbsession.add(InvalidSingularEvent(
                request=request, event_id='5fae6179-e108-4962-83be-c909259c0584', user_id=1001,
                occured_at=occured_at, payload=GLib.Variant('mv', GLib.Variant('s', 'discard')),
                error='discard'))

            # Add an invalid singular event which will be unknown after the replay
            unknown_singular = GLib.Variant('mv', GLib.Variant('s', 'unknown'))
            dbsession.add(InvalidSingularEvent(
                request=request, event_id='ffffffff-ffff-ffff-ffff-ffffffffffff', user_id=1002,
                occured_at=occured_at, payload=unknown_singular, error='unknown'))

            # Add an invalid singular event which will be replayed as an uptime event
            dbsession.add(InvalidSingularEvent(
                request=request, event_id='9af2cc74-d6dd-423f-ac44-600a6eee2d96', user_id=1003,
                occured_at=occured_at, payload=GLib.Variant('mv', GLib.Variant('(xx)', (2, 1))),
                error='ok'))

            # Add an invalid singular event which will be replayed as an uptime event, but with an
            # error we decided to ignore
            dbsession.add(InvalidSingularEvent(
                request=request, event_id='9af2cc74-d6dd-423f-ac44-600a6eee2d96', user_id=1004,
                occured_at=occured_at, payload=GLib.Variant('mv', None), error='discard'))

            # Add an invalid singular event which will still be invalid after the replay
            invalid_singular = GLib.Variant('mv', GLib.Variant('as', ['invalid', 'payload']))
            dbsession.add(InvalidSingularEvent(
                request=request, event_id='9af2cc74-d6dd-423f-ac44-600a6eee2d96', user_id=1005,
                occured_at=occured_at, payload=invalid_singular, error='invalid'))

            # -- Invalid aggregate events -------

            # TODO: Implement this when we actually have aggregate events to test

        # Replay the invalid events
        self.run_subcommand('test_replay_invalid', 'replay-invalid')

        with self.db as dbsession:
            request = dbsession.query(Request).one()

            # -- Singular events ----------------

            unknown = dbsession.query(UnknownSingularEvent).one()
            assert unknown.request == request
            assert unknown.user_id == 1002
            assert unknown.occured_at == occured_at
            assert unknown.payload_data == unknown_singular.get_data_as_bytes().get_data()

            uptime = dbsession.query(Uptime).one()
            assert uptime.request == request
            assert uptime.user_id == 1003
            assert uptime.occured_at == occured_at
            assert uptime.accumulated_uptime == 2
            assert uptime.number_of_boots == 1

            invalid = dbsession.query(InvalidSingularEvent).one()
            assert invalid.request == request
            assert invalid.user_id == 1005
            assert invalid.occured_at == occured_at
            assert invalid.payload_data == invalid_singular.get_data_as_bytes().get_data()
            assert invalid.error == 'invalid'

            # -- Aggregate events ---------------

            # TODO: Implement this when we actually have aggregate events to test

    def test_replay_unknown(self):
        from azafea.event_processors.endless.metrics.v3.model import (
            InvalidSingularEvent, Request, ShellAppIsOpen, UnknownAggregateEvent,
            UnknownSingularEvent, Uptime)

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(
            Request, ShellAppIsOpen, Uptime, InvalidSingularEvent, UnknownAggregateEvent,
            UnknownSingularEvent)

        occured_at = datetime.utcnow().replace(tzinfo=timezone.utc)

        with self.db as dbsession:
            request = Request(sha512='whatever', received_at=occured_at,
                              absolute_timestamp=1, relative_timestamp=2, machine_id='whatever',
                              send_number=0)
            dbsession.add(request)

            # -- Unknown singular events --------

            # Add an unknown singular event which will be ignored after the replay
            dbsession.add(UnknownSingularEvent(
                request=request, event_id='5fae6179-e108-4962-83be-c909259c0584', user_id=1001,
                occured_at=occured_at, payload=GLib.Variant('mv', GLib.Variant('s', 'discard'))))

            # Add an unknown singular event which will still be unknown after the replay
            unknown_singular = GLib.Variant('mv', GLib.Variant('s', 'unknown'))
            dbsession.add(UnknownSingularEvent(
                request=request, event_id='ffffffff-ffff-ffff-ffff-ffffffffffff', user_id=1002,
                occured_at=occured_at, payload=unknown_singular))

            # Add an unknown singular event which will be replayed as an uptime event
            dbsession.add(UnknownSingularEvent(
                request=request, event_id='9af2cc74-d6dd-423f-ac44-600a6eee2d96', user_id=1003,
                occured_at=occured_at, payload=GLib.Variant('mv', GLib.Variant('(xx)', (2, 1)))))

            # Add an unknown singular event which will be replayed as an uptime event, but with an
            # error we decided to ignore
            dbsession.add(UnknownSingularEvent(
                request=request, event_id='9af2cc74-d6dd-423f-ac44-600a6eee2d96', user_id=1004,
                occured_at=occured_at, payload=GLib.Variant('mv', None)))

            # Add an unknown singular event which will be replayed as an uptime event, but with an
            # actual error making it invalid
            invalid_singular = GLib.Variant('mv', GLib.Variant('as', ['invalid', 'payload']))
            dbsession.add(UnknownSingularEvent(
                request=request, event_id='9af2cc74-d6dd-423f-ac44-600a6eee2d96', user_id=1005,
                occured_at=occured_at, payload=invalid_singular))

            # -- Unknown aggregate events -------

            # Add an unknown aggregate event which will be ignored after the replay
            dbsession.add(UnknownAggregateEvent(
                request=request, event_id='9a0cf836-12cd-4887-95d8-e48ccdf6e552', user_id=1001,
                count=10, occured_at=occured_at,
                payload=GLib.Variant('mv', GLib.Variant('s', 'discard'))))

        with self.db as dbsession:
            assert dbsession.query(Request).count() == 1
            assert dbsession.query(UnknownSingularEvent).count() == 5
            assert dbsession.query(UnknownAggregateEvent).count() == 1

        # Replay the unknown events
        self.run_subcommand('test_replay_unknown', 'replay-unknown')

        with self.db as dbsession:
            request = dbsession.query(Request).one()

            # -- Singular events ----------------

            unknown = dbsession.query(UnknownSingularEvent).one()
            assert unknown.request == request
            assert unknown.user_id == 1002
            assert unknown.occured_at == occured_at
            assert unknown.payload_data == unknown_singular.get_data_as_bytes().get_data()

            uptime = dbsession.query(Uptime).one()
            assert uptime.request == request
            assert uptime.user_id == 1003
            assert uptime.occured_at == occured_at
            assert uptime.accumulated_uptime == 2
            assert uptime.number_of_boots == 1

            invalid = dbsession.query(InvalidSingularEvent).one()
            assert invalid.request == request
            assert invalid.user_id == 1005
            assert invalid.occured_at == occured_at
            assert invalid.payload_data == invalid_singular.get_data_as_bytes().get_data()

            # -- Aggregate events ---------------

            assert dbsession.query(UnknownAggregateEvent).count() == 0

    def test_parse_old_images(self):
        from azafea.event_processors.endless.metrics.v3.model import Machine

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Machine)

        # Insert a machine without parsed image components
        image_id = 'eos-eos3.7-amd64-amd64.190419-225606.base'

        with self.db as dbsession:
            dbsession.add(Machine(machine_id='ffffffffffffffffffffffffffffffff', image_id=image_id))

        with self.db as dbsession:
            machine = dbsession.query(Machine).one()
            assert machine.image_id == image_id
            assert machine.image_product is None
            assert machine.image_branch is None
            assert machine.image_arch is None
            assert machine.image_platform is None
            assert machine.image_timestamp is None
            assert machine.image_personality is None

        # Parse the image for old machine records
        self.run_subcommand('test_parse_old_images', 'parse-old-images')

        with self.db as dbsession:
            machine = dbsession.query(Machine).one()
            assert machine.image_id == image_id
            assert machine.image_product == 'eos'
            assert machine.image_branch == 'eos3.7'
            assert machine.image_arch == 'amd64'
            assert machine.image_platform == 'amd64'
            assert machine.image_timestamp == datetime(2019, 4, 19, 22, 56, 6, tzinfo=timezone.utc)
            assert machine.image_personality == 'base'

    def test_parse_old_images_skips_already_done(self, capfd):
        from azafea.event_processors.endless.metrics.v3.model import Machine

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Machine)

        # Insert a machine without parsed image components
        image_id = 'eos-eos3.7-amd64-amd64.190419-225606.base'

        with self.db as dbsession:
            dbsession.add(Machine(machine_id='ffffffffffffffffffffffffffffffff', image_id=image_id,
                                  image_product='eos', image_branch='eos3.7', image_arch='amd64',
                                  image_platform='amd64', image_personality='base',
                                  image_timestamp=datetime(2019, 4, 19, 22, 56, 6,
                                                           tzinfo=timezone.utc)))

        with self.db as dbsession:
            machine = dbsession.query(Machine).one()
            assert machine.image_id == image_id
            assert machine.image_product == 'eos'
            assert machine.image_branch == 'eos3.7'
            assert machine.image_arch == 'amd64'
            assert machine.image_platform == 'amd64'
            assert machine.image_timestamp == datetime(2019, 4, 19, 22, 56, 6, tzinfo=timezone.utc)
            assert machine.image_personality == 'base'

        # Parse the image for old machine records
        self.run_subcommand('test_parse_old_images_skips_already_done', 'parse-old-images')

        with self.db as dbsession:
            machine = dbsession.query(Machine).one()
            assert machine.image_id == image_id
            assert machine.image_product == 'eos'
            assert machine.image_branch == 'eos3.7'
            assert machine.image_arch == 'amd64'
            assert machine.image_platform == 'amd64'
            assert machine.image_timestamp == datetime(2019, 4, 19, 22, 56, 6, tzinfo=timezone.utc)
            assert machine.image_personality == 'base'

        capture = capfd.readouterr()
        assert 'No machine record with unparsed image ids' in capture.out

    def test_set_open_durations(self):
        from azafea.event_processors.endless.metrics.v3.model import ShellAppIsOpen

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(ShellAppIsOpen)

        start = datetime(2019, 4, 19, 22, 56, 6, 100000, tzinfo=timezone.utc)
        stop = datetime(2019, 4, 19, 22, 56, 7, 555555, tzinfo=timezone.utc)
        duration = (stop - start).total_seconds()

        # Insert an open shell app record with no duration
        with self.db as dbsession:
            payload = GLib.Variant('mv', GLib.Variant('s', 'org.gnome.Calendar'))
            dbsession.add(ShellAppIsOpen(
                started_at=start, stopped_at=stop, duration=0, user_id=1001,
                payload=payload))

        # Set duration on records
        self.run_subcommand('test_set_open_durations', 'set-open-durations')

        with self.db as dbsession:
            app = dbsession.query(ShellAppIsOpen).one()
            assert app.started_at == start
            assert app.stopped_at == stop
            assert app.app_id == 'org.gnome.Calendar'
            assert app.duration == duration

    def test_set_open_durations_already_set(self, capfd):
        from azafea.event_processors.endless.metrics.v3.model import ShellAppIsOpen

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(ShellAppIsOpen)

        start = datetime(2019, 4, 19, 22, 56, 6, 100000, tzinfo=timezone.utc)
        stop = datetime(2019, 4, 19, 22, 56, 7, 555555, tzinfo=timezone.utc)
        duration = (stop - start).total_seconds()

        # Insert an open shell app record with no duration
        with self.db as dbsession:
            payload = GLib.Variant('mv', GLib.Variant('s', 'org.gnome.Calendar'))
            dbsession.add(ShellAppIsOpen(
                started_at=start, stopped_at=stop, user_id=1001, payload=payload))

        # Set duration on records
        self.run_subcommand('test_set_open_durations_already_set', 'set-open-durations')

        with self.db as dbsession:
            app = dbsession.query(ShellAppIsOpen).one()
            assert app.started_at == start
            assert app.stopped_at == stop
            assert app.app_id == 'org.gnome.Calendar'
            assert app.duration == duration

        capture = capfd.readouterr()
        assert '-> No open app with unset duration' in capture.out

    def test_remove_os_info_quotes(self):
        from azafea.event_processors.endless.metrics.v3.model import OSVersion

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(OSVersion)

        payload = GLib.Variant('mv', GLib.Variant('(sss)', ['"Endless"', '"1.2.3"', 'useless']))
        occured_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        with self.db as dbsession:
            version = OSVersion(
                version='"1.2.3"', user_id=1, payload=payload, occured_at=occured_at)
            # Bypass quotes removed by _get_fields_from_payload
            version.version = '"1.2.3"'
            dbsession.add(version)

        with self.db as dbsession:
            version = dbsession.query(OSVersion).one()
            assert version.version == '"1.2.3"'

        self.run_subcommand('test_remove_os_info_quotes', 'remove-os-info-quotes')

        with self.db as dbsession:
            version = dbsession.query(OSVersion).one()
            assert version.version == '1.2.3'

    def test_remove_os_info_no_quotes(self, capfd):
        from azafea.event_processors.endless.metrics.v3.model import OSVersion

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(OSVersion)

        payload = GLib.Variant('mv', GLib.Variant('(sss)', ['Endless', '1.2.3', 'useless']))
        occured_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        with self.db as dbsession:
            dbsession.add(OSVersion(
                version='1.2.3', user_id=1, occured_at=occured_at, payload=payload))

        self.run_subcommand('test_remove_os_info_no_quotes', 'remove-os-info-quotes')

        with self.db as dbsession:
            version = dbsession.query(OSVersion).one()
            assert version.version == '1.2.3'

        capture = capfd.readouterr()
        assert 'No OS info with extra quotes in database' in capture.out

    def test_remove_empty_location_info_none(self, capfd):
        from azafea.event_processors.endless.metrics.v3.model import LocationLabel, Request

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(LocationLabel)

        info = {
            'id': '',
            'city': 'CAJEME',
            'state': 'SONORA',
            'street': 'KILOMETRO 11',
            'country': 'MEXICO',
            'facility': '22KPJ9043L',
        }
        payload = GLib.Variant('mv', GLib.Variant('a{ss}', info))
        occured_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        with self.db as dbsession:
            request = Request(sha512='whatever', received_at=occured_at,
                              absolute_timestamp=1, relative_timestamp=2, machine_id='whatever',
                              send_number=0)
            dbsession.add(request)
            dbsession.add(LocationLabel(
                user_id=1, occured_at=occured_at, request=request, payload=payload))

        self.run_subcommand('test_remove_empty_location_info_none', 'remove-empty-location-info')

        info.pop('id')
        with self.db as dbsession:
            location_label = dbsession.query(LocationLabel).one()
            assert location_label.info == info

        capture = capfd.readouterr()
        assert 'No locations events with empty info in database' in capture.out

    def test_remove_empty_location_info(self):
        from azafea.event_processors.endless.metrics.v3.model import LocationLabel, Request

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(LocationLabel)

        info = {
            'id': '',
            'city': 'CAJEME',
            'state': 'SONORA',
            'street': 'KILOMETRO 11',
            'country': 'MEXICO',
            'facility': '22KPJ9043L',
        }
        empty_info = {
            'id': '', 'city': '', 'state': '', 'street': '', 'country': '', 'facility': ''}
        payload = GLib.Variant('mv', GLib.Variant('a{ss}', info))
        occured_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        with self.db as dbsession:
            request = Request(sha512='whatever', received_at=occured_at,
                              absolute_timestamp=1, relative_timestamp=2, machine_id='whatever',
                              send_number=0)
            dbsession.add(request)
            dbsession.add(LocationLabel(
                user_id=1, occured_at=occured_at, request=request, payload=payload))
            empty_location = LocationLabel(
                user_id=1, occured_at=occured_at, request=request, payload=payload)
            empty_location.info = empty_info
            dbsession.add(empty_location)

        self.run_subcommand('test_remove_empty_location_info', 'remove-empty-location-info')

        info.pop('id')
        with self.db as dbsession:
            location_label = dbsession.query(LocationLabel).one()
            assert location_label.info == info

    def test_refresh_views(self):
        from azafea.event_processors.endless.metrics.v3.model import MachineIdsByDay, Request

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Request)

        occured_at_1 = datetime.utcnow().replace(tzinfo=timezone.utc)
        occured_at_2 = occured_at_1 + timedelta(days=1)

        with self.db as dbsession:
            dbsession.add(Request(sha512='sha512-1', received_at=occured_at_1, absolute_timestamp=1,
                                  relative_timestamp=2, machine_id='machine1', send_number=0))
            dbsession.add(Request(sha512='sha512-2', received_at=occured_at_1, absolute_timestamp=3,
                                  relative_timestamp=4, machine_id='machine2', send_number=0))
            dbsession.add(Request(sha512='sha512-3', received_at=occured_at_1, absolute_timestamp=5,
                                  relative_timestamp=6, machine_id='machine2', send_number=0))
            dbsession.add(Request(sha512='sha512-4', received_at=occured_at_2, absolute_timestamp=7,
                                  relative_timestamp=8, machine_id='machine2', send_number=0))

        with self.db as dbsession:
            assert dbsession.query(MachineIdsByDay).count() == 0

        self.run_subcommand('refresh-views')

        with self.db as dbsession:
            query = dbsession.query(MachineIdsByDay)
            query = query.order_by(MachineIdsByDay.machine_id, MachineIdsByDay.day)
            req1, req2, req3 = query.all()
            assert (req1.machine_id, req1.day) == ('machine1', occured_at_1.date())
            assert (req2.machine_id, req2.day) == ('machine2', occured_at_1.date())
            assert (req3.machine_id, req3.day) == ('machine2', occured_at_2.date())
