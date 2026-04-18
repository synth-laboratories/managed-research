"""Trained-model registry SDK namespace.

Wraps the ``/smr/trained_models`` and ``/smr/runs/{run_id}/trained_models``
routes. Used by agents to register a Tinker LoRA after training, update its
metrics once offline eval is done, and tear down the adapter (Tinker + Wasabi
+ PG) at end of run.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from managed_research.sdk._base import _ClientNamespace


class TrainedModelsAPI(_ClientNamespace):
    def register(
        self,
        *,
        run_id: str,
        base_model: str,
        method: str,
        tinker_path: str,
        task_id: str | None = None,
        episode_id: str | None = None,
        lora_rank: int | None = None,
        base_metric: float | None = None,
        tuned_metric: float | None = None,
        uplift_abs: float | None = None,
        train_cost_usd: float | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        body = {
            "run_id": run_id,
            "base_model": base_model,
            "method": method,
            "tinker_path": tinker_path,
            "task_id": task_id,
            "episode_id": episode_id,
            "lora_rank": lora_rank,
            "metrics": {
                "base_metric": base_metric,
                "tuned_metric": tuned_metric,
                "uplift_abs": uplift_abs,
            },
            "train_cost_usd": train_cost_usd,
            "metadata": dict(metadata or {}),
        }
        return self._client._request_json("POST", "/smr/trained_models", json_body=body)

    def get(self, model_id: str) -> dict[str, Any]:
        return self._client._request_json("GET", f"/smr/trained_models/{model_id}")

    def list_for_run(self, run_id: str) -> list[dict[str, Any]]:
        result = self._client._request_json(
            "GET", f"/smr/runs/{run_id}/trained_models"
        )
        return list(result) if isinstance(result, list) else []

    def update(
        self,
        model_id: str,
        *,
        tuned_metric: float | None = None,
        uplift_abs: float | None = None,
        train_cost_usd: float | None = None,
        status: str | None = None,
        metadata_patch: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {}
        if tuned_metric is not None:
            body["tuned_metric"] = tuned_metric
        if uplift_abs is not None:
            body["uplift_abs"] = uplift_abs
        if train_cost_usd is not None:
            body["train_cost_usd"] = train_cost_usd
        if status is not None:
            body["status"] = status
        if metadata_patch is not None:
            body["metadata_patch"] = dict(metadata_patch)
        return self._client._request_json(
            "PATCH", f"/smr/trained_models/{model_id}", json_body=body
        )

    def delete(self, model_id: str) -> dict[str, Any]:
        return self._client._request_json(
            "DELETE", f"/smr/trained_models/{model_id}"
        )


__all__ = ["TrainedModelsAPI"]
