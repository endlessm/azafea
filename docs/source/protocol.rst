Network Protocol
================

The metrics system has a particular wire format that it must adhere to (that
is, a format for the network request containing a bundle of metrics.) It should
be kept up to date with `emer-daemon.c
<https://github.com/endlessm/eos-event-recorder-daemon/blob/master/daemon/emer-daemon.c>`_.
If this document is inconsistent with the code, please make sure the document
is updated accordingly.

.. note::

    Any changes that modify the network protocol must increment the network
    protocol version number in the same commit.


Wire Format
-----------

Global Structure
~~~~~~~~~~~~~~~~

The format is entirely little-endian. In order, its elements are:

Network Send Number
+++++++++++++++++++

- 32-bit signed integer
- GVariant symbol: ``i``
- Begins at 0 on each client and goes up by 1 each time we attempt a metrics network upload.
- Does not go up on network retries.

Relative Timestamp
++++++++++++++++++

- 64 bit signed integer
- GVariant symbol: ``x``
- See: http://linux.die.net/man/3/clock_gettime

Absolute Timestamp
++++++++++++++++++

- 64 bit signed integer
- GVariant symbol: ``x``
- Nanoseconds since the Unix epoch
- See: http://linux.die.net/man/3/clock_gettime

Machine ID
++++++++++

- Array of 16 unsigned bytes
- GVariant symbol: ``ay``
- Should uniquely identify a user's machine.
- See: http://man7.org/linux/man-pages/man5/machine-id.5.html

Singular Metrics
++++++++++++++++

- Array of singular metrics.
- See `Singular Metric`_
- GVariant symbol: ``a(uayxmv)``

Aggregate Metrics
+++++++++++++++++

- Array of aggregate metrics
- See `Aggregate Metric`_
- GVariant symbol: ``a(uayxxmv)``

Sequence Metrics
++++++++++++++++

- Array of sequence metrics
- See `Sequence Metric`_
- GVariant symbol: ``a(uaya(xmv))``

Total GVariant Format String
++++++++++++++++++++++++++++

All together it should look like: ``(ixxaya(uayxmv)a(uayxxmv)a(uaya(xmv)))``.

Singular Metric
~~~~~~~~~~~~~~~

Singular metrics indicate simple events that occur and don't need to be
aggregated (like an aggregate metric) or linked together across time (like a
sequence metric) to make sense.

In order:

User ID
+++++++

- Unsigned 32-bit integer
- GVariant symbol: ``u``
- See: http://man7.org/linux/man-pages/man2/getuid.2.html

Event ID
++++++++

- Array of 16 unsigned bytes
- GVariant symbol: ``ay``
- Listed in :ref:`events page`
- See: http://linux.die.net/man/3/uuid

Relative Timestamp
++++++++++++++++++

- 64-bit signed integer
- GVariant symbol: ``x``
- See: http://linux.die.net/man/3/clock_gettime

Auxiliary Payload
+++++++++++++++++

- Maybe Variant
- Allows for no contents ``(NULL)`` or content of any type.
- Used to contain data associated with an event that is logged.
- GVariant symbol: ``mv``
- See: https://developer.gnome.org/glib/stable/gvariant-format-strings.html#gvariant-format-strings-maybe-types
- Details for each event ID listed in :ref:`events page`

Total format
++++++++++++

In total should look like ``(uayxmv)``.

Aggregate Metric
~~~~~~~~~~~~~~~~

Aggregate metrics indicate counts that summarize a value of interest (e.g., a
very common event happening n times in a particular time interval or
fluctuations in heap size over time). Counts can be positive, zero, or
negative. They are identical to the singular metrics but have an added counter
field in the wire format.

Aggregates can be used to record noisy events such as cache hit ratios, heap
usage, or any number items that would be impractical to send a `singular
metric`_ for each instance.

In order:

User ID
+++++++

- Unsigned 32-bit integer
- GVariant symbol: ``u``
- See: http://man7.org/linux/man-pages/man2/getuid.2.html

Event ID
++++++++

- Array of 16 unsigned bytes
- GVariant symbol: ``ay``
- Listed in :ref:`events page`
- See: http://linux.die.net/man/3/uuid

Count
+++++

- 64-bit signed integer
- GVariant symbol: ``x``

Relative Timestamp
++++++++++++++++++

- 64-bit signed integer
- GVariant symbol: ``x``
- See: http://linux.die.net/man/3/clock_gettime

Auxiliary Payload
+++++++++++++++++

- Maybe Variant
- Allows for no contents ``(NULL)`` or content of any type.
- Used to contain data associated with an event that is logged.
- GVariant symbol: ``mv``
- See: https://developer.gnome.org/glib/stable/gvariant-format-strings.html#gvariant-format-strings-maybe-types
- Details for each event ID listed in :ref:`events page`

Total format
++++++++++++

In total should look like ``(uayxxmv)``.

Oddities
++++++++

Aggregates currently have no starting time, only a stopping time. Will be fixed
by `T8261: Metrics Client: Aggregates record start time <https://phabricator.endlessm.com/T8261>`_

Sequence Metric
~~~~~~~~~~~~~~~

Sequence metrics are a type of metric that has elements spread across time,
sequentially (hence the name!) All sequence metrics have a **start** event,
zero or more **progress** event, and terminate with a **stop** event.

Sequences Metrics' events are chronologically ordered. It should not be
possible for events in an event sequence to arrive out-of-order
chronologically.

In order:

User ID
+++++++

- Unsigned 32-bit integer
- GVariant symbol ``u``
- See: http://man7.org/linux/man-pages/man2/getuid.2.html

Event ID
++++++++

- Array of 16 unsigned bytes
- GVariant symbol ``ay``
- Listed in :ref:`events page`
- See: http://linux.die.net/man/3/uuid

Events
++++++

- Array of relative timestamps and auxiliary payloads.
- First element in array is a start event.
- Last element in array is a stop event.
- Any elements in between are progress events.
- GVariant symbol ``a(xmv)``

Relative Timestamp
++++++++++++++++++

- 64-bit signed integer
- GVariant symbol ``x``
- See: http://linux.die.net/man/3/clock_gettime

Auxiliary Payload
+++++++++++++++++

- Maybe Variant
- Allows for no contents (NULL) or content of any type.
- Used to contain data associated with an event that is logged.
- GVariant symbol ``mv``
- See: https://developer.gnome.org/glib/stable/gvariant-format-strings.html#gvariant-format-strings-maybe-types
- Details for each event ID listed in :ref:`events page`

Total format
++++++++++++

In total, the format should look like ``(uaya(xmv))``.

Oddities
++++++++

- Event sequences only make sense within the lifetime of a given event
  recorder. If the event recorder dies and is restarted during the same boot,
  sequence events in progress will be lost.
- Event sequences do not persist across boots unless completed. Thus, Sequence
  Metrics should be started and stopped before shutdown.

Version History
---------------

Version 0
~~~~~~~~~

- Initial Release
- URI Format: ``https://production.metrics.endlessm.com/0/<SHA-512-Hash>``
- No compression
- Little Endian
- GVariant Payload Format: ``(xxaya(uayxmv)a(uayxxmv)a(uaya(xmv)))``

Contents:

- Relative Timestamp
- Absolute Timestamp
- Machine ID (**unusable id**)
- Singular Events (User ID, Event ID, Relative Timestamp, Auxiliary Payload)
- Aggregate Events (User ID, Event ID, Count, Relative Timestamp, Auxiliary Payload)
- Sequence Events (User ID, Event ID, Array of (Relative Timestamp, Auxiliary Payload))

Version 1
~~~~~~~~~

- Endless 2.1.2
- URI Format: ``https://production.metrics.endlessm.com/1/<SHA-512-Hash>``
- No compression
- Little Endian
- GVariant Payload Format: ``(xxaya(uayxmv)a(uayxxmv)a(uaya(xmv)))``
- Now uses valid Machine ID

Contents:

- Relative Timestamp
- Absolute Timestamp
- Machine ID fixed
- Singular Events (User ID, Event ID, Relative Timestamp, Auxiliary Payload)
- Aggregate Events (User ID, Event ID, Count, Relative Timestamp, Auxiliary Payload)
- Sequence Events (User ID, Event ID, Array of (Relative Timestamp, Auxiliary Payload))

Version 2
~~~~~~~~~

- Endless 2.1.5 (current protocol version)
- URI Format: ``https://production.metrics.endlessm.com/2/<SHA-512-Hash>``
- No compression
- Little Endian
- GVariant Payload Format: ``(ixxaya(uayxmv)a(uayxxmv)a(uaya(xmv)))``
- Added "network send number" as a signed 32-bit integer to help glean information regarding the number of metric bundles that fail to make it to the databases.

Contents:

- Network Send Number
- Relative Timestamp
- Absolute Timestamp
- Machine ID
- Singular Events (User ID, Event ID, Relative Timestamp, Auxiliary Payload)
- Aggregate Events (User ID, Event ID, Count, Relative Timestamp, Auxiliary Payload)
- Sequence Events (User ID, Event ID, Array of (Relative Timestamp, Auxiliary Payload))
