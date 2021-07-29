# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import copy
from operator import attrgetter
from types import TracebackType
from typing import Any, Dict, Iterator, Optional, Tuple, Type

from sqlalchemy.dialects.postgresql.base import PGDDLCompiler
from sqlalchemy.engine import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.event import listen
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative.api import DeclarativeMeta
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.query import Query
from sqlalchemy.orm.relationships import RelationshipProperty
from sqlalchemy.orm.session import Session as SaSession, sessionmaker
from sqlalchemy.schema import Column, CreateColumn, DDL, MetaData, Table
from sqlalchemy.types import Enum, TypeDecorator

from .config import PostgreSQL as PgConfig
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
    id: Column

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
                related = getattr(self, name)
                value = related.id if related is not None else None

            else:
                value = getattr(self, column.key)

            if value is not None:
                result.append(f'* {name}: {value}')

        return '\n'.join(result)


class ChunkedQuery:
    def __init__(self, dbsession: 'DbSession', model: Type['Base'], chunk_size: int):
        self._query = dbsession.query(model).order_by(model.id)
        self._chunk_size = chunk_size
        self._total_count: Optional[int] = None
        self._descending = False

    def __iter__(self) -> Iterator[Query]:
        total = self.count()

        if self._descending:
            for stop in range(total, 0, -self._chunk_size):
                start = max(stop - self._chunk_size, 0)

                yield self._query.slice(start, stop)

        else:
            for start in range(0, total, self._chunk_size):
                stop = min(start + self._chunk_size, total)

                yield self._query.slice(start, stop)

    def count(self) -> int:
        if self._total_count is None:
            self._total_count = self._query.count()

        return self._total_count

    def reverse_chunks(self) -> 'ChunkedQuery':
        self._descending = True

        return self

    # FIXME: sqlalchemy-stubs doesn't have type hints for this
    def filter(self, *criterion) -> 'ChunkedQuery':  # type: ignore
        self._query = self._query.filter(*criterion)

        return self


class DbSession(SaSession):
    def chunked_query(self, model: Type['Base'], chunk_size: int = 5000) -> ChunkedQuery:
        return ChunkedQuery(self, model, chunk_size)


class Db:
    def __init__(self, pgconfig: PgConfig) -> None:
        connect_args = copy.deepcopy(pgconfig.connect_args)
        connect_args['password'] = pgconfig.password

        self._url = URL('postgresql+psycopg2', username=pgconfig.user, host=pgconfig.host,
                        port=pgconfig.port, database=pgconfig.database)
        self._engine = create_engine(self._url, connect_args=connect_args)
        self._session_factory = sessionmaker(bind=self._engine, class_=DbSession)

        # Try to connect, to fail early if the PostgreSQL server can't be reached.
        self._ensure_connection()

        try:
            # Make sure the Alembic version table is known, this is useful when dropping all tables
            Base.metadata.reflect(bind=self._engine, only=('alembic_version', ))

        except Exception:
            # The Alembic version table doesn't exist, migrations haven't been run yet
            pass

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

        if not self._sa_session.is_active:
            self._sa_session.close()
            return

        try:
            self._sa_session.commit()

        except Exception:
            self._sa_session.rollback()
            raise

        finally:
            self._sa_session.close()

    def _ensure_connection(self) -> None:
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


class NullableBoolean(TypeDecorator):
    """A three-states boolean, which allows working with UNIQUE constraints

    In PostgreSQL, when making a composite UNIQUE constraint where one of the columns is a nullable
    boolean, then null values for that column are counted as always different.

    So if you have:

        class MyModel(Base):
            __tablename__ = 'mymodel'

            id = Column(Integer, primary_key=True)
            col1 = Column(Unicode, nullable=False)
            col2 = Column(Unicode, nullable=False)
            col3 = Column(Boolean)

            __table_args__ = (
                UniqueConstraint(col1, col2, col3, name='uq_mymodel_col1_col2_col3'),
            }

    Then you could INSERT multiple records which have the same (col1, col2) when col3 is None.

    If you want None to be considered a "proper" value that triggers the unicity constraint, then
    use this type instead of a nullable Boolean. Make sure you declare it with `nullable=False`
    though.
    """
    impl = Enum

    def __init__(self, **kwargs: Any) -> None:
        kwargs['name'] = 'nullable_boolean_enum'

        super().__init__('true', 'false', 'unknown', **kwargs)

    coerce_to_is_types = ()

    def process_bind_param(self, value: Optional[bool], dialect: Any) -> str:
        """Convert the Python values into the SQL ones"""
        return {
            True: 'true',
            False: 'false',
            None: 'unknown',
        }[value]

    def process_result_value(self, value: Optional[str], dialect: Any) -> Optional[bool]:
        """Convert the SQL values into the Python ones"""
        # The function signature says value is an Optional[Any], but in our case it can never be
        # None, as long as the model declares this column as nullable=False.
        return {
            'true': True,
            'false': False,
            'unknown': None,
        }[value]  # type: ignore


class PostgresqlConnectionError(Exception):
    pass


metadata = MetaData(naming_convention=NAMING_CONVENTION)
Base = declarative_base(cls=BaseModel, constructor=BaseModel.__init__, metadata=metadata)
views = {}


class ViewMeta(DeclarativeMeta):
    __materialized__ = False

    def __new__(mcl, name: str, bases: Tuple[type, ...], attrs: Dict[str, Any]) -> 'ViewMeta':
        cls = super().__new__(mcl, name, bases, attrs)

        tablename, query = attrs.get('__tablename__'), attrs.get('__query__')
        if not tablename or not query:
            # Mainly useful for the View abstract class
            return cls

        table = cls.__table__ = views[tablename] = Table(tablename, MetaData())
        # Add properties needed to reference views in other views
        cls.c, cls.self_group = table.c, table.self_group

        for column in query.column_descriptions:
            # FIXME: Always set all columns as primary keys, may need to be changed for other tables
            table.append_column(Column(column['name'], column['type'], primary_key=True))
        for from_table in query.selectable.locate_all_froms():
            table.add_is_dependent_on(from_table)

        if cls.__materialized__:
            listen(Base.metadata, 'after_create', DDL(
                f'CREATE MATERIALIZED VIEW IF NOT EXISTS "{tablename}" AS {query}'))
            listen(Base.metadata, 'before_drop', DDL(
                f'DROP MATERIALIZED VIEW IF EXISTS "{tablename}"'))
        else:
            # For some reason, create_all doesn’t use the right order when
            # creating views that depend on other views. Commenting these lines
            # is a dirty way to solve this problem, because we only have
            # "normal" views depending on materialized views. Moreover, these
            # "normal" views are not tested, so they don’t need to be created
            # by SQLAlchemy for tests.
            #
            # listen(Base.metadata, 'after_create', DDL(
            #     f'CREATE OR REPLACE VIEW "{tablename}" AS {query}'))
            # listen(Base.metadata, 'before_drop', DDL(f'DROP VIEW IF EXISTS "{tablename}"'))
            pass

        return cls


class View(Base, metaclass=ViewMeta):
    """Declarative class for PostgreSQL materialized views."""
    __abstract__ = True

    __materialized__ = False
    __query__: Query


# https://docs.sqlalchemy.org/en/13/dialects/postgresql.html#postgresql-10-identity-columns
@compiles(CreateColumn, 'postgresql')
def use_identity(element: CreateColumn, compiler: PGDDLCompiler, **kwargs: Any) -> str:
    text = compiler.visit_create_column(element, **kwargs)
    text = text.replace("SERIAL", "INT GENERATED ALWAYS AS IDENTITY")

    return text
