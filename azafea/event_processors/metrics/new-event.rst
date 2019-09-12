========================
Implementing New Metrics
========================

The metrics event processor implements a few events. When it receives a request
containing events it doesn't know about,t hey will get stored in the following
tables:

* ``unknown_singular_event`` for singular metrics;
* ``unknown_aggregate_event`` for aggregate metrics;
* ``unknown_sequence`` for sequence metrics;

The records in those table should contain everything needed to replay them once
the corresponding event model has been implemented.


Adding a new model
==================

New metrics models should be added in
``azafea/event_processors/metrics/events/__init__.py``. Do look at the existing
ones for examples.

All it takes is defining a new class inheriting from the appropriate base event:

* ``SingularEvent``;
* ``AggregateEvent``;
* ``SequenceEvent``;

The file is organized in 3 sections, one for each event type. Please keep it
tidy by adding your new model in the correct section. It's also nice to order
models alphabetically within each section.

The class needs at least a few special attributes:

* ``__tablename__`` is the name of the table in PostgreSQL; this will usually
  be the same as the class name, but using snake_case;
* ``__event_uuid__`` is the unique identifier for the event; it is how Azafea
  will know which model to use for any incoming event;
* ``__payload_type__`` is the format string of the GVariant payload; if the
  event has no payload, then use ``None``;

If an event has a payload, then you will want that payload to be deserialized
and stored into columns of the new table.

This is achieved by adding the right ``sqlalchemy.schema.Column``-s to the
model, and implementing the ``_get_fields_from_payload`` method. The latter is
responsible for deserializing the GVariant payload. (by the time the method is
called, the payload has already been validated against the
``__payload_type__``)


Creating the tables
===================

After adding a new model, stop Azafea and create the new tables with Azafea's
``initdb`` command, then restart the application.


Replaying previously unknown events
===================================

TODO: Write a tool to do that.
