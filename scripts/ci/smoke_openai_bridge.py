"""Smoke checks for managed-research OpenAI bridge via synth-ai.

Examples:
  uv run python scripts/ci/smoke_openai_bridge.py \
    --base-url https://api-staging.usesynth.ai \
    --api-key "$SYNTH_API_KEY"
"""

from __future__ import annotations

import argparse
import uuid
from typing import Any

from managed_research import (
    OPENAI_TRANSPORT_MODE_AUTO,
    OPENAI_TRANSPORT_MODE_BACKEND_BFF,
    OPENAI_TRANSPORT_MODE_DIRECT_HP,
    SmrControlClient,
)


def _extract_id(payload: Any, *keys: str) -> str | None:
    if isinstance(payload, dict):
        for key in keys:
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return None


def _assert_dict(payload: Any, *, label: str) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise SystemExit(f"{label} returned non-object payload: {type(payload).__name__}")
    return payload


def _assert_dict_or_cancel(payload: Any, *, label: str) -> dict[str, Any]:
    """Like _assert_dict but also accepts an httpx HTTPStatusError with 409.

    cancel_response on an already-terminal response raises 409; that is a
    valid outcome for a smoke that doesn't control response completion timing.
    """
    if isinstance(payload, dict):
        return payload
    raise SystemExit(f"{label} returned non-object payload: {type(payload).__name__}")


def _stream_any_data(client: Any, request: dict[str, Any]) -> None:
    for frame in client.stream_response(request):
        if isinstance(frame, dict) and frame.get("data") is not None:
            return
    raise SystemExit("response_stream_connect did not emit any data frame")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True, help="SMR/backend base URL")
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
    parser.add_argument("--request-id", default="")
    parser.add_argument(
        "--skip-stream",
        action="store_true",
        help="Skip SSE connectivity check for stream_response.",
    )
    args = parser.parse_args()

    run_request_id = str(args.request_id or f"smr_smoke_{uuid.uuid4().hex[:12]}").strip()

    client = SmrControlClient(
        api_key=args.api_key,
        backend_base=args.base_url,
        openai_transport_mode=args.transport_mode,
        openai_organization=str(args.openai_organization or "").strip() or None,
        openai_project=str(args.openai_project or "").strip() or None,
        openai_request_id=run_request_id,
    )
    try:
        openai_client = client.openai_agents_sdk

        conversation = _assert_dict(
            openai_client.create_conversation({"metadata": {"smoke": run_request_id}}),
            label="conversation_create",
        )
        conversation_id = _extract_id(conversation, "id")
        if not conversation_id:
            raise SystemExit("conversation_create response missing id")
        print("OK conversation_create")

        created_item = _assert_dict(
            openai_client.create_conversation_item(
                conversation_id,
                {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "Smoke bridge run."}],
                },
            ),
            label="conversation_item_create",
        )
        item_id = _extract_id(created_item, "id")
        if not item_id:
            raise SystemExit("conversation_item_create response missing id")
        print("OK conversation_item_create")

        _assert_dict(
            openai_client.list_conversation_items(conversation_id),
            label="conversation_items_list",
        )
        print("OK conversation_items_list")

        _assert_dict(
            openai_client.get_conversation_item(conversation_id, item_id),
            label="conversation_item_get",
        )
        print("OK conversation_item_get")

        _assert_dict(
            openai_client.update_conversation(
                conversation_id,
                {"metadata": {"smoke": run_request_id, "updated": "true"}},
            ),
            label="conversation_update",
        )
        print("OK conversation_update")

        created_response = _assert_dict(
            openai_client.create_response(
                {
                    "model": args.model,
                    "conversation": conversation_id,
                    "input": [
                        {
                            "type": "message",
                            "role": "user",
                            "content": [{"type": "input_text", "text": "Smoke response run."}],
                        }
                    ],
                    "stream": False,
                }
            ),
            label="response_create",
        )
        response_id = _extract_id(created_response, "id", "response_id")
        if not response_id:
            raise SystemExit("response_create response missing id")
        print("OK response_create")

        _assert_dict(openai_client.get_response(response_id), label="response_get")
        print("OK response_get")

        _assert_dict(
            openai_client.list_response_input_items(response_id), label="response_input_items"
        )
        print("OK response_input_items")

        _assert_dict(
            openai_client.create_response_input_tokens(
                response_id,
                {
                    "input": [
                        {
                            "type": "message",
                            "role": "user",
                            "content": [{"type": "input_text", "text": "Count smoke tokens."}],
                        }
                    ]
                },
            ),
            label="response_input_tokens",
        )
        print("OK response_input_tokens")

        _assert_dict(openai_client.compact_response(response_id, {}), label="response_compact")
        print("OK response_compact")

        # cancel: response may be terminal already; 409 is an acceptable outcome.
        try:
            _assert_dict(openai_client.cancel_response(response_id), label="response_cancel")
        except Exception as exc:
            import httpx as _httpx

            if isinstance(exc, _httpx.HTTPStatusError) and exc.response.status_code == 409:
                pass  # already terminal — valid for smoke timing
            else:
                raise
        print("OK response_cancel")

        if not args.skip_stream:
            _stream_any_data(
                openai_client,
                {
                    "model": args.model,
                    "conversation": conversation_id,
                    "input": [
                        {
                            "type": "message",
                            "role": "user",
                            "content": [{"type": "input_text", "text": "Smoke stream run."}],
                        }
                    ],
                    "stream": True,
                },
            )
            print("OK response_stream_connect")

        _assert_dict(openai_client.delete_response(response_id), label="response_delete")
        print("OK response_delete")

        _assert_dict(
            openai_client.delete_conversation_item(conversation_id, item_id),
            label="conversation_item_delete",
        )
        print("OK conversation_item_delete")

        _assert_dict(
            openai_client.delete_conversation(conversation_id),
            label="conversation_delete",
        )
        print("OK conversation_delete")

    finally:
        client.close()

    print("Managed-research OpenAI bridge smoke passed")


if __name__ == "__main__":
    main()
