"""Run-scoped SDK namespace."""

from __future__ import annotations

from typing import Any

from managed_research.models.run_observability import (
    RunObservationCursor,
    RunObservabilitySnapshot,
)
from managed_research.models.run_timeline import (
    SmrBranchMode,
    SmrLogicalTimeline,
    SmrRunBranchResponse,
)
from managed_research.models.canonical_usage import SmrRunUsage
from managed_research.models.run_diagnostics import (
    SmrRunActorUsage,
    SmrRunTraces,
)
from managed_research.sdk._base import _ClientNamespace


class RunsAPI(_ClientNamespace):
    def trigger(self, project_id: str, **kwargs: Any) -> dict[str, Any]:
        return self._client.trigger_run(project_id, **kwargs)

    def list(self, project_id: str, *, active_only: bool = False, **kwargs: Any) -> list[dict[str, Any]]:
        return self._client.list_runs(project_id, active_only=active_only, **kwargs)

    def list_active(self, project_id: str) -> list[dict[str, Any]]:
        return self._client.list_active_runs(project_id)

    def get(self, run_id: str, *, project_id: str | None = None) -> dict[str, Any]:
        return self._client.get_run(run_id, project_id=project_id)

    def get_usage(self, run_id: str) -> SmrRunUsage:
        return self._client.get_run_usage(run_id)

    def get_observability_snapshot(
        self,
        project_id: str,
        run_id: str,
        *,
        event_limit: int = 100,
        actor_limit: int = 25,
        task_limit: int = 50,
        question_limit: int = 25,
        timeline_limit: int = 10,
        message_limit: int = 10,
    ) -> RunObservabilitySnapshot:
        return self._client.get_run_observability_snapshot(
            project_id,
            run_id,
            event_limit=event_limit,
            actor_limit=actor_limit,
            task_limit=task_limit,
            question_limit=question_limit,
            timeline_limit=timeline_limit,
            message_limit=message_limit,
        )

    def poll_observability_snapshot(
        self,
        project_id: str,
        run_id: str,
        *,
        cursor: RunObservationCursor | dict[str, Any] | None = None,
        event_limit: int = 100,
        actor_limit: int = 25,
        task_limit: int = 50,
        question_limit: int = 25,
        timeline_limit: int = 10,
        message_limit: int = 10,
    ) -> RunObservabilitySnapshot:
        return self._client.poll_run_observability_snapshot(
            project_id,
            run_id,
            cursor=cursor,
            event_limit=event_limit,
            actor_limit=actor_limit,
            task_limit=task_limit,
            question_limit=question_limit,
            timeline_limit=timeline_limit,
            message_limit=message_limit,
        )

    def get_actor_counts(self, project_id: str, run_id: str) -> dict[str, int]:
        return self.get_observability_snapshot(project_id, run_id).actors.counts_by_state

    def get_task_counts(self, project_id: str, run_id: str) -> dict[str, int]:
        return self.get_observability_snapshot(project_id, run_id).tasks.counts_by_state

    def get_terminal_classifier(self, project_id: str, run_id: str) -> str:
        snapshot = self.get_observability_snapshot(project_id, run_id)
        authority_phase = snapshot.lifecycle.authority_phase.strip().lower()
        if authority_phase in {"accepted", "bootstrapping", "ready", "running", "terminalizing"}:
            return "active"
        publication = snapshot.candidate_publication.outcome
        if publication.value == "pr_published":
            return "pr_published"
        if publication.value == "awaiting_pr_binding":
            return "awaiting_pr"
        return snapshot.run_state

    def get_primary_parent(self, run_id: str) -> dict[str, Any]:
        return self._client.get_run_primary_parent(run_id)

    def list_primary_parent_milestones(
        self, run_id: str, *, limit: int | None = None
    ) -> list[dict[str, Any]]:
        return self._client.list_run_primary_parent_milestones(run_id, limit=limit)

    def stop(self, run_id: str, *, project_id: str | None = None) -> dict[str, Any]:
        return self._client.stop_run(run_id, project_id=project_id)

    def pause(self, run_id: str, *, project_id: str | None = None) -> dict[str, Any]:
        return self._client.pause_run(run_id, project_id=project_id)

    def resume(self, run_id: str, *, project_id: str | None = None) -> dict[str, Any]:
        return self._client.resume_run(run_id, project_id=project_id)

    def list_questions(self, run_id: str, *, project_id: str | None = None, **kwargs: Any) -> list[dict[str, Any]]:
        return self._client.list_run_questions(run_id, project_id=project_id, **kwargs)

    def respond_to_question(
        self,
        run_id: str,
        question_id: str,
        *,
        response_text: str,
        project_id: str | None = None,
    ) -> dict[str, Any]:
        return self._client.respond_to_run_question(
            run_id,
            question_id,
            project_id=project_id,
            response_text=response_text,
        )

    def create_checkpoint(self, run_id: str, *, project_id: str | None = None, **kwargs: Any) -> dict[str, Any]:
        return self._client.create_run_checkpoint(run_id, project_id=project_id, **kwargs)

    def list_checkpoints(self, run_id: str, *, project_id: str | None = None) -> list[dict[str, Any]]:
        return self._client.list_run_checkpoints(run_id, project_id=project_id)

    def restore_checkpoint(self, run_id: str, *, project_id: str | None = None, **kwargs: Any) -> dict[str, Any]:
        return self._client.restore_run_checkpoint(run_id, project_id=project_id, **kwargs)

    def get_logical_timeline(self, project_id: str, run_id: str) -> SmrLogicalTimeline:
        return self._client.get_run_logical_timeline(project_id, run_id)

    def get_traces(
        self,
        run_id: str,
        *,
        project_id: str | None = None,
    ) -> SmrRunTraces:
        if project_id:
            return self._client.get_project_run_traces(project_id, run_id)
        return self._client.get_run_traces(run_id)

    def get_actor_usage(
        self,
        run_id: str,
        *,
        project_id: str | None = None,
    ) -> SmrRunActorUsage:
        if project_id:
            return self._client.get_project_run_actor_usage(project_id, run_id)
        return self._client.get_run_actor_usage(run_id)

    def branch_from_checkpoint(
        self,
        run_id: str | None = None,
        *,
        project_id: str | None = None,
        checkpoint_id: str | None = None,
        checkpoint_record_id: str | None = None,
        checkpoint_uri: str | None = None,
        mode: SmrBranchMode | str = SmrBranchMode.EXACT,
        message: str | None = None,
        reason: str | None = None,
        title: str | None = None,
        source_node_id: str | None = None,
    ) -> SmrRunBranchResponse:
        return self._client.branch_run_from_checkpoint(
            run_id,
            project_id=project_id,
            checkpoint_id=checkpoint_id,
            checkpoint_record_id=checkpoint_record_id,
            checkpoint_uri=checkpoint_uri,
            mode=mode,
            message=message,
            reason=reason,
            title=title,
            source_node_id=source_node_id,
        )

    def list_runtime_messages(
        self,
        run_id: str,
        *,
        status: str | None = None,
        viewer_role: str | None = None,
        viewer_target: str | list[str] | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        return self._client.list_runtime_messages(
            run_id,
            status=status,
            viewer_role=viewer_role,
            viewer_target=viewer_target,
            limit=limit,
        )

    def enqueue_runtime_message(self, run_id: str, **kwargs: Any) -> dict[str, Any]:
        return self._client.enqueue_runtime_message(run_id, **kwargs)


__all__ = ["RunsAPI"]
