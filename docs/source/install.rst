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

We'll create a Docker volume to store the data:::

    # sudo docker volume create postgresql

We can now run PostgreSQL, telling it to use that volume::

    $ sudo docker run --env=POSTGRES_USER=azafea \
                      --env=POSTGRES_PASSWORD=S3cretPgAdminP@ssw0rd \
                      --env=POSTGRES_DB=azafea \
                      --publish=5432:5432 \
                      --volume=postgresql:/var/lib/postgresql:rw \
                      postgres:latest

Azafea
------

The easiest deployment method is also to use Docker. The image is published on
`Docker Hub`_ and can be downloaded by running ``sudo docker pull
docker.io/endlessm/azafea``.

.. _Docker Hub: https://hub.docker.com/r/endlessm/azafea

If you prefer, you can first get the sources and build the Docker image
locally::

    $ git clone https://github.com/endlessm/azafea
    $ cd azafea
    $ sudo docker build --tag azafea .

At this point you need to configure Azafea. In particular, you will at
the very least want to:

* change the Redis and PostgreSQL hosts, to point them to the IP addresses of
  their respective containers;
* change the Redis and PostgreSQL passwords;
* add at least one queue configuration.

The container will automatically generate a :doc:`configuration file
<configuration>` from environment variables. The supported environment
variables are:

* ``VERBOSE``: Sets the ``main.verbose`` value. (Default: ``false``)
* ``NUM_OF_WORKERS``: Sets the ``main.number_of_workers`` value.
* ``REDIS_HOST``: Sets the ``redis.host`` value. (Default: ``localhost``)
* ``REDIS_PASSWORD``: Sets the ``redis.password`` value. (Default: ``CHANGE
  ME!!``)
* ``POSTGRES_HOST``: Sets the ``postgresql.host`` value. (Default:
  ``localhost``)
* ``POSTGRES_PASSWORD``: Sets the ``postgresql.password`` value. (Default:
  ``CHANGE ME!!``)
* ``POSTGRES_SSL_MODE``: Sets the ``postgresql.connect_args.sslmode`` value.
  (Default: ``allow``)

Alternatively, you can :doc:`write a local configuration file <configuration>`
before running Azafea. This requires running the Docker container differently
as described below.

Running
=======

.. note::
    The commands below all assume that you're using the Docker Hub image with
    environment variable configuration. If you're using a built image, adapt
    the ``docker.io/endlessm/azafea`` argument to use the tag you passed in
    ``--tag``. See the end of this section if you want to use a local
    configuration file.

Once you built the Docker image and wrote your configuration file, you can
ensure that Azafea loads your configuration correctly with the following
command::

    $ sudo docker run --env=REDIS_HOST=localhost \
                      --env=REDIS_PASSWORD=S3cretRedisP@ssw0rd \
                      --env=POSTGRES_HOST=localhost \
                      --env=POSTGRES_PASSWORD=S3cretPgAdminP@ssw0rd \
                      docker.io/endlessm/azafea \
                      print-config

If everything is the way you want it, it is time to initialize the database,
creating all the tables::

    $ sudo docker run --env=REDIS_HOST=localhost \
                      --env=REDIS_PASSWORD=S3cretRedisP@ssw0rd \
                      --env=POSTGRES_HOST=localhost \
                      --env=POSTGRES_PASSWORD=S3cretPgAdminP@ssw0rd \
                      docker.io/endlessm/azafea \
                      migratedb

Finally, you can run Azafea::

    $ sudo docker run --env=REDIS_HOST=localhost \
                      --env=REDIS_PASSWORD=S3cretRedisP@ssw0rd \
                      --env=POSTGRES_HOST=localhost \
                      --env=POSTGRES_PASSWORD=S3cretPgAdminP@ssw0rd \
                      docker.io/endlessm/azafea \
                      run

If you're using a local configuration file, 2 changes are needed. First, rather
than passing ``--env`` to ``docker run``, the file needs to be mounted into the
container using the ``--volume`` option. For example,
``--volume=/path/to/config.toml:/config.toml:ro`` would mount the configuration
file at ``/path/to/config.toml`` to ``/config.toml`` within the container and
makes it read-only.

Second, Azafea needs to be told about the location of the configuration within
the container. This needs to be passed as the first argument in the container
command using the ``-c`` option. For example, ``-c /config.toml print-config``.

Upgrading the Database
======================

New versions of Azafea and/or queue handlers will sometimes modify the
database model.

To reflect the code changes into PostgreSQL, you should run the following
command every time you update::

    $ sudo docker run --env=REDIS_HOST=localhost \
                      --env=REDIS_PASSWORD=S3cretRedisP@ssw0rd \
                      --env=POSTGRES_HOST=localhost \
                      --env=POSTGRES_PASSWORD=S3cretPgAdminP@ssw0rd \
                      docker.io/endlessm/azafea \
                      migratedb
