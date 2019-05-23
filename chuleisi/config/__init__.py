import dataclasses
import logging

from pydantic.dataclasses import dataclass

from ..utils import get_cpu_count


logger = logging.getLogger(__name__)


class NoSuchConfigurationError(Exception):
    pass


class _Base:
    def __getattr__(self, name: str) -> Any:
        raise NoSuchConfigurationError(f'No such configuration option: {name!r}')


@dataclass(frozen=True)
class Main(_Base):
    verbose: bool = False
    number_of_workers: int = dataclasses.field(default_factory=get_cpu_count)


@dataclass(frozen=True)
class Config(_Base):
    main: Main = dataclasses.field(default_factory=Main)
