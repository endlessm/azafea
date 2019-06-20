# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# Azafea is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Azafea is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Azafea.  If not, see <http://www.gnu.org/licenses/>.


from operator import attrgetter
from typing import Any, Optional, Type
from types import TracebackType

from sqlalchemy.dialects.postgresql.base import PGDDLCompiler
from sqlalchemy.engine import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.relationships import RelationshipProperty
from sqlalchemy.orm.session import Session as DbSession, sessionmaker
from sqlalchemy.schema import CreateColumn, MetaData

from .utils import get_fqdn


# Recommended naming convention used by Alembic, as various different database
# providers will autogenerate vastly different names making migrations more
# difficult. See: http://alembic.zzzcomputing.com/en/latest/naming.html
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}


class BaseModel:
    def __init__(self, **kwargs: Any):
        columns = inspect(self.__class__).attrs

        for k, v in kwargs.items():
            if k in columns:
                setattr(self, k, v)

    def __str__(self) -> str:
        result = [f'# {get_fqdn(self.__class__)}']
        mapper = inspect(self.__class__)

        for column in sorted(mapper.attrs, key=attrgetter('key')):
            name = column.key

            if isinstance(column, RelationshipProperty):
                value = getattr(self, name).id

            else:
                value = getattr(self, column.key)

            if value is not None:
                result.append(f'* {name}: {value}')

        return '\n'.join(result)


class Db:
    def __init__(self, host: str, port: int, user: str, password: str, db: str) -> None:
        self._engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}')
        self._session_factory = sessionmaker(bind=self._engine)

        # Store the URL to use in exceptions
        self._url = f'postgresql://{user}@{host}:{port}/{db}'

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

    def ensure_connection(self) -> None:
        with self as dbsession:
            try:
                dbsession.connection()

            except OperationalError:
                # FIXME: Are we sure this is the only error possible?
                raise PostgresqlConnectionError(f'connection refused on {self._url}')

    # These 2 methods create or drop all the tables for registered models.
    #
    # With SQLAlchemy, a model is registered if it inherits from Base, and the model class has been
    # imported. In Azafea, the model classes are imported when the queue config imports their
    # handlers.
    def create_all(self) -> None:
        Base.metadata.create_all(self._engine)

    def drop_all(self) -> None:
        Base.metadata.drop_all(self._engine)


class PostgresqlConnectionError(Exception):
    pass


metadata = MetaData(naming_convention=NAMING_CONVENTION)
Base = declarative_base(cls=BaseModel, constructor=BaseModel.__init__, metadata=metadata)


# https://docs.sqlalchemy.org/en/13/dialects/postgresql.html#postgresql-10-identity-columns
@compiles(CreateColumn, 'postgresql')
def use_identity(element: CreateColumn, compiler: PGDDLCompiler, **kwargs: Any) -> str:
    text = compiler.visit_create_column(element, **kwargs)
    text = text.replace("SERIAL", "INT GENERATED ALWAYS AS IDENTITY")

    return text
