# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import copy
import dataclasses
import logging
import os
from typing import Any, Callable, Dict, List, Mapping, MutableMapping, Optional

from pydantic import field_validator, ValidationError
from pydantic.dataclasses import dataclass
from pydantic_core import ErrorDetails

import toml

from ._validators import is_boolean, is_non_empty_string, is_strictly_positive_integer
from ..utils import get_callable, get_cpu_count


log = logging.getLogger(__name__)

DEFAULT_PASSWORD = 'CHANGE ME!!'


class InvalidConfigurationError(Exception):
    def __init__(self, errors: List[ErrorDetails]) -> None:
        self.errors = errors

    def __str__(self) -> str:
        msg = ['Invalid configuration:']

        for e in self.errors:
            loc = self._loc_str(e)
            msg.append(f"* {loc}: {e['msg']}")

        return '\n'.join(msg)

    # The loc field in ErrorDetails is a tuple of strings and ints.
    # https://docs.pydantic.dev/latest/errors/errors/#customize-error-messages
    @staticmethod
    def _loc_str(details: ErrorDetails) -> str:
        # Make the output prettier
        # FIXME: Do that better: https://github.com/samuelcolvin/pydantic/issues/982
        loc = details['loc']
        if loc[0] == 'queues':
            loc += ('handler',)

        path = ''
        for i, element in enumerate(loc):
            if isinstance(element, str):
                if i > 0:
                    path += '.'
                path += element
            else:  # pragma: no cover (our config does not use lists)
                path += f'[{element}]'

        return path


class NoSuchConfigurationError(Exception):
    pass


class _Base:
    def __getattr__(self, name: str) -> Any:
        # Special dunder names aren't used as config options
        if name.startswith('__') and name.endswith('__'):
            raise AttributeError(name)

        raise NoSuchConfigurationError(f'No such configuration option: {name!r}')


def asdict(obj):  # type: ignore
    # We don't use dataclasses.asdict because we want to hide some fields
    if isinstance(obj, _Base):
        result = {}

        for f in dataclasses.fields(obj):
            if not f.init:
                # Ignore computed fields
                continue

            k = f.name
            if k == 'password':
                result[k] = '** hidden **'
            else:
                result[k] = asdict(getattr(obj, k))

        return result

    elif isinstance(obj, dict):
        return {
            k: asdict(v)
            for k, v in obj.items()
        }

    else:
        return copy.deepcopy(obj)


@dataclass(frozen=True)
class Main(_Base):
    verbose: bool = False
    number_of_workers: int = dataclasses.field(default_factory=get_cpu_count)
    exit_on_empty_queues: bool = False

    @field_validator('verbose', mode='before')
    @classmethod
    def verbose_is_boolean(cls, value: Any) -> bool:
        return is_boolean(value)

    @field_validator('number_of_workers', mode='before')
    @classmethod
    def number_of_workers_is_strictly_positive_integer(cls, value: Any) -> int:
        return is_strictly_positive_integer(value)

    @field_validator('exit_on_empty_queues', mode='before')
    @classmethod
    def exit_on_empty_queues_is_boolean(cls, value: Any) -> bool:
        return is_boolean(value)


@dataclass(frozen=True)
class Redis(_Base):
    host: str = 'localhost'
    port: int = 6379
    password: str = DEFAULT_PASSWORD
    ssl: bool = False

    @field_validator('host', mode='before')
    @classmethod
    def host_is_non_empty_string(cls, value: Any) -> str:
        return is_non_empty_string(value)

    @field_validator('port', mode='before')
    @classmethod
    def port_is_strictly_positive_integer(cls, value: Any) -> int:
        return is_strictly_positive_integer(value)


@dataclass(frozen=True)
class PostgreSQL(_Base):
    host: str = 'localhost'
    port: int = 5432
    user: str = 'azafea'
    password: str = DEFAULT_PASSWORD
    database: str = 'azafea'
    connect_args: Dict[str, str] = dataclasses.field(default_factory=dict)

    @field_validator('host', mode='before')
    @classmethod
    def host_is_non_empty_string(cls, value: Any) -> str:
        return is_non_empty_string(value)

    @field_validator('port', mode='before')
    @classmethod
    def port_is_strictly_positive_integer(cls, value: Any) -> int:
        return is_strictly_positive_integer(value)

    @field_validator('user', mode='before')
    @classmethod
    def user_is_non_empty_string(cls, value: Any) -> str:
        return is_non_empty_string(value)

    @field_validator('password', mode='before')
    @classmethod
    def password_is_non_empty_string(cls, value: Any) -> str:
        return is_non_empty_string(value)

    @field_validator('database', mode='before')
    @classmethod
    def database_is_non_empty_string(cls, value: Any) -> str:
        return is_non_empty_string(value)


@dataclass(frozen=True)
class Queue(_Base):
    handler: str
    processor: Callable = dataclasses.field(init=False)
    cli: Optional[Callable] = dataclasses.field(default=None, init=False)

    @staticmethod
    def _validate_callable(module_name: str, callable_name: str) -> Callable:
        try:
            return get_callable(module_name, callable_name)

        except ImportError:
            raise ValueError(f'Could not import module {module_name!r}')

        except AttributeError:
            raise ValueError(f'Module {module_name!r} is missing a {callable_name!r} function')

    # Since processor and cli are init=False, they need to be set in __post_init__ instead of
    # @model_validator. Also, since the dataclass is frozen, they need to be set with
    # object.__setattr__.
    def __post_init__(self) -> None:
        processor = self._validate_callable(self.handler, 'process')
        object.__setattr__(self, 'processor', processor)

        try:
            cli = self._validate_callable(self.handler, 'register_commands')
            object.__setattr__(self, 'cli', cli)

        except ValueError:
            # No CLI then
            pass


@dataclass(frozen=True)
class Config(_Base):
    main: Main = dataclasses.field(default_factory=Main)
    redis: Redis = dataclasses.field(default_factory=Redis)
    postgresql: PostgreSQL = dataclasses.field(default_factory=PostgreSQL)
    queues: Mapping[str, Queue] = dataclasses.field(default_factory=dict)

    def __post_init__(self) -> None:
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
        return toml.dumps(asdict(self)).strip()
