"""End-to-end test: code-reviewer task via the OpenAI Agents SDK compat layer.

Drives a real model call through the full pipeline:

  managed-research SmrControlClient
    → synth-ai OpenAIAgentsSdkClient (BFF transport)
    → backend /api/managed-agents/openai/v1/*
    → horizons-private managed runtime
    → model (gpt-5.4 by default)
    → streamed response back to caller

The task is a brief code-review request — simple enough that any model will
produce a non-empty text response, but real enough to confirm the full execution
chain, not just API connectivity.

Exit codes:
  0  — model produced a non-empty text response
  1  — model ran but produced no output text
  2  — API-level failure or transport error

Examples:
  uv run --project managed-research/ \
    python scripts/e2e/run_openai_agents_sdk_reviewer_e2e.py \
    --base-url https://api-staging.usesynth.ai \
    --api-key "$SYNTH_API_KEY"

  uv run --project managed-research/ \
    python scripts/e2e/run_openai_agents_sdk_reviewer_e2e.py \
    --base-url http://127.0.0.1:8080 \
    --api-key sk_dev_00000000000000000000000000000001 \
    --transport-mode backend_bff
"""

from __future__ import annotations

import argparse
import sys
import time
import uuid
from datetime import datetime, timezone
from typing import Any

from managed_research import (
    OPENAI_TRANSPORT_MODE_AUTO,
    OPENAI_TRANSPORT_MODE_BACKEND_BFF,
    OPENAI_TRANSPORT_MODE_DIRECT_HP,
    SmrControlClient,
)

_CODE_SNIPPET = """\
def merge_sorted(a: list[int], b: list[int]) -> list[int]:
    result = []
    i, j = 0, 0
    while i < len(a) and j < len(b):
        if a[i] < b[j]:
            result.append(a[i]); i += 1
        else:
            result.append(b[j]); j += 1
    result += a[i:]
    result += b[j:]
    return result
"""

_REVIEW_PROMPT = f"""\
You are a senior software engineer reviewing a pull request. \
Review the following Python function and give a short critique (1–3 sentences) \
covering correctness, edge cases, and style.

```python
{_CODE_SNIPPET}
```
"""


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stream_to_text(client: Any, request: dict[str, Any]) -> str:
    """Collect all output_text delta frames into a single string."""
    parts: list[str] = []
    for frame in client.stream_response(request):
        if isinstance(frame, dict):
            data = frame.get("data") or {}
            if isinstance(data, dict):
                delta = data.get("delta") or data.get("text") or ""
                if isinstance(delta, str) and delta:
                    parts.append(delta)
    return "".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", required=True, help="Backend base URL")
    parser.add_argument("--api-key", required=True, help="SYNTH_API_KEY")
    parser.add_argument("--model", default="gpt-5.4")
    parser.add_argument(
        "--transport-mode",
        default=OPENAI_TRANSPORT_MODE_AUTO,
        choices=(
            OPENAI_TRANSPORT_MODE_AUTO,
            OPENAI_TRANSPORT_MODE_BACKEND_BFF,
            OPENAI_TRANSPORT_MODE_DIRECT_HP,
        ),
    )
    parser.add_argument("--openai-organization", default="")
    parser.add_argument("--openai-project", default="")
    parser.add_argument(
        "--skip-stream",
        action="store_true",
        help="Use non-streaming response_create instead of SSE stream.",
    )
    args = parser.parse_args()

    run_id = f"e2e_reviewer_{uuid.uuid4().hex[:10]}"
    print(f"[{_utcnow()}] run_id={run_id} model={args.model} transport={args.transport_mode}")

    client = SmrControlClient(
        api_key=args.api_key,
        backend_base=args.base_url,
        openai_transport_mode=args.transport_mode,
        openai_organization=str(args.openai_organization or "").strip() or None,
        openai_project=str(args.openai_project or "").strip() or None,
        openai_request_id=run_id,
    )
    try:
        oai = client.openai_agents_sdk

        # Step 1: create a durable conversation so the model can access history.
        t0 = time.monotonic()
        conversation = oai.create_conversation({"metadata": {"e2e_run": run_id}})
        conversation_id = (conversation or {}).get("id") or ""
        if not conversation_id:
            print(f"[FAIL] conversation_create: missing id — {conversation!r}", file=sys.stderr)
            return 2
        print(f"[{_utcnow()}] conversation_create OK  id={conversation_id}")

        # Step 2: drive a streaming response that asks the model to review the code.
        request: dict[str, Any] = {
            "model": args.model,
            "conversation": conversation_id,
            "input": [
                {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": _REVIEW_PROMPT}],
                }
            ],
            "stream": not args.skip_stream,
        }

        output_text = ""
        if args.skip_stream:
            resp = oai.create_response(request)
            if not isinstance(resp, dict):
                print(f"[FAIL] response_create: non-dict response — {type(resp)}", file=sys.stderr)
                return 2
            response_id = resp.get("id") or resp.get("response_id") or ""
            # Extract text from the completed response object.
            for item in (resp.get("output") or []):
                for part in (item.get("content") or []):
                    if part.get("type") == "output_text":
                        output_text += str(part.get("text") or "")
        else:
            output_text = _stream_to_text(oai, request)
            # stream_response doesn't return the response_id; use an empty placeholder.
            response_id = "(streamed)"

        elapsed = time.monotonic() - t0
        print(f"[{_utcnow()}] response OK  elapsed={elapsed:.1f}s response_id={response_id}")

        if output_text.strip():
            print(f"\n--- model output ({len(output_text)} chars) ---")
            # Print first 600 chars so the log stays readable.
            truncated = output_text[:600]
            print(truncated)
            if len(output_text) > 600:
                print(f"... ({len(output_text) - 600} more chars truncated)")
            print("--- end model output ---\n")
            print(f"[{_utcnow()}] PASS  model produced {len(output_text)} chars of review text")
            return 0
        else:
            print(f"[{_utcnow()}] WARN  model response completed but output_text is empty", file=sys.stderr)
            return 1

    except Exception as exc:  # noqa: BLE001
        print(f"[{_utcnow()}] FAIL  {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    finally:
        client.close()


if __name__ == "__main__":
    sys.exit(main())
