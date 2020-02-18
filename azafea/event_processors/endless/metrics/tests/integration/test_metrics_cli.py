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
    handler_module = 'azafea.event_processors.endless.metrics.v2'

    def test_dedupe_no_image_versions(self, capfd):
        from azafea.event_processors.endless.metrics.events import ImageVersion

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
        from azafea.event_processors.endless.metrics.events import ImageVersion
        from azafea.event_processors.endless.metrics.request import Request

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Request, ImageVersion)

        occured_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        image_id = 'eos-eos3.7-amd64-amd64.190419-225606.base'

        with self.db as dbsession:
            dbsession.add(Request(serialized=b'whatever', sha512='sha512-1', received_at=occured_at,
                                  absolute_timestamp=1, relative_timestamp=2, machine_id='machine1',
                                  send_number=0))
            dbsession.add(Request(serialized=b'whatever', sha512='sha512-2', received_at=occured_at,
                                  absolute_timestamp=3, relative_timestamp=4, machine_id='machine2',
                                  send_number=0))
            dbsession.add(Request(serialized=b'whatever', sha512='sha512-3', received_at=occured_at,
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

    def test_normalize_no_vendors(self, capfd):
        from azafea.event_processors.endless.metrics.events import UpdaterBranchSelected

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
        from azafea.event_processors.endless.metrics.events import UpdaterBranchSelected
        from azafea.event_processors.endless.metrics.request import Request

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
        from azafea.event_processors.endless.metrics.events import UpdaterBranchSelected
        from azafea.event_processors.endless.metrics.request import Request

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

    def test_replay_machine_images(self):
        from azafea.event_processors.endless.metrics.events import ImageVersion
        from azafea.event_processors.endless.metrics.machine import Machine
        from azafea.event_processors.endless.metrics.request import Request

        self.run_subcommand('initdb')
        self.ensure_tables(ImageVersion, Machine, Request)

        occured_at = datetime.utcnow().replace(tzinfo=timezone.utc)

        with self.db as dbsession:
            request = Request(serialized=b'whatever', sha512='whatever', received_at=occured_at,
                              absolute_timestamp=1, relative_timestamp=2, machine_id='machine1',
                              send_number=0)
            dbsession.add(request)

            image_id_1 = 'eos-eos3.6-amd64-amd64.190619-225606.base'
            dbsession.add(ImageVersion(request=request, user_id=1001, occured_at=occured_at,
                                       payload=GLib.Variant('mv', GLib.Variant('s', image_id_1))))

            request = Request(serialized=b'whatever2', sha512='whatever2', received_at=occured_at,
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
            request = Request(serialized=b'whatever3', sha512='whatever3', received_at=occured_at,
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

    def test_replay_invalid(self):
        from azafea.event_processors.endless.metrics.events import ShellAppIsOpen, Uptime
        from azafea.event_processors.endless.metrics.events._base import (
            InvalidSequence, InvalidSingularEvent, UnknownSequence, UnknownSingularEvent)
        from azafea.event_processors.endless.metrics.request import Request

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Request, ShellAppIsOpen, Uptime, InvalidSequence, InvalidSingularEvent,
                           UnknownSequence, UnknownSingularEvent)

        occured_at = datetime.utcnow().replace(tzinfo=timezone.utc)

        with self.db as dbsession:
            request = Request(serialized=b'whatever', sha512='whatever', received_at=occured_at,
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

            # -- Invalid sequence events --------

            # Add an invalid sequence which will be ignored after the replay
            dbsession.add(InvalidSequence(
                request=request, event_id='9c33a734-7ed8-4348-9e39-3c27f4dc2e62', user_id=3001,
                payload=GLib.Variant('a(xmv)', [
                    (3, GLib.Variant('s', 'discard')),
                    (4, None),
                ]), error='discard'))

            # Add an invalid sequence which will be unknown after the replay
            unknown_sequence = GLib.Variant('a(xmv)', [
                (3, GLib.Variant('s', 'unknown')),
                (4, None),
            ])
            dbsession.add(InvalidSequence(
                request=request, event_id='ffffffff-ffff-ffff-ffff-ffffffffffff', user_id=3002,
                payload=unknown_sequence, error='unknown'))

            # Add an invalid sequence which will be replayed as a shell app is open event
            dbsession.add(InvalidSequence(
                request=request, event_id='b5e11a3d-13f8-4219-84fd-c9ba0bf3d1f0', user_id=3003,
                payload=GLib.Variant('a(xmv)', [
                    (3, GLib.Variant('s', 'org.gnome.Calendar')),
                    (4, None),
                ]), error='ok'))

            # Add an invalid sequence which will be replayed as a user is logged in event, but with
            # an error we decided to ignore
            dbsession.add(InvalidSequence(
                request=request, event_id='add052be-7b2a-4959-81a5-a7f45062ee98', user_id=3004,
                payload=GLib.Variant('a(xmv)', [
                    (3, None),
                    (4, None),
                ]), error='discard'))

            # Add an invalid sequence which will be replayed as an shell app is open event, but
            # with an actual error making it invalid
            invalid_sequence = GLib.Variant('a(xmv)', [
                (3, GLib.Variant('ay', b'invalid')),
                (4, None)
            ])
            dbsession.add(InvalidSequence(
                request=request, event_id='b5e11a3d-13f8-4219-84fd-c9ba0bf3d1f0', user_id=3005,
                payload=invalid_sequence, error='invalid'))

            # Add an invalid sequence with only a single event
            missing_events = GLib.Variant('a(xmv)', [
                (3, GLib.Variant('ay', b'invalid')),
            ])
            dbsession.add(InvalidSequence(
                request=request, event_id='b5e11a3d-13f8-4219-84fd-c9ba0bf3d1f0', user_id=3006,
                payload=missing_events, error='missing'))

        with self.db as dbsession:
            assert dbsession.query(Request).count() == 1
            assert dbsession.query(InvalidSingularEvent).count() == 5
            assert dbsession.query(InvalidSequence).count() == 6

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

            # -- Sequence events ----------------

            unknown = dbsession.query(UnknownSequence).one()
            assert unknown.request == request
            assert unknown.user_id == 3002
            assert unknown.payload_data == unknown_sequence.get_data_as_bytes().get_data()

            app = dbsession.query(ShellAppIsOpen).one()
            assert app.request == request
            assert app.user_id == 3003
            assert app.app_id == 'org.gnome.Calendar'

            invalids = dbsession.query(InvalidSequence).order_by(InvalidSequence.id).all()
            assert len(invalids) == 2

            invalid = invalids[0]
            assert invalid.request == request
            assert invalid.user_id == 3005
            assert invalid.payload_data == invalid_sequence.get_data_as_bytes().get_data()

            invalid = invalids[1]
            assert invalid.request == request
            assert invalid.user_id == 3006
            assert invalid.payload_data == missing_events.get_data_as_bytes().get_data()

    def test_replay_unknown(self):
        from azafea.event_processors.endless.metrics.events import ShellAppIsOpen, Uptime
        from azafea.event_processors.endless.metrics.events._base import (
            InvalidSequence, InvalidSingularEvent,
            UnknownAggregateEvent, UnknownSequence, UnknownSingularEvent)
        from azafea.event_processors.endless.metrics.request import Request

        # Create the table
        self.run_subcommand('initdb')
        self.ensure_tables(Request, ShellAppIsOpen, Uptime, InvalidSequence, InvalidSingularEvent,
                           UnknownAggregateEvent, UnknownSequence, UnknownSingularEvent)

        occured_at = datetime.utcnow().replace(tzinfo=timezone.utc)

        with self.db as dbsession:
            request = Request(serialized=b'whatever', sha512='whatever', received_at=occured_at,
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

            # -- Unknown sequence events --------

            # Add an unknown sequence which will be ignored after the replay
            dbsession.add(UnknownSequence(
                request=request, event_id='9c33a734-7ed8-4348-9e39-3c27f4dc2e62', user_id=3001,
                payload=GLib.Variant('a(xmv)', [(3, GLib.Variant('s', 'discard')), (4, None)])))

            # Add an unknown sequence which will still be unknown after the replay
            unknown_sequence = GLib.Variant('a(xmv)', [
                (3, GLib.Variant('s', 'unknown')),
                (4, None),
            ])
            dbsession.add(UnknownSequence(
                request=request, event_id='ffffffff-ffff-ffff-ffff-ffffffffffff', user_id=3002,
                payload=unknown_sequence))

            # Add an unknown sequence which will be replayed as a shell app is open event
            dbsession.add(UnknownSequence(
                request=request, event_id='b5e11a3d-13f8-4219-84fd-c9ba0bf3d1f0', user_id=3003,
                payload=GLib.Variant('a(xmv)', [
                    (3, GLib.Variant('s', 'org.gnome.Calendar')),
                    (4, None),
                ])))

            # Add an unknown sequence which will be replayed as a user is logged in event, but with
            # an error we decided to ignore
            dbsession.add(UnknownSequence(
                request=request, event_id='add052be-7b2a-4959-81a5-a7f45062ee98', user_id=3004,
                payload=GLib.Variant('a(xmv)', [
                    (3, None),
                    (4, None),
                ])))

            # Add an unknown sequence which will be replayed as an shell app is open event, but
            # with an actual error making it invalid
            invalid_sequence = GLib.Variant('a(xmv)', [
                (3, GLib.Variant('ay', b'invalid')),
                (4, None)
            ])
            dbsession.add(UnknownSequence(
                request=request, event_id='b5e11a3d-13f8-4219-84fd-c9ba0bf3d1f0', user_id=3005,
                payload=invalid_sequence))

        with self.db as dbsession:
            assert dbsession.query(Request).count() == 1
            assert dbsession.query(UnknownSingularEvent).count() == 5
            assert dbsession.query(UnknownAggregateEvent).count() == 1
            assert dbsession.query(UnknownSequence).count() == 5

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

            # -- Sequence events ----------------

            unknown = dbsession.query(UnknownSequence).one()
            assert unknown.request == request
            assert unknown.user_id == 3002
            assert unknown.payload_data == unknown_sequence.get_data_as_bytes().get_data()

            app = dbsession.query(ShellAppIsOpen).one()
            assert app.request == request
            assert app.user_id == 3003
            assert app.app_id == 'org.gnome.Calendar'

            invalid = dbsession.query(InvalidSequence).one()
            assert invalid.request == request
            assert invalid.user_id == 3005
            assert invalid.payload_data == invalid_sequence.get_data_as_bytes().get_data()