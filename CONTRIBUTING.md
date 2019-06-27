# Contributing

Thank you for considering contributing to this project.

Following these guidelines helps to communicate that you respect the time of
the developers managing and developing this project.

In return, we will reciprocate that respect in addressing your issues,
assessing changes, and helping you finalize your contributions in a timely
manner.


## Filing Issues

Whenever you experience a problem with this software, please let us know so we
can make it better.

But first, take the time to search through the list of [existing issues] to see
whether it is already known.

Be sure to provide all the information you can, as that will really help us
fixing your issue as quickly as possible.

[existing issues]: https://github.com/endlessm/azafea/issues


## Pre-requisites

The tools required to work on Azafea are the following:

*   Python >= 3.7, with Pip
*   [pipenv](https://docs.pipenv.org/)

Pipenv is not strictly mandatory to contribute to Azafea, you can use any way
you prefer to manage the dependencies. We do recommend using it though, as it
makes it very easy to manage a virtual environment dedicated to Azafea. The
rest of this documentation will assume you use Pipenv.


## Getting the Sources

You can simply clone the Git repository:

```
$ git clone https://github.com/endlessm/azafea
```

At this point you will want to install the runtime and development
dependencies:

```
$ pipenv install --dev
```

Now try running the unit tests:

```
$ pipenv run test
```


## Coding Standards

In order to keep the code readable and avoid common mistakes, we use
[flake8](https://pypi.org/project/flake8/) a common linter in the Python
community.

We also use type checking with [mypy](http://www.mypy-lang.org/), which
prevents a lot of problems inherent to dynamically typed languages like Python.

Both are run automatically with the tests:

```
$ pipenv run test
```


## Writing Unit Tests

Unit tests are simply files in the `azafea/tests/` directory. They must be
named `test_*.py`, and we use [Pytest](https://pytest.org/) to help us write
them.

Feel free to mock liberally as you need it with the
[`monkeypatch`](https://docs.pytest.org/en/latest/monkeypatch.html) fixture.
Unit tests should generally not require additional dependencies from what
Azafea itself requires. They should specifically not require:

* access to an external service like Redis or PostgreSQL;
* any kind of network access.

You can run them with the following command:

```
$ pipenv run test
```


## Writing Integration Tests

Integration tests are a bit more involved and require more set up before they
can run. They have the same requirements as
[running Azafea in production](docs/source/install.rst) so see that
documentation to install things like PostgreSQL and Redis.

A key difference from the production deployment is the PostgreSQL database
which must be named `azafea-tests`. The PostgreSQL user must be named
`azafea`, and Redis and PostgreSQL are both expecting to connect with the
default password, `CHANGE ME!!`.

So with PostgreSQL running, create the test database as follows (enter a
password when prompted) :

```
$ sudo docker run --env=PGDATA=/var/lib/postgresql/azafea/data/pgdata \
                  --env=POSTGRES_PASSWORD=S3cretPgAdminP@ssw0rd \
                  --volume=/var/lib/postgresql/azafea/data:/var/lib/postgresql/azafea/data:rw \
                  --interactive --tty --rm \
                  postgres:latest bash
[docker]# su - postgres
[docker]$ createuser -h [container-ip] --pwprompt azafea
[docker]$ createdb -h [container-ip] --owner=azafea azafea-tests
```

Once you have everything set up, you can run all the tests, unit and
integration, with a single command:

```
$ pipenv run test-all
```

Integration tests consist of directories under `azafea/tests/integration/`.
There should be at least one file named `test_*.py` in each of them, as that is
how Pytest finds the tests to run.

Such test files should contain a class inheriting from
`azafea.tests.integration.IntegrationTest` which handles a lot of the setup and
teardown necessary for the tests, like getting a configuration file, a
connection to the dabase, or running Azafea.

You can add additional setup in the directory like event handler modules or
data files, to help writing your tests.

Look at existing integration tests for examples.


## Running a Local Instance

Running a local instance has the same requirement as running Azafea in
production or running the integration tests (see above). If you managed to have
all the integration tests passing, then the local instance should run properly.

We recommend you run Azafea with a different database from the one used by the
integration tests (`azafea-tests`). You could simply call it `azafea`, as that
is the name in the default configuration.

One additional thing you will need to do is
[write a configuration file](docs/source/configuration.rst). In particular, you
will at the very least want to:

* change the Redis and PostgreSQL hosts, to point them to the IP addresses of
  their respective containers;
* change the Redis and PostgreSQL user and passwords;
* add at least one queue configuration.

Once you're ready, you can ensure that Azafea loads your configuration
correctly with the following command:

```
$ pipenv run azafea -c config.toml print-config
```

If everything is the way you want it, it is time to initialize the database,
creating all the tables:

```
$ pipenv run azafea -c config.toml initdb
```

Finally, you can run Azafea itself:

```
$ pipenv run azafea -c config.toml run
```


## Building the Documentation

The documentation pages are maintained with
[Sphinx](https://www.sphinx-doc.org/) and written in
[reStructuredText](http://docutils.sourceforge.net/rst.html).

If you modify them, you can test your changes by building them:

```
$ pipenv run doc
```

The built HTML files will be in `docs/build/html/`, so you can just open
`docs/build/html/index.html` in your favourite web browser.


## Submitting Changes

If you want to implement a new feature, make sure you first open an issue to
discuss it and ensure the feature is desired.

We accept changes through the usual merge request process.

We want Azafea to be well tested, with as good a test coverage as possible. If
you add a new feature, add tests to cover it. If you fix a bug, add a test
reproducing the problem first, then verify your change fixes it, so we can be
more confident the problem never comes back.

If you're unsure about anything just ask, either in your merge request or in an
issue.


### Commit History

Try to keep your branch split into atomic commits.

For example, if you made a first commit to implement a change, then a second
one to fix a problem in the first commit, squash them together.

If you need help doing that, please mention it in your merge request and we
will guide you towards using Git to achieve a nice and clean branch history.


### Commit Messages

Commit messages are extremely important. They tell the story of the project,
how it arrived to where it is now, why we took the decisions that made it the
way it is.

Chris Beams wrote [a wonderful post](https://chris.beams.io/posts/git-commit/)
that we highly recommend you read. The highlight of the post are 7 rules we ask
you to try and follow:

1.  Separate subject from body with a blank line
2.  Limit the subject line to 50 characters
3.  Capitalize the subject line
4.  Do not end the subject line with a period
5.  Use the imperative mood in the subject line
6.  Wrap the body at 72 characters
7.  Use the body to explain what and why vs. how

We further want to add our own rules:

*   if the commit is related to an issue, please mention the id of that issue
    in the commit message; for example, use something like `Fixes #123`.
