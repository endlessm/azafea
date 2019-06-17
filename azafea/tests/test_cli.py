import azafea.cli
import azafea.config


def test_initdb(capfd, monkeypatch, make_config_file):
    class MockDb:
        def __init__(self, *args):
            pass

        def create_all(self):
            print('Creating the tables…')

    def mock_get_handler(module):
        def process(*args, **kwargs):
            pass

        return process

    config_file = make_config_file({'queues': {'some-queue': {'handler': 'azafea.tests.test_cli'}}})

    args = azafea.cli.parse_args([
        '-c', str(config_file),
        'initdb',
    ])

    with monkeypatch.context() as m:
        m.setattr(azafea.config, 'get_handler', mock_get_handler)
        m.setattr(azafea.cli, 'Db', MockDb)
        result = args.subcommand(args)

    assert result == azafea.cli.ExitCode.OK

    capture = capfd.readouterr()
    assert 'Creating the tables…' in capture.out


def test_initdb_invalid_config(capfd, make_config_file):
    # Make a wrong config file
    config_file = make_config_file({'main': {'verbose': 'blah'}})

    args = azafea.cli.parse_args([
        '-c', str(config_file),
        'initdb',
    ])

    result = args.subcommand(args)

    assert result == azafea.cli.ExitCode.INVALID_CONFIG

    capture = capfd.readouterr()
    assert "Invalid [main] configuration:\n* verbose: 'blah' is not a boolean" in capture.err


def test_initdb_no_event_queue(capfd, make_config_file):
    config_file = make_config_file({})

    args = azafea.cli.parse_args([
        '-c', str(config_file),
        'initdb',
    ])

    result = args.subcommand(args)

    assert result == azafea.cli.ExitCode.NO_EVENT_QUEUE

    capture = capfd.readouterr()
    assert "Could not initialize the database: no event queue configured" in capture.err


def test_print_config(capfd, monkeypatch, make_config_file):
    def mock_get_handler(module):
        def process(*args, **kwargs):
            pass

        return process

    config_file = make_config_file({
        'main': {'number_of_workers': 1},
        'redis': {'host': 'redis-server'},
        'postgresql': {'user': 'Léo'},
        'queues': {'some-queue': {'handler': 'azafea.tests.test_cli'}},
    })

    args = azafea.cli.parse_args([
        '-c', str(config_file),
        'print-config',
    ])

    with monkeypatch.context() as m:
        m.setattr(azafea.config, 'get_handler', mock_get_handler)
        result = args.subcommand(args)

    assert result == azafea.cli.ExitCode.OK

    capture = capfd.readouterr()
    assert capture.out.strip() == '\n'.join([
        '[main]',
        'verbose = false',
        'number_of_workers = 1',
        '',
        '[redis]',
        'host = "redis-server"',
        'port = 6379',
        '',
        '[postgresql]',
        'host = "localhost"',
        'port = 5432',
        'user = "Léo"',
        'password = "** hidden **"',
        'database = "azafea"',
        '',
        '[queues.some-queue]',
        'handler = "azafea.tests.test_cli"',
    ])


def test_print_invalid_config(capfd, make_config_file):
    # Make a wrong config file
    config_file = make_config_file({'main': {'verbose': 'blah'}})

    args = azafea.cli.parse_args([
        '-c', str(config_file),
        'print-config',
    ])

    result = args.subcommand(args)

    assert result == azafea.cli.ExitCode.INVALID_CONFIG

    capture = capfd.readouterr()
    assert "Invalid [main] configuration:\n* verbose: 'blah' is not a boolean" in capture.err


def test_print_config_no_event_queue(capfd, make_config_file):
    config_file = make_config_file({})

    args = azafea.cli.parse_args([
        '-c', str(config_file),
        'print-config',
    ])

    result = args.subcommand(args)

    assert result == azafea.cli.ExitCode.NO_EVENT_QUEUE

    capture = capfd.readouterr()
    assert "Did you forget to configure event queues?" in capture.err


def test_run(capfd, monkeypatch, make_config_file):
    class MockController:
        def __init__(self, config):
            pass

        def main(self):
            print('Running the mock controller…')

    def mock_get_handler(module):
        def process(*args, **kwargs):
            pass

        return process

    config_file = make_config_file({'queues': {'some-queue': {'handler': 'azafea.tests.test_cli'}}})

    args = azafea.cli.parse_args([
        '-c', str(config_file),
        'run',
    ])

    with monkeypatch.context() as m:
        m.setattr(azafea.config, 'get_handler', mock_get_handler)
        m.setattr(azafea.cli, 'Controller', MockController)
        result = args.subcommand(args)

    assert result == azafea.cli.ExitCode.OK

    capture = capfd.readouterr()
    assert 'Running the mock controller…' in capture.out


def test_run_invalid_config(capfd, make_config_file):
    # Make a wrong config file
    config_file = make_config_file({'main': {'verbose': 'blah'}})

    args = azafea.cli.parse_args([
        '-c', str(config_file),
        'run',
    ])

    result = args.subcommand(args)

    assert result == azafea.cli.ExitCode.INVALID_CONFIG

    capture = capfd.readouterr()
    assert "Invalid [main] configuration:\n* verbose: 'blah' is not a boolean" in capture.err


def test_run_no_event_queue(capfd, make_config_file):
    # Make a wrong config file
    config_file = make_config_file({})

    args = azafea.cli.parse_args([
        '-c', str(config_file),
        'run',
    ])

    result = args.subcommand(args)

    assert result == azafea.cli.ExitCode.NO_EVENT_QUEUE

    capture = capfd.readouterr()
    assert 'Could not start: no event queue configured' in capture.err


def test_run_redis_connection_error(capfd, monkeypatch, make_config_file):
    def mock_get_handler(module):
        def process(*args, **kwargs):
            pass

        return process

    # Hopefully nobody will ever run the tests with a Redis server accessible at this host:port
    config_file = make_config_file({
        'redis': {'host': 'no-such-host', 'port': 1},
        'queues': {'some-queue': {'handler': 'azafea.tests.test_cli'}}
    })

    args = azafea.cli.parse_args([
        '-c', str(config_file),
        'run',
    ])

    with monkeypatch.context() as m:
        m.setattr(azafea.config, 'get_handler', mock_get_handler)
        result = args.subcommand(args)

    assert result == azafea.cli.ExitCode.CONNECTION_ERROR

    capture = capfd.readouterr()
    assert 'Could not connect to Redis:' in capture.err
    assert 'Name or service not known' in capture.err
