==========
Deployment
==========


.. _pre-requisites:

Pre-requisites
==============

Azafea pulls events from `Redis <https://redis.io>`_ and stores them in
`PostgreSQL <https://www.postgresql.org>`_. As a result, those two servers need
to be installed and accessible.

Each can be installed in multiple ways depending on your operating system. A
simple installation method is to use `Docker <https://www.docker.com>`_, which
we will detail below.

.. note::
    Some operating systems provide `Podman <https://podman.io>`_ instead of
    Docker. For the purpose of this guide, both should be entirely equivalent.
    If you use Podman, simply replace ``sudo docker`` by ``podman`` (no sudo
    required) in all the commands below.

Redis
-----

Installing and running Redis with Docker should be as simple as::

    $ sudo docker pull redis:latest
    $ sudo docker run --publish=6379:6379 redis:latest

If you want Redis to require a password, or for any other local configuration,
you can create the ``/etc/redis/redis.conf`` file with something like the
following:

.. code-block:: none

   requirepass S3cretRedisP@ssw0rd

Then instead of the command above, run Redis as follows::

    $ sudo docker run --publish=6379:6379 \
                      --volume=/etc/redis/redis.conf:/etc/redis/redis.conf:ro \
                      redis:latest redis-server /etc/redis/redis.conf

PostgreSQL
----------

Azafea requires PostgreSQL 11 or later. Installing it with Docker is simply::

    $ sudo docker pull postgres:latest

Before running PostgreSQL, you need to choose a directory in which to store the
database files.

In this example we will use ``/var/lib/pgsql/azafea/data``, so let's create
it::

    $ sudo mkdir -p /var/lib/pgsql/azafea/data

We can now run PostgreSQL, telling it to use that directory::

    $ sudo docker run --env=PGDATA=/var/lib/postgresql/azafea/data/pgdata \
                      --env=POSTGRES_PASSWORD=S3cretPgAdminP@ssw0rd \
                      --publish=5432:5432 \
                      --volume=/var/lib/postgresql/azafea/data:/var/lib/postgresql/azafea/data:rw \
                      postgres:latest

.. note::
    PostgreSQL creates a ``postgres`` super user which can administrate the
    whole database. Its password is given in the ``POSTGRES_PASSWORD``
    environment variable above.

With PostgreSQL running, we can now create the user and database for Azafea
(enter a password when prompted) ::

    $ sudo docker run --env=PGDATA=/var/lib/postgresql/azafea/data/pgdata \
                      --env=POSTGRES_PASSWORD=S3cretPgAdminP@ssw0rd \
                      --volume=/var/lib/postgresql/azafea/data:/var/lib/postgresql/azafea/data:rw \
                      --interactive --tty --rm \
                      postgres:latest bash
    [docker]# su - postgres
    [docker]$ createuser -h [container-ip] --pwprompt azafea
    [docker]$ createdb -h [container-ip] --owner=azafea azafea


Azafea
------

The easiest deployment method is also to use Docker.

You need to first get the sources and build the Docker image::

    $ git clone https://github.com/endlessm/azafea
    $ cd azafea
    $ sudo docker build --tag azafea .

At this point you will probably want to
:doc:`write a local configuration file <configuration>` before running Azafea.

In particular, you will at the very least want to:

* change the Redis and PostgreSQL hosts, to point them to the IP addresses of
  their respective containers;
* change the Redis and PostgreSQL passwords;
* add at least one queue configuration.

We recommend saving the configuration file as ``/etc/azafea/config.toml`` on
the production host.


Running
=======

.. note::
    The commands  below all assume that your config file is at
    ``/etc/azafea/config.toml``. If you saved it elsewhere, you will need to
    adapt the ``--volume`` argument.

Once you built the Docker image and wrote your configuration file, you can
ensure that Azafea loads your configuration correctly with the following
command::

    $ sudo docker run --volume=/etc/azafea:/etc/azafea:ro azafea print-config

If everything is the way you want it, it is time to initialize the database,
creating all the tables::

    $ sudo docker run --volume=/etc/azafea:/etc/azafea:ro azafea initdb

Finally, you can run Azafea::

    $ sudo docker run --volume=/etc/azafea:/etc/azafea:ro azafea run
