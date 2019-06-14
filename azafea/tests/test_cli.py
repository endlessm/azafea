import azafea.cli


def test_print_config(capfd, make_config_file):
    config_file = make_config_file({
        'main': {'number_of_workers': 1},
        'redis': {'host': 'redis-server'},
        'postgresql': {'user': 'Léo'},
    })

    args = azafea.cli.parse_args([
        '-c', str(config_file),
        '--print-config',
    ])

    # FIXME: This is a silly temporary test, it will make more sense soon
    from azafea.config import Config
    if args.print_config:
        print(Config.from_file(str(config_file)))

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
