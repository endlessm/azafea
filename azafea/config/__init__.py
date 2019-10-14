# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import dataclasses
import logging
import os
from typing import Any, Callable, Dict, List, Mapping, MutableMapping

from pydantic.class_validators import validator
from pydantic.dataclasses import dataclass
from pydantic.error_wrappers import ValidationError

from sqlalchemy.orm.session import Session as DbSession

import toml

from ._validators import is_boolean, is_non_empty_string, is_strictly_positive_integer
from ..utils import get_callable, get_cpu_count, wrap_with_repr


log = logging.getLogger(__name__)

DEFAULT_PASSWORD = 'CHANGE ME!!'


class InvalidConfigurationError(Exception):
    def __init__(self, errors: List[Dict[str, Any]]) -> None:
        self.errors = errors

    def __str__(self) -> str:
        msg = ['Invalid configuration:']

        for e in self.errors:
            loc = e['loc']
            msg.append(f"* {'.'.join(loc)}: {e['msg']}")

        return '\n'.join(msg)


class NoSuchConfigurationError(Exception):
    pass


class _Base:
    def __getattr__(self, name: str) -> Any:
        raise NoSuchConfigurationError(f'No such configuration option: {name!r}')


class _Dictifier(dict):
    def __init__(self, items: List = None) -> None:
        super().__init__()

        if items is not None:
            for k, v in items:
                if k == 'password':
                    # Don't print passwords
                    v = '** hidden **'

                self[k] = v


@dataclass(frozen=True)
class Main(_Base):
    verbose: bool = False
    number_of_workers: int = dataclasses.field(default_factory=get_cpu_count)
    exit_on_empty_queues: bool = False

    @validator('verbose', pre=True)
    def verbose_is_boolean(cls, value: Any) -> bool:
        return is_boolean(value)

    @validator('number_of_workers', pre=True)
    def number_of_workers_is_strictly_positive_integer(cls, value: Any) -> int:
        return is_strictly_positive_integer(value)

    @validator('exit_on_empty_queues', pre=True)
    def exit_on_empty_queues_is_boolean(cls, value: Any) -> bool:
        return is_boolean(value)


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

    @staticmethod
    def _validate_callable(module_name: str, callable_name: str) -> Callable:
        try:
            result = get_callable(module_name, callable_name)

        except ImportError:
            raise ValueError(f'Could not import module {module_name!r}')

        except AttributeError:
            raise ValueError(f'Module {module_name!r} is missing a {callable_name!r} function')

        return wrap_with_repr(result, module_name)

    @validator('handler', pre=True)
    def get_handler(cls, value: str) -> Callable[[DbSession, bytes], None]:
        return cls._validate_callable(value, 'process')


@dataclass(frozen=True)
class Config(_Base):
    main: Main = dataclasses.field(default_factory=Main)
    redis: Redis = dataclasses.field(default_factory=Redis)
    postgresql: PostgreSQL = dataclasses.field(default_factory=PostgreSQL)
    queues: Mapping[str, Queue] = dataclasses.field(default_factory=dict)

    def __post_init_post_parse__(self) -> None:
        self.warn_about_default_passwords()

    @classmethod
    def from_file(cls, config_file_path: str) -> 'Config':
        overrides: MutableMapping[str, Any] = {}

        if os.path.exists(config_file_path):
            overrides = toml.load(config_file_path)

        try:
            return cls(**overrides)

        except ValidationError as e:
            raise InvalidConfigurationError(e.errors())

    def warn_about_default_passwords(self) -> None:
        if self.postgresql.password == DEFAULT_PASSWORD:
            log.warning('Did you forget to change the PostgreSQL password?')

        if self.redis.password == DEFAULT_PASSWORD:
            log.warning('Did you forget to change the Redis password?')

    def __str__(self) -> str:
        return toml.dumps(dataclasses.asdict(self, dict_factory=_Dictifier)).strip()
