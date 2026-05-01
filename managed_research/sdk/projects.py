"""Project-scoped SDK namespace."""

from __future__ import annotations

from typing import Any

from managed_research.models.canonical_usage import (
    BillingEntitlementSnapshot,
    SmrProjectEconomics,
    SmrProjectUsage,
)
from managed_research.models.project import CreateRunnableResult, ManagedResearchProject
from managed_research.models.project_workspace import ProjectWorkspaceProjection
from managed_research.models.types import (
    ProviderKeyStatus,
    SmrLaunchPreflight,
    SmrProjectSetup,
    SmrRunnableProjectRequest,
)
from managed_research.sdk._base import _ClientNamespace
from managed_research.sdk.project import ManagedResearchProjectClient


class ProjectsAPI(_ClientNamespace):
    def create_runnable(
        self,
        request: SmrRunnableProjectRequest | dict[str, Any],
    ) -> CreateRunnableResult:
        return CreateRunnableResult.from_wire(self._client.create_runnable_project(request))

    def list(
        self, *, include_archived: bool = False, limit: int = 100
    ) -> list[ManagedResearchProject]:
        return [
            ManagedResearchProject.from_wire(item)
            for item in self._client.list_projects(
                include_archived=include_archived,
                limit=limit,
            )
        ]

    def get(self, project_id: str) -> ManagedResearchProject:
        return ManagedResearchProject.from_wire(self._client.get_project(project_id))

    def get_schedule(self, project_id: str) -> dict[str, Any]:
        return self.get(project_id).schedule

    def update_schedule(
        self,
        project_id: str,
        schedule: dict[str, Any],
    ) -> ManagedResearchProject:
        return ManagedResearchProject.from_wire(
            self._client.update_project_schedule(project_id, schedule)
        )

    def default(self) -> ManagedResearchProjectClient:
        payload = self._client.get_default_project()
        project = ManagedResearchProject.from_wire(payload)
        return ManagedResearchProjectClient(self._client, project.project_id)

    def patch(self, project_id: str, payload: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        return self._client.patch_project(project_id, payload, **kwargs)

    def rename(self, project_id: str, name: str) -> dict[str, Any]:
        return self._client.rename_project(project_id, name)

    def pause(self, project_id: str) -> dict[str, Any]:
        return self._client.pause_project(project_id)

    def resume(self, project_id: str) -> dict[str, Any]:
        return self._client.resume_project(project_id)

    def archive(self, project_id: str) -> dict[str, Any]:
        return self._client.archive_project(project_id)

    def unarchive(self, project_id: str) -> dict[str, Any]:
        return self._client.unarchive_project(project_id)

    def get_notes(self, project_id: str) -> dict[str, Any]:
        return self._client.get_project_notes(project_id)

    def set_notes(self, project_id: str, notes: str) -> dict[str, Any]:
        return self._client.set_project_notes(project_id, notes)

    def append_notes(self, project_id: str, notes: str) -> dict[str, Any]:
        return self._client.append_project_notes(project_id, notes)

    def get_knowledge(self, project_id: str) -> dict[str, Any]:
        return self._client.get_project_knowledge(project_id)

    def set_knowledge(self, project_id: str, content: str) -> dict[str, Any]:
        return self._client.set_project_knowledge(project_id, content)

    def get_status(self, project_id: str) -> dict[str, Any]:
        return self._client.get_project_status(project_id)

    def get_status_snapshot(self, project_id: str) -> dict[str, Any]:
        return self._client.get_project_status_snapshot(project_id)

    def get_workspace(self, project_id: str) -> ProjectWorkspaceProjection:
        return ProjectWorkspaceProjection.from_wire(
            self._client.get_project_workspace(project_id)
        )

    def list_changesets(
        self,
        project_id: str,
        *,
        status: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        return self._client.list_project_changesets(
            project_id,
            status=status,
            limit=limit,
        )

    def create_changeset(
        self,
        project_id: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        return self._client.create_project_changeset(project_id, payload)

    def get_changeset(
        self,
        project_id: str,
        changeset_id: str,
    ) -> dict[str, Any]:
        return self._client.get_project_changeset(project_id, changeset_id)

    def decide_changeset(
        self,
        project_id: str,
        changeset_id: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        return self._client.decide_project_changeset(
            project_id,
            changeset_id,
            payload,
        )

    def get_entitlement(self, project_id: str) -> dict[str, Any]:
        return self._client.get_project_entitlement(project_id)

    def get_usage(self, project_id: str) -> SmrProjectUsage:
        return self._client.get_project_usage(project_id)

    def get_economics(self, project_id: str) -> SmrProjectEconomics:
        return self._client.get_project_economics(project_id)

    def get_billing_entitlements(self) -> BillingEntitlementSnapshot:
        return self._client.get_billing_entitlements()

    def get_capabilities(self) -> dict[str, Any]:
        return self._client.get_capabilities()

    def get_agent_models(self) -> dict[str, Any]:
        return self._client.get_agent_models()

    def get_limits(self) -> dict[str, Any]:
        return self._client.get_limits()

    def get_capacity_lane_preview(self, project_id: str) -> dict[str, Any]:
        return self._client.get_capacity_lane_preview(project_id)

    def get_workspace_download_url(self, project_id: str) -> dict[str, Any]:
        return self._client.get_workspace_download_url(project_id)

    def get_git(self, project_id: str) -> dict[str, Any]:
        return self._client.get_project_git(project_id)

    def get_setup(self, project_id: str) -> SmrProjectSetup:
        return SmrProjectSetup.from_wire(self._client.get_project_setup(project_id))

    def get_setup_authority(self, project_id: str) -> SmrProjectSetup:
        return SmrProjectSetup.from_wire(
            self._client.get_project_setup_authority(project_id)
        )

    def prepare_setup(self, project_id: str) -> SmrProjectSetup:
        return SmrProjectSetup.from_wire(
            self._client.prepare_project_setup(project_id)
        )

    def prepare_setup_authority(self, project_id: str) -> SmrProjectSetup:
        return SmrProjectSetup.from_wire(
            self._client.prepare_project_setup_authority(project_id)
        )

    def get_launch_preflight(self, project_id: str, **kwargs: Any) -> SmrLaunchPreflight:
        return SmrLaunchPreflight.from_wire(
            self._client.get_launch_preflight(project_id, **kwargs)
        )

    def get_run_start_blockers(self, project_id: str, **kwargs: Any) -> SmrLaunchPreflight:
        """Backward-compatible alias for launch preflight readiness checks."""

        return self.get_launch_preflight(project_id, **kwargs)

    def list_open_ended_questions(
        self, project_id: str, *, run_id: str | None = None, limit: int | None = None
    ) -> list[dict[str, Any]]:
        return self._client.list_open_ended_questions(
            project_id, run_id=run_id, limit=limit
        )

    def create_open_ended_question(
        self, project_id: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        return self._client.create_open_ended_question(project_id, payload)

    def get_open_ended_question(self, project_id: str, objective_id: str) -> dict[str, Any]:
        return self._client.get_open_ended_question(project_id, objective_id)

    def patch_open_ended_question(
        self, project_id: str, objective_id: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        return self._client.patch_open_ended_question(project_id, objective_id, payload)

    def transition_open_ended_question(
        self, project_id: str, objective_id: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        return self._client.transition_open_ended_question(
            project_id, objective_id, payload
        )

    def list_directed_effort_outcomes(
        self, project_id: str, *, run_id: str | None = None, limit: int | None = None
    ) -> list[dict[str, Any]]:
        return self._client.list_directed_effort_outcomes(
            project_id, run_id=run_id, limit=limit
        )

    def create_directed_effort_outcome(
        self, project_id: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        return self._client.create_directed_effort_outcome(project_id, payload)

    def get_directed_effort_outcome(
        self, project_id: str, objective_id: str
    ) -> dict[str, Any]:
        return self._client.get_directed_effort_outcome(project_id, objective_id)

    def patch_directed_effort_outcome(
        self, project_id: str, objective_id: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        return self._client.patch_directed_effort_outcome(
            project_id, objective_id, payload
        )

    def transition_directed_effort_outcome(
        self, project_id: str, objective_id: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        return self._client.transition_directed_effort_outcome(
            project_id, objective_id, payload
        )

    def list_milestones(
        self,
        project_id: str,
        *,
        run_id: str | None = None,
        parent_kind: str | None = None,
        parent_id: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        return self._client.list_project_milestones(
            project_id,
            run_id=run_id,
            parent_kind=parent_kind,
            parent_id=parent_id,
            limit=limit,
        )

    def get_milestone(self, project_id: str, milestone_id: str) -> dict[str, Any]:
        return self._client.get_project_milestone(project_id, milestone_id)

    def list_experiments(
        self,
        project_id: str,
        *,
        run_id: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        return self._client.list_project_experiments(
            project_id,
            run_id=run_id,
            limit=limit,
        )

    def get_experiment(self, project_id: str, experiment_id: str) -> dict[str, Any]:
        return self._client.get_project_experiment(project_id, experiment_id)

    def set_provider_key(self, project_id: str, **kwargs: Any) -> ProviderKeyStatus:
        return ProviderKeyStatus.from_wire(
            self._client.set_provider_key(project_id, **kwargs)
        )

    def get_provider_key_status(self, project_id: str, **kwargs: Any) -> ProviderKeyStatus:
        return ProviderKeyStatus.from_wire(
            self._client.get_provider_key_status(project_id, **kwargs)
        )

    def download_workspace_archive(
        self,
        project_id: str,
        output_path: str,
        *,
        timeout_seconds: float | None = None,
    ) -> dict[str, Any]:
        if timeout_seconds is not None:
            return self._client.download_workspace_archive(
                project_id,
                output_path,
                timeout_seconds=timeout_seconds,
            )
        return self._client.download_workspace_archive(project_id, output_path)


__all__ = ["ProjectsAPI"]
