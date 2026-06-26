from __future__ import annotations

from typing import Any, Optional

from .._transport import ZabyCoreClient
from .._util import encode_path

AGENTIC_OS = "/api/v1/provisioning/agentic-os"
KBS = f"{AGENTIC_OS}/knowledge-bases"
KNOWLEDGE_LIBRARY = f"{AGENTIC_OS}/knowledge-library"


class KnowledgeBasesClient:
    def __init__(self, core: ZabyCoreClient):
        self._core = core

    async def create(self, input: Any, **kwargs: Any) -> Any:
        return await self._core.request("POST", KBS, json_body=input, **kwargs)

    async def upload_text_document(self, knowledge_base_id: str, input: Any, **kwargs: Any) -> Any:
        return await self._core.request("POST", f"{KBS}/{encode_path(knowledge_base_id)}/documents/text", json_body=input, **kwargs)

    async def create_library_text_document(self, input: Any, **kwargs: Any) -> Any:
        return await self._core.request("POST", f"{KNOWLEDGE_LIBRARY}/documents/text", json_body=input, **kwargs)

    async def list_library_documents(self, query: Any = None, **kwargs: Any) -> Any:
        return await self._core.request("GET", f"{KNOWLEDGE_LIBRARY}/documents", query=query, **kwargs)

    async def list_library_document_findings(self, library_document_id: str, query: Any = None, **kwargs: Any) -> Any:
        return await self._core.request("GET", f"{KNOWLEDGE_LIBRARY}/documents/{encode_path(library_document_id)}/findings", query=query, **kwargs)

    async def link_library_document(self, knowledge_base_id: str, input: Any, **kwargs: Any) -> Any:
        return await self._core.request("POST", f"{KBS}/{encode_path(knowledge_base_id)}/library-documents", json_body=input, **kwargs)

    async def project_library_document(self, knowledge_base_id: str, selection_id: str, input: Any, **kwargs: Any) -> Any:
        return await self._core.request("POST", f"{KBS}/{encode_path(knowledge_base_id)}/library-documents/{encode_path(selection_id)}/project", json_body=input, **kwargs)

    async def retrieve(self, knowledge_base_id: str, input: Any, **kwargs: Any) -> Any:
        return await self._core.request("POST", f"{KBS}/{encode_path(knowledge_base_id)}/retrieve", json_body=input, **kwargs)

    async def provisional_answer(self, knowledge_base_id: str, input: Any, **kwargs: Any) -> Any:
        return await self._core.request("POST", f"{KBS}/{encode_path(knowledge_base_id)}/provisional-answer", json_body=input, **kwargs)

    async def list_source_groups(self, knowledge_base_id: str, query: Any = None, **kwargs: Any) -> Any:
        return await self._core.request("GET", f"{KBS}/{encode_path(knowledge_base_id)}/source-groups", query=query, **kwargs)

    async def create_source_group(self, knowledge_base_id: str, input: Any, **kwargs: Any) -> Any:
        return await self._core.request("POST", f"{KBS}/{encode_path(knowledge_base_id)}/source-groups", json_body=input, **kwargs)

    async def update_source_group(self, knowledge_base_id: str, source_group_id: str, input: Any, **kwargs: Any) -> Any:
        return await self._core.request("PATCH", f"{KBS}/{encode_path(knowledge_base_id)}/source-groups/{encode_path(source_group_id)}", json_body=input, **kwargs)

    async def list_sources(self, knowledge_base_id: str, query: Any = None, **kwargs: Any) -> Any:
        return await self._core.request("GET", f"{KBS}/{encode_path(knowledge_base_id)}/sources", query=query, **kwargs)

    async def create_source(self, knowledge_base_id: str, input: Any, **kwargs: Any) -> Any:
        return await self._core.request("POST", f"{KBS}/{encode_path(knowledge_base_id)}/sources", json_body=input, **kwargs)

    async def update_source(self, knowledge_base_id: str, source_id: str, input: Any, **kwargs: Any) -> Any:
        return await self._core.request("PATCH", f"{KBS}/{encode_path(knowledge_base_id)}/sources/{encode_path(source_id)}", json_body=input, **kwargs)

    async def reprocess_source(self, knowledge_base_id: str, source_id: str, **kwargs: Any) -> Any:
        return await self._core.request("POST", f"{KBS}/{encode_path(knowledge_base_id)}/sources/{encode_path(source_id)}/reprocess", **kwargs)

    async def link_source_credential(self, knowledge_base_id: str, source_id: str, input: Any, **kwargs: Any) -> Any:
        return await self._core.request("POST", f"{KBS}/{encode_path(knowledge_base_id)}/sources/{encode_path(source_id)}/auth", json_body=input, **kwargs)

    async def list_ingestion_policies(self, knowledge_base_id: str, query: Any = None, **kwargs: Any) -> Any:
        return await self._core.request("GET", f"{KBS}/{encode_path(knowledge_base_id)}/ingestion-policies", query=query, **kwargs)

    async def create_ingestion_policy(self, knowledge_base_id: str, input: Any, **kwargs: Any) -> Any:
        return await self._core.request("POST", f"{KBS}/{encode_path(knowledge_base_id)}/ingestion-policies", json_body=input, **kwargs)

    async def update_ingestion_policy(self, knowledge_base_id: str, policy_id: str, input: Any, **kwargs: Any) -> Any:
        return await self._core.request("PATCH", f"{KBS}/{encode_path(knowledge_base_id)}/ingestion-policies/{encode_path(policy_id)}", json_body=input, **kwargs)

    async def upsert_governance_policy(self, knowledge_base_id: str, input: Any, **kwargs: Any) -> Any:
        return await self._core.request("POST", f"{KBS}/{encode_path(knowledge_base_id)}/governance-policy", json_body=input, **kwargs)

    async def list_profiles(self, knowledge_base_id: str, **kwargs: Any) -> Any:
        return await self._core.request("GET", f"{KBS}/{encode_path(knowledge_base_id)}/profiles", **kwargs)

    async def create_profile(self, knowledge_base_id: str, input: Any, **kwargs: Any) -> Any:
        return await self._core.request("POST", f"{KBS}/{encode_path(knowledge_base_id)}/profiles", json_body=input, **kwargs)

    async def update_profile(self, knowledge_base_id: str, profile_id: str, input: Any, **kwargs: Any) -> Any:
        return await self._core.request("PATCH", f"{KBS}/{encode_path(knowledge_base_id)}/profiles/{encode_path(profile_id)}", json_body=input, **kwargs)

    async def list_jobs(self, knowledge_base_id: str, query: Any = None, **kwargs: Any) -> Any:
        return await self._core.request("GET", f"{KBS}/{encode_path(knowledge_base_id)}/idocs-jobs", query=query, **kwargs)

    async def get_job(self, knowledge_base_id: str, job_id: str, **kwargs: Any) -> Any:
        return await self._core.request("GET", f"{KBS}/{encode_path(knowledge_base_id)}/idocs-jobs/{encode_path(job_id)}", **kwargs)

    async def cancel_job(self, knowledge_base_id: str, job_id: str, **kwargs: Any) -> Any:
        return await self._core.request("POST", f"{KBS}/{encode_path(knowledge_base_id)}/idocs-jobs/{encode_path(job_id)}/cancel", **kwargs)
