=====================
Writing Queue Plugins
=====================

Event handlers
==============

For each :ref:`configured queue <queue-config>`, Azafea needs an event handler
to which it passes the pulled events.

An event handler is a Python module located somewhere Azafea can import it,
which means it must be in Python's ``sys.path``.

An event handler needs at the very least a ``process()`` function at the top
level of the module, defined as follows:

.. code-block:: python

   def process(dbsession: DbSession, record: bytes) -> None:
       ...

Azafea will call the function and pass it the following arguments:

.. |session-class| replace:: ``sqlalchemy.orm.session.Session``
.. _session-class: https://docs.sqlalchemy.org/en/13/orm/session_api.html#sqlalchemy.orm.session.Session

``dbsession``
  An instance of the ``azafea.model.DbSession`` class, itself a subclass of the
  |session-class|_ class.

  The session is connected to the PostgreSQL database, and the handler can
  simply ``add()`` model instances, and they will be automatically inserted
  into the right table.

``record``
  This contains the bytes representing the event as pulled from the Redis queue
  associated with this event handler.

  The handler is free to do whatever it wants with this, but will typically
  deserialize the record, process the result and then instanciate a custom
  model to store the event in PostgreSQL.

Here is an example of a complete event handler module, which should just work
if you copy-paste it:

.. code-block:: python

   import json
   import logging

   from sqlalchemy.orm.session import Session
   from sqlalchemy.schema import Column
   from sqlalchemy.types import DateTime, Integer, Unicode

   from azafea.model import Base


   log = logging.getLogger(__name__)


   class MyEvent(Base):
       __tablename__ = 'my_event'

       id = Column(Integer, primary_key=True)
       name = Column(Unicode, nullable=False)
       timestamp = Column(DateTime(timezone=True), nullable=False)


   def process(dbsession: Session, record: bytes) -> None:
       # Deserialize the record; for example it could be JSON
       record = json.loads(record.decode('utf-8'))

       # Create the event, and add it to the transaction; it will be automatically
       # committed by Azafea if no error is raised
       event = MyEvent(**record)
       dbsession.add(event)

       # Models can be pretty-printed, to make debugging easier
       log.debug('Inserting event record:\n%s', event)


Let's unpack the example a bit. First come the imports, and then:

.. code-block:: python

   log = logging.getLogger(__name__)

This will allow logging things in your handler, to help you debug-print things,
or just to log informative stuff or problems which could occur.

.. code-block:: python

   class MyEvent(Base):

This declares a model class. Making it inherit from ``azafea.model.Base`` is
how the model is registered into SQLAlchemy, so its table can be created and
so Azafea can be able to insert the created records into the database.

.. code-block:: python

   class MyEvent(Base):
       __tablename__ = 'my_event'

       id = Column(Integer, primary_key=True)
       name = Column(Unicode, nullable=False)
       timestamp = Column(DateTime(timezone=True), nullable=False)

This defines the model and its associated table in the database, with its 3
columns, eventual constraints and indices on them, etc. Refer to
`the SQLAlchemy ORM documentation on mappings <https://docs.sqlalchemy.org/en/13/orm/tutorial.html#declare-a-mapping>`_
for more details on defining models.

.. code-block:: python

   def process(dbsession: Session, record: bytes) -> None:
       # Deserialize the record; for example it could be JSON
       record = json.loads(record.decode('utf-8'))

       # Create the event, and add it to the transaction; it will be automatically
       # committed by Azafea if no error is raised
       event = MyEvent(**record)
       dbsession.add(event)

       # Models can be pretty-printed, to make debugging easier
       log.debug('Inserting event record:\n%s', event)

This is the entry-point function for the handler, it is what Azafea will look
for in the module and what it will run. Azafea will call it passing it those
exact arguments.

The ``Session`` can be used to query the database, or to insert instances of
your custom model. Refer to
`the SQLAlchemy ORM documentation on sessions <https://docs.sqlalchemy.org/en/13/orm/tutorial.html#adding-and-updating-objects>`_
for more details on how to use the ``Session``.

Do note that except in some very specific cases, you should never have to
explicitly ``commit()`` or ``rollback()`` the transaction, Azafea will take
care of this automatically for you once your method returns and if no error
is raised.

The ``record`` is simply the byte string which was pulled from Redis. It can be
anything as far as Azafea is concerned: you know what your system put in Redis,
you know how to process it in your handler.

The example above assumes it is a valid UTF-8-encoded JSON string which can be
directly used to construct the model instance. Your actual event handler can do
any amount of processing here.


Custom subcommands
==================

In addition to an event handler, each :ref:`configured queue <queue-config>`
may optionally register its own subcommands, to be launched through the main
`azafea` CLI.

Any configured ``handler`` can include a ``register_commands()`` function at
the top level of the module, defined as follows:

.. code-block:: python

   def register_commands(subs: argparse._SubParsersAction) -> None:
       ...

Azafea will call the function and pass it the following argument:

.. |subparser-class| replace:: ``argparse._SubParsersAction``
.. _subparser-class: https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.add_subparsers

``subs``
  An instance of the |subparser-class|_ class.

Here is an example of a complete CLI registration module, which should just work
if you copy-paste it:

.. code-block:: python

    import argparse

    from azafea.config import Config


    def register_commands(subs: argparse._SubParsersAction) -> None:
        something = subs.add_parser('do-something',
                                    help='This will do something specific to the queue')
        something.set_defaults(subcommand=do_something)

        something_else = subs.add_parser('do-something-else',
                                         help='This will do something else specific to the queue')
        something_else.add_argument('-f', '--force', help='Forcefully do it')
        something_else.set_defaults(subcommand=do_something_else)


    def do_something(config: Config, args: argparse.Namespace) -> None:
        print("We're doing something!")


    def do_something_else(config: Config, args: argparse.Namespace) -> None:
        if not args.force:
            print("We're doing something else!")
        else:
            print("WE'RE DOING SOMETHING ELSE!!!")

The above registers the ``do-something`` and ``do-something-else`` subcommands,
the latter with an optional ``--force`` argument and its ``-f`` shorthand.

Let's say the configuration for the queue is:

.. code-block:: toml

    [queues.some-queue]
    handler = "another.python.module.processor"

Then the ``do-something`` subcommand becomes accessible to the user::

    $ azafea -c path/to/config.toml some-queue -h
    usage: azafea some-queue [-h] {do-something,do-something-else} ...

    optional arguments:
      -h, --help            show this help message and exit

    subcommands:
      {do-something,do-something-else}
        do-something        This will do something specific to the queue
        do-something-else   This will do something else specific to the queue
    $ azafea -c config.toml some-queue do-something
    We're doing something!
    $ azafea -c config.toml some-queue do-something-else --force
    WE'RE DOING SOMETHING ELSE!!!

As can be seen above, the custom subcommands specific to the ``some-queue``
queue are available to the CLI under a ``some-queue`` command, not directly at
the root of the ``azafea`` command.

.. |argparse| replace:: ``argparse``
.. _argparse: https://docs.python.org/3/library/argparse.html

You can use any facility provided by Python's |argparse|_ module when
registering your subcommands.


Database Migrations
===================

If your queue plugin has its own model, you will eventually want to update it.

Azafea provides a handy command to automatically generate migration scripts
based on the difference between your model and the state of the database::

    $ azafea make-migration some-queue

This uses `Alembic <https://alembic.sqlalchemy.org/>`_ under the hood, which will
usually detect model changes correctly, but
`not everything <https://alembic.sqlalchemy.org/en/latest/autogenerate.html#what-does-autogenerate-detect-and-what-does-it-not-detect>`_,
so you might need to manually adapt some migration scripts eventually.

Note that your queue plugin will need a ``migrations/`` directory inside the
handler module.
