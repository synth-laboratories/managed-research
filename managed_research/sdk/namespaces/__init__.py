"""Namespace authorities for the Managed Research SDK."""

from managed_research.sdk.approvals import ApprovalsAPI
from managed_research.sdk.cost import RunCostAPI
from managed_research.sdk.credentials import CredentialsAPI
from managed_research.sdk.datasets import DatasetsAPI
from managed_research.sdk.exports import ExportsAPI
from managed_research.sdk.files import FilesAPI
from managed_research.sdk.github import GithubAPI
from managed_research.sdk.integrations import IntegrationsAPI
from managed_research.sdk.logs import LogsAPI
from managed_research.sdk.models import ModelsAPI
from managed_research.sdk.outputs import OutputsAPI
from managed_research.sdk.progress import ProgressAPI
from managed_research.sdk.projects import ProjectsAPI
from managed_research.sdk.prs import PrsAPI
from managed_research.sdk.readiness import ReadinessAPI
from managed_research.sdk.repos import ReposAPI
from managed_research.sdk.repositories import RepositoriesAPI
from managed_research.sdk.runs import RunsAPI
from managed_research.sdk.setup import SetupAPI
from managed_research.sdk.trained_models import TrainedModelsAPI
from managed_research.sdk.usage import UsageAPI
from managed_research.sdk.workspace_inputs import WorkspaceInputsAPI

__all__ = [
    "ApprovalsAPI",
    "CredentialsAPI",
    "DatasetsAPI",
    "ExportsAPI",
    "FilesAPI",
    "GithubAPI",
    "IntegrationsAPI",
    "LogsAPI",
    "ModelsAPI",
    "OutputsAPI",
    "ProgressAPI",
    "ProjectsAPI",
    "PrsAPI",
    "ReadinessAPI",
    "RepositoriesAPI",
    "ReposAPI",
    "RunCostAPI",
    "RunsAPI",
    "SetupAPI",
    "TrainedModelsAPI",
    "UsageAPI",
    "WorkspaceInputsAPI",
]
