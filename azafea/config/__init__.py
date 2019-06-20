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


import dataclasses
import logging
import os
from typing import Any, Callable, Mapping, MutableMapping, Sequence, Union

from pydantic.class_validators import validator
from pydantic.dataclasses import dataclass
from pydantic.error_wrappers import ErrorWrapper, ValidationError

from sqlalchemy.orm.session import Session as DbSession

import toml

from ._validators import is_boolean, is_non_empty_string, is_strictly_positive_integer
from ..utils import get_cpu_count, get_handler, wrap_with_repr


log = logging.getLogger(__name__)

DEFAULT_PASSWORD = 'CHANGE ME!!'


class InvalidConfigurationError(Exception):
    def __init__(self, section: str, errors: Sequence[Union[Sequence[Any], ErrorWrapper]]) -> None:
        self.section = section
        self.errors = errors

    def __str__(self) -> str:
        msg = [f'Invalid [{self.section}] configuration:']

        for e in self.errors:
            if isinstance(e, ErrorWrapper):
                for loc in e.loc:
                    msg.append(f'* {loc}: {e.msg}')

            else:
                msg.append(str(e))

        return '\n'.join(msg)


class NoSuchConfigurationError(Exception):
    pass


class _Base:
    def __getattr__(self, name: str) -> Any:
        raise NoSuchConfigurationError(f'No such configuration option: {name!r}')


@dataclass(frozen=True)
class Main(_Base):
    verbose: bool = False
    number_of_workers: int = dataclasses.field(default_factory=get_cpu_count)

    @validator('verbose', pre=True)
    def verbose_is_boolean(cls, value: Any) -> bool:
        return is_boolean(value)

    @validator('number_of_workers', pre=True)
    def number_of_workers_is_strictly_positive_integer(cls, value: Any) -> int:
        return is_strictly_positive_integer(value)


@dataclass(frozen=True)
class Redis(_Base):
    host: str = 'localhost'
    port: int = 6379
    password: str = DEFAULT_PASSWORD

    @validator('host', pre=True)
    def host_is_non_empty_string(cls, value: Any) -> str:
        return is_non_empty_string(value)

    @validator('port', pre=True)
    def port_is_strictly_positive_integer(cls, value: Any) -> int:
        return is_strictly_positive_integer(value)


@dataclass(frozen=True)
class PostgreSQL(_Base):
    host: str = 'localhost'
    port: int = 5432
    user: str = 'azafea'
    password: str = DEFAULT_PASSWORD
    database: str = 'azafea'

    @validator('host', pre=True)
    def host_is_non_empty_string(cls, value: Any) -> str:
        return is_non_empty_string(value)

    @validator('port', pre=True)
    def port_is_strictly_positive_integer(cls, value: Any) -> int:
        return is_strictly_positive_integer(value)

    @validator('user', pre=True)
    def user_is_non_empty_string(cls, value: Any) -> str:
        return is_non_empty_string(value)

    @validator('password', pre=True)
    def password_is_non_empty_string(cls, value: Any) -> str:
        return is_non_empty_string(value)

    @validator('database', pre=True)
    def database_is_non_empty_string(cls, value: Any) -> str:
        return is_non_empty_string(value)


@dataclass(frozen=True)
class Queue(_Base):
    handler: Callable

    @validator('handler', pre=True)
    def get_handler(cls, value: str) -> Callable[[DbSession, bytes], None]:
        try:
            handler = get_handler(value)

        except ImportError:
            raise ValueError(f'Could not import handler module {value!r}')

        except AttributeError:
            raise ValueError(f'Handler {value!r} is missing a "process" function')

        return wrap_with_repr(handler, value)


@dataclass(frozen=True)
class Config(_Base):
    main: Main = dataclasses.field(default_factory=Main)
    redis: Redis = dataclasses.field(default_factory=Redis)
    postgresql: PostgreSQL = dataclasses.field(default_factory=PostgreSQL)
    queues: Mapping[str, Queue] = dataclasses.field(default_factory=dict)

    @classmethod
    def from_file(cls, config_file_path: str) -> 'Config':
        overrides: MutableMapping[str, Any] = {}
        queues: MutableMapping[str, Queue] = {}

        if os.path.exists(config_file_path):
            overrides = toml.load(config_file_path)

        try:
            main = Main(**overrides.get('main', {}))
        except ValidationError as e:
            raise InvalidConfigurationError('main', e.raw_errors)

        try:
            redis = Redis(**overrides.get('redis', {}))
        except ValidationError as e:
            raise InvalidConfigurationError('redis', e.raw_errors)

        try:
            postgresql = PostgreSQL(**overrides.get('postgresql', {}))
        except ValidationError as e:
            raise InvalidConfigurationError('postgresql', e.raw_errors)

        try:
            for name, queue_options in overrides.get('queues', {}).items():
                queues[name] = Queue(**queue_options)
        except ValidationError as e:
            raise InvalidConfigurationError('queues', e.raw_errors)

        return cls(main=main, redis=redis, postgresql=postgresql, queues=queues)

    def warn_about_default_passwords(self) -> None:
        if self.postgresql.password == DEFAULT_PASSWORD:
            log.warning('Did you forget to change the PostgreSQL password?')

        if self.redis.password == DEFAULT_PASSWORD:
            log.warning('Did you forget to change the Redis password?')

    def __str__(self) -> str:
        pg_no_password = dataclasses.replace(self.postgresql, password='** hidden **')
        redis_no_password = dataclasses.replace(self.redis, password='** hidden **')
        self_no_passwords = dataclasses.replace(self, postgresql=pg_no_password,
                                                redis=redis_no_password)

        return toml.dumps(dataclasses.asdict(self_no_passwords)).strip()
