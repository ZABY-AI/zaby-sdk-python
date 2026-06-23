from __future__ import annotations

import json
import re
from typing import Any, AsyncIterator, Optional

from ._types import SseEvent


async def parse_sse_response(
    body: Optional[str] = None,
    body_stream: Optional[AsyncIterator[bytes]] = None,
) -> AsyncIterator[SseEvent]:
    split_re = re.compile(r"(?:\r?\n){2,}")

    if body is not None:
        for block in split_re.split(body):
            stripped = block.strip()
            if not stripped:
                continue
            event = _parse_block(stripped)
            if event:
                yield event
        return

    if body_stream is None:
        return

    buffer = ""
    async for chunk in body_stream:
        text = chunk.decode("utf-8", errors="replace")
        buffer += text
        parts = split_re.split(buffer)
        if len(parts) > 1:
            for i in range(len(parts) - 1):
                stripped = parts[i].strip()
                if stripped:
                    event = _parse_block(stripped)
                    if event:
                        yield event
            buffer = parts[-1]

    if buffer.strip():
        for block in split_re.split(buffer):
            stripped = block.strip()
            if stripped:
                event = _parse_block(stripped)
                if event:
                    yield event


def _parse_block(block: str) -> Optional[SseEvent]:
    if not block.strip():
        return None
    event_id: Optional[str] = None
    event_type: Optional[str] = None
    data_lines: list[str] = []
    for raw_line in block.split("\n"):
        line = raw_line.rstrip("\r")
        if not line or line.startswith(":"):
            continue
        separator = line.find(":")
        if separator == -1:
            field = line
            value = ""
        else:
            field = line[:separator]
            value = line[separator + 1:]
            if value.startswith(" "):
                value = value[1:]
        if field == "id":
            event_id = value
        elif field == "event":
            event_type = value
        elif field == "data":
            data_lines.append(value)
    payload = "\n".join(data_lines)
    return SseEvent(
        id=event_id,
        event=event_type,
        data=_parse_data(payload),
    )


def _parse_data(value: str) -> Any:
    if value == "":
        return ""
    try:
        return json.loads(value)
    except (json.JSONDecodeError, ValueError):
        return value
