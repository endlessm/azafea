import dataclasses
import logging
import os
from typing import Any, MutableMapping, Sequence, Union

from pydantic.class_validators import validator
from pydantic.dataclasses import dataclass
from pydantic.error_wrappers import ErrorWrapper, ValidationError

import toml

from ._validators import is_boolean, is_strictly_positive_integer
from ..utils import get_cpu_count


logger = logging.getLogger(__name__)


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
class Config(_Base):
    main: Main = dataclasses.field(default_factory=Main)

    @classmethod
    def from_file(cls, config_file_path: str) -> 'Config':
        overrides: MutableMapping[str, Any] = {}

        if os.path.exists(config_file_path):
            overrides = toml.load(config_file_path)

        try:
            main = Main(**overrides.get('main', {}))
        except ValidationError as e:
            raise InvalidConfigurationError('main', e.raw_errors)

        return cls(main=main)
