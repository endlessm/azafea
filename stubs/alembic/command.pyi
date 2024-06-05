from typing import Callable, List, Optional

from .config import Config


def revision(config: Config, message: Optional[str] = None, autogenerate: bool = False,
             sql: bool = False, head: str = "head", splice: bool = False,
             branch_label: Optional[str] = None, version_path: Optional[str] = None,
             rev_id: Optional[str] = None, depends_on: Optional[str] = None,
             process_revision_directives: Optional[Callable] = None) -> List: ...


def upgrade(config: Config, revision: str, sql: bool = False,
            tag: Optional[str] = None) -> None: ...
