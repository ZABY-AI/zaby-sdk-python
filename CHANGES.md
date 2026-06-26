# Python SDK Changes

## What was done

### 1. Added missing client classes in `_agents.py`

**`RuntimeTokenFamiliesClient`**
- `list()` — GET `/api/v1/provisioning/managed-agents/runtime-token-families`
- `revoke(family_id)` — POST `/api/v1/provisioning/managed-agents/runtime-token-families/{id}/revoke`

**`RuntimeTokenPoliciesClient`**
- `list()` — GET `/api/v1/provisioning/managed-agents/runtime-token-policies`
- `create(input)` — POST `/api/v1/provisioning/managed-agents/runtime-token-policies`
- `get(policy_id)` — GET `/api/v1/provisioning/managed-agents/runtime-token-policies/{id}`
- `update(policy_id, input)` — PATCH `/api/v1/provisioning/managed-agents/runtime-token-policies/{id}`

**`RuntimeTokenGrantsClient`**
- `revoke(grant_id, input)` — POST `/api/v1/provisioning/managed-agents/runtime-token-grants/{id}/revoke`

**`RuntimeTokenUsageClient`**
- `get(query)` — GET `/api/v1/provisioning/managed-agents/runtime-token-usage`

### 2. Added missing method on `AgentsClient`

- `playground_runtime_tokens(agent_id)` — GET `/api/v1/tenant/agents/{id}/playground/runtime-tokens`

### 3. Wired new clients into `_zaby.py`

New attributes on `Zaby`:
- `zaby.runtime_token_families`
- `zaby.runtime_token_policies`
- `zaby.runtime_token_grants`
- `zaby.runtime_token_usage`

### 4. Added 29 missing tests to `test_client_methods.py`

| Client | Tests added |
|--------|-----------|
| `AgentsClient` | `test_agents_test_run`, `test_agents_playground_runtime_tokens` |
| `ExternalAppsClient` | `test_external_apps_create` |
| `IntelligenceClient` | `test_intelligence_reject_improvement` |
| `MemoryClient` | `test_memory_reject_candidate` |
| `McpClient` | `get_server`, `update_server`, `list_installations`, `update_installation`, `revoke_installation`, `list_installation_tools`, `update_tool_policy`, `preflight_invocation`, `invoke_tool`, `create_credential_binding`, `delete_credential_binding`, `upsert_auth_policy`, `grant_access` |
| `KnowledgeBasesClient` | `create_library_text_document`, `list_library_documents`, `list_library_document_findings`, `link_library_document`, `project_library_document`, `list_sources`, `update_source`, `link_source_credential`, `update_ingestion_policy`, `upsert_governance_policy`, `create_profile`, `update_profile` |
| `RuntimeTokenFamiliesClient` | `list`, `revoke` |
| `RuntimeTokenPoliciesClient` | `list`, `create`, `get`, `update` |
| `RuntimeTokenGrantsClient` | `revoke` |
| `RuntimeTokenUsageClient` | `get` |

### 5. Test results

- **Python SDK**: 202 tests pass (up from 173)
- **TypeScript SDK**: 88 client-method tests pass
- All methods that exist in the TypeScript SDK now have corresponding tests in the Python SDK

## Key decision

The Python SDK uses `/api/v1/tenant/agents` as its `AGENTS` base path (set by the senior engineer), while the TypeScript SDK uses `/api/v1/provisioning/agentic-os/agents`. Both paths work with the platform — the provisioning path works with just the API key, while the tenant path needs a JWT bearer token.

The provisioning paths for the new runtime-token clients (`/api/v1/provisioning/managed-agents/runtime-token-*`) work with just the API key, matching the TypeScript convention.

## Files modified

- `src/zaby/clients/_agents.py` — added 4 new classes + 1 new method + `PROVISIONING` constant
- `src/zaby/_zaby.py` — imported and wired new clients
- `tests/test_client_methods.py` — added 29 tests
