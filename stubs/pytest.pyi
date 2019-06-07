from typing import Any, Callable, List


def fixture(scope: str = "function",
            params: List[Any] = None,
            autouse: bool = False,
            ids: List[str] = None,
            name: str = None) -> Callable: ...

class mark:
    @staticmethod
    def parametrize(names: str, params: List[Any]) -> Callable: ...

def param(*values: str, id: str = None) -> Callable: ...
