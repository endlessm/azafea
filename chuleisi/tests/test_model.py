import pytest

from chuleisi.config import Config
import chuleisi.model


class MockSqlAlchemySession:
    def __init__(self):
        self.open = True
        self.committed = False
        self.rolled_back = False

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def close(self):
        self.open = False


def mock_sessionmaker(bind=None):
    return MockSqlAlchemySession


def test_use_db_session(monkeypatch):
    config = Config()

    with monkeypatch.context() as m:
        m.setattr(chuleisi.model, 'sessionmaker', mock_sessionmaker)
        db = chuleisi.model.Db(config.postgresql.host, config.postgresql.port,
                               config.postgresql.user, config.postgresql.password,
                               config.postgresql.database)

        with db as dbsession:
            assert dbsession.open
            assert not dbsession.committed
            assert not dbsession.rolled_back

        assert not dbsession.open
        assert dbsession.committed
        assert not dbsession.rolled_back


def test_fail_committing_db_session(monkeypatch):
    config = Config()

    def raise_when_committing():
        raise ValueError('Could not commit')

    with monkeypatch.context() as m:
        m.setattr(chuleisi.model, 'sessionmaker', mock_sessionmaker)
        db = chuleisi.model.Db(config.postgresql.host, config.postgresql.port,
                               config.postgresql.user, config.postgresql.password,
                               config.postgresql.database)

        with pytest.raises(ValueError) as exc_info:
            with db as dbsession:
                dbsession.commit = raise_when_committing

        assert 'Could not commit' in str(exc_info.value)

        assert not dbsession.open
        assert not dbsession.committed
        assert dbsession.rolled_back


def test_fail_in_db_session(monkeypatch):
    config = Config()

    with monkeypatch.context() as m:
        m.setattr(chuleisi.model, 'sessionmaker', mock_sessionmaker)
        db = chuleisi.model.Db(config.postgresql.host, config.postgresql.port,
                               config.postgresql.user, config.postgresql.password,
                               config.postgresql.database)

        with pytest.raises(ValueError) as exc_info:
            with db as dbsession:
                raise ValueError('Oh no!')

        assert 'Oh no!' in str(exc_info.value)

        assert not dbsession.open
        assert not dbsession.committed
        assert dbsession.rolled_back
