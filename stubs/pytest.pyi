# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from typing import Any, Callable, List, Optional


def fixture(scope: str = "function",
            params: Optional[List[Any]] = None,
            autouse: bool = False,
            ids: Optional[List[str]] = None,
            name: Optional[str] = None) -> Callable: ...

class mark:
    @staticmethod
    def parametrize(names: str, params: List[Any]) -> Callable: ...

    @staticmethod
    def integration(func: Callable[[Any, Any], Any]) -> Callable: ...

def param(*values: Any, id: Optional[str] = None) -> Callable: ...
