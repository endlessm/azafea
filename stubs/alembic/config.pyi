from typing import Any, MutableMapping


class Config:
    attributes: MutableMapping[str, Any]

    def __init__(self, file_: str = None) -> None: ...
    def get_main_option(self, name: str) -> str: ...
    def set_main_option(self, name: str, value: str) -> None: ...
