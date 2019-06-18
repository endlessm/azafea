import pytest

from sqlalchemy.exc import ProgrammingError

from azafea import cli
from azafea.config import Config
from azafea.model import Db


def test_initdb(make_config_file):
    from .handler_module import Event

    config_file = make_config_file({
        'main': {'verbose': True},
        'postgresql': {'database': 'azafea-tests'},
        'queues': {'event': {'handler': 'azafea.tests.integration.initdb.handler_module'}},
    })
    config = Config.from_file(str(config_file))
    db = Db(config.postgresql.host, config.postgresql.port, config.postgresql.user,
            config.postgresql.password, config.postgresql.database)

    # Ensure there is no table at the start
    with pytest.raises(ProgrammingError) as exc_info:
        with db as dbsession:
            dbsession.query(Event).all()
    assert 'relation "event" does not exist' in str(exc_info.value)

    # Create the table
    args = cli.parse_args([
        '-c', str(config_file),
        'initdb',
    ])
    assert args.subcommand(args) == cli.ExitCode.OK

    # Ensure the table exists
    with db as dbsession:
        dbsession.query(Event).all()

    # Drop all tables to avoid side-effects between tests
    db.drop_all()
