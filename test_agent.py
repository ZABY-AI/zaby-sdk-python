import asyncio
import json
from zaby import Zaby, configure_zaby, ZabyGlobalConfig

API_KEY = "zaby_pk__VnJy94hIGsDiDsivz_IC3O0z92ihWQBH2XVLn2mFL4"
API_ORIGIN = "http://192.168.68.61:9080"

async def main():
    configure_zaby(ZabyGlobalConfig(api_origin=API_ORIGIN))
    zaby = Zaby(api_key=API_KEY)
    import time
    suffix = str(int(time.time()))[-6:]

    # 1. Create agent
    agent = await zaby.agents.create({
        "name": f"test-py-{suffix}",
        "slug": f"test-py-{suffix}",
        "description": "Created via Python SDK test",
    })
    agent_id = agent.get("id") or agent.get("agentId")
    print(f"Created agent: {agent_id}")

    # 2. Publish to create a version
    version = await zaby.agents.publish(agent_id)
    agent_version_id = version.get("id") or version.get("agentVersionId")
    print(f"Published version: {agent_version_id}")

    # 3. Deploy
    deployment = await zaby.deployments.create(agent_id, {
        "agentVersionId": agent_version_id,
        "environment": "TEST",
        "metadata": {"source": "python-sdk-test"},
    })
    deployment_id = deployment.get("id") or deployment.get("deploymentId")
    print(f"Deployment: {deployment_id}")

    # 4. Create external app
    external_app = await zaby.external_apps.create({
        "name": f"test-py-app-{suffix}",
        "slug": f"test-py-app-{suffix}",
        "allowedOrigins": ["http://localhost:3000"],
        "tokenTtlSeconds": 600,
    })
    external_app_id = external_app.get("id") or external_app.get("externalAppId")
    print(f"External app: {external_app_id}")

    # 5. Bind deployment to external app
    try:
        bind = await zaby.external_apps.bind_deployment(external_app_id, {
            "deploymentId": deployment_id,
            "allowBrowserRuntime": True,
        })
        print(f"Bound deployment to external app")
    except Exception as e:
        print(f"Bind deployment skipped: {e}")

    # 6. Create a runtime token
    try:
        token = await zaby.runtime_tokens.create({
            "externalAppId": external_app_id,
            "deploymentId": deployment_id,
            "externalUserId": "test-user",
            "externalSessionId": "test-session",
            "ttlSeconds": 600,
            "maxUses": 20,
        })
        print(f"Runtime token: {json.dumps(token, indent=2, default=str)}")
    except Exception as e:
        print(f"Runtime token failed: {e}")

    print("\n=== Full lifecycle test complete ===")
    print(f"Agent ID: {agent_id}")
    print(f"Deployment ID: {deployment_id}")
    print(f"External App ID: {external_app_id}")

asyncio.run(main())
