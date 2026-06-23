# Zaby Python SDK

Python SDK for the Zaby Agentic OS.

## Install

```sh
pip install zaby-sdk
```

## Configure

```py
from zaby import configure_zaby

configure_zaby(environment="production")
```

## Server SDK

```py
from zaby import Zaby

zaby = Zaby(api_key="zaby_pk_...", access_token="...")

app = await zaby.external_apps.create(name="Acme Web", slug="acme-web")
```

## Runtime SDK

```py
from zaby import ZabyRuntime

runtime = ZabyRuntime(token="disposable_token")
run = await runtime.runs.start(input={"message": "Hello"})
async for event in runtime.runs.stream(str(run.run_id)):
    print(event)
```

## Development

```sh
pip install -e ".[test]"
pytest
```
