"""Usage and economics SDK namespace."""

from __future__ import annotations

from typing import Literal

from managed_research.sdk._base import _ClientNamespace


class UsageAPI(_ClientNamespace):
    def get_project_usage(self, project_id: str) -> dict:
        return self._client.get_usage(project_id)

    def get_ops_status(self, project_id: str, *, include_done_tasks: bool = False) -> dict:
        return self._client.get_ops_status(project_id, include_done_tasks=include_done_tasks)

    def get_run_economics(self, run_id: str) -> dict:
        return self._client.get_run_economics(run_id)

    def get_run_economics_typed(self, run_id: str) -> dict:
        return self._client.get_run_economics_typed(run_id)

    def set_execution_preferences(
        self,
        project_id: str,
        *,
        preferred_lane: Literal["auto", "synth_hosted", "user_connected"],
        allow_fallback_to_synth: bool | None = None,
        free_tier_eligible: bool | None = None,
        monthly_soft_limit_tokens: int | None = None,
    ) -> dict:
        return self._client.set_execution_preferences(
            project_id,
            preferred_lane=preferred_lane,
            allow_fallback_to_synth=allow_fallback_to_synth,
            free_tier_eligible=free_tier_eligible,
            monthly_soft_limit_tokens=monthly_soft_limit_tokens,
        )

    def get_capacity_lane_preview(self, project_id: str) -> dict:
        return self._client.get_capacity_lane_preview(project_id)


__all__ = ["UsageAPI"]
