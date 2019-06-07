from typing import Optional, Type
from types import TracebackType

from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import Session as DbSession, sessionmaker


class Db:
    def __init__(self, pg_host: str, pg_port: int, pg_user: str, pg_password: str,
                 pg_db: str) -> None:
        self._engine = create_engine(
            f'postgresql+psycopg2://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}')
        self._session_factory = sessionmaker(bind=self._engine)

    def __enter__(self) -> DbSession:
        self._sa_session = self._session_factory()

        return self._sa_session

    def __exit__(self, exc_type: Optional[Type[BaseException]], exc_value: Optional[BaseException],
                 traceback: Optional[TracebackType]) -> None:
        if exc_type is not None:
            # There was an exception in the code using this context manager; rollback the
            # the transaction, then let the exception bubble up.
            self._sa_session.rollback()
            self._sa_session.close()

            return

        try:
            self._sa_session.commit()

        except Exception:
            self._sa_session.rollback()
            raise

        finally:
            self._sa_session.close()
