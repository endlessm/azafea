# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from typing import Any, Dict

from gi.repository import GLib

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.schema import Column
from sqlalchemy.types import ARRAY, BigInteger, Boolean, Unicode

from ..utils import clamp_to_int64, get_child_values
from ._base import (  # noqa: F401
    AGGREGATE_EVENT_MODELS,
    IGNORED_EMPTY_PAYLOAD_ERRORS,
    IGNORED_EVENTS,
    SINGULAR_EVENT_MODELS,
    AggregateEvent,
    EmptyPayloadError,
    InvalidAggregateEvent,
    InvalidSingularEvent,
    SingularEvent,
    UnknownAggregateEvent,
    UnknownEvent,
    UnknownSingularEvent,
    WrongPayloadError,
    new_aggregate_event,
    new_singular_event,
    replay_invalid_aggregate_events,
    replay_invalid_singular_events,
    replay_unknown_aggregate_events,
    replay_unknown_singular_events,
    aggregate_event_is_known,
    parse_record,
    singular_event_is_known,
)


# -- Singular events ----------------------------------------------------------

class LaunchedEquivalentExistingFlatpak(SingularEvent):
    """Double-click on Windows exe or Linux package with a similar installed app.

    We launch the native version of a similar application since it is already
    installed. We record shell command line along with any arguments as well as
    the app ID of the replacement application. The purpose of this metric is to
    determine whether transparently launching a similar application reduces
    bounce rate.

    :UUID name: ``EVENT_LAUNCHED_EQUIVALENT_EXISTING_FLATPAK`` in eos-gates

    .. versionadded:: 3.2.4

    """
    __tablename__ = 'launched_equivalent_existing_flatpak_v3'
    __event_uuid__ = '00d7bc1e-ec93-4c53-ae78-a6b40450be4a'
    __payload_type__ = '(sas)'

    #: replacement application ID
    replacement_app_id = Column(Unicode, nullable=False)
    #: argv of the executable (Windows app or Linux package) the user tried to launch
    argv = Column(ARRAY(Unicode, dimensions=1), nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'replacement_app_id': payload.get_child_value(0).get_string(),
            'argv': payload.get_child_value(1).unpack(),
        }


class LaunchedEquivalentInstallerForFlatpak(SingularEvent):
    """Double-click on Windows exe or Linux package with a similar but not installed app in Store.

    We record shell command line along with any arguments as well as the app ID
    of the replacement application. The purpose of this metric is to determine
    whether guiding the user to the app store to install a similar application
    reduces bounce rate.

    :UUID name: ``EVENT_LAUNCHED_EQUIVALENT_INSTALLER_FOR_FLATPAK`` in eos-gates

    .. versionadded:: 3.2.4

    """
    __tablename__ = 'launched_equivalent_installer_for_flatpak_v3'
    __event_uuid__ = '7de69d43-5f6b-4bef-b5f3-a21295b79185'
    __payload_type__ = '(sas)'

    #: replacement application ID
    replacement_app_id = Column(Unicode, nullable=False)
    #: argv of the executable (Windows app or Linux package) the user tried to launch
    argv = Column(ARRAY(Unicode, dimensions=1), nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'replacement_app_id': payload.get_child_value(0).get_string(),
            'argv': payload.get_child_value(1).unpack(),
        }


class LaunchedExistingFlatpak(SingularEvent):
    """Double-click on Windows exe or Linux package with a native installed app.

    We launch the native version of the application since it is already
    installed. We record shell command line along with any arguments as well as
    the app ID of the replacement application. The purpose of this metric is to
    determine whether transparently launching the same application reduces
    bounce rate.

    :UUID name: ``EVENT_LAUNCHED_EXISTING_FLATPAK`` in eos-gates

    .. versionadded:: 3.2.4

    """
    __tablename__ = 'launched_existing_flatpak_v3'
    __event_uuid__ = '192f39dd-79b3-4497-99fa-9d8aea28760c'
    __payload_type__ = '(sas)'

    #: replacement application ID
    replacement_app_id = Column(Unicode, nullable=False)
    #: argv of the executable (Windows app or Linux package) the user tried to launch
    argv = Column(ARRAY(Unicode, dimensions=1), nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'replacement_app_id': payload.get_child_value(0).get_string(),
            'argv': payload.get_child_value(1).unpack(),
        }


class LaunchedInstallerForFlatpak(SingularEvent):
    """Double-click on Windows exe or Linux package with the same but not installed app in Store.

    We record shell command line along with any arguments as well as the app ID
    of the replacement application. The purpose of this metric is to determine
    whether guiding the user to the app store to install the *same* application
    reduces bounce rate.

    :UUID name: ``EVENT_LAUNCHED_INSTALLER_FOR_FLATPAK`` in eos-gates

    .. versionadded:: 3.2.4

    """
    __tablename__ = 'launched_installer_for_flatpak_v3'
    __event_uuid__ = 'e98bf6d9-8511-44f9-a1bd-a1d0518934b9'
    __payload_type__ = '(sas)'

    #: replacement application ID
    replacement_app_id = Column(Unicode, nullable=False)
    #: argv of the executable (Windows app or Linux package) the user tried to launch
    argv = Column(ARRAY(Unicode, dimensions=1), nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'replacement_app_id': payload.get_child_value(0).get_string(),
            'argv': payload.get_child_value(1).unpack(),
        }


class LinuxPackageOpened(SingularEvent):
    """A user tries to open a ``.rpm`` or ``.deb`` file.

    :UUID name: ``LINUX_PACKAGE_OPENED`` in eos-gates

    .. versionadded:: 2.1.7
    """
    __tablename__ = 'linux_package_opened_v3'
    __event_uuid__ = '0bba3340-52e3-41a2-854f-e6ed36621379'
    __payload_type__ = 'as'

    #: argv of the launched Windows application
    argv = Column(ARRAY(Unicode, dimensions=1), nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'argv': payload.unpack(),
        }


class ParentalControlsBlockedFlatpakInstall(SingularEvent):
    """An app prevented from being installed due to parental controls restrictions.

    This can happen if using the flatpak CLI, or if a UI app fails to hide a
    restricted app from its interface.

    See https://phabricator.endlessm.com/T28741#810046.

    :UUID name: ``FLATPAK_PARENTAL_CONTROLS_INSTALL_EVENT`` in flatpak

    .. versionadded:: 3.8.0

    """
    __tablename__ = 'parental_controls_blocked_flatpak_install_v3'
    __event_uuid__ = '9d03daad-f1ed-41a8-bc5a-6b532c075832'
    __payload_type__ = 's'

    #: flatpak reference for the app which as blocked from being installed
    #: (e.g. ``app/org.gnome.Totem/x86_64/stable``)
    app = Column(Unicode, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'app': payload.get_string(),
        }


class ParentalControlsBlockedFlatpakRun(SingularEvent):
    """An app prevented from being run due to parental controls restrictions.

    This can happen if using the flatpak CLI, or if a UI app fails to hide a
    restricted app from its interface.

    See https://phabricator.endlessm.com/T28741#810046.

    :UUID name: ``FLATPAK_PARENTAL_CONTROLS_INSTALL_EVENT`` in flatpak

    .. versionadded:: 3.8.0

    """
    __tablename__ = 'parental_controls_blocked_flatpak_run_v3'
    __event_uuid__ = 'afca2515-e9ce-43aa-b355-7663c770b4b6'
    __payload_type__ = 's'

    #: flatpak reference for the app which as blocked from being run
    #: (e.g. ``app/org.gnome.Totem/x86_64/stable``)
    app = Column(Unicode, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'app': payload.get_string(),
        }


class ParentalControlsChanged(SingularEvent):
    """Parental control app is closed.

    Recorded whenever ``malcontent-control`` is closed, presumably after the
    user has edited one or more parental controls.

    The payload contains the current parental controls settings for one user on
    the system, including identification about whether the user is an
    admin. Other user details (such as username or full name) are not
    included. The event is submitted multiple times, once for each (non-system)
    user on the system.

    The same event is also recorded at the end of Initial Setup if (and only
    if) parental controls were enabled for the main user during Initial
    Setup. In that case, the main user account has been set up as a child user,
    with no administrator privileges, and with parental controls enabled. A
    second user has been created as the administrator. The event contains the
    values of the initial parental controls settings, but no identifying
    information about the user (such as their username or full name). The
    intention is to allow comparisons of which parental controls are enabled
    initially by users, and which are enabled long term.

    See `T28741 <https://phabricator.endlessm.com/T28741#810046>`_ and `#101
    <https://github.com/endlessm/azafea/pull/101#discussion_r402610338>`_.

    The fields in the payload have the same semantics as the properties in the
    `AppFilter <https://gitlab.freedesktop.org/pwithnall/malcontent/-/blob/master/\
    accounts-service/com.endlessm.ParentalControls.AppFilter.xml>` interface.

    :UUID name: ``MCT_PARENTAL_CONTROLS_EVENT`` in malcontent and gnome-initial-setup

    .. versionadded:: 3.8.0

    """
    __tablename__ = 'parental_controls_changed_v3'
    __event_uuid__ = '449ec188-cb7b-45d3-a0ed-291d943b9aa6'
    __payload_type__ = 'a{sv}'

    #: boolean indicating whether the following app filter is a whitelist
    #: (true) or blacklist (false)
    app_filter_is_whitelist = Column(Boolean, nullable=False)
    #: list of strings containing filtered apps (either flatpak refs,
    #: absolute paths, or content types)
    app_filter = Column(ARRAY(Unicode, dimensions=1), nullable=False)
    #: string giving the filter schema (oars-1.0 or oars-1.1 at the moment),
    #: followed by a dictionary mapping OARS category strings to filter levels
    #: (none, mild, moderate, intense)
    oars_filter = Column(JSONB, nullable=False)
    #: boolean indicating whether installation of software to the user flatpak
    #: repository is allowed
    allow_user_installation = Column(Boolean, nullable=False)
    #: boolean indicating whether installation of software to the system
    #: flatpak repository is allowed
    allow_system_installation = Column(Boolean, nullable=False)
    #: boolean indicating whether the user is an administrator (optional,
    #: defaults to false)
    is_administrator = Column(Boolean, nullable=False)
    #: boolean indicating whether this event is being submitted from initial
    #: setup or from an installed desktop (optional, defaults to false)
    is_initial_setup = Column(Boolean, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        # Default values, as some a{sv} fields are optional:
        result: Dict[str, Any] = {
            'is_administrator': False,
            'is_initial_setup': False,
        }

        for item in get_child_values(payload):
            name = item.get_child_value(0).get_string()
            value = item.get_child_value(1).get_variant()

            if name == 'AppFilter':
                result['app_filter_is_whitelist'] = \
                    value.get_child_value(0).get_boolean()
                result['app_filter'] = value.get_child_value(1).unpack()

            elif name == 'OarsFilter':
                if value.get_child_value(0).get_string() not in ['oars-1.0', 'oars-1.1']:
                    raise ValueError('Metric event '
                                     f'{ParentalControlsChanged.__event_uuid__} '
                                     'needs an "OarsFilter" key in oars-1.0 '
                                     'or oars-1.1 format, but actually got '
                                     f'{payload}')
                result['oars_filter'] = value.get_child_value(1).unpack()

            elif name == 'AllowUserInstallation':
                result['allow_user_installation'] = value.get_boolean()

            elif name == 'AllowSystemInstallation':
                result['allow_system_installation'] = value.get_boolean()

            elif name == 'IsAdministrator':
                result['is_administrator'] = value.get_boolean()

            elif name == 'IsInitialSetup':
                result['is_initial_setup'] = value.get_boolean()

        if result.keys() < {'app_filter_is_whitelist', 'app_filter',
                            'oars_filter', 'allow_user_installation',
                            'allow_system_installation', 'is_administrator',
                            'is_initial_setup'}:
            raise ValueError('Metric event '
                             f'{ParentalControlsChanged.__event_uuid__} '
                             'needs an "a{sv}" payload with certain keys, but '
                             f'some were missing: got {payload}')

        return result


class ParentalControlsEnabled(SingularEvent):
    """Any parental controls are enabled for the current user.

    Recorded every time the App Center checks for OS updates (using its
    ``eos-updater plugin``). This was chosen as a convenient regular event
    which happens inside the user session, rather than because of some deeper
    link to parental controls.

    No identifying details about the user or which parental controls are
    enabled. It’s intended to allow aggregate statistics about how widely
    parental controls are enabled (in any form).

    See `T28741 <https://phabricator.endlessm.com/T28741#810046>`_.

    :UUID name: ``GS_PARENTAL_CONTROLS_USAGE_EVENT`` in gnome-software

    .. versionadded:: 3.8.0

    """
    __tablename__ = 'parental_controls_enabled_v3'
    __event_uuid__ = 'c227a817-808c-4fcb-b797-21002d17b69a'
    __payload_type__ = 'b'

    #: whether parental controls are enabled for this user
    enabled = Column(Boolean, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'enabled': payload.get_boolean(),
        }


class ProgramDumpedCore(SingularEvent):
    """A program crashes and ``systemd-coredump`` catches.

    We include the name of the program that crashed and the ostree commits of
    ostree repos on the system. We do not include programs that crashed within
    ``/home`` or ``/sysroot/home``.

    See `T18444 <https://phabricator.endlessm.com/T18444>`_.

    :UUID name: ``PROGRAM_DUMPED_CORE_EVENT`` in eos-metrics-instrumentation

    .. versionadded:: 3.2.5

    """
    __tablename__ = 'program_dumped_core_v3'
    __event_uuid__ = 'ed57b607-4a56-47f1-b1e4-5dc3e74335ec'
    __payload_type__ = 'a{sv}'

    #: Dictionary of strign-to-variant containing the following keys:
    #:
    #: - ``binary``: the path to the binary on the system
    #: - ``signal``: what signal caused the program to crash
    #: - ``timestamp``: the timestamp the kernel reported the crash at
    #: - ``ostree_commit``: the hash of the OSTree commit
    #: - ``ostree_url``: the URL of the OSTree repository
    #: - ``app_ref``: optionally, the full Flatpak app ref,
    #:   e.g. ``app/net.sourceforge.ExtremeTuxRacer/x86_64/stable``
    #: - ``app_commit``: optionally, the hash of the OSTree commit for the crashed Flatpak app
    #: - ``app_url``: optionally, the URL of the Flatpak repository for the crashed app
    #: - ``runtime_ref``: optionally, the full Flatpak runtime ref used by the crashed app
    #: - ``runtime_commit``: optionally, the hash of the OSTree commit for the Flatpak runtime used
    #:   by the crashed app
    #: - ``runtime_url``: optionally, the URL of the Flatpak repository for the runtime used by the
    #:   crashed app
    info = Column(JSONB, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {'info': payload.unpack()}


class UpdaterFailure(SingularEvent):
    """Failure of eos-updater or eos-updater-flatpak-installer for whatever reason.

    This can happen if an upgrade fails, or if installing required flatpaks fails.

    See `T29247 <https://phabricator.endlessm.com/T29247>`_.

    :UUID name: ``EOS_UPDATER_METRIC_FAILURE`` in eos-updater

    .. versionadded:: 2.6.0

    """
    __tablename__ = 'updater_failure_v3'
    __event_uuid__ = '927d0f61-4890-4912-a513-b2cb0205908f'
    __payload_type__ = '(ss)'

    component = Column(Unicode, nullable=False)
    error_message = Column(Unicode, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'component': payload.get_child_value(0).get_string(),
            'error_message': payload.get_child_value(1).get_string(),
        }


class WindowsAppOpened(SingularEvent):
    """A user tries to open a ``.exe`` or ``.msi`` file.

    :UUID name: ``WINDOWS_APP_OPENED`` in eos-gates

    .. versionadded:: 2.1.5

    """
    __tablename__ = 'windows_app_opened_v3'
    __event_uuid__ = 'cf09194a-3090-4782-ab03-87b2f1515aed'
    __payload_type__ = 'as'

    #: argv of the launched Windows application
    argv = Column(ARRAY(Unicode, dimensions=1), nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'argv': payload.unpack(),
        }


class StartupFinished(SingularEvent):
    """Computer startup finishes.

    We send this event when startup finishes with a breakdown of how long was
    spent in each of several different phases of startup.

    The value comes directly from `systemd’s StartupFinished signal
    <https://www.freedesktop.org/wiki/Software/systemd/dbus/\
    #Manager-StartupFinished>`_.

    :UUID name: ``STARTUP_FINISHED`` in eos-metrics-instrumentation

    .. versionadded:: 2.1.2

    """
    __tablename__ = 'startup_finished_v3'
    __event_uuid__ = 'bf7e8aed-2932-455c-a28e-d407cfd5aaba'
    __payload_type__ = '(tttttt)'

    # These come in as uint64, but the values won’t reach the limit of a BIGINT (int64, 2**63):
    # 2**63 microseconds ≈ 300,000 years
    #: time spent in the firmware (if known) in µsec
    firmware = Column(BigInteger, nullable=False)
    #: time spent in the boot loader (if known) in µsec
    loader = Column(BigInteger, nullable=False)
    #: time spent in the kernel initialization phase in µsec
    kernel = Column(BigInteger, nullable=False)
    #: time spent in the initrd (if known) in µsec
    initrd = Column(BigInteger, nullable=False)
    #: time spent in userspace in µsec
    userspace = Column(BigInteger, nullable=False)
    #: total time spent to boot in µsec
    total = Column(BigInteger, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {
            'firmware': clamp_to_int64(payload.get_child_value(0).get_uint64()),
            'loader': clamp_to_int64(payload.get_child_value(1).get_uint64()),
            'kernel': clamp_to_int64(payload.get_child_value(2).get_uint64()),
            'initrd': clamp_to_int64(payload.get_child_value(3).get_uint64()),
            'userspace': clamp_to_int64(payload.get_child_value(4).get_uint64()),
            'total': clamp_to_int64(payload.get_child_value(5).get_uint64()),
        }


class ComputerInformation(SingularEvent):
    """Information about the computer RAM, disk and CPU.

    Sent at most once a day.

    :UUID name: TODO

    .. versionadded:: 4.0.0

    """
    __tablename__ = 'computer_information_v3'
    __event_uuid__ = '81f303aa-448d-443d-97f9-8d8a9169321c'
    __payload_type__ = '(uuuua(sqd))'

    #: total RAM size in mebibytes (2^20)
    total_ram = Column(BigInteger, nullable=False)
    #: total disk space in gibibytes (2^30)
    total_disk = Column(BigInteger, nullable=False)
    #: used disk space in gibibytes (2^30)
    used_disk = Column(BigInteger, nullable=False)
    #: free disk space in gibibytes (2^30)
    free_disk = Column(BigInteger, nullable=False)
    #: array of CPU model (e.g. Intel(R) Core(TM) i7-5500U CPU @ 2.40GHz),
    #: number of cores (e.g. 4) and maximum CPU speed in MHz or current CPU speed
    #: if maximum can’t be determined (e.g. 3000.0)
    info = Column(JSONB, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        cpu_info = []
        for i in range(payload.get_child_value(4).n_children()):
            item = payload.get_child_value(i)
            cpu_info.append({
                'model': item.get_child_value(0).get_string(),
                'cores': item.get_child_value(1).get_uint16(),
                'max_frequency': item.get_child_value(2).get_double(),
            })
        return {
            'total_ram': payload.get_child_value(0).get_uint32(),
            'total_disk': payload.get_child_value(1).get_uint32(),
            'used_disk': payload.get_child_value(2).get_uint32(),
            'free_disk': payload.get_child_value(3).get_uint32(),
            'cpu_info': cpu_info,
        }


# -- Aggregate events ---------------------------------------------------------

class TimeSpentByForegroundApp(AggregateEvent):
    """Number of seconds spent by an application open in foreground.

    Aggregation is done by day.

    :UUID name: TODO

    .. versionadded:: 4.0.0

    """
    __tablename__ = 'time_spent_by_foreground_app_v3'
    __event_uuid__ = '49d0451a-f706-4f50-81d2-70cc0ec923a4'
    __payload_type__ = 's'

    #: application ID
    app_id = Column(Unicode, nullable=False)

    @staticmethod
    def _get_fields_from_payload(payload: GLib.Variant) -> Dict[str, Any]:
        return {'app_id': payload.get_string()}


class DifferentUsers(AggregateEvent):
    """Number of different users who opened a session.

    Aggregation is done by month.

    :UUID name: TODO

    .. versionadded:: 4.0.0

    """
    __tablename__ = 'different_users_v3'
    __event_uuid__ = 'a3826320-9192-446a-8886-e2129c0ce302'


class TimeSpentInSession(AggregateEvent):
    """Number of seconds spent on the computer with an open session.

    Aggregation is done by hour.

    :UUID name: TODO

    .. versionadded:: 4.0.0

    """
    __tablename__ = 'time_spent_in_session_v3'
    __event_uuid__ = '5dc0b53c-93f9-4df0-ad6f-bd25e9fe638f'
