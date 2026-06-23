from __future__ import annotations

from typing import Optional, Sequence, Union
from urllib.parse import quote, urlencode

from ._types import Query


def join_path(*parts: str) -> str:
    filtered: list[str] = []
    for i, part in enumerate(parts):
        if not part:
            continue
        if i == 0:
            filtered.append(part.rstrip("/"))
        else:
            filtered.append(part.strip("/"))
    return "/".join(filtered)


def encode_path(value: str) -> str:
    return quote(value, safe="!'()*")


def append_query(path: str, query: Optional[Query] = None) -> str:
    if not query:
        return path
    params: list[tuple[str, str]] = []
    for key, value in query.items():
        if value is None:
            continue
        if isinstance(value, (list, tuple)):
            for item in value:
                if item is not None:
                    params.append((key, str(item)))
        else:
            params.append((key, str(value)))
    if not params:
        return path
    return f"{path}?{urlencode(params)}"
