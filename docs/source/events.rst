.. _events page:

Events
======

This page is a list of events that Endless OS currently records for users that
have not opted out of metrics recording, as well as events recorded by previous
versions of Endless OS which are not recorded by current versions.


Stored Events
-------------

.. automodule:: azafea.event_processors.endless.metrics.v3.model
   :members:


Deprecated Events
-----------------

System Shutdown
~~~~~~~~~~~~~~~

.. note::

   This event has been deprecated in 3.7.0 and is not sent any more. See the
   uptime event which replaced it. See `T27963
   <https://phabricator.endlessm.com/T27963>`_.

We records shutdowns as well as the total length of time the computer has been
powered on across all boots. Since 2.5.0, we also include the total number of
boots the computer has been through.

- UUID from 2.2.0: ``SHUTDOWN`` − ``ae391c82-1937-4ae5-8539-8d1aceed037d`` − eos-metrics-instrumentation
- UUID from 2.5.0: ``SHUTDOWN_EVENT`` − ``91de63ea-c7b7-412c-93f3-6f3d9b2f864c`` − eos-metrics-instrumentation
- UUID from 2.5.2: ``SHUTDOWN_EVENT`` − ``8f70276e-3f78-45b2-99f8-94db231d42dd`` − eos-metrics-instrumentation

- Payload: type ``(xx)``

  - total uptime across all boots
  - number of boots the computer has been through

.. note::

   A serious bug that often prevented this event from being recorded was fixed
   in the 2.3.0 release. Another serious bug that often prevented this event
   from being recorded was introduced in 2.4.0 and fixed in 2.5.1. A serious
   bug that often prevented the boot count from being incremented was fixed in
   the 2.5.2 release.

Companion App - Device Authenticate
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note:

   The companion app is no more.

Reported when a user authenticates a device with the Companion App Service

- UUID from 3.4: ``6dad6c44-f52f-4bca-8b4c-dc203f175b97`` − eos-companion-app-integration

- Payload: type ``a{ss}``

  - A dictionary of string keys to string values:

    - ``deviceUUID``: hash of unique device identifier

See `T21316 <https://phabricator.endlessm.com/T21316>`_.

Companion App - List Applications
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::

   The companion app is no more.

Reported when a user gets an application listing from the Companion App Service

- UUID from 3.4: ``337fa66d-5163-46ae-ab20-dc605b5d7307`` − eos-companion-app-integration

- Payload: type ``a{ss}``

  - a dictionary of string keys to string values:

    - ``deviceUUID``: hash of unique device identifier
    - ``referrer``: optional, name of view that the user came from, one of:

      - ``feed``: the content feed
      - ``search_content``: search
      - ``list_content_for_tags``: listing of content for a category
      - ``list_applications``: listing of available applications
      - ``list_application_sets``: listing of categories for an application
      - ``device_authenticate``: when a user first associates a device with a computer
      - ``refresh``: when a user pulls down to refresh
      - ``retry``: when the user manually retries after a timeout
      - ``back``: when the user goes back
      - ``content``: following a link from within content

See `T21316 <https://phabricator.endlessm.com/T21316>`_.

Companion App - List Sets for Applications
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::

   The companion app is no more.

Reported when a user gets a listing of application sets from the Companion App
Service.

- UUID from 3.4: ``c02a5764-7f81-48c7-aea4-1413fd4e829c``

- Payload: type ``a{ss}``

  - A dictionary of string keys to string values:

    - ``deviceUUID``: hash of unique device identifier
    - ``applicationId``: application ID
    - ``referrer``: see "Companion App - List applications"

See `T21316 <https://phabricator.endlessm.com/T21316>`_.

Companion App - List Content for Tags of Application
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::

   The companion app is no more.

Reported when a user gets a listing of application content for a set of tags
from the Companion App Service.

- UUID from 3.4: ``bef3d12c-df9b-43cd-a67c-31abc5361f03``

- Payload: type ``a{ss}``

  - A dictionary of string keys to string values:

    - ``deviceUUID``: hash of unique device identifier
    - ``applicationId``: application ID
    - ``tags``: semicolon delimited list of tags
    - ``referrer``: see "Companion App - List applications"

See `T21316 <https://phabricator.endlessm.com/T21316>`_.

Companion App - View Content
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::

   The companion app is no more.

Reported when a user views some requested content EKN-ID on the Companion App.

- UUID from 3.4: ``e6541049-9462-4db5-96df-1977f3051578``

- Payload: type ``a{ss}``

  - A dictionary of string keys to string values:

    - ``deviceUUID``: hash of unique device identifier
    - ``applicationId``: application ID
    - ``contentTitle``: content title
    - ``contentType``: content MIME type
    - ``referrer``: see "Companion App - List applications"

See `T21316 <https://phabricator.endlessm.com/T21316>`_.

Companion App - Get Content Metadata
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::

   The companion app is no more.

Reported when a user gets some metadata about some requested content EKN-ID on
the Companion App.

- UUID from 3.4: ``3a4eff55-5d01-48c8-a827-fca5732fd767``

- Payload: type ``a{ss}``

  - A dictionary of string keys to string values:

    - ``deviceUUID``: hash of unique device identifier
    - ``applicationId``: application ID
    - ``contentId``: EKN ID
    - ``referrer``: see "Companion App - List applications"

See `T21316 <https://phabricator.endlessm.com/T21316>`_.

Companion App - Search for Content or Applications
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::

   The companion app is no more.

Reported when a user uses the search functionality on the app to search for
things.

- UUID from 3.4: ``9f06d0f7-677e-43ca-b732-ccbb40847a31``

- Payload: type ``a{ss}``

  - A dictionary of string keys to string values:

    - ``deviceUUID``: hash of unique device identifier
    - ``applicationId``: application ID
    - ``tags``: semicolon delimited list of tags
    - ``searchTerm``: optional, search term
    - ``referrer``: see "Companion App - List applications"

See `T21316 <https://phabricator.endlessm.com/T21316>`_.

Companion App - Request Content Feed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::

   The companion app is no more.

Reported when the user opens the Companion App and requests the content feed.

- UUID from 3.4: ``af3e89b2-8293-4703-809c-8e0231c128cb``

- Payload: type ``a{ss}``

  - A dictionary of string keys to string values:
    - ``deviceUUID``: hash of unique device identifier
    - ``mode``: 'ascending' or 'descending'
    - ``referrer``: see "Companion App - List applications"

See `T22203 <https://phabricator.endlessm.com/T22203>`_.

Companion App - Download Bundled Application
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::

   The companion app is no more.

- UUID from TBC: ``7be595662b23-408a-acf6-91490fc1df1c``

- Payload: type ``a{ss}``

  - A dictionary of string keys to string values:

    - ``deviceUUID``: hash of unique device identifier
    - ``referrer``: see "Companion App - List applications"

See `T22053 <https://phabricator.endlessm.com/T22053>`_.

Network Status Changed
~~~~~~~~~~~~~~~~~~~~~~

Removed in 3.7.4. See `T28301 <https://phabricator.endlessm.com/T28301>`_.

We record when the network status changes from one state to another. A common
case of this is moving from an "unknown" state to a "connecting" to a "globally
connected" state on startup.

See `the comprehensive list of status codes
<https://developer.gnome.org/NetworkManager/stable/nm-dbus-types.html#NMState>`_.

- UUID from 2.10: ``EMTR_EVENT_NETWORK_STATUS_CHANGED`` − ``5fae6179-e108-4962-83be-c909259c0584`` − eos-metrics

- Payload: type ``(uu)``

  - Previous network state
  - New network state

.. note::

   Since https://github.com/endlessm/eos-shell/issues/2684 was fixed in 2.2.0,
   we no longer misrepresent local and site connectivity as global
   connectivity.

Social Bar Is Visible
~~~~~~~~~~~~~~~~~~~~~

Removed in 3.2.0.

We record when the social bar is made visible to the user and when it is no
longer visible. Basically, it corresponds to the user clicking on the social
bar icon.

- UUID from 2.10: ``EMTR_EVENT_SOCIAL_BAR_IS_VISIBLE`` − ``9c33a734-7ed8-4348-9e39-3c27f4dc2e62`` - eos-social
- Payload of start event: ``NULL``
- Payload of stop event: ``NULL``

Desktop Searches
~~~~~~~~~~~~~~~~

Removed in OS 4.0.0.

We record searches made from the desktop search bar.

- Since: 2.1.2
- UUID: ``b02266bc-b010-44b2-ae0f-8f116ffa50eb``
- UUID name: ``EVENT_DESKTOP_SEARCH`` in gnome-shell
- Payload: type ``(us)``

  - search provider

    - local: 0
    - Google: 1

  - query string (what the user searched for)

.. note::

   Since the 2.1.6. release, Google searches have no longer been recorded.

Knowledge App Search
~~~~~~~~~~~~~~~~~~~~

Not stored since Endless OS 4.0.0.

We record the search terms used for searching within the knowledge apps along
with the app ID of the knowledge app. (We also record the search term used when
a user performed a desktop search and clicked through to a knowledge app.)

- Since: 2.3.0
- UUID: ``a628c936-5d87-434a-a57a-015a0f223838``
- UUID name: ``SEARCH_METRIC_EVENT_ID`` in eos-knowledge-lib
- Payload: type ``(ss)``

  - search terms
  - application ID

Link Shared from Knowledge App
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Not stored since Endless OS 4.0.0.

Reported when a user shares a link from one of our content apps on a social network.

- Since: SDK 2
- UUID: ``6775771a-afe7-4158-b7bb-6296fcc7b70d``
- UUID name: ``SHARE_METRIC_EVENT_ID`` in eos-knowledge-lib
- Payload: type ``(sayssu)``

  - Application ID (e.g. ``com.endlessm.animals.en``)
  - ID of content record as a byte array of length 20
    (``ekn://043fd69fe153ac69a05000b60bfea9cff110f14c`` becomes ``[0x04, 0x3f,
    0xd6, 0x9f, 0xe1, 0x53, 0xac, 0x69, 0xa0, 0x50, 0x00, 0xb6, 0x0b, 0xfe,
    0xa9, 0xcf, 0xf1, 0x10, 0xf1, 0x4c]``)
  - Content title
  - The exact URL of the content online, as it was shared to the social network
  - A numerical code indicating which social network the content was shared to

    - Facebook: 0
    - Twitter: 1
    - Whatsapp: 2

See `T18524 <https://phabricator.endlessm.com/T18524>`_.

Knowledge App – Article Open/Close
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Not stored since Endless OS 4.0.0.

We record when an article is opened or closed in a knowledge app. We record the
ID of the content, the entry point (whether the article was accessed via
article link, desktop search, app link click, or a nav button), the app ID, the
article title, and the content type.

- Since: SDK 2
- UUID: ``fae00ef3-aad7-44ca-aff2-16555e45f0d9``
- UUID name: ``CONTENT_ACCESS_METRIC_EVENT_ID`` in eos-knowledge-lib
- Payload of start event: type ``(ssss)``

  - Entry point
  - Application ID
  - Title
  - Content type

- Payload of stop event: ``NULL``

See `T18516 <https://phabricator.endlessm.com/T18516>`_.

Hack Toolbox - Code View Error - Hack Episode 1
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Not reported since Hack was moved to Flathub in Endless OS 3.9.1.

- Since: 3.5.3
- UUID: ``e98aa2b8-3f11-4a25-b8e9-b10a635df121``
- UUID name: ``CODEVIEW_ERROR_EVENT``
- Payload of start event: type ``sssa(suquq)``

  - Application ID that this toolbox belongs to (string)
  - ID of function that was being edited in the toolbox (string) (currently always blank)
  - Contents of code view (string)
  - List of the error messages that are displayed, each containing:
  - Text of error message (string)
  - Start line number where error is shown, 1-based (32-bit unsigned)
  - Start column number where error is shown, 0-based (16-bit unsigned)
  - End line number where error is shown, 1-based (32-bit unsigned)
  - End column number where error is shown, 0-based (16-bit unsigned)

- Payload of progress and stop events: type ``s``

  - Diff of the contents of the code view to the state from the previous event,
    in the form of an `ed script
    <https://www.gnu.org/software/diffutils/manual/html_node/ed-Scripts.html>`_,
    chosen because it's the shortest form that the ``diff`` utility can output

See `T24429 <https://phabricator.endlessm.com/T24429>`_.

Hack Clubhouse - Quest
~~~~~~~~~~~~~~~~~~~~~~

Not reported since Hack was moved to Flathub in Endless OS 3.9.1.

- Since: 3.7.4
- UUID: ``50aebb1b-7a93-4caf-8698-3a601a0fc0f6``
- UUID name: ``QUEST_EVENT``
- Key: The quest name
- Payload of start event: type ``(bsas)``

  - ``True`` if the quest is completed
  - The quest ID
  - The list of pathway names of this quest

- Payload of stop event: type ``(bsas)``

  - ``True`` if the quest is completed
  - The quest ID
  - The list of pathway names of this quest

See `T28004 <https://phabricator.endlessm.com/T28004>`_.

Uptime
~~~~~~

Removed in 4.0.0.

Total length of time the computer has been powered on and total number of boots.

The difference with the system shutdown event is that this is sent
periodically while the computer is up, not just at shutdown. This allows
catching "dirty" shutdowns and makes it easier to estimate connectivity.

See https://github.com/endlessm/eos-metrics-instrumentation/commit/8dfd1e5b9.

:UUID name: ``UPTIME_EVENT`` in eos-metrics-instrumentation

UUID was ``005096c4-9444-48c6-844b-6cb693c15235`` before 2.5.2.

.. note::

    A serious bug that often prevented the boot count from being
    incremented was fixed in the 2.5.2 release.

.. versionadded:: 2.5.0

Shell App Is Open
~~~~~~~~~~~~~~~~~

Removed in 4.0.0.

An application opens and closes.

By subtracting the time of closing from time of opening, we can tell how
long an application has been open. This basically includes all applications
of interest to non-developers.

:UUID name: ``SHELL_APP_IS_OPEN_EVENT`` in gnome-shell

.. versionadded:: 2.1.0

User Is Logged In
~~~~~~~~~~~~~~~~~

Removed in 4.0.0.

A user logs in and logs out to Endless OS.

As of 2.1.2 we also records which user logged in. This is still anonymous
data, so we only record an arbitrary number (the user ID), but we can
discover (among other things) how many different users use the computer
that way.

:UUID name: ``USER_IS_LOGGED_IN`` in eos-metrics-instrumentation (since 2.1.2)

UUID was called ``EMTR_EVENT_USER_IS_LOGGED_IN``
(``ab839fd2-a927-456c-8c18-f1136722666b``) before 2.1.2.

.. note::

    A serious bug that often prevented this event from being recorded was
    introduced in 2.4.0 and fixed in 2.5.1.

.. versionadded:: 2.1.0

Network ID
~~~~~~~~~~

Removed in 4.0.0.

A change in the default route happens after the network connectivity has changed.

The intention behind the payload is to provide a value which is opaque and
stable which is the same for every system located on the same physical
network (also visible from the ``eos-network-id`` command).

See `T16934 <https://phabricator.endlessm.com/T16934>`_.

:UUID name: ``NETWORK_ID_EVENT`` in eos-metrics-instrumentation

.. versionadded:: 3.1.2

Cache Is Corrupt
~~~~~~~~~~~~~~~~

Removed in 4.0.0.

Cache has been found to be corrupt and was reset.

We've observed that in some situations the metrics recorder daemon's cached
data contains only a few valid items and then corrupt data, and that some
other times the whole thing becomes corrupt and completely unusable,
bringing down the whole metrics recorder daemon and effectively killing
metrics reporting forever for that machine.

As it's still unclear why that happens, we now detect those situations and
correct them when they happen, so that the metrics system can still be used
afterwards.

:UUID name: ``CACHE_IS_CORRUPT_EVENT_ID`` in eos-event-recorder-daemon

.. versionadded:: 3.0.9

Cache Metadata Is Corrupt
~~~~~~~~~~~~~~~~~~~~~~~~~

Removed in 4.0.0.

Cache metadata is corrupt and was reset, any cached metrics were discarded.

We've observed that in some situations the metrics recorder daemon's cached
data contains only a few valid items and then corrupt data, and that some
other times the whole thing becomes corrupt and completely unusable,
bringing down the whole metrics recorder daemon and effectively killing
metrics reporting forever for that machine.

As it's still unclear why that happens, we now detect those situations and
correct them when they happen, so that the metrics system can still be used
afterwards.

See `T19953 <https://phabricator.endlessm.com/T19953>`_.

:UUID name: ``CACHE_METADATA_IS_CORRUPT_EVENT_ID`` in eos-event-recorder-daemon

.. versionadded:: 3.3.5

Cache Has Invalid Elements
~~~~~~~~~~~~~~~~~~~~~~~~~~

Removed in 4.0.0.

Some invalid cache elements were found.

We've observed that in some situations the metrics recorder daemon's cached
data contains only a few valid items and then corrupt data, and that some
other times the whole thing becomes corrupt and completely unusable,
bringing down the whole metrics recorder daemon and effectively killing
metrics reporting forever for that machine.

As it's still unclear why that happens, we now detect those situations and
correct them when they happen, so that the metrics system can still be used
afterwards.

:UUID name: ``CACHE_HAS_INVALID_ELEMENTS_EVENT_ID`` in eos-event-recorder-daemon

.. versionadded:: 3.0.9

Discovery Feed Clicked
~~~~~~~~~~~~~~~~~~~~~~

Not reported since 3.9.0 when the Discovery Feed was removed from Endless OS.

Something is clicked on the Discovery Feed, including content which is not "clickable".

The payload tells us about what users are clicking on generally and whether
they are clicking on things that we don't expect to be clicked. The
intention is to allow the operator to determine what content should be made
clickable and what kinds of content are being opened.

The ``content_type`` field that can be included in the payload is currently
one of:

- ``knowledge_content``: text-based article in a knowledge-app
- ``knowledge_video``: video based article in a knowledge-app
- ``knowledge_artwork``: "artwork" card (larger images in a "Gallery" style format)
- ``undefined``: user clicked on a non-clickable area

:UUID name: ``EVENT_DISCOVERY_FEED_CLICK`` in eos-discovery-feed

.. versionadded:: 3.2.0

Discovery Feed Closed
~~~~~~~~~~~~~~~~~~~~~

Not reported since 3.9.0 when the Discovery Feed was removed from Endless OS.

Something is clicked on the Discovery Feed, including content which is not "clickable".

The payload tells us about what users are clicking on generally and whether
they are clicking on things that we don't expect to be clicked. The
intention is to allow the operator to determine what content should be made
clickable and what kinds of content are being opened.

The ``content_type`` field that can be included in the payload is currently
one of:

- ``knowledge_content``: text-based article in a knowledge-app
- ``knowledge_video``: video based article in a knowledge-app
- ``knowledge_artwork``: "artwork" card (larger images in a "Gallery" style format)
- ``undefined``: user clicked on a non-clickable area

:UUID name: ``EVENT_DISCOVERY_FEED_CLICK`` in eos-discovery-feed

.. versionadded:: 3.2.0

Discovery Feed Opened
~~~~~~~~~~~~~~~~~~~~~

Not reported since 3.9.0 when the Discovery Feed was removed from Endless OS.

The Discovery Feed is open.

The payload tells us about the language the user is using when interacting
with the discovery feed and how they opened it. The intention is to allow
the operator to determine which languages the discovery feed is most
popular in and how users generally open the feed.

:UUID name: ``EVENT_DISCOVERY_FEED_OPEN`` in eos-discovery-feed

.. versionadded:: 3.2.0

Disk Space Extra
~~~~~~~~~~~~~~~~

Removed in 4.0.0, along with split-disk support in general.

Total, used and free disk space for ``/var/endless-extra``.

Sent on startup, and every 24 hours.

See `T18445 <https://phabricator.endlessm.com/T18445>`_.

:UUID name: ``EXTRA_DISK_SPACE_EVENT`` in eos-metrics-instrumentation

.. versionadded:: 3.4.3

Entered Demo Mode
~~~~~~~~~~~~~~~~~

Not reported since demo mode was removed in Endless OS 3.9.0.

The systems enters demo mode.

Note that the machine ID will be reset just before the system enters demo
mode, so any metrics collected for this machine ID after this event has
been fired are metrics for a system that is in demo mode.

Demo mode was removed in EOS 3.9, so this metric will not be seen for
systems on 3.9.0 or later.

See `T18983 <https://phabricator.endlessm.com/T18983>`_.

:UUID name: ``DEMO_MODE_ENTERED_METRIC`` in gnome-initial-setup

.. versionadded:: 3.2.5

Endless Application Unmaximized
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Not stored since Endless OS 4.0.0.

An in-house application is unmaximized for the first time in each run.

We record a metric with the application ID.

:UUID name: ``UNMAXIMIZE_EVENT`` in eos-sdk

.. versionadded:: 3.0.0

Hack Clubhouse Achievement
~~~~~~~~~~~~~~~~~~~~~~~~~~

Not reported since Hack was moved to Flathub in Endless OS 3.9.1.

Achievement reached in the Hack Clubhouse.

See `T28004 <https://phabricator.endlessm.com/T28004>`_.

:UUID name: ``ACHIEVEMENT_EVENT``

.. versionadded:: 3.7.4

Hack Clubhouse Achievement Points
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Not reported since Hack was moved to Flathub in Endless OS 3.9.1.

Points earned in the Hack Clubhouse.

See `T28004 <https://phabricator.endlessm.com/T28004>`_.

:UUID name: ``ACHIEVEMENT_POINTS_EVENT``

.. versionadded:: 3.7.4

Hack Clubhouse Change Page
~~~~~~~~~~~~~~~~~~~~~~~~~~

Not reported since Hack was moved to Flathub in Endless OS 3.9.1.

Page changed in the Hack Clubhouse.

See `T28004 <https://phabricator.endlessm.com/T28004>`_.

:UUID name: ``CLUBHOUSE_SET_PAGE_EVENT``

.. versionadded:: 3.7.4

Hack Clubhouse Enter Pathway
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Not reported since Hack was moved to Flathub in Endless OS 3.9.1.

Pathway entered in the Hack Clubhouse.

See `T28004 <https://phabricator.endlessm.com/T28004>`_.

:UUID name: ``CLUBHOUSE_PATHWAY_ENTER_EVENT``

.. versionadded:: 3.7.4

Hack Clubhouse Mode
~~~~~~~~~~~~~~~~~~~

Not reported since Hack was moved to Flathub in Endless OS 3.9.1.

Hack mode changed in the Hack Clubhouse.

See `T28501 <https://phabricator.endlessm.com/T28501>`_.

:UUID name: ``HACK_MODE_EVENT``

.. versionadded:: 3.7.4

Hack Clubhouse News Quest Link
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Not reported since Hack was moved to Flathub in Endless OS 3.9.1.

Quest link clicked in the Hack Clubhouse news.

See `T29192 <https://phabricator.endlessm.com/T29192>`_.

:UUID name: ``CLUBHOUSE_NEWS_QUEST_LINK_EVENT``

.. versionadded:: 3.7.4

Hack Clubhouse Progress
~~~~~~~~~~~~~~~~~~~~~~~

Not reported since Hack was moved to Flathub in Endless OS 3.9.1.

Progress updated in the Hack Clubhouse.

See `T28004 <https://phabricator.endlessm.com/T28004>`_.

:UUID name: ``PROGRESS_UPDATE_EVENT``

.. versionadded:: 3.7.4

Location
~~~~~~~~

Removed in 4.0.0.

The user’s location at city-level granularity.

An event is sent once per boot and subsequently every time it changes by a
distance of 15 km or more during the same boot. We include latitude,
longitude, altitude if known, and accuracy of the location estimate.

.. note::

    Since around 3.7.0, for privacy reasons this is only recorded on a
    `small set of products <https://github.com/endlessm/\
    eos-metrics-instrumentation/blob/master/src/eins-location.c#L192-L196>`_
    − at the time of writing this is fnde, impact, payg, solutions, and
    spark. See `T27743 <https://phabricator.endlessm.com/T27743>`_ and
    `T27655 <https://phabricator.endlessm.com/T27655>`_ for more details.

:UUID name: ``USER_LOCATION`` in eos-metrics-instrumentation

.. versionadded:: 2.1.5

Missing Codec
~~~~~~~~~~~~~

Removed in 4.0.0.

A GStreamer-based application tries to install a missing codec.

:UUID name: ``EOS_CODECS_MANAGER_MISSING_CODEC`` in eos-codecs-manager

.. versionadded:: 2.6.0

Monitor Connected
~~~~~~~~~~~~~~~~~

Removed in 4.0.0.

A display is connected (e.g. computer monitor, television) to the machine.

We include any information about the display (e.g. with, height).

:UUID name: ``MONITOR_CONNECTED`` in mutter

UUID was ``566adb36-7701-4067-a971-a398312c2874`` before 2.1.7.

.. versionadded:: 2.1.4

Monitor Disconnected
~~~~~~~~~~~~~~~~~~~~

Removed in 4.0.0.

A display is disconnected (e.g. computer monitor, television) from the machine.

We include any information about the display (e.g. with, height).

:UUID name: ``MONITOR_DISCONNECTED`` in mutter

UUID was ``ce179909-dacb-4b7e-83a5-690480bf21eb`` before 2.1.7.

.. versionadded:: 2.1.4

Shell App Added To Desktop
~~~~~~~~~~~~~~~~~~~~~~~~~~

Removed in OS 3.9.0.

Shell application is added to desktop.

:UUID name: ``SHELL_APP_ADDED_EVENT`` in gnome-shell

.. note::

    Since 3.9.0 this metric is no longer recorded.
    See `T30661 <https://phabricator.endlessm.com/T30661>`_.

.. versionadded:: 2.1.0

Shell App Removed From Desktop
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Removed in 3.9.0.

Shell application is removed from desktop.

:UUID name: ``SHELL_APP_REMOVED_EVENT`` in gnome-shell

.. note::

    Since 3.9.0 this metric is no longer recorded.
    See `T30661 <https://phabricator.endlessm.com/T30661>`_.

.. versionadded:: 2.1.0

Underscan Enabled
~~~~~~~~~~~~~~~~~

Removed in 3.9.0.

Underscan is enabled on a monitor.

:UUID name: ``UNDERSCAN_ENABLED`` in mutter

.. versionadded:: 3.8.7

Windows License Tables
~~~~~~~~~~~~~~~~~~~~~~

Removed in 4.0.0.

ACPI tables are present on the system, at startup.

The tables we check for are MSDM and SLIC, which hold OEM Windows license
information on newer and older systems respectively.

We have not seen systems which have both tables, but they might exist in
the wild and would appear with a value of 3. With this information,
assuming Metrics Events is not sent, then we can distinguish:

- SLIC/MSDM > 0 and no dual boot: Endless OS is the sole OS, PC came with Windows
- SLIC/MSDM > 0 and dual boot: Endless OS installed alongside OEM Windows
- SLIC/MSDM = 0 and no dual boot: Endless OS is the sole OS, PC came without Windows
- SLIC/MSDM = 0 and dual boot: Dual-booting with a retail Windows

See `T18296 <https://phabricator.endlessm.com/T18296>`_.

:UUID name: ``WINDOWS_LICENSE_TABLES_EVENT`` in eos-metrics-instrumentation

.. versionadded:: 3.2.0

Updater Branch Selected
~~~~~~~~~~~~~~~~~~~~~~~

Removed in 4.0.0.

An eos-updater branch has been selected.

:UUID name: ``EOS_UPDATER_METRIC_BRANCH_SELECTED`` in eos-updater

.. versionadded:: 2.6.0

Control Center Panel Opened
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Removed in 4.0.0.

A panel is open in the control center.

:UUID name: ``PANEL_OPENED_EVENT_ID`` in gnome-control-center

.. versionadded:: 3.2.5

Control Center Automatic Updates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Removed in 4.0.0.

Automatic updates settings have changed.

:UUID name: ``CC_METRIC_AUTOMATIC_UPDATES`` in gnome-control-center

.. versionadded:: 3.9.1


Test Events
-----------

The following are only ever used in tests, and are thus discarded by the server
upon reception.

We document them here to make sure they don't get reused inadvertently by real
events.

- `Smoke tests <https://github.com/endlessm/eos-metrics/blob/ab66c7319c573999740f636555b14b6f658e82c0/tests/smoke-tests/smokeLibrary.js#L22-L27>`_

  - ``72fea371-15d1-401d-8a40-c47f379f64fd``
  - ``9a0cf836-12cd-4887-95d8-e48ccdf6e552``
  - ``b1f87a3f-a464-48d4-8e35-35dd45659010``
  - ``b2b17dfd-c30e-4789-abcc-4a38323127f6``
  - ``b89f9a4a-3035-4fc3-9bef-584367fe2c96``
  - ``fb59199e-5384-472e-af1e-00b7a419d5c2``

- `Event recorder tests <https://github.com/endlessm/eos-metrics/blob/ab66c7319c573999740f636555b14b6f658e82c0/tests/test-event-recorder.c#L29-L30>`_

  - ``350ac4ff-3026-4c25-9e7e-e8103b4fd5d8``
  - ``d936cd5c-08de-4d4e-8a87-8df1f4a33cba``

- `Daemon tests <https://github.com/endlessm/eos-event-recorder-daemon/blob/efc6bb0e1283236ee4fe9c3d7fc992c4a53436d8/tests/daemon/test-daemon.c#L51>`_

  - ``350ac4ff-3026-4c25-9e7e-e8103b4fd5d8``


Implementing New Events
-----------------------

Preliminary Considerations
~~~~~~~~~~~~~~~~~~~~~~~~~~

Before adding new events, you have to discuss and justify the metric: what
question are you trying to answer, is this the most appropriate metric for
answering that question, and does it preserve users’ privacy? Are we legally
allowed to collect and store it?

The second step is to define the submission (``GVariant``) and storage (SQL)
formats for the new metric, generate a UUID with the uuidgen command, and
document it on this page.

Finally, you can add code in the OS to submit the metrics at relevant points,
as done in `this example <https://github.com/endlessm/malcontent/pull/17>`_. At
its core, this will be a call to ``emtr_event_recorder_get_default()`` and then
a call to ``emtr_event_recorder_record_event()``. You will probably need to
`add a dependency on eos-metrics-0-dev
<https://github.com/endlessm/malcontent/pull/18>`_ to the Debian packaging. The
code to submit new metrics can be shipped before the server is ready to process
them, as unknown metrics are stored and re-parsed when Azafea is updated.

Technical Introduction
~~~~~~~~~~~~~~~~~~~~~~

The metrics event processor implements a few events. When it receives a request
containing events it doesn't know about, they will get stored in the following
tables:

* ``unknown_singular_event`` for singular metrics;
* ``unknown_aggregate_event`` for aggregate metrics.

The records in those table should contain everything needed to replay them once
the corresponding event model has been implemented.

Adding a New Model
~~~~~~~~~~~~~~~~~~

New metrics models should be added in
``azafea/event_processors/endless/metrics/v3/events.py``. Do look at the
existing ones for examples.

All it takes is defining a new class inheriting from the appropriate base event:

* ``SingularEvent``;
* ``AggregateEvent``.

The file is organized in 2 sections, one for each event type. Please keep it
tidy by adding your new model in the correct section. It's also nice to order
models alphabetically within each section.

The class needs at least a few special attributes:

* ``__tablename__`` is the name of the table in PostgreSQL; this will usually
  be the same as the class name, but using snake_case;
* ``__event_uuid__`` is the unique identifier for the event; it is how Azafea
  will know which model to use for any incoming event;
* ``__payload_type__`` is the format string of the GVariant payload; if the
  event has no payload, then use ``None``.

If an event has a payload, then you will want that payload to be deserialized
and stored into columns of the new table.

This is achieved by adding the right ``sqlalchemy.schema.Column``-s to the
model, and implementing the ``_get_fields_from_payload`` method. The latter is
responsible for deserializing the GVariant payload. By the time the method is
called, the payload has already been validated against the
``__payload_type__``.

You can also look at `this example of new models addition
<https://github.com/endlessm/azafea/commit/591e7a27bffe14cf3ef68e255806b5b282db50c2>`_.

Creating the Tables
~~~~~~~~~~~~~~~~~~~

After adding a new model, stop Azafea and create the database migration::

    [azafea-dev]$ pipenv run azafea -c config.toml make-migration queue-name

The queue-name is the configured name of a :ref:`queue <queue-config>` set up
with the handler which contains the new model.

Carefully review the generated migration file, and commit it along with your
new event.

You can test that the migration is functional by running it::

    [azafea-dev]$ pipenv run azafea -c config.toml migratedb

You can also look at `this example of database migration in Azafea
<https://github.com/endlessm/azafea/commit/bb827ae1363efd903510d896bec3f18ab217b079>`_.

Deploying
~~~~~~~~~

Deployment steps depend on the infrastructure you use for Azafea.

For Endless OS, Azafea changes are deployed to the ``dev`` server and tested by
looking at https://metabase.dev.endlessm-sf.com/ while submitting the new
metrics events from an Endless OS system. The EOS system should be configured
with ``environment=dev`` in ``/etc/metrics/eos-metrics-permissions.conf``.

If all looks good, deploy the changes to the Azafea ``production`` server.

Replaying Previously Unknown Events
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If some instances of your new event had been received by Azafea before you
implemented it and Azafea had stored them in the corresponding "unknown" table,
you can run the migration to create the table, then replay them to "make them
known"::

    $ pipenv run azafea -c config.toml migratedb
    $ pipenv run azafea -c config.toml metrics-3 replay-unknown

The above commands need to be run in an environment with access to Azafea
itself. If you deployed Azafea in production using Docker, then you will want
to run them in an instance of that production container.
