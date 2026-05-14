"""Open Research MCP tools.

Wraps the locked HTTP contract at
``Jstack/specifications/daily/2026-05-13/open_research_http_contract_v1.md``
so MCP clients can list projects, list queues, submit questions,
poll submissions, list experiments, fetch experiment detail and
receipts. The bundle download is exposed separately through the
existing artifact tooling.

Locked v1 cut list (see
``Jstack/.jstack/daily_notes/2026-05-13/release_planning/launch_2_finish_handoff.md``):
- mandatory sign-in. The MCP transport already carries the Synth API
  key, so this is satisfied for free; the anonymous fingerprint path
  is v1.5.
- live message moderation deferred; ``open_research_send_message``
  ships in v1.5.
- the Spark reviewer gates every submission. **No MCP bypass** per
  ``feedback_no_fallbacks.md``. Both the computer-use composer and
  this MCP path call the same ``POST /api/open-research/v1/submissions``
  endpoint.
"""

from __future__ import annotations

from typing import Any

from managed_research.mcp.registry import ToolDefinition, tool_schema


_BASE = "/api/open-research/v1"


def build_open_research_tools(server: Any) -> list[ToolDefinition]:
    return [
        ToolDefinition(
            name="open_research_list_projects",
            description=(
                "List public Open Research projects (themes). Stateless; no "
                "auth required. Mirrors GET /api/open-research/v1/projects."
            ),
            input_schema=tool_schema({}, required=[]),
            handler=lambda args: _list_projects(server, args),
        ),
        ToolDefinition(
            name="open_research_get_project",
            description=(
                "Fetch full detail for a single Open Research theme by slug "
                "(e.g. 'craftax')."
            ),
            input_schema=tool_schema(
                {
                    "project_slug": {
                        "type": "string",
                        "description": "Open Research project slug (e.g. 'craftax').",
                    },
                },
                required=["project_slug"],
            ),
            handler=lambda args: _get_project(server, args),
        ),
        ToolDefinition(
            name="open_research_list_queues",
            description=(
                "List public submission queues. v1 exposes 1h and 4h "
                "public Craftax queues; the 24h Synth-selected queue "
                "is deferred to v1.5."
            ),
            input_schema=tool_schema(
                {
                    "project_slug": {
                        "type": "string",
                        "description": "Optional Open Research project slug filter.",
                    },
                },
                required=[],
            ),
            handler=lambda args: _list_queues(server, args),
        ),
        ToolDefinition(
            name="open_research_submit_question",
            description=(
                "Submit a research question to a public Open Research queue. "
                "Synchronous: the Spark reviewer runs inline and returns its "
                "verdict in the response. Accepted submissions stay in state "
                "'approved' until an operator schedules the run; the response "
                "carries the submission_id used to poll progress."
            ),
            input_schema=tool_schema(
                {
                    "project_slug": {"type": "string"},
                    "queue_id": {
                        "type": "string",
                        "description": "Queue id from open_research_list_queues.",
                    },
                    "prompt": {
                        "type": "string",
                        "description": "Research question, 1..2000 chars.",
                    },
                    "hypothesis": {
                        "type": "string",
                        "description": "Optional 0..1000 char hypothesis.",
                    },
                    "metric_target": {
                        "type": "object",
                        "description": (
                            "Target metric the run must hit. "
                            "{name, operator: >=|<=|==, value: number}."
                        ),
                        "properties": {
                            "name": {"type": "string"},
                            "operator": {
                                "type": "string",
                                "enum": [">=", "<=", "=="],
                            },
                            "value": {"type": "number"},
                        },
                        "required": ["name", "operator", "value"],
                    },
                    "deo_kind": {
                        "type": "string",
                        "enum": ["open_ended_discovery"],
                    },
                    "rubric_acknowledged": {
                        "type": "boolean",
                        "description": (
                            "Must be true. Confirms the submitter has read the "
                            "public rubric on the project detail page."
                        ),
                    },
                    "submitter_handle": {
                        "type": "string",
                        "description": "Optional public handle (≤64 chars).",
                    },
                },
                required=[
                    "project_slug",
                    "queue_id",
                    "prompt",
                    "metric_target",
                    "deo_kind",
                    "rubric_acknowledged",
                ],
            ),
            handler=lambda args: _submit_question(server, args),
        ),
        ToolDefinition(
            name="open_research_get_submission",
            description=(
                "Poll a submission for review verdict and launched experiment id."
            ),
            input_schema=tool_schema(
                {
                    "submission_id": {
                        "type": "string",
                        "description": "Submission id (sub_…).",
                    },
                },
                required=["submission_id"],
            ),
            handler=lambda args: _get_submission(server, args),
        ),
        ToolDefinition(
            name="open_research_list_experiments",
            description=(
                "List Open Research experiments (≡ public SMR runs) for a project."
            ),
            input_schema=tool_schema(
                {
                    "project_slug": {"type": "string"},
                    "status": {
                        "type": "string",
                        "enum": ["running", "done", "failed", "all"],
                    },
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 100,
                    },
                    "cursor": {"type": "string"},
                },
                required=[],
            ),
            handler=lambda args: _list_experiments(server, args),
        ),
        ToolDefinition(
            name="open_research_get_experiment",
            description=(
                "Fetch full Open Research experiment detail: reward series, "
                "achievements, score table, rollouts, artifact + receipt URLs."
            ),
            input_schema=tool_schema(
                {
                    "experiment_id": {
                        "type": "string",
                        "description": "Experiment id (== SMR run id).",
                    },
                },
                required=["experiment_id"],
            ),
            handler=lambda args: _get_experiment(server, args),
        ),
        ToolDefinition(
            name="open_research_get_receipt",
            description=(
                "Fetch a finalized Open Research experiment receipt. Returns "
                "404 until the run is terminal and the work product is viewable."
            ),
            input_schema=tool_schema(
                {
                    "experiment_id": {"type": "string"},
                },
                required=["experiment_id"],
            ),
            handler=lambda args: _get_receipt(server, args),
        ),
    ]


# ---------------------------------------------------------------------------
# Tool implementations — route everything through the existing SDK transport
# so the MCP path matches the computer-use composer's gate (single Spark
# reviewer, no fallbacks).
# ---------------------------------------------------------------------------


def _client(server: Any, args: dict[str, Any]):
    return server._client_from_args(args)


def _list_projects(server: Any, args: dict[str, Any]) -> Any:
    with _client(server, args) as client:
        return client._transport.request_json("GET", f"{_BASE}/projects")


def _get_project(server: Any, args: dict[str, Any]) -> Any:
    slug = args["project_slug"]
    with _client(server, args) as client:
        return client._transport.request_json(
            "GET", f"{_BASE}/projects/{slug}", allow_not_found=True
        )


def _list_queues(server: Any, args: dict[str, Any]) -> Any:
    params: dict[str, Any] = {}
    if args.get("project_slug"):
        params["project_slug"] = args["project_slug"]
    with _client(server, args) as client:
        return client._transport.request_json(
            "GET", f"{_BASE}/queues", params=params or None
        )


def _submit_question(server: Any, args: dict[str, Any]) -> Any:
    body = {
        "project_slug": args["project_slug"],
        "queue_id": args["queue_id"],
        "prompt": args["prompt"],
        "hypothesis": args.get("hypothesis", ""),
        "metric_target": args["metric_target"],
        "deo_kind": args["deo_kind"],
        "rubric_acknowledged": bool(args["rubric_acknowledged"]),
        "submitter": {"handle": args.get("submitter_handle")},
    }
    with _client(server, args) as client:
        return client._transport.request_json(
            "POST", f"{_BASE}/submissions", json_body=body
        )


def _get_submission(server: Any, args: dict[str, Any]) -> Any:
    sid = args["submission_id"]
    with _client(server, args) as client:
        return client._transport.request_json(
            "GET", f"{_BASE}/submissions/{sid}", allow_not_found=True
        )


def _list_experiments(server: Any, args: dict[str, Any]) -> Any:
    params: dict[str, Any] = {}
    for key in ("project_slug", "status", "cursor"):
        value = args.get(key)
        if value:
            params[key] = value
    if args.get("limit") is not None:
        params["limit"] = int(args["limit"])
    with _client(server, args) as client:
        return client._transport.request_json(
            "GET", f"{_BASE}/experiments", params=params or None
        )


def _get_experiment(server: Any, args: dict[str, Any]) -> Any:
    eid = args["experiment_id"]
    with _client(server, args) as client:
        return client._transport.request_json(
            "GET", f"{_BASE}/experiments/{eid}", allow_not_found=True
        )


def _get_receipt(server: Any, args: dict[str, Any]) -> Any:
    eid = args["experiment_id"]
    with _client(server, args) as client:
        return client._transport.request_json(
            "GET", f"{_BASE}/experiments/{eid}/receipt", allow_not_found=True
        )


__all__ = ["build_open_research_tools"]
