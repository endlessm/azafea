from typing import Any, Callable, List


class mark:
    @staticmethod
    def parametrize(names: str, params: List[Any]) -> Callable: ...
