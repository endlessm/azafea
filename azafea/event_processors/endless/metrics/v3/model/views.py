from azafea.model import DbSession, View
from azafea.event_processors.endless.metrics.v2.model import (
    LaunchedEquivalentExistingFlatpak as LaunchedEquivalentExistingFlatpakV2,
    LaunchedEquivalentInstallerForFlatpak as LaunchedEquivalentInstallerForFlatpakV2,
    LaunchedExistingFlatpak as LaunchedExistingFlatpakV2,
    LaunchedInstallerForFlatpak as LaunchedInstallerForFlatpakV2,
    LinuxPackageOpened as LinuxPackageOpenedV2,
    ParentalControlsBlockedFlatpakInstall as ParentalControlsBlockedFlatpakInstallV2,
    ParentalControlsBlockedFlatpakRun as ParentalControlsBlockedFlatpakRunV2,
    ParentalControlsChanged as ParentalControlsChangedV2,
    ParentalControlsEnabled as ParentalControlsEnabledV2,
    ProgramDumpedCore as ProgramDumpedCoreV2,
    UpdaterFailure as UpdaterFailureV2,
    WindowsAppOpened as WindowsAppOpenedV2,
    StartupFinished as StartupFinishedV2,
    Request,
    Machine,
    OSVersion
)


class LaunchedEquivalentExistingFlatpakViewV2(View):
    __tablename__ = 'launched_equivalent_existing_flatpak_view_v2'

    __query__ = DbSession().query(
        LaunchedEquivalentExistingFlatpakV2.occured_at,
        OSVersion.version.label('os_version'),
        LaunchedEquivalentExistingFlatpakV2.replacement_app_id,
        LaunchedEquivalentExistingFlatpakV2.argv,
        Machine.image_id,
        Machine.location.label('site'),
        Machine.dualboot.label('dual_boot'),
        Machine.live
    ).select_from(
        LaunchedEquivalentExistingFlatpakV2
    ).outerjoin(
        Request
    ).outerjoin(
        Machine, Request.machine_id == Machine.machine_id
    ).outerjoin(
        OSVersion
    ).filter(
        Machine.demo.is_(False)
    ).distinct(
        LaunchedExistingFlatpakV2.id
    )


class LaunchedEquivalentInstallerForFlatpakViewV2(View):
    __tablename__ = 'launched_equivalent_installer_for_flatpak_view_v2'

    __query__ = DbSession().query(
        LaunchedEquivalentInstallerForFlatpakV2.occured_at,
        OSVersion.version.label('os_version'),
        LaunchedEquivalentInstallerForFlatpakV2.replacement_app_id,
        LaunchedEquivalentInstallerForFlatpakV2.argv,
        Machine.image_id,
        Machine.location.label('site'),
        Machine.dualboot.label('dual_boot'),
        Machine.live
    ).select_from(
        LaunchedEquivalentInstallerForFlatpakV2
    ).outerjoin(
        Request
    ).outerjoin(
        Machine, Request.machine_id == Machine.machine_id
    ).outerjoin(
        OSVersion
    ).filter(
        Machine.demo.is_(False)
    ).distinct(
        LaunchedEquivalentInstallerForFlatpakV2.id
    )


class LaunchedExistingFlatpakViewV2(View):
    __tablename__ = 'launched_existing_flatpak_view_v2'

    __query__ = DbSession().query(
        LaunchedExistingFlatpakV2.occured_at,
        OSVersion.version.label('os_version'),
        LaunchedExistingFlatpakV2.replacement_app_id,
        LaunchedExistingFlatpakV2.argv,
        Machine.image_id,
        Machine.location.label('site'),
        Machine.dualboot.label('dual_boot'),
        Machine.live
    ).select_from(
        LaunchedExistingFlatpakV2
    ).outerjoin(
        Request
    ).outerjoin(
        Machine, Request.machine_id == Machine.machine_id
    ).outerjoin(
        OSVersion
    ).filter(
        Machine.demo.is_(False)
    ).distinct(
        LaunchedExistingFlatpakV2.id
    )


class LaunchedInstallerForFlatpakViewV2(View):
    __tablename__ = 'launched_installer_for_flatpak_view_v2'

    __query__ = DbSession().query(
        LaunchedInstallerForFlatpakV2.occured_at,
        OSVersion.version.label('os_version'),
        LaunchedInstallerForFlatpakV2.replacement_app_id,
        LaunchedInstallerForFlatpakV2.argv,
        Machine.image_id,
        Machine.location.label('site'),
        Machine.dualboot.label('dual_boot'),
        Machine.live
    ).select_from(
        LaunchedInstallerForFlatpakV2
    ).outerjoin(
        Request
    ).outerjoin(
        Machine, Request.machine_id == Machine.machine_id
    ).outerjoin(
        OSVersion
    ).filter(
        Machine.demo.is_(False)
    ).distinct(
        LaunchedInstallerForFlatpakV2.id
    )


class LinuxPackageOpenedViewV2(View):
    __tablename__ = 'linux_package_opened_view_v2'

    __query__ = DbSession().query(
        LinuxPackageOpenedV2.occured_at,
        OSVersion.version.label('os_version'),
        LinuxPackageOpenedV2.argv,
        Machine.image_id,
        Machine.location.label('site'),
        Machine.dualboot.label('dual_boot'),
        Machine.live
    ).select_from(
        LinuxPackageOpenedV2
    ).outerjoin(
        Request
    ).outerjoin(
        Machine, Request.machine_id == Machine.machine_id
    ).outerjoin(
        OSVersion
    ).filter(
        Machine.demo.is_(False)
    ).distinct(
        LinuxPackageOpenedV2.id
    )


class ParentalControlsBlockedFlatpakInstallViewV2(View):
    __tablename__ = 'parental_controls_blocked_flatpak_install_view_v2'

    __query__ = DbSession().query(
        ParentalControlsBlockedFlatpakInstallV2.occured_at,
        OSVersion.version.label('os_version'),
        ParentalControlsBlockedFlatpakInstallV2.app,
        Machine.image_id,
        Machine.location.label('site'),
        Machine.dualboot.label('dual_boot'),
        Machine.live
    ).select_from(
        ParentalControlsBlockedFlatpakInstallV2
    ).outerjoin(
        Request
    ).outerjoin(
        Machine, Request.machine_id == Machine.machine_id
    ).outerjoin(
        OSVersion
    ).filter(
        Machine.demo.is_(False)
    ).distinct(
        ParentalControlsBlockedFlatpakInstallV2.id
    )


class ParentalControlsBlockedFlatpakRunViewV2(View):
    __tablename__ = 'parental_controls_blocked_flatpak_run_view_v2'

    __query__ = DbSession().query(
        ParentalControlsBlockedFlatpakRunV2.occured_at,
        OSVersion.version.label('os_version'),
        ParentalControlsBlockedFlatpakRunV2.app,
        Machine.image_id,
        Machine.location.label('site'),
        Machine.dualboot.label('dual_boot'),
        Machine.live
    ).select_from(
        ParentalControlsBlockedFlatpakRunV2
    ).outerjoin(
        Request
    ).outerjoin(
        Machine, Request.machine_id == Machine.machine_id
    ).outerjoin(
        OSVersion
    ).filter(
        Machine.demo.is_(False)
    ).distinct(
        ParentalControlsBlockedFlatpakRunV2.id
    )


class ParentalControlsChangedViewV2(View):
    __tablename__ = 'parental_controls_changed_view_v2'

    __query__ = DbSession().query(
        ParentalControlsChangedV2.occured_at,
        OSVersion.version.label('os_version'),
        ParentalControlsChangedV2.app_filter_is_whitelist,
        ParentalControlsChangedV2.app_filter,
        ParentalControlsChangedV2.oars_filter,
        ParentalControlsChangedV2.allow_user_installation,
        ParentalControlsChangedV2.allow_system_installation,
        ParentalControlsChangedV2.is_administrator,
        ParentalControlsChangedV2.is_initial_setup,
        Machine.image_id,
        Machine.location.label('site'),
        Machine.dualboot.label('dual_boot'),
        Machine.live
    ).select_from(
        ParentalControlsChangedV2
    ).outerjoin(
        Request
    ).outerjoin(
        Machine, Request.machine_id == Machine.machine_id
    ).outerjoin(
        OSVersion
    ).filter(
        Machine.demo.is_(False)
    ).distinct(
        ParentalControlsChangedV2.id
    )


class ParentalControlsEnabledViewV2(View):
    __tablename__ = 'parental_controls_enabled_view_v2'

    __query__ = DbSession().query(
        ParentalControlsEnabledV2.occured_at,
        OSVersion.version.label('os_version'),
        ParentalControlsEnabledV2.enabled,
        Machine.image_id,
        Machine.location.label('site'),
        Machine.dualboot.label('dual_boot'),
        Machine.live
    ).select_from(
        ParentalControlsEnabledV2
    ).outerjoin(
        Request
    ).outerjoin(
        Machine, Request.machine_id == Machine.machine_id
    ).outerjoin(
        OSVersion
    ).filter(
        Machine.demo.is_(False)
    ).distinct(
        ParentalControlsEnabledV2.id
    )


class ProgramDumpedCoreViewV2(View):
    __tablename__ = 'program_dumped_core_view_v2'

    __query__ = DbSession().query(
        ProgramDumpedCoreV2.occured_at,
        OSVersion.version.label('os_version'),
        ProgramDumpedCoreV2.info,
        Machine.image_id,
        Machine.location.label('site'),
        Machine.dualboot.label('dual_boot'),
        Machine.live
    ).select_from(
        ProgramDumpedCoreV2
    ).outerjoin(
        Request
    ).outerjoin(
        Machine, Request.machine_id == Machine.machine_id
    ).outerjoin(
        OSVersion
    ).filter(
        Machine.demo.is_(False)
    ).distinct(
        ProgramDumpedCoreV2.id
    )


class UpdaterFailureViewV2(View):
    __tablename__ = 'updater_failure_view_v2'

    __query__ = DbSession().query(
        UpdaterFailureV2.occured_at,
        OSVersion.version.label('os_version'),
        UpdaterFailureV2.component,
        UpdaterFailureV2.error_message,
        Machine.image_id,
        Machine.location.label('site'),
        Machine.dualboot.label('dual_boot'),
        Machine.live
    ).select_from(
        UpdaterFailureV2
    ).outerjoin(
        Request
    ).outerjoin(
        Machine, Request.machine_id == Machine.machine_id
    ).outerjoin(
        OSVersion
    ).filter(
        Machine.demo.is_(False)
    ).distinct(
        UpdaterFailureV2.id
    )


class WindowsAppOpenedViewV2(View):
    __tablename__ = 'windows_app_opened_view_v2'

    __query__ = DbSession().query(
        WindowsAppOpenedV2.occured_at,
        OSVersion.version.label('os_version'),
        WindowsAppOpenedV2.argv,
        Machine.image_id,
        Machine.location.label('site'),
        Machine.dualboot.label('dual_boot'),
        Machine.live
    ).select_from(
        WindowsAppOpenedV2
    ).outerjoin(
        Request
    ).outerjoin(
        Machine, Request.machine_id == Machine.machine_id
    ).outerjoin(
        OSVersion
    ).filter(
        Machine.demo.is_(False)
    ).distinct(
        WindowsAppOpenedV2.id
    )


class StartupFinishedViewV2(View):
    __tablename__ = 'startup_finished_view_v2'

    __query__ = DbSession().query(
        StartupFinishedV2.occured_at,
        OSVersion.version.label('os_version'),
        StartupFinishedV2.firmware,
        StartupFinishedV2.loader,
        StartupFinishedV2.kernel,
        StartupFinishedV2.initrd,
        StartupFinishedV2.userspace,
        StartupFinishedV2.total,
        Machine.image_id,
        Machine.location.label('site'),
        Machine.dualboot.label('dual_boot'),
        Machine.live
    ).select_from(
        StartupFinishedV2
    ).outerjoin(
        Request
    ).outerjoin(
        Machine, Request.machine_id == Machine.machine_id
    ).outerjoin(
        OSVersion
    ).filter(
        Machine.demo.is_(False)
    ).distinct(
        StartupFinishedV2.id
    )
