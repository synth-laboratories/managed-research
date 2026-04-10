"""Project-setup SDK namespace."""

from __future__ import annotations

from managed_research.models.types import SmrProjectSetup
from managed_research.sdk._base import _ClientNamespace


class SetupAPI(_ClientNamespace):
    def get(self, project_id: str) -> SmrProjectSetup:
        return SmrProjectSetup.from_wire(self._client.get_project_setup(project_id))

    def prepare(self, project_id: str) -> SmrProjectSetup:
        return SmrProjectSetup.from_wire(
            self._client.prepare_project_setup(project_id)
        )


__all__ = ["SetupAPI"]
