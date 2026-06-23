import pytest
from zaby._sse import parse_sse_response
from zaby._types import SseEvent


async def collect_events(body=None, stream=None):
    events = []
    async for event in parse_sse_response(body=body, body_stream=stream):
        events.append(event)
    return events


class TestSseParser:
    async def test_single_event(self):
        events = await collect_events('data: {"hello":"world"}\n\n')
        assert len(events) == 1
        assert events[0].data == {"hello": "world"}

    async def test_multiple_events(self):
        events = await collect_events('data: {"a":1}\n\ndata: {"b":2}\n\n')
        assert len(events) == 2
        assert events[0].data == {"a": 1}
        assert events[1].data == {"b": 2}

    async def test_event_with_id_and_type(self):
        events = await collect_events('id: 42\nevent: UPDATE\ndata: {"x":1}\n\n')
        assert events[0].id == "42"
        assert events[0].event == "UPDATE"
        assert events[0].data == {"x": 1}

    async def test_empty_data_returns_empty_string(self):
        events = await collect_events("data:\n\n")
        assert len(events) == 1
        assert events[0].data == ""

    async def test_missing_data_field(self):
        events = await collect_events("event: ping\n\n")
        assert len(events) == 1
        assert events[0].event == "ping"
        assert events[0].data == ""

    async def test_multi_line_data(self):
        events = await collect_events('data: {"type":"text","delta":"Hel\ndata: lo"}\n\n')
        assert len(events) == 1
        assert isinstance(events[0].data, str)

    async def test_comment_lines(self):
        events = await collect_events(": comment\n: another comment\ndata: {\"ok\":true}\n\n")
        assert len(events) == 1
        assert events[0].data == {"ok": True}

    async def test_empty_input(self):
        events = await collect_events("")
        assert len(events) == 0

    async def test_crlf_line_endings(self):
        events = await collect_events('id: 1\r\nevent: MSG\r\ndata: {"x":1}\r\n\r\n')
        assert len(events) == 1
        assert events[0].id == "1"
        assert events[0].event == "MSG"
        assert events[0].data == {"x": 1}

    async def test_field_with_colon_in_value(self):
        events = await collect_events('data: {"url":"http://example.com"}\n\n')
        assert len(events) == 1
        assert events[0].data == {"url": "http://example.com"}

    async def test_skips_unknown_fields(self):
        events = await collect_events('random: garbage\ndata: {"ok":true}\n\n')
        assert len(events) == 1
        assert events[0].data == {"ok": True}

    async def test_parse_data_returns_string_for_invalid_json(self):
        events = await collect_events("data: hello world\n\n")
        assert len(events) == 1
        assert events[0].data == "hello world"


class TestSseEdgeCases:
    async def test_trailing_buffer_without_newline(self):
        body = 'data: {"a":1}\n\ndata: {"b":2}'
        events = await collect_events(body=body)
        assert len(events) == 2
        assert events[0].data == {"a": 1}
        assert events[1].data == {"b": 2}

    async def test_leading_space_stripped_from_value(self):
        body = 'data: {"x":1}\nevent: update\n\n'
        events = await collect_events(body=body)
        assert len(events) == 1
        assert events[0].event == "update"

    async def test_empty_blocks_are_skipped(self):
        body = 'data: {"a":1}\n\n\n\n\ndata: {"b":2}\n\n'
        events = await collect_events(body=body)
        assert len(events) == 2

    async def test_remaining_buffer_after_stream_ends(self):
        async def stream():
            yield b'data: {"a":1}\n\ndata: {"b":2}\n\n'
            yield b''
        events = []
        async for event in parse_sse_response(body_stream=stream()):
            events.append(event)
        assert len(events) == 2

    async def test_split_across_chunks_crlf(self):
        async def stream():
            yield b'data: {"a":1}\r\n'
            yield b'\r\ndata: {"b":2}\r\n\r\n'
        events = []
        async for event in parse_sse_response(body_stream=stream()):
            events.append(event)
        assert len(events) == 2
        assert events[0].data == {"a": 1}
        assert events[1].data == {"b": 2}

    async def test_crlf_body_multiple_events(self):
        body = 'data: {"a":1}\r\n\r\ndata: {"b":2}\r\n\r\n'
        events = await collect_events(body=body)
        assert len(events) == 2
        assert events[0].data == {"a": 1}
        assert events[1].data == {"b": 2}

    async def test_nothing_for_none_input(self):
        events = []
        async for event in parse_sse_response(body=None, body_stream=None):
            events.append(event)
        assert len(events) == 0

    async def test_empty_blocks_in_stream_are_skipped(self):
        async def stream():
            yield b'data: {"a":1}\n\n\n\n\ndata: {"b":2}\n\n'
        events = []
        async for event in parse_sse_response(body_stream=stream()):
            events.append(event)
        assert len(events) == 2


class TestSseStreaming:
    async def test_yields_incrementally(self):
        async def stream():
            for i in range(200):
                yield f'data: {{"chunk": {i}}}\n\n'.encode()

        events = []
        async for event in parse_sse_response(body_stream=stream()):
            events.append(event)
        assert len(events) == 200
        assert events[0].data == {"chunk": 0}
        assert events[199].data == {"chunk": 199}

    async def test_yields_nothing_for_null_stream(self):
        events = await collect_events()
        assert len(events) == 0

    async def test_handles_chunk_boundaries(self):
        async def stream():
            yield b'data: {"a":1}\n\n'
            yield b'data: {"b":2}\n\n'

        events = await collect_events(stream=stream())
        assert len(events) == 2
        assert events[0].data == {"a": 1}
        assert events[1].data == {"b": 2}

    async def test_handles_large_payload(self):
        large = "x" * 100_000
        async def stream():
            yield f"data: {large}\n\n".encode()

        events = await collect_events(stream=stream())
        assert len(events) == 1
        assert events[0].data == large
