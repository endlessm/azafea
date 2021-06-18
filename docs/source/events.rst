.. _events page:

Events
======

This page is a list of events that Endless OS currently records for users that
have not opted out of metrics recording, as well as events recorded by previous
versions of Endless OS which are not recorded by current versions.


Stored Events
-------------

.. automodule:: azafea.event_processors.endless.metrics.v2.model
   :members:


Unknown Events
--------------

Desktop Searches
~~~~~~~~~~~~~~~~

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

We record when the social bar is made visible to the user and when it is no
longer visible. Basically, it corresponds to the user clicking on the social
bar icon.

- UUID from 2.10: ``EMTR_EVENT_SOCIAL_BAR_IS_VISIBLE`` − ``9c33a734-7ed8-4348-9e39-3c27f4dc2e62`` - eos-social
- Payload of start event: ``NULL``
- Payload of stop event: ``NULL``


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
