Timestamp Algorithm
===================

This chapter is not intended to be formal documentation but rather a primer to
understanding how the timestamp algorithm for the metrics system works. As
such, some simplifications are made at the expense of accuracy.

Analogies
---------

Analogy to help understand the problem of determining correct event timestamps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A tourist just arrived in San Francisco and wanted to visit the beautiful
sights and tourist spots in the city. Unfortunately, instead of bringing his
watch, he accidentally brought his stopwatch. Not to be deterred, right before
he started touring the city, he started his stopwatch.

Along the way, the man sees many beautiful sights, including a fireworks
display, an awesome office on the 3rd floor of 512 2nd Street, and sunset at
the Golden Gate Bridge. He records all of these events in his journal, writing
down the event and the time on his stopwatch.

Eventually, he gets tired and decides to catch a bus ride North all the way to
Seattle. He hops on the bus by the San Francisco Ferry Building, and right
before the bus leaves, he stops his stopwatch and checks the time on the clock
tower on the building. Right as he writes down the current date and time, and
the time on his stopwatch, the bus leaves.

Long after the bus has departed, he starts talking with the passenger sitting
next to him. The passenger informs the tourist that the clock tower is
sometimes inaccurate.

Not wishing to repeat his mistake of trusting a fallible clock tower, the
tourist consults an atomic clock upon arriving in Seattle. He then realizes
that he forgot to time the trip from San Francisco to Seattle, but he sighs in
relief when he remembers that his train ticket lists the estimated duration.

He checks into a hotel and starts going through his journal. He tries to
convert the stopwatch times of each San Francisco event to the time the event
happened. What can he do to make the times he calculates as accurate as
possible?

Analogy to help visualize the problem of calculating correct timestamps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All of the relative timestamps of events are correct relative to each other.
However, the problem is placing the groups of events on the right scale.

Imagine moving a sliding weight on a scale. The problem is finding the right
position of the weight on the scale where the scale is balanced. The weight is
analogous to a group of events with relative timestamps. The scale is analogous
to a timeline. The problem is finding the right position on the timeline where
the events occurred.

Client Side
-----------

Suppose we want to find out what time an event occurred.

Naive Attempt
~~~~~~~~~~~~~

- Definition: **Absolute Timestamp** - Time elapsed since the Unix Epoch in
  1970 -- at least according to the system clock.

Well, this should be simple, right? We will just use an **absolute timestamp**,
package it with the event, and pat ourselves on the back! Let's see what
happens in this case::

  User boots up system at Noon (Day X).
  User plays Akintu for 1 hour. It is now 1:00 PM (Day X).
  User sets the system clock forward one day, tricking the metrics system. It is now 1:00 PM (Day X + 1).
  Any events recorded now will appear to have occurred in the future.
  (The previous Akintu event would still be correct as it was recorded before the clock change)

This problem also exists without setting the system clock to a bogus time. If
the user's computer is offline for a long time, his or her system clock will
slowly drift away from true time. This could end up being minutes off in
extreme cases of no connectivity. We cannot trust the **absolute timestamps**
alone.

- Definition: **Relative Timestamp** - Time elapsed since the OS booted up.

We cannot use purely **relative timestamps** either, as that wouldn't be able
to track the time while the computer is powered off. Rather we'll need a
combination of the two as well as something we call the **boot offset**.

- Definition: **Boot Offset** - The value to add to any relative timestamp
  within the current boot to correct (or "true up") to an accurate time.

Smart Algorithm
~~~~~~~~~~~~~~~

(This algorithm is based on the `Kurt Truth Premise <https://www.youtube.com/watch?v=dQw4w9WgXcQ>`_.)

So we need some way to track the time that isn't vulnerable to user-changes to
the system clock or clock drift, but doesn't neglect to track time spent
offline. Turns out we need a **boot offset** to tell us how much to adjust our
events' timestamps by. This will make use of both a **relative time** and an
**absolute time** combined with some logging to persistent storage on shutdown
and computation on start up.

We will use the following quantities:

- Boot Offset (What we ultimately add to correct the events' relative timestamps.)
- Stored Boot Offset (The previously written boot offset.)
- Current Relative Time (How long the OS has been running for today. When computed at startup, will be about 0.)
- Stored Relative Time (How long the OS was running for the previous boot.)
- Current Absolute Time (What time the system clock says it is *right now*.)
- Stored Absolute Time (What time the system clock said it was during our last shutdown.)

In the following formula::

  Boot Offset = Stored Boot Offset + (Stored Relative Time - Current Relative Time) + (Current Absolute Time - Stored Absolute Time)

Let us give it a shot::

  User starts up at noon (Day X).
    -- Absolute Time = noon (Day X) Define this quantity as 0 for easier math!
    -- Relative Time = 0
    -- Boot Offset = 0 (When no boot offset exists, it is set to 0.)
  User learns about Racket until 1:00 PM (Day X).
  User powers off machine.
    -- Relative Time STORED --> 1
    -- Absolute Time STORED --> 1
  User powers on machine at 2:00 PM (Day X).
    -- Absolute Time = 2
    -- Stored Absolute Time = 1
    -- Relative Time = 0
    -- Stored Relative Time = 1
    -- Stored Boot Offset = 0
    -- New Boot Offset = 0 + (1 - 0) + (2 - 1) = 2
  User hooks up dance pads and plays Stepmania until 3:00 PM (Day X).
  User sets system clock back one day. It is now 3:00 PM (Day X - 1) according to the absolute clock.
  User reads up on the "Time Cube" until 4:00 PM (Day X in reality, Day X - 1 according to the absolute clock).
  User powers off machine.
    -- Relative Time STORED --> 2
    -- Absolute Time STORED --> -20
  User powers on machine at 5:00 PM (Day X, Day X - 1 according to the absolute clock).
    -- Absolute Time = -19
    -- Stored Absolute Time = -20
    -- Relative Time = 0
    -- Stored Relative Time = 2
    -- Stored Boot Offset = 2
    -- New Boot Offset = 2 + (2 - 0) + (-19 - -20) = 5

As you can see, the boot offsets are correctly determining the number of hours
since the true first boot. There are some subtleties that are being ignored
such as why we bother with the "current" relative time at all, but the intent
is to illustrate the motivation for and essentials of the algorithm.

Server Side
-----------

The metrics system packages bundles of events/metrics together into a **network
request** and sends it off to the server(s) when a connection is detected. This
network request has a couple of timestamps of its own.

- Definition: **Network Request Relative Timestamp** - Time elapsed between the
  "origin" boot and when the network request was created. Was also corrected
  via the client algorithm.
- Definition: **Network Request Absolute Timestamp** - The system clock's
  estimation of when the network request was created (in terms of the Unix
  Epoch, as before.)
- Definition: **Metric Corrected Relative Timestamp** - The result of our
  client-side algorithm to generate the time a metric occurred, relative to the
  "origin" boot.

When the server receives a network request, it will first examine the **network
request absolute time** to see if it varies significantly from its own
(trusted) clock. If it does, some special action will be taken with that
request, such as putting it in its own special table or attempting to correct
the timestamp in some fashion.

What we want is the **metric corrected absolute timestamp**.

- Definition: **Metric Corrected Absolute Timestamp** - The result of our
  server-side algorithm to generate the actual real-world time a metric
  occurred.
- Definition: **Origin Boot Absolute Time** - The time at which the "first"
  boot occurred on a system. In a perfect world, this is always the first boot
  of the system ever.

Assuming it passes this sanity check, the server then unpacks the network
request and examines each **metric corrected relative timestamp**. The server
does the following::

  … Assuming we've passed the sanity check …
  Origin Boot Absolute Time = Network Request Absolute Time - Network Request Relative Time
  For each metric in request:
      Metric Corrected Absolute Timestamp = Origin Boot Absolute Time + Metric Corrected Relative Timestamp
