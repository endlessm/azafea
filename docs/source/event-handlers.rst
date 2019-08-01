======================
Writing event handlers
======================

For each :ref:`configured queue <queue-config>`, Azafea needs an event handler
to which it passes the pulled events.

An event handler is a Python module located somewhere Azafea can import it,
which means it must be in Python's ``sys.path``.

An event handler needs at the very least a ``process()`` function at the top
level of the module, defined as follows:

.. code-block:: python

   def process(dbsession: Session, record: bytes) -> None:
       ...

Azafea will call the function and pass it the following arguments:

.. |session-class| replace:: ``sqlalchemy.orm.session.Session``
.. _session-class: https://docs.sqlalchemy.org/en/13/orm/session_api.html#sqlalchemy.orm.session.Session

``dbsession``
  An instance of the |session-class|_ class.

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
