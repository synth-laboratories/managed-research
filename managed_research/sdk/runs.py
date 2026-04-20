"""Run-scoped SDK namespace."""

from __future__ import annotations

import time
from typing import Any

from managed_research.models.checkpoints import Checkpoint
from managed_research.models.canonical_usage import SmrRunUsage
from managed_research.models.run_control import ManagedResearchRunControlAck
from managed_research.models.run_diagnostics import (
    SmrRunActorUsage,
    SmrRunTraces,
)
from managed_research.models.run_observability import (
    RunObservabilitySnapshot,
    RunObservationCursor,
)
from managed_research.models.run_state import ManagedResearchRun
from managed_research.models.run_timeline import (
    SmrBranchMode,
    SmrLogicalTimeline,
    SmrRunBranchResponse,
)
from managed_research.models.runtime_intent import (
    RuntimeIntent,
    RuntimeIntentReceipt,
    RuntimeIntentView,
)
from managed_research.models.smr_host_kinds import SmrHostKind
from managed_research.models.smr_network_topology import SmrNetworkTopology
from managed_research.models.smr_providers import (
    ProviderBinding,
    ProviderCapability,
    UsageLimit,
)
from managed_research.models.smr_work_modes import SmrWorkMode
from managed_research.models.types import RunArtifact, RunArtifactManifest
from managed_research.sdk._base import _ClientNamespace


class RunHandle:
    """Project-scoped handle for one managed-research run."""

    def __init__(self, client: Any, project_id: str, run_id: str) -> None:
        project_text = str(project_id or "").strip()
        run_text = str(run_id or "").strip()
        if not project_text:
            raise ValueError("project_id is required")
        if not run_text:
            raise ValueError("run_id is required")
        self._client = client
        self.project_id = project_text
        self.run_id = run_text

    def get(self) -> ManagedResearchRun:
        return ManagedResearchRun.from_wire(
            self._client.get_project_run(self.project_id, self.run_id)
        )

    def wait(
        self,
        *,
        timeout: float | None = None,
        poll_interval: float = 10.0,
    ) -> ManagedResearchRun:
        if poll_interval <= 0:
            raise ValueError("poll_interval must be greater than 0")
        if timeout is not None and timeout < 0:
            raise ValueError("timeout must be non-negative when provided")
        deadline = time.monotonic() + timeout if timeout is not None else None
        while True:
            run = self.get()
            if run.state.is_terminal:
                return run
            if deadline is not None and time.monotonic() >= deadline:
                raise TimeoutError(
                    f"run {self.run_id} did not complete within {timeout}s"
                )
            time.sleep(poll_interval)

    @property
    def host_kind(self) -> SmrHostKind | None:
        return self.get().host_kind

    @property
    def resolved_host_kind(self) -> SmrHostKind | None:
        return self.get().resolved_host_kind

    @property
    def work_mode(self) -> SmrWorkMode | None:
        return self.get().work_mode

    @property
    def resolved_work_mode(self) -> SmrWorkMode | None:
        return self.get().resolved_work_mode

    @property
    def runbook(self) -> str | None:
        return self.get().runbook

    @property
    def network_topology(self) -> SmrNetworkTopology | None:
        return self.get().network_topology

    @property
    def network_surfaces(self) -> dict[str, object]:
        return self.get().network_surfaces

    @property
    def providers(self) -> tuple[ProviderBinding, ...]:
        return self.get().providers

    @property
    def capabilities(self) -> frozenset[ProviderCapability]:
        return self.get().capabilities

    @property
    def limit(self) -> UsageLimit | None:
        return self.get().limit

    def task_counts(self) -> dict[str, int]:
        return self._client.get_run_observability_snapshot(
            self.project_id,
            self.run_id,
        ).tasks.counts_by_state

    def actor_counts(self) -> dict[str, int]:
        return self._client.get_run_observability_snapshot(
            self.project_id,
            self.run_id,
        ).actors.counts_by_state

    def messages(
        self,
        *,
        status: str | None = None,
        viewer_role: str | None = None,
        viewer_target: str | list[str] | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        return self._client.list_project_run_runtime_messages(
            self.project_id,
            self.run_id,
            status=status,
            viewer_role=viewer_role,
            viewer_target=viewer_target,
            limit=limit,
        )

    def submit_intent(
        self,
        intent: RuntimeIntent | dict[str, Any],
        *,
        mode: str = "queue",
        body: str | None = None,
        causation_id: str | None = None,
    ) -> RuntimeIntentReceipt:
        return self._client.submit_runtime_intent(
            self.run_id,
            intent,
            project_id=self.project_id,
            mode=mode,
            body=body,
            causation_id=causation_id,
        )

    def intents(
        self,
        *,
        status: str | None = None,
        limit: int | None = None,
    ) -> list[RuntimeIntentView]:
        return self._client.list_runtime_intents(
            self.run_id,
            project_id=self.project_id,
            status=status,
            limit=limit,
        )

    def intent(self, runtime_intent_id: str) -> RuntimeIntentView:
        return self._client.get_runtime_intent(
            self.run_id,
            runtime_intent_id,
            project_id=self.project_id,
        )

    def timeline(self) -> SmrLogicalTimeline:
        return self._client.get_run_logical_timeline(self.project_id, self.run_id)

    def traces(self) -> SmrRunTraces:
        return self._client.get_project_run_traces(self.project_id, self.run_id)

    def actor_usage(self) -> SmrRunActorUsage:
        return self._client.get_project_run_actor_usage(self.project_id, self.run_id)

    def checkpoints(self) -> list[Checkpoint]:
        return self._client.list_run_checkpoints(
            self.run_id,
            project_id=self.project_id,
        )

    def checkpoint(self, checkpoint_id: str) -> Checkpoint:
        return self._client.get_run_checkpoint(
            self.run_id,
            checkpoint_id,
            project_id=self.project_id,
        )

    def create_checkpoint(
        self,
        *,
        checkpoint_id: str | None = None,
        reason: str | None = None,
        timeout_seconds: float = 120.0,
        poll_interval_seconds: float = 1.0,
    ) -> Checkpoint:
        return self._client.create_run_checkpoint(
            self.run_id,
            project_id=self.project_id,
            checkpoint_id=checkpoint_id,
            reason=reason,
            timeout_seconds=timeout_seconds,
            poll_interval_seconds=poll_interval_seconds,
        )

    def request_checkpoint(
        self,
        *,
        checkpoint_id: str | None = None,
        reason: str | None = None,
    ) -> dict[str, Any]:
        return self._client.request_run_checkpoint(
            self.run_id,
            project_id=self.project_id,
            checkpoint_id=checkpoint_id,
            reason=reason,
        )

    def restore_checkpoint(
        self,
        *,
        checkpoint_id: str | None = None,
        checkpoint_record_id: str | None = None,
        checkpoint_uri: str | None = None,
        reason: str | None = None,
        mode: str = "in_place",
    ) -> dict[str, Any]:
        return self._client.restore_run_checkpoint(
            self.run_id,
            project_id=self.project_id,
            checkpoint_id=checkpoint_id,
            checkpoint_record_id=checkpoint_record_id,
            checkpoint_uri=checkpoint_uri,
            reason=reason,
            mode=mode,
        )

    def branch_from_checkpoint(
        self,
        *,
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
            self.run_id,
            project_id=self.project_id,
            checkpoint_id=checkpoint_id,
            checkpoint_record_id=checkpoint_record_id,
            checkpoint_uri=checkpoint_uri,
            mode=mode,
            message=message,
            reason=reason,
            title=title,
            source_node_id=source_node_id,
        )

    def artifact_manifest(self) -> RunArtifactManifest:
        return self._client.get_run_artifact_manifest(
            self.run_id,
            project_id=self.project_id,
        )

    def artifacts(
        self,
        *,
        artifact_type: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> list[RunArtifact]:
        return self._client.list_run_artifacts(
            self.run_id,
            project_id=self.project_id,
            artifact_type=artifact_type,
            limit=limit,
            cursor=cursor,
        )

    def output_file(self, name: str) -> RunArtifact | None:
        wanted = str(name or "").strip().lower()
        if not wanted:
            raise ValueError("name is required")
        for artifact in self.artifact_manifest().output_files:
            candidates = {
                artifact.artifact_id,
                artifact.artifact_type,
                artifact.title,
                artifact.path,
            }
            if artifact.path:
                candidates.add(artifact.path.rsplit("/", 1)[-1])
            if any(str(candidate or "").strip().lower() == wanted for candidate in candidates):
                return artifact
        return None

    def download(self, path: str) -> dict[str, Any]:
        return self._client.download_run_workspace_archive(
            self.project_id,
            self.run_id,
            path,
        )

    def models(self) -> list[dict[str, Any]]:
        return self._client.list_run_models(self.run_id, project_id=self.project_id)

    def datasets(self) -> list[dict[str, Any]]:
        return self._client.list_run_datasets(self.run_id, project_id=self.project_id)

    def stop(self) -> ManagedResearchRunControlAck:
        return ManagedResearchRunControlAck.from_wire(
            self._client.stop_run(self.run_id, project_id=self.project_id)
        )

    def pause(self) -> ManagedResearchRunControlAck:
        return ManagedResearchRunControlAck.from_wire(
            self._client.pause_run(self.run_id, project_id=self.project_id)
        )

    def resume(self) -> ManagedResearchRunControlAck:
        return ManagedResearchRunControlAck.from_wire(
            self._client.resume_run(self.run_id, project_id=self.project_id)
        )


class RunsAPI(_ClientNamespace):
    def _handle(self, project_id: str, run_id: str) -> RunHandle:
        return RunHandle(self._client, project_id, run_id)

    def trigger(self, project_id: str, **kwargs: Any) -> dict[str, Any]:
        return self._client.trigger_run(project_id, **kwargs)

    def start(
        self,
        objective: str,
        *,
        project_id: str | None = None,
        **kwargs: Any,
    ) -> RunHandle:
        objective_text = str(objective or "").strip()
        if not objective_text:
            raise ValueError("objective is required")
        initial_runtime_messages = list(kwargs.pop("initial_runtime_messages", ()) or ())
        initial_runtime_messages.append({"body": objective_text, "mode": "queue"})
        payload = dict(kwargs)
        payload["initial_runtime_messages"] = initial_runtime_messages
        if project_id is None:
            wire = self._client.trigger_one_off_run(**payload)
        else:
            wire = self._client.trigger_run(project_id, **payload)
        run = ManagedResearchRun.from_wire(wire)
        return RunHandle(self._client, run.project_id, run.run_id)

    def launch(
        self,
        objective: str,
        *,
        project_id: str | None = None,
        **kwargs: Any,
    ) -> RunHandle:
        return self.start(objective, project_id=project_id, **kwargs)

    def list(
        self, project_id: str, *, active_only: bool = False, **kwargs: Any
    ) -> list[dict[str, Any]]:
        return self._client.list_runs(project_id, active_only=active_only, **kwargs)

    def list_active(self, project_id: str) -> list[dict[str, Any]]:
        return self._client.list_active_runs(project_id)

    def get(self, run_id: str, *, project_id: str | None = None) -> ManagedResearchRun:
        return ManagedResearchRun.from_wire(self._client.get_run(run_id, project_id=project_id))

    def wait(
        self,
        project_id: str,
        run_id: str,
        *,
        timeout: float | None = None,
        poll_interval: float = 10.0,
    ) -> ManagedResearchRun:
        return self._handle(project_id, run_id).wait(
            timeout=timeout,
            poll_interval=poll_interval,
        )

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
        return snapshot.run_state.value

    def get_primary_parent(self, run_id: str) -> dict[str, Any]:
        return self._client.get_run_primary_parent(run_id)

    def list_primary_parent_milestones(
        self, run_id: str, *, limit: int | None = None
    ) -> list[dict[str, Any]]:
        return self._client.list_run_primary_parent_milestones(run_id, limit=limit)

    def stop(self, run_id: str, *, project_id: str | None = None) -> ManagedResearchRunControlAck:
        return ManagedResearchRunControlAck.from_wire(
            self._client.stop_run(run_id, project_id=project_id)
        )

    def pause(self, run_id: str, *, project_id: str | None = None) -> ManagedResearchRunControlAck:
        return ManagedResearchRunControlAck.from_wire(
            self._client.pause_run(run_id, project_id=project_id)
        )

    def resume(self, run_id: str, *, project_id: str | None = None) -> ManagedResearchRunControlAck:
        return ManagedResearchRunControlAck.from_wire(
            self._client.resume_run(run_id, project_id=project_id)
        )

    def submit_intent(
        self,
        run_id: str,
        intent: RuntimeIntent | dict[str, Any],
        *,
        project_id: str | None = None,
        mode: str = "queue",
        body: str | None = None,
        causation_id: str | None = None,
    ) -> RuntimeIntentReceipt:
        return self._client.submit_runtime_intent(
            run_id,
            intent,
            project_id=project_id,
            mode=mode,
            body=body,
            causation_id=causation_id,
        )

    def intents(
        self,
        run_id: str,
        *,
        project_id: str | None = None,
        status: str | None = None,
        limit: int | None = None,
    ) -> list[RuntimeIntentView]:
        return self._client.list_runtime_intents(
            run_id,
            project_id=project_id,
            status=status,
            limit=limit,
        )

    def intent(
        self,
        run_id: str,
        runtime_intent_id: str,
        *,
        project_id: str | None = None,
    ) -> RuntimeIntentView:
        return self._client.get_runtime_intent(
            run_id,
            runtime_intent_id,
            project_id=project_id,
        )

    def list_questions(
        self, run_id: str, *, project_id: str | None = None, **kwargs: Any
    ) -> list[dict[str, Any]]:
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

    def create_checkpoint(
        self, run_id: str, *, project_id: str | None = None, **kwargs: Any
    ) -> Checkpoint:
        return self._client.create_run_checkpoint(run_id, project_id=project_id, **kwargs)

    def list_checkpoints(
        self, run_id: str, *, project_id: str | None = None
    ) -> list[Checkpoint]:
        return self._client.list_run_checkpoints(run_id, project_id=project_id)

    def checkpoint(
        self,
        run_id: str,
        checkpoint_id: str,
        *,
        project_id: str | None = None,
    ) -> Checkpoint:
        return self._client.get_run_checkpoint(
            run_id,
            checkpoint_id,
            project_id=project_id,
        )

    def request_checkpoint(
        self,
        run_id: str,
        *,
        project_id: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        return self._client.request_run_checkpoint(run_id, project_id=project_id, **kwargs)

    def artifact_manifest(
        self,
        run_id: str,
        *,
        project_id: str | None = None,
    ) -> RunArtifactManifest:
        return self._client.get_run_artifact_manifest(run_id, project_id=project_id)

    def artifacts(
        self,
        run_id: str,
        *,
        project_id: str | None = None,
        artifact_type: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> list[RunArtifact]:
        return self._client.list_run_artifacts(
            run_id,
            project_id=project_id,
            artifact_type=artifact_type,
            limit=limit,
            cursor=cursor,
        )

    def output_file(
        self,
        run_id: str,
        name: str,
        *,
        project_id: str | None = None,
    ) -> RunArtifact | None:
        wanted = str(name or "").strip().lower()
        if not wanted:
            raise ValueError("name is required")
        for artifact in self.artifact_manifest(
            run_id,
            project_id=project_id,
        ).output_files:
            candidates = {
                artifact.artifact_id,
                artifact.artifact_type,
                artifact.title,
                artifact.path,
            }
            if artifact.path:
                candidates.add(artifact.path.rsplit("/", 1)[-1])
            if any(str(candidate or "").strip().lower() == wanted for candidate in candidates):
                return artifact
        return None

    def download(
        self,
        project_id: str,
        run_id: str,
        path: str,
    ) -> dict[str, Any]:
        return self._client.download_run_workspace_archive(project_id, run_id, path)

    def models(
        self,
        run_id: str,
        *,
        project_id: str | None = None,
    ) -> list[dict[str, Any]]:
        return self._client.list_run_models(run_id, project_id=project_id)

    def datasets(
        self,
        run_id: str,
        *,
        project_id: str | None = None,
    ) -> list[dict[str, Any]]:
        return self._client.list_run_datasets(run_id, project_id=project_id)

    def restore_checkpoint(
        self, run_id: str, *, project_id: str | None = None, **kwargs: Any
    ) -> dict[str, Any]:
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


__all__ = ["RunHandle", "RunsAPI"]
