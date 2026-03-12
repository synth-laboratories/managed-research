"""Approval and question SDK namespace."""

from __future__ import annotations

from managed_research.sdk._base import _ClientNamespace


class ApprovalsAPI(_ClientNamespace):
    def list_questions(
        self, project_id: str, *, status_filter: str | None = None
    ) -> list[dict]:
        return self._client.list_project_questions(project_id, status_filter=status_filter)

    def respond_question(
        self,
        run_id: str,
        question_id: str,
        response_text: str,
        *,
        project_id: str | None = None,
    ) -> dict:
        return self._client.respond_question(
            run_id,
            question_id,
            response_text,
            project_id=project_id,
        )

    def list_project_approvals(
        self, project_id: str, *, status_filter: str | None = None
    ) -> list[dict]:
        return self._client.list_project_approvals(project_id, status_filter=status_filter)

    def resolve(
        self,
        decision: str,
        run_id: str,
        approval_id: str,
        *,
        comment: str | None = None,
        project_id: str | None = None,
    ) -> dict:
        return self._client.resolve_approval(
            decision,
            run_id,
            approval_id,
            comment=comment,
            project_id=project_id,
        )


__all__ = ["ApprovalsAPI"]
