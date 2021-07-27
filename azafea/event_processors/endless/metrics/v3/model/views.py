from .events import (
    LaunchedEquivalentExistingFlatpak as LaunchedEquivalentExistingFlatpakV3,
    LaunchedEquivalentInstallerForFlatpak as LaunchedEquivalentInstallerForFlatpakV3,
    LaunchedExistingFlatpak as LaunchedExistingFlatpakV3,
    LaunchedInstallerForFlatpak as LaunchedInstallerForFlatpakV3,
    LinuxPackageOpened as LinuxPackageOpenedV3,
    ParentalControlsBlockedFlatpakInstall as ParentalControlsBlockedFlatpakInstallV3,
    ParentalControlsBlockedFlatpakRun as ParentalControlsBlockedFlatpakRunV3,
    ParentalControlsChanged as ParentalControlsChangedV3,
    ParentalControlsEnabled as ParentalControlsEnabledV3,
    ProgramDumpedCore as ProgramDumpedCoreV3,
    UpdaterFailure as UpdaterFailureV3,
    WindowsAppOpened as WindowsAppOpenedV3,
    StartupFinished as StartupFinishedV3
)
from ._base import Channel
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
    __materialized__ = True

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
    __materialized__ = True

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
    __materialized__ = True

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
    __materialized__ = True

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
    __materialized__ = True

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
    __materialized__ = True

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
    __materialized__ = True

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
    __materialized__ = True

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
    __materialized__ = True

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
    __materialized__ = True

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
    __materialized__ = True

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
    __materialized__ = True

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
    __materialized__ = True

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


class LaunchedEquivalentExistingFlatpakView(View):
    __tablename__ = 'launched_equivalent_existing_flatpak_view'

    __query__ = DbSession().query(
        LaunchedEquivalentExistingFlatpakV3.occured_at,
        LaunchedEquivalentExistingFlatpakV3.os_version,
        LaunchedEquivalentExistingFlatpakV3.replacement_app_id,
        LaunchedEquivalentExistingFlatpakV3.argv,
        Channel.image_id,
        Channel.site,
        Channel.dual_boot,
        Channel.live
    ).select_from(
        LaunchedEquivalentExistingFlatpakV3
    ).join(
        Channel
    ).union_all(
        LaunchedEquivalentExistingFlatpakViewV2
    )


class LaunchedEquivalentInstallerForFlatpakView(View):
    __tablename__ = 'launched_equivalent_installer_for_flatpak_view'

    __query__ = DbSession().query(
        LaunchedEquivalentInstallerForFlatpakV3.occured_at,
        LaunchedEquivalentInstallerForFlatpakV3.os_version,
        LaunchedEquivalentInstallerForFlatpakV3.replacement_app_id,
        LaunchedEquivalentInstallerForFlatpakV3.argv,
        Channel.image_id,
        Channel.site,
        Channel.dual_boot,
        Channel.live
    ).select_from(
        LaunchedEquivalentInstallerForFlatpakV3
    ).join(
        Channel
    ).union_all(
        LaunchedEquivalentInstallerForFlatpakViewV2
    )


class LaunchedExistingFlatpakView(View):
    __tablename__ = 'launched_existing_flatpak_view'

    __query__ = DbSession().query(
        LaunchedExistingFlatpakV3.occured_at,
        LaunchedExistingFlatpakV3.os_version,
        LaunchedExistingFlatpakV3.replacement_app_id,
        LaunchedExistingFlatpakV3.argv,
        Channel.image_id,
        Channel.site,
        Channel.dual_boot,
        Channel.live
    ).select_from(
        LaunchedExistingFlatpakV3
    ).join(
        Channel
    ).union_all(
        LaunchedExistingFlatpakViewV2
    )


class LaunchedInstallerForFlatpakView(View):
    __tablename__ = 'launched_installer_for_flatpak_view'

    __query__ = DbSession().query(
        LaunchedInstallerForFlatpakV3.occured_at,
        LaunchedInstallerForFlatpakV3.os_version,
        LaunchedInstallerForFlatpakV3.replacement_app_id,
        LaunchedInstallerForFlatpakV3.argv,
        Channel.image_id,
        Channel.site,
        Channel.dual_boot,
        Channel.live
    ).select_from(
        LaunchedInstallerForFlatpakV3
    ).join(
        Channel
    ).union(
        LaunchedInstallerForFlatpakViewV2
    )


class LinuxPackageOpenedView(View):
    __tablename__ = 'linux_package_opened_view'

    __query__ = DbSession().query(
        LinuxPackageOpenedV3.occured_at,
        LinuxPackageOpenedV3.os_version,
        LinuxPackageOpenedV3.argv,
        Channel.image_id,
        Channel.site,
        Channel.dual_boot,
        Channel.live
    ).select_from(
        LinuxPackageOpenedV3
    ).join(
        Channel
    ).union(
        LinuxPackageOpenedViewV2
    )


class ParentalControlsBlockedFlatpakInstallView(View):
    __tablename__ = 'parental_controls_blocked_flatpak_install_view'

    __query__ = DbSession().query(
        ParentalControlsBlockedFlatpakInstallV3.occured_at,
        ParentalControlsBlockedFlatpakInstallV3.os_version,
        ParentalControlsBlockedFlatpakInstallV3.app,
        Channel.image_id,
        Channel.site,
        Channel.dual_boot,
        Channel.live
    ).select_from(
        ParentalControlsBlockedFlatpakInstallV3
    ).join(
        Channel
    ).union(
        ParentalControlsBlockedFlatpakInstallViewV2
    )


class ParentalControlsBlockedFlatpakRunView(View):
    __tablename__ = 'parental_controls_blocked_flatpak_run_view'

    __query__ = DbSession().query(
        ParentalControlsBlockedFlatpakRunV3.occured_at,
        ParentalControlsBlockedFlatpakRunV3.os_version,
        ParentalControlsBlockedFlatpakRunV3.app,
        Channel.image_id,
        Channel.site,
        Channel.dual_boot,
        Channel.live
    ).select_from(
        ParentalControlsBlockedFlatpakRunV3
    ).join(
        Channel
    ).union(
        ParentalControlsBlockedFlatpakRunViewV2
    )


class ParentalControlsChangedView(View):
    __tablename__ = 'parental_controls_changed_view'

    __query__ = DbSession().query(
        ParentalControlsChangedV3.occured_at,
        ParentalControlsChangedV3.os_version,
        ParentalControlsChangedV3.app_filter_is_whitelist,
        ParentalControlsChangedV3.app_filter,
        ParentalControlsChangedV3.oars_filter,
        ParentalControlsChangedV3.allow_user_installation,
        ParentalControlsChangedV3.allow_system_installation,
        ParentalControlsChangedV3.is_administrator,
        ParentalControlsChangedV3.is_initial_setup,
        Channel.image_id,
        Channel.site,
        Channel.dual_boot,
        Channel.live
    ).select_from(
        ParentalControlsChangedV3
    ).join(
        Channel
    ).union(
        ParentalControlsChangedViewV2
    )


class ParentalControlsEnabledView(View):
    __tablename__ = 'parental_controls_enabled_view'

    __query__ = DbSession().query(
        ParentalControlsEnabledV3.occured_at,
        ParentalControlsEnabledV3.os_version,
        ParentalControlsEnabledV3.enabled,
        Channel.image_id,
        Channel.site,
        Channel.dual_boot,
        Channel.live
    ).select_from(
        ParentalControlsEnabledV3
    ).join(
        Channel
    ).union(
        ParentalControlsEnabledViewV2
    )


class ProgramDumpedCoreView(View):
    __tablename__ = 'program_dumped_core_view'

    __query__ = DbSession().query(
        ProgramDumpedCoreV3.occured_at,
        ProgramDumpedCoreV3.os_version,
        ProgramDumpedCoreV3.info,
        Channel.image_id,
        Channel.site,
        Channel.dual_boot,
        Channel.live
    ).select_from(
        ProgramDumpedCoreV3
    ).join(
        Channel
    ).union(
        ProgramDumpedCoreViewV2
    )


class UpdaterFailureView(View):
    __tablename__ = 'updater_failure_view'

    __query__ = DbSession().query(
        UpdaterFailureV3.occured_at,
        UpdaterFailureV3.os_version,
        UpdaterFailureV3.component,
        UpdaterFailureV3.error_message,
        Channel.image_id,
        Channel.site,
        Channel.dual_boot,
        Channel.live
    ).select_from(
        UpdaterFailureV3
    ).join(
        Channel
    ).union(
        UpdaterFailureViewV2
    )


class WindowsAppOpenedView(View):
    __tablename__ = 'windows_app_opened_view'

    __query__ = DbSession().query(
        WindowsAppOpenedV3.occured_at,
        WindowsAppOpenedV3.os_version,
        WindowsAppOpenedV3.argv,
        Channel.image_id,
        Channel.site,
        Channel.dual_boot,
        Channel.live
    ).select_from(
        WindowsAppOpenedV3
    ).join(
        Channel
    ).union(
        WindowsAppOpenedViewV2
    )


class StartupFinishedView(View):
    __tablename__ = 'startup_finished_view'

    __query__ = DbSession().query(
        StartupFinishedV3.occured_at,
        StartupFinishedV3.os_version,
        StartupFinishedV3.firmware,
        StartupFinishedV3.loader,
        StartupFinishedV3.kernel,
        StartupFinishedV3.initrd,
        StartupFinishedV3.userspace,
        StartupFinishedV3.total,
        Channel.image_id,
        Channel.site,
        Channel.dual_boot,
        Channel.live
    ).select_from(
        StartupFinishedV3
    ).join(
        Channel
    ).union_all(
        StartupFinishedViewV2
    )
