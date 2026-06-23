import pytest
from zaby._util import append_query, encode_path, join_path


class TestEncodePath:
    def test_encodes_special_characters(self):
        assert encode_path("hello world") == "hello%20world"
        assert encode_path("a/b?c=d") == "a%2Fb%3Fc%3Dd"
        assert encode_path("user@example.com") == "user%40example.com"

    def test_simple_strings(self):
        assert encode_path("abc123") == "abc123"
        assert encode_path("run_123") == "run_123"

    def test_unicode(self):
        assert encode_path("héllo") == "h%C3%A9llo"


class TestAppendQuery:
    def test_single_param(self):
        assert append_query("/path", {"key": "val"}) == "/path?key=val"

    def test_undefined_query(self):
        assert append_query("/path") == "/path"

    def test_empty_query(self):
        assert append_query("/path", {}) == "/path"

    def test_multiple_params(self):
        result = append_query("/path", {"a": "1", "b": "2"})
        assert "a=1" in result
        assert "b=2" in result

    def test_skips_none(self):
        result = append_query("/path", {"a": "1", "b": None})
        assert result == "/path?a=1"

    def test_array_values(self):
        result = append_query("/path", {"id": ["a", "b", "c"]})
        assert result == "/path?id=a&id=b&id=c"

    def test_number_and_bool(self):
        result = append_query("/path", {"num": 42, "flag": True})
        assert "num=42" in result
        assert "flag=True" in result


class TestJoinPath:
    def test_joins_segments(self):
        assert join_path("/api", "v1", "users") == "/api/v1/users"

    def test_trailing_slashes(self):
        assert join_path("/api/", "v1/", "/users") == "/api/v1/users"

    def test_empty_segments(self):
        assert join_path("/api", "", "v1") == "/api/v1"

    def test_empty_args(self):
        assert join_path() == ""
