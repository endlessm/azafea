=============
Configuration
=============

Azafea can run almost without any configuration, using reasonable defaults for
its options, with the exception of the event queues.

However many things can be configured in a
`TOML <https://github.com/toml-lang/toml>`_ configuration file, usually located
at ``/etc/azafea/config.toml``.

You don't need to write a full configuration file. Azafea will let you write
only the sections and options you want to override.

Before detailing every option, here is an example configuration file showing
the default options:

.. code-block:: toml

   [main]
   verbose = true
   number_of_workers = 4

   [redis]
   host = "localhost"
   port = 6379
   password = "CHANGE ME!!"

   [postgresql]
   host = "localhost"
   port = 5432
   user = "azafea"
   password = "CHANGE ME!!"
   database = "azafea"

   [queues]


The ``main`` table
==================

This section controls the general behaviour of Azafea.

``verbose`` (boolean)
  This option controls how verbose Azafea will be. If True, Azafea will log
  everything, including debug messages. Otherwise only informative, warning
  and error messages are logged.

  The default is ``false``

``number_of_workers`` (strictly positive integer)
  The number of worker processes to spawn, in order to process multiple events
  in parallel.

  The default is to spawn as many processes as there are CPU cores on the
  machine.


The ``redis`` table
===================

This section controls how Azafea connects to the Redis server holding the event
queues.

``host`` (string)
  The hostname on which the Redis server is accessible.

  The default is ``"localhost"``.

``port`` (strictly positive integer)
  The port on which the Redis server is listening.

  The default is ``6379``.

``password`` (string)
  The password Redis expects when connecting to it.

  The default is ``"CHANGE ME!!"``.


The ``postgresql`` table
========================

This section controls how Azafea connects to the PostgreSQL server in which it
stores its data.

``host`` (string)
  The hostname on which the PostgreSQL server is accessible.

  The default is ``"localhost"``.

``port`` (strictly positive integer)
  The port on which the PostgreSQL server is listening.

  The default is ``5432``.

``user`` (string)
  The user owning the database in which Azafea will store its processed events.

  The default is ``"azafea"``

``password`` (string)
  The password for the user owning the database in which Azafea will store its
  processed events.

  The default is ``"CHANGE ME!!"``.

``database`` (string)
  The database in which Azafea will store its processed events.

  The default is ``"azafea"``

.. _queue-config:

The ``queues`` table
====================

This section lists the various Redis queues from which Azafea will pull events.

By default no queue is configured, and Azafea will refuse to start unless you
configure at least one.

Here is an example for a queue configuration:

.. code-block:: toml

   [queues.be]
   handler = "a.python.module"

   [queues.te]
   handler = "another.python.module"

Each queue is its own table with its own options:

``handler`` (string)
  The dotted-path of the Python module responsible to process the events pulled
  from this queue. Azafea will try importing that module.

  Make sure you read :doc:`how to write event handler modules <event-handlers>`
  for all the details on what Azafea expects from them.

So in the above example, Azafea will pull events from 2 Redis queues, one named
``"be"`` and one named ``"te"``, and will pass them to the ``a.python.module``
handler for the former and to the ``another.python.module`` for the latter.
