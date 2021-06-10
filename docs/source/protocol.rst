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

Image
+++++

- String
- GVariant symbol: ``s``

Site
++++

- String
- GVariant symbol: ``a{ss}``

Dualboot
++++++++

- Boolean
- GVariant symbol: ``b``

Live
++++

- Boolean
- GVariant symbol: ``b``

Singular Metrics
++++++++++++++++

- Array of singular metrics.
- See `Singular Metric`_
- GVariant symbol: ``a(aysxmv)``

Aggregate Metrics
+++++++++++++++++

- Array of aggregate metrics
- See `Aggregate Metric`_
- GVariant symbol: ``a(uayxxmv)``

Total GVariant Format String
++++++++++++++++++++++++++++

All together it should look like: ``(isa{ss}bba(aysxmv)a(aysyxxmv))``.

Singular Metric
~~~~~~~~~~~~~~~

Singular metrics indicate simple events that occur and don't need to be
aggregated (like an aggregate metric) to make sense.

In order:

Event ID
++++++++

- Array of 16 unsigned bytes
- GVariant symbol: ``ay``
- Listed in :ref:`events page`
- See: http://linux.die.net/man/3/uuid

OS Version
++++++++++

- String
- GVariant symbol: ``s``

Timestamp
+++++++++

- 64-bit signed integer
- GVariant symbol: ``x``

Auxiliary Payload
+++++++++++++++++

- Maybe Variant
- Allows for no contents ``(NULL)`` or content of any type.
- Used to contain data associated with an event that is logged.
- GVariant symbol: ``mv``
- See: https://developer.gnome.org/glib/stable/gvariant-format-strings.html#gvariant-format-strings-maybe-types
- Details for each event ID listed in :ref:`events page`

Total Format
++++++++++++

In total should look like ``(aysxmv)``.

Aggregate Metric
~~~~~~~~~~~~~~~~

Aggregate metrics indicate counts that summarize a value of interest (e.g., a
very common event happening n times in a particular time interval or
fluctuations in heap size over time). Counts are always strictly positive. They
are identical to the singular metrics but have an added counter field in the
wire format.

Aggregates can be used to record noisy events such as cache hit ratios, heap
usage, or any number items that would be impractical to send a `singular
metric`_ for each instance.

In order:

Event ID
++++++++

- Array of 16 unsigned bytes
- GVariant symbol: ``ay``
- Listed in :ref:`events page`
- See: http://linux.die.net/man/3/uuid

OS Version
++++++++++

- String
- GVariant symbol: ``s``

Period
++++++

- Unsigned byte
- GVariant symbol: ``y``
- Aggregation period (``h`` for hour, ``d`` for day, ``w`` for week, ``m`` for
  month)

Timestamp
+++++++++

- 64-bit signed integer
- GVariant symbol: ``x``
- Nanoseconds since the Unix epoch
- Beginning of the period, with aggregation done using user’s computer time

Count
+++++

- 64-bit signed integer
- GVariant symbol: ``x``

Auxiliary Payload
+++++++++++++++++

- Maybe Variant
- Allows for no contents ``(NULL)`` or content of any type.
- Used to contain data associated with an event that is logged.
- GVariant symbol: ``mv``
- See: https://developer.gnome.org/glib/stable/gvariant-format-strings.html#gvariant-format-strings-maybe-types
- Details for each event ID listed in :ref:`events page`

Total Format
++++++++++++

In total should look like ``(aysyxxmv)``.

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

- Endless 2.1.5
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

Version 3
~~~~~~~~~

- Endless X.X.X
- URI Format: ``https://production.metrics.endlessm.com/3/<SHA-512-Hash>``
- No compression
- Little Endian
- GVariant Payload Format: ``(xxsa{ss}ya(aysxmv)a(aysyxxmv))``
- Removed "network send number".

Contents:

- Network Send Number
- Relative Timestamp
- Absolute Timestamp
- Channel (image, site, dualboot, live)
- Singular Events (Event ID, OS Version, Relative Timestamp, Absolute
  Timestamp, Auxiliary Payload)
- Aggregate Events (Event ID, OS Version, Period, Relative Timestamp, Count,
  Auxiliary Payload)
