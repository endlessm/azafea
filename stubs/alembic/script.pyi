from typing import Optional, Tuple

from .config import Config


class Script:
    branch_labels: Optional[Tuple[str]] = None


class ScriptDirectory:
    @classmethod
    def from_config(cls, config: Config) -> ScriptDirectory: ...

    def get_revisions(self, id_: str) -> Tuple[Script]: ...
