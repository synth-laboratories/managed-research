"""MCP tool definitions for the trained-model registry."""

from __future__ import annotations

from typing import Any

from managed_research.mcp.registry import ToolDefinition, tool_schema


def build_trained_model_tools(server: Any) -> list[ToolDefinition]:
    return [
        ToolDefinition(
            name="smr_register_trained_model",
            description=(
                "Register a Tinker-trained LoRA adapter produced by the current SMR "
                "run. This downloads the adapter from Tinker, uploads it to Wasabi, "
                "and inserts an ``smr_models`` registry row so the adapter can be "
                "rehydrated for offline evaluation and cleaned up at end of run."
            ),
            input_schema=tool_schema(
                {
                    "run_id": {"type": "string", "description": "SMR run identifier."},
                    "base_model": {
                        "type": "string",
                        "description": "Base model name, e.g. 'meta-llama/Llama-3.2-1B'.",
                    },
                    "method": {
                        "type": "string",
                        "description": "Training method id: 'dpo', 'sft', 'rlvr', etc.",
                    },
                    "tinker_path": {
                        "type": "string",
                        "description": "tinker:// URI returned by save_weights_for_sampler.",
                    },
                    "task_id": {"type": "string"},
                    "episode_id": {"type": "string"},
                    "lora_rank": {"type": "integer"},
                    "base_metric": {"type": "number"},
                    "tuned_metric": {"type": "number"},
                    "uplift_abs": {"type": "number"},
                    "train_cost_usd": {"type": "number"},
                    "metadata": {
                        "type": "object",
                        "description": "Free-form training hyperparameters.",
                    },
                },
                required=["run_id", "base_model", "method", "tinker_path"],
            ),
            handler=server._tool_register_trained_model,
        ),
        ToolDefinition(
            name="smr_get_trained_model",
            description="Fetch a trained-model registry record by id.",
            input_schema=tool_schema(
                {"model_id": {"type": "string"}},
                required=["model_id"],
            ),
            handler=server._tool_get_trained_model,
        ),
        ToolDefinition(
            name="smr_list_trained_models_for_run",
            description="List trained models registered for a given SMR run.",
            input_schema=tool_schema(
                {"run_id": {"type": "string"}},
                required=["run_id"],
            ),
            handler=server._tool_list_trained_models_for_run,
        ),
        ToolDefinition(
            name="smr_update_trained_model",
            description=(
                "Patch metrics on a trained-model record — typically called after "
                "offline eval completes with the replayed tuned accuracy."
            ),
            input_schema=tool_schema(
                {
                    "model_id": {"type": "string"},
                    "tuned_metric": {"type": "number"},
                    "uplift_abs": {"type": "number"},
                    "train_cost_usd": {"type": "number"},
                    "status": {
                        "type": "string",
                        "enum": ["registered", "evaluated", "deleted"],
                    },
                    "metadata_patch": {"type": "object"},
                },
                required=["model_id"],
            ),
            handler=server._tool_update_trained_model,
        ),
        ToolDefinition(
            name="smr_delete_trained_model",
            description=(
                "Delete a trained-model record: removes the Tinker checkpoint, the "
                "Wasabi object, and soft-deletes the ``smr_models`` row. Call this "
                "at the end of the run after offline evaluation confirms the score."
            ),
            input_schema=tool_schema(
                {"model_id": {"type": "string"}},
                required=["model_id"],
            ),
            handler=server._tool_delete_trained_model,
        ),
        ToolDefinition(
            name="smr_get_run_cost_summary",
            description=(
                "Return the per-run cost summary, broken down by meter_kind "
                "(tinker_training_job, token_input, sandbox_seconds, etc.)."
            ),
            input_schema=tool_schema(
                {"run_id": {"type": "string"}},
                required=["run_id"],
            ),
            handler=server._tool_get_run_cost_summary,
        ),
    ]


__all__ = ["build_trained_model_tools"]
