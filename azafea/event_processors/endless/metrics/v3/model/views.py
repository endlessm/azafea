# type: ignore

from . import events as v3
from ._base import Channel
from azafea.model import DbSession, View
from azafea.event_processors.endless.metrics.v2 import model as v2


class LaunchedEquivalentExistingFlatpakViewV2(View):
    __tablename__ = 'launched_equivalent_existing_flatpak_view_v2'
    __materialized__ = True

    __query__ = DbSession().query(
        v2.LaunchedEquivalentExistingFlatpak.occured_at,
        v2.OSVersion.version.label('os_version'),
        v2.LaunchedEquivalentExistingFlatpak.replacement_app_id,
        v2.LaunchedEquivalentExistingFlatpak.argv,
        v2.Machine.image_id,
        v2.Machine.location.label('site'),
        v2.Machine.dualboot.label('dual_boot'),
        v2.Machine.live
    ).select_from(
        v2.LaunchedEquivalentExistingFlatpak
    ).outerjoin(
        v2.Request
    ).outerjoin(
        v2.Machine, v2.Request.machine_id == v2.Machine.machine_id
    ).outerjoin(
        v2.OSVersion
    ).filter(
        v2.Machine.demo.is_(False)
    ).distinct(
        v2.LaunchedExistingFlatpak.id
    )


class LaunchedEquivalentInstallerForFlatpakViewV2(View):
    __tablename__ = 'launched_equivalent_installer_for_flatpak_view_v2'
    __materialized__ = True

    __query__ = DbSession().query(
        v2.LaunchedEquivalentInstallerForFlatpak.occured_at,
        v2.OSVersion.version.label('os_version'),
        v2.LaunchedEquivalentInstallerForFlatpak.replacement_app_id,
        v2.LaunchedEquivalentInstallerForFlatpak.argv,
        v2.Machine.image_id,
        v2.Machine.location.label('site'),
        v2.Machine.dualboot.label('dual_boot'),
        v2.Machine.live
    ).select_from(
        v2.LaunchedEquivalentInstallerForFlatpak
    ).outerjoin(
        v2.Request
    ).outerjoin(
        v2.Machine, v2.Request.machine_id == v2.Machine.machine_id
    ).outerjoin(
        v2.OSVersion
    ).filter(
        v2.Machine.demo.is_(False)
    ).distinct(
        v2.LaunchedEquivalentInstallerForFlatpak.id
    )


class LaunchedExistingFlatpakViewV2(View):
    __tablename__ = 'launched_existing_flatpak_view_v2'
    __materialized__ = True

    __query__ = DbSession().query(
        v2.LaunchedExistingFlatpak.occured_at,
        v2.OSVersion.version.label('os_version'),
        v2.LaunchedExistingFlatpak.replacement_app_id,
        v2.LaunchedExistingFlatpak.argv,
        v2.Machine.image_id,
        v2.Machine.location.label('site'),
        v2.Machine.dualboot.label('dual_boot'),
        v2.Machine.live
    ).select_from(
        v2.LaunchedExistingFlatpak
    ).outerjoin(
        v2.Request
    ).outerjoin(
        v2.Machine, v2.Request.machine_id == v2.Machine.machine_id
    ).outerjoin(
        v2.OSVersion
    ).filter(
        v2.Machine.demo.is_(False)
    ).distinct(
        v2.LaunchedExistingFlatpak.id
    )


class LaunchedInstallerForFlatpakViewV2(View):
    __tablename__ = 'launched_installer_for_flatpak_view_v2'
    __materialized__ = True

    __query__ = DbSession().query(
        v2.LaunchedInstallerForFlatpak.occured_at,
        v2.OSVersion.version.label('os_version'),
        v2.LaunchedInstallerForFlatpak.replacement_app_id,
        v2.LaunchedInstallerForFlatpak.argv,
        v2.Machine.image_id,
        v2.Machine.location.label('site'),
        v2.Machine.dualboot.label('dual_boot'),
        v2.Machine.live
    ).select_from(
        v2.LaunchedInstallerForFlatpak
    ).outerjoin(
        v2.Request
    ).outerjoin(
        v2.Machine, v2.Request.machine_id == v2.Machine.machine_id
    ).outerjoin(
        v2.OSVersion
    ).filter(
        v2.Machine.demo.is_(False)
    ).distinct(
        v2.LaunchedInstallerForFlatpak.id
    )


class LinuxPackageOpenedViewV2(View):
    __tablename__ = 'linux_package_opened_view_v2'
    __materialized__ = True

    __query__ = DbSession().query(
        v2.LinuxPackageOpened.occured_at,
        v2.OSVersion.version.label('os_version'),
        v2.LinuxPackageOpened.argv,
        v2.Machine.image_id,
        v2.Machine.location.label('site'),
        v2.Machine.dualboot.label('dual_boot'),
        v2.Machine.live
    ).select_from(
        v2.LinuxPackageOpened
    ).outerjoin(
        v2.Request
    ).outerjoin(
        v2.Machine, v2.Request.machine_id == v2.Machine.machine_id
    ).outerjoin(
        v2.OSVersion
    ).filter(
        v2.Machine.demo.is_(False)
    ).distinct(
        v2.LinuxPackageOpened.id
    )


class ParentalControlsBlockedFlatpakInstallViewV2(View):
    __tablename__ = 'parental_controls_blocked_flatpak_install_view_v2'
    __materialized__ = True

    __query__ = DbSession().query(
        v2.ParentalControlsBlockedFlatpakInstall.occured_at,
        v2.OSVersion.version.label('os_version'),
        v2.ParentalControlsBlockedFlatpakInstall.app,
        v2.Machine.image_id,
        v2.Machine.location.label('site'),
        v2.Machine.dualboot.label('dual_boot'),
        v2.Machine.live
    ).select_from(
        v2.ParentalControlsBlockedFlatpakInstall
    ).outerjoin(
        v2.Request
    ).outerjoin(
        v2.Machine, v2.Request.machine_id == v2.Machine.machine_id
    ).outerjoin(
        v2.OSVersion
    ).filter(
        v2.Machine.demo.is_(False)
    ).distinct(
        v2.ParentalControlsBlockedFlatpakInstall.id
    )


class ParentalControlsBlockedFlatpakRunViewV2(View):
    __tablename__ = 'parental_controls_blocked_flatpak_run_view_v2'
    __materialized__ = True

    __query__ = DbSession().query(
        v2.ParentalControlsBlockedFlatpakRun.occured_at,
        v2.OSVersion.version.label('os_version'),
        v2.ParentalControlsBlockedFlatpakRun.app,
        v2.Machine.image_id,
        v2.Machine.location.label('site'),
        v2.Machine.dualboot.label('dual_boot'),
        v2.Machine.live
    ).select_from(
        v2.ParentalControlsBlockedFlatpakRun
    ).outerjoin(
        v2.Request
    ).outerjoin(
        v2.Machine, v2.Request.machine_id == v2.Machine.machine_id
    ).outerjoin(
        v2.OSVersion
    ).filter(
        v2.Machine.demo.is_(False)
    ).distinct(
        v2.ParentalControlsBlockedFlatpakRun.id
    )


class ParentalControlsChangedViewV2(View):
    __tablename__ = 'parental_controls_changed_view_v2'
    __materialized__ = True

    __query__ = DbSession().query(
        v2.ParentalControlsChanged.occured_at,
        v2.OSVersion.version.label('os_version'),
        v2.ParentalControlsChanged.app_filter_is_whitelist,
        v2.ParentalControlsChanged.app_filter,
        v2.ParentalControlsChanged.oars_filter,
        v2.ParentalControlsChanged.allow_user_installation,
        v2.ParentalControlsChanged.allow_system_installation,
        v2.ParentalControlsChanged.is_administrator,
        v2.ParentalControlsChanged.is_initial_setup,
        v2.Machine.image_id,
        v2.Machine.location.label('site'),
        v2.Machine.dualboot.label('dual_boot'),
        v2.Machine.live
    ).select_from(
        v2.ParentalControlsChanged
    ).outerjoin(
        v2.Request
    ).outerjoin(
        v2.Machine, v2.Request.machine_id == v2.Machine.machine_id
    ).outerjoin(
        v2.OSVersion
    ).filter(
        v2.Machine.demo.is_(False)
    ).distinct(
        v2.ParentalControlsChanged.id
    )


class ParentalControlsEnabledViewV2(View):
    __tablename__ = 'parental_controls_enabled_view_v2'
    __materialized__ = True

    __query__ = DbSession().query(
        v2.ParentalControlsEnabled.occured_at,
        v2.OSVersion.version.label('os_version'),
        v2.ParentalControlsEnabled.enabled,
        v2.Machine.image_id,
        v2.Machine.location.label('site'),
        v2.Machine.dualboot.label('dual_boot'),
        v2.Machine.live
    ).select_from(
        v2.ParentalControlsEnabled
    ).outerjoin(
        v2.Request
    ).outerjoin(
        v2.Machine, v2.Request.machine_id == v2.Machine.machine_id
    ).outerjoin(
        v2.OSVersion
    ).filter(
        v2.Machine.demo.is_(False)
    ).distinct(
        v2.ParentalControlsEnabled.id
    )


class ProgramDumpedCoreViewV2(View):
    __tablename__ = 'program_dumped_core_view_v2'
    __materialized__ = True

    __query__ = DbSession().query(
        v2.ProgramDumpedCore.occured_at,
        v2.OSVersion.version.label('os_version'),
        v2.ProgramDumpedCore.info,
        v2.Machine.image_id,
        v2.Machine.location.label('site'),
        v2.Machine.dualboot.label('dual_boot'),
        v2.Machine.live
    ).select_from(
        v2.ProgramDumpedCore
    ).outerjoin(
        v2.Request
    ).outerjoin(
        v2.Machine, v2.Request.machine_id == v2.Machine.machine_id
    ).outerjoin(
        v2.OSVersion
    ).filter(
        v2.Machine.demo.is_(False)
    ).distinct(
        v2.ProgramDumpedCore.id
    )


class UpdaterFailureViewV2(View):
    __tablename__ = 'updater_failure_view_v2'
    __materialized__ = True

    __query__ = DbSession().query(
        v2.UpdaterFailure.occured_at,
        v2.OSVersion.version.label('os_version'),
        v2.UpdaterFailure.component,
        v2.UpdaterFailure.error_message,
        v2.Machine.image_id,
        v2.Machine.location.label('site'),
        v2.Machine.dualboot.label('dual_boot'),
        v2.Machine.live
    ).select_from(
        v2.UpdaterFailure
    ).outerjoin(
        v2.Request
    ).outerjoin(
        v2.Machine, v2.Request.machine_id == v2.Machine.machine_id
    ).outerjoin(
        v2.OSVersion
    ).filter(
        v2.Machine.demo.is_(False)
    ).distinct(
        v2.UpdaterFailure.id
    )


class WindowsAppOpenedViewV2(View):
    __tablename__ = 'windows_app_opened_view_v2'
    __materialized__ = True

    __query__ = DbSession().query(
        v2.WindowsAppOpened.occured_at,
        v2.OSVersion.version.label('os_version'),
        v2.WindowsAppOpened.argv,
        v2.Machine.image_id,
        v2.Machine.location.label('site'),
        v2.Machine.dualboot.label('dual_boot'),
        v2.Machine.live
    ).select_from(
        v2.WindowsAppOpened
    ).outerjoin(
        v2.Request
    ).outerjoin(
        v2.Machine, v2.Request.machine_id == v2.Machine.machine_id
    ).outerjoin(
        v2.OSVersion
    ).filter(
        v2.Machine.demo.is_(False)
    ).distinct(
        v2.WindowsAppOpened.id
    )


class StartupFinishedViewV2(View):
    __tablename__ = 'startup_finished_view_v2'
    __materialized__ = True

    __query__ = DbSession().query(
        v2.StartupFinished.occured_at,
        v2.OSVersion.version.label('os_version'),
        v2.StartupFinished.firmware,
        v2.StartupFinished.loader,
        v2.StartupFinished.kernel,
        v2.StartupFinished.initrd,
        v2.StartupFinished.userspace,
        v2.StartupFinished.total,
        v2.Machine.image_id,
        v2.Machine.location.label('site'),
        v2.Machine.dualboot.label('dual_boot'),
        v2.Machine.live
    ).select_from(
        v2.StartupFinished
    ).outerjoin(
        v2.Request
    ).outerjoin(
        v2.Machine, v2.Request.machine_id == v2.Machine.machine_id
    ).outerjoin(
        v2.OSVersion
    ).filter(
        v2.Machine.demo.is_(False)
    ).distinct(
        v2.StartupFinished.id
    )


class LaunchedEquivalentExistingFlatpakView(View):
    __tablename__ = 'launched_equivalent_existing_flatpak_view'

    __query__ = DbSession().query(
        v3.LaunchedEquivalentExistingFlatpak.occured_at,
        v3.LaunchedEquivalentExistingFlatpak.os_version,
        v3.LaunchedEquivalentExistingFlatpak.replacement_app_id,
        v3.LaunchedEquivalentExistingFlatpak.argv,
        Channel.image_id,
        Channel.site,
        Channel.dual_boot,
        Channel.live
    ).select_from(
        v3.LaunchedEquivalentExistingFlatpak
    ).join(
        Channel
    ).union_all(
        DbSession().query(
            LaunchedEquivalentExistingFlatpakViewV2.occured_at,
            LaunchedEquivalentExistingFlatpakViewV2.os_version,
            LaunchedEquivalentExistingFlatpakViewV2.replacement_app_id,
            LaunchedEquivalentExistingFlatpakViewV2.argv,
            LaunchedEquivalentExistingFlatpakViewV2.image_id,
            LaunchedEquivalentExistingFlatpakViewV2.site,
            LaunchedEquivalentExistingFlatpakViewV2.dual_boot,
            LaunchedEquivalentExistingFlatpakViewV2.live
        )
    )


class LaunchedEquivalentInstallerForFlatpakView(View):
    __tablename__ = 'launched_equivalent_installer_for_flatpak_view'

    __query__ = DbSession().query(
        v3.LaunchedEquivalentInstallerForFlatpak.occured_at,
        v3.LaunchedEquivalentInstallerForFlatpak.os_version,
        v3.LaunchedEquivalentInstallerForFlatpak.replacement_app_id,
        v3.LaunchedEquivalentInstallerForFlatpak.argv,
        Channel.image_id,
        Channel.site,
        Channel.dual_boot,
        Channel.live
    ).select_from(
        v3.LaunchedEquivalentInstallerForFlatpak
    ).join(
        Channel
    ).union_all(
        DbSession().query(
            LaunchedEquivalentInstallerForFlatpakViewV2.occured_at,
            LaunchedEquivalentInstallerForFlatpakViewV2.os_version,
            LaunchedEquivalentInstallerForFlatpakViewV2.replacement_app_id,
            LaunchedEquivalentInstallerForFlatpakViewV2.argv,
            LaunchedEquivalentInstallerForFlatpakViewV2.image_id,
            LaunchedEquivalentInstallerForFlatpakViewV2.site,
            LaunchedEquivalentInstallerForFlatpakViewV2.dual_boot,
            LaunchedEquivalentInstallerForFlatpakViewV2.live
        )
    )


class LaunchedExistingFlatpakView(View):
    __tablename__ = 'launched_existing_flatpak_view'

    __query__ = DbSession().query(
        v3.LaunchedExistingFlatpak.occured_at,
        v3.LaunchedExistingFlatpak.os_version,
        v3.LaunchedExistingFlatpak.replacement_app_id,
        v3.LaunchedExistingFlatpak.argv,
        Channel.image_id,
        Channel.site,
        Channel.dual_boot,
        Channel.live
    ).select_from(
        v3.LaunchedExistingFlatpak
    ).join(
        Channel
    ).union_all(
        DbSession().query(
            LaunchedExistingFlatpakViewV2.occured_at,
            LaunchedExistingFlatpakViewV2.os_version,
            LaunchedExistingFlatpakViewV2.replacement_app_id,
            LaunchedExistingFlatpakViewV2.argv,
            LaunchedExistingFlatpakViewV2.image_id,
            LaunchedExistingFlatpakViewV2.site,
            LaunchedExistingFlatpakViewV2.dual_boot,
            LaunchedExistingFlatpakViewV2.live
        )
    )


class LaunchedInstallerForFlatpakView(View):
    __tablename__ = 'launched_installer_for_flatpak_view'

    __query__ = DbSession().query(
        v3.LaunchedInstallerForFlatpak.occured_at,
        v3.LaunchedInstallerForFlatpak.os_version,
        v3.LaunchedInstallerForFlatpak.replacement_app_id,
        v3.LaunchedInstallerForFlatpak.argv,
        Channel.image_id,
        Channel.site,
        Channel.dual_boot,
        Channel.live
    ).select_from(
        v3.LaunchedInstallerForFlatpak
    ).join(
        Channel
    ).union_all(
        DbSession().query(
            LaunchedInstallerForFlatpakViewV2.occured_at,
            LaunchedInstallerForFlatpakViewV2.os_version,
            LaunchedInstallerForFlatpakViewV2.replacement_app_id,
            LaunchedInstallerForFlatpakViewV2.argv,
            LaunchedInstallerForFlatpakViewV2.image_id,
            LaunchedInstallerForFlatpakViewV2.site,
            LaunchedInstallerForFlatpakViewV2.dual_boot,
            LaunchedInstallerForFlatpakViewV2.live
        )
    )


class LinuxPackageOpenedView(View):
    __tablename__ = 'linux_package_opened_view'

    __query__ = DbSession().query(
        v3.LinuxPackageOpened.occured_at,
        v3.LinuxPackageOpened.os_version,
        v3.LinuxPackageOpened.argv,
        Channel.image_id,
        Channel.site,
        Channel.dual_boot,
        Channel.live
    ).select_from(
        v3.LinuxPackageOpened
    ).join(
        Channel
    ).union_all(
        DbSession().query(
            LinuxPackageOpenedViewV2.occured_at,
            LinuxPackageOpenedViewV2.os_version,
            LinuxPackageOpenedViewV2.argv,
            LinuxPackageOpenedViewV2.image_id,
            LinuxPackageOpenedViewV2.site,
            LinuxPackageOpenedViewV2.dual_boot,
            LinuxPackageOpenedViewV2.live
        )
    )


class ParentalControlsBlockedFlatpakInstallView(View):
    __tablename__ = 'parental_controls_blocked_flatpak_install_view'

    __query__ = DbSession().query(
        v3.ParentalControlsBlockedFlatpakInstall.occured_at,
        v3.ParentalControlsBlockedFlatpakInstall.os_version,
        v3.ParentalControlsBlockedFlatpakInstall.app,
        Channel.image_id,
        Channel.site,
        Channel.dual_boot,
        Channel.live
    ).select_from(
        v3.ParentalControlsBlockedFlatpakInstall
    ).join(
        Channel
    ).union_all(
        DbSession().query(
            ParentalControlsBlockedFlatpakInstallViewV2.occured_at,
            ParentalControlsBlockedFlatpakInstallViewV2.os_version,
            ParentalControlsBlockedFlatpakInstallViewV2.app,
            ParentalControlsBlockedFlatpakInstallViewV2.image_id,
            ParentalControlsBlockedFlatpakInstallViewV2.site,
            ParentalControlsBlockedFlatpakInstallViewV2.dual_boot,
            ParentalControlsBlockedFlatpakInstallViewV2.live
        )
    )


class ParentalControlsBlockedFlatpakRunView(View):
    __tablename__ = 'parental_controls_blocked_flatpak_run_view'

    __query__ = DbSession().query(
        v3.ParentalControlsBlockedFlatpakRun.occured_at,
        v3.ParentalControlsBlockedFlatpakRun.os_version,
        v3.ParentalControlsBlockedFlatpakRun.app,
        Channel.image_id,
        Channel.site,
        Channel.dual_boot,
        Channel.live
    ).select_from(
        v3.ParentalControlsBlockedFlatpakRun
    ).join(
        Channel
    ).union_all(
        DbSession().query(
            ParentalControlsBlockedFlatpakRunViewV2.occured_at,
            ParentalControlsBlockedFlatpakRunViewV2.os_version,
            ParentalControlsBlockedFlatpakRunViewV2.app,
            ParentalControlsBlockedFlatpakRunViewV2.image_id,
            ParentalControlsBlockedFlatpakRunViewV2.site,
            ParentalControlsBlockedFlatpakRunViewV2.dual_boot,
            ParentalControlsBlockedFlatpakRunViewV2.live
        )
    )


class ParentalControlsChangedView(View):
    __tablename__ = 'parental_controls_changed_view'

    __query__ = DbSession().query(
        v3.ParentalControlsChanged.occured_at,
        v3.ParentalControlsChanged.os_version,
        v3.ParentalControlsChanged.app_filter_is_whitelist,
        v3.ParentalControlsChanged.app_filter,
        v3.ParentalControlsChanged.oars_filter,
        v3.ParentalControlsChanged.allow_user_installation,
        v3.ParentalControlsChanged.allow_system_installation,
        v3.ParentalControlsChanged.is_administrator,
        v3.ParentalControlsChanged.is_initial_setup,
        Channel.image_id,
        Channel.site,
        Channel.dual_boot,
        Channel.live
    ).select_from(
        v3.ParentalControlsChanged
    ).join(
        Channel
    ).union_all(
        DbSession().query(
            ParentalControlsChangedViewV2.occured_at,
            ParentalControlsChangedViewV2.os_version,
            ParentalControlsChangedViewV2.app_filter_is_whitelist,
            ParentalControlsChangedViewV2.app_filter,
            ParentalControlsChangedViewV2.oars_filter,
            ParentalControlsChangedViewV2.allow_user_installation,
            ParentalControlsChangedViewV2.allow_system_installation,
            ParentalControlsChangedViewV2.is_administrator,
            ParentalControlsChangedViewV2.is_initial_setup,
            ParentalControlsChangedViewV2.image_id,
            ParentalControlsChangedViewV2.site,
            ParentalControlsChangedViewV2.dual_boot,
            ParentalControlsChangedViewV2.live
        )
    )


class ParentalControlsEnabledView(View):
    __tablename__ = 'parental_controls_enabled_view'

    __query__ = DbSession().query(
        v3.ParentalControlsEnabled.occured_at,
        v3.ParentalControlsEnabled.os_version,
        v3.ParentalControlsEnabled.enabled,
        Channel.image_id,
        Channel.site,
        Channel.dual_boot,
        Channel.live
    ).select_from(
        v3.ParentalControlsEnabled
    ).join(
        Channel
    ).union_all(
        DbSession().query(
            ParentalControlsEnabledViewV2.occured_at,
            ParentalControlsEnabledViewV2.os_version,
            ParentalControlsEnabledViewV2.enabled,
            ParentalControlsEnabledViewV2.image_id,
            ParentalControlsEnabledViewV2.site,
            ParentalControlsEnabledViewV2.dual_boot,
            ParentalControlsEnabledViewV2.live
        )
    )


class ProgramDumpedCoreView(View):
    __tablename__ = 'program_dumped_core_view'

    __query__ = DbSession().query(
        v3.ProgramDumpedCore.occured_at,
        v3.ProgramDumpedCore.os_version,
        v3.ProgramDumpedCore.info,
        Channel.image_id,
        Channel.site,
        Channel.dual_boot,
        Channel.live
    ).select_from(
        v3.ProgramDumpedCore
    ).join(
        Channel
    ).union_all(
        DbSession().query(
            ProgramDumpedCoreViewV2.occured_at,
            ProgramDumpedCoreViewV2.os_version,
            ProgramDumpedCoreViewV2.info,
            ProgramDumpedCoreViewV2.image_id,
            ProgramDumpedCoreViewV2.site,
            ProgramDumpedCoreViewV2.dual_boot,
            ProgramDumpedCoreViewV2.live
        )
    )


class UpdaterFailureView(View):
    __tablename__ = 'updater_failure_view'

    __query__ = DbSession().query(
        v3.UpdaterFailure.occured_at,
        v3.UpdaterFailure.os_version,
        v3.UpdaterFailure.component,
        v3.UpdaterFailure.error_message,
        Channel.image_id,
        Channel.site,
        Channel.dual_boot,
        Channel.live
    ).select_from(
        v3.UpdaterFailure
    ).join(
        Channel
    ).union_all(
        DbSession().query(
            UpdaterFailureViewV2.occured_at,
            UpdaterFailureViewV2.os_version,
            UpdaterFailureViewV2.component,
            UpdaterFailureViewV2.error_message,
            UpdaterFailureViewV2.image_id,
            UpdaterFailureViewV2.site,
            UpdaterFailureViewV2.dual_boot,
            UpdaterFailureViewV2.live
        )
    )


class WindowsAppOpenedView(View):
    __tablename__ = 'windows_app_opened_view'

    __query__ = DbSession().query(
        v3.WindowsAppOpened.occured_at,
        v3.WindowsAppOpened.os_version,
        v3.WindowsAppOpened.argv,
        Channel.image_id,
        Channel.site,
        Channel.dual_boot,
        Channel.live
    ).select_from(
        v3.WindowsAppOpened
    ).join(
        Channel
    ).union_all(
        DbSession().query(
            WindowsAppOpenedViewV2.occured_at,
            WindowsAppOpenedViewV2.os_version,
            WindowsAppOpenedViewV2.argv,
            WindowsAppOpenedViewV2.image_id,
            WindowsAppOpenedViewV2.site,
            WindowsAppOpenedViewV2.dual_boot,
            WindowsAppOpenedViewV2.live
        )
    )


class StartupFinishedView(View):
    __tablename__ = 'startup_finished_view'

    __query__ = DbSession().query(
        v3.StartupFinished.occured_at,
        v3.StartupFinished.os_version,
        v3.StartupFinished.firmware,
        v3.StartupFinished.loader,
        v3.StartupFinished.kernel,
        v3.StartupFinished.initrd,
        v3.StartupFinished.userspace,
        v3.StartupFinished.total,
        Channel.image_id,
        Channel.site,
        Channel.dual_boot,
        Channel.live
    ).select_from(
        v3.StartupFinished
    ).join(
        Channel
    ).union_all(
        DbSession().query(
            StartupFinishedViewV2.occured_at,
            StartupFinishedViewV2.os_version,
            StartupFinishedViewV2.firmware,
            StartupFinishedViewV2.loader,
            StartupFinishedViewV2.kernel,
            StartupFinishedViewV2.initrd,
            StartupFinishedViewV2.userspace,
            StartupFinishedViewV2.total,
            StartupFinishedViewV2.image_id,
            StartupFinishedViewV2.site,
            StartupFinishedViewV2.dual_boot,
            StartupFinishedViewV2.live
        )
    )
