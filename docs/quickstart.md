# Quickstart

## Python SDK

```python
from managed_research import ManagedResearchClient

client = ManagedResearchClient(api_key="sk_...")

project = client.projects.default()
preflight = project.runs.preflight(
    host_kind="daytona",
    work_mode="directed_effort",
    providers=[{"provider": "openrouter"}],
)

if preflight.clear_to_trigger:
    run = project.runs.start(
        "Improve the benchmark score and summarize the changes.",
        host_kind="daytona",
        work_mode="directed_effort",
        providers=[{"provider": "openrouter"}],
    )
    print(run.id)
```

## Explicit Project Flow

```python
from managed_research import ManagedResearchClient

client = ManagedResearchClient(api_key="sk_...")

project = client.projects.create(name="Improve my eval runner")
project.repositories.attach(github_repo="owner/repo")
readiness = project.readiness()
setup = project.setup.prepare()
preflight = project.runs.preflight(
    host_kind="daytona",
    work_mode="directed_effort",
    providers=[{"provider": "openrouter"}],
)
```

## OpenCode Harness

```python
from managed_research import ManagedResearchClient

client = ManagedResearchClient(api_key="sk_...")

run = client.runs.start(
    "Review the repo and propose the smallest high-impact fix.",
    host_kind="daytona",
    work_mode="directed_effort",
    providers=[{"provider": "openrouter"}],
    agent_harness="opencode_sdk",
    agent_model="anthropic/claude-sonnet-4-6",
)
```

Supported OpenCode models:

- `anthropic/claude-sonnet-4-6`
- `anthropic/claude-haiku-4-5-20251001`
- `x-ai/grok-4.1-fast`

If the requested `(agent_harness, agent_model)` pair is unsupported, launch
preflight and run start fail loudly with structured denials.
