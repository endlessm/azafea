import azafea.cli


def test_initdb(capfd, monkeypatch, make_config_file):
    class MockDb:
        def __init__(self, *args):
            pass

        def create_all(self):
            print('Creating the tables…')

    config_file = make_config_file({})

    args = azafea.cli.parse_args([
        '-c', str(config_file),
        'initdb',
    ])

    with monkeypatch.context() as m:
        m.setattr(azafea.cli, 'Db', MockDb)
        result = args.subcommand(args)

    assert result == azafea.cli.ExitCode.OK

    capture = capfd.readouterr()
    assert 'Creating the tables…' in capture.out


def test_print_config(capfd, make_config_file):
    config_file = make_config_file({
        'main': {'number_of_workers': 1},
        'redis': {'host': 'redis-server'},
        'postgresql': {'user': 'Léo'},
    })

    args = azafea.cli.parse_args([
        '-c', str(config_file),
        'print-config',
    ])
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
        '[queues]',
    ])


def test_run(capfd, monkeypatch, make_config_file):
    class MockController:
        def __init__(self, config):
            pass

        def main(self):
            print('Running the mock controller…')

    config_file = make_config_file({})

    args = azafea.cli.parse_args([
        '-c', str(config_file),
        'run',
    ])

    with monkeypatch.context() as m:
        m.setattr(azafea.cli, 'Controller', MockController)
        result = args.subcommand(args)

    assert result == azafea.cli.ExitCode.OK

    capture = capfd.readouterr()
    assert 'Running the mock controller…' in capture.out
