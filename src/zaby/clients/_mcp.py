from __future__ import annotations

from typing import Any, Optional

from .._transport import ZabyCoreClient
from .._util import encode_path

MCP = "/api/v1/tenant/mcp"


class McpClient:
    def __init__(self, core: ZabyCoreClient):
        self._core = core

    async def list_catalog(self, **kwargs: Any) -> Any:
        return await self._core.request("GET", f"{MCP}/catalog", **kwargs)

    async def create_server(self, input: Any, **kwargs: Any) -> Any:
        return await self._core.request("POST", f"{MCP}/servers", json_body=input, **kwargs)

    async def get_server(self, server_id: str, **kwargs: Any) -> Any:
        return await self._core.request("GET", f"{MCP}/servers/{encode_path(server_id)}", **kwargs)

    async def update_server(self, server_id: str, input: Any, **kwargs: Any) -> Any:
        return await self._core.request("PATCH", f"{MCP}/servers/{encode_path(server_id)}", json_body=input, **kwargs)

    async def discover_tools(self, server_id: str, **kwargs: Any) -> Any:
        return await self._core.request("POST", f"{MCP}/servers/{encode_path(server_id)}/discover-tools", **kwargs)

    async def install_server(self, input: Any, **kwargs: Any) -> Any:
        return await self._core.request("POST", f"{MCP}/installations", json_body=input, **kwargs)

    async def list_installations(self, **kwargs: Any) -> Any:
        return await self._core.request("GET", f"{MCP}/installations", **kwargs)

    async def update_installation(self, installation_id: str, input: Any, **kwargs: Any) -> Any:
        return await self._core.request("PATCH", f"{MCP}/installations/{encode_path(installation_id)}", json_body=input, **kwargs)

    async def revoke_installation(self, installation_id: str, **kwargs: Any) -> Any:
        return await self._core.request("DELETE", f"{MCP}/installations/{encode_path(installation_id)}", **kwargs)

    async def list_installation_tools(self, installation_id: str, **kwargs: Any) -> Any:
        return await self._core.request("GET", f"{MCP}/installations/{encode_path(installation_id)}/tools", **kwargs)

    async def update_tool_policy(self, installation_id: str, tool_id: str, input: Any, **kwargs: Any) -> Any:
        return await self._core.request("PATCH", f"{MCP}/installations/{encode_path(installation_id)}/tools/{encode_path(tool_id)}/policy", json_body=input, **kwargs)

    async def preflight_invocation(self, installation_id: str, tool_name: str, input: Any, **kwargs: Any) -> Any:
        return await self._core.request("POST", f"{MCP}/installations/{encode_path(installation_id)}/tools/{encode_path(tool_name)}/preflight", json_body=input, **kwargs)

    async def invoke_tool(self, installation_id: str, tool_name: str, input: Any, **kwargs: Any) -> Any:
        return await self._core.request("POST", f"{MCP}/installations/{encode_path(installation_id)}/tools/{encode_path(tool_name)}/invoke", json_body=input, **kwargs)

    async def create_credential_binding(self, installation_id: str, input: Any, **kwargs: Any) -> Any:
        return await self._core.request("POST", f"{MCP}/installations/{encode_path(installation_id)}/credential-bindings", json_body=input, **kwargs)

    async def delete_credential_binding(self, binding_id: str, **kwargs: Any) -> Any:
        return await self._core.request("DELETE", f"{MCP}/credential-bindings/{encode_path(binding_id)}", **kwargs)

    async def upsert_auth_policy(self, installation_id: str, input: Any, **kwargs: Any) -> Any:
        return await self._core.request("POST", f"{MCP}/installations/{encode_path(installation_id)}/auth-policies", json_body=input, **kwargs)

    async def grant_access(self, installation_id: str, input: Any, **kwargs: Any) -> Any:
        return await self._core.request("POST", f"{MCP}/installations/{encode_path(installation_id)}/access-grants", json_body=input, **kwargs)
