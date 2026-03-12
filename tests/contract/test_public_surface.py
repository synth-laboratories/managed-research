import managed_research
import managed_research.models.generated.v1 as generated_models
import managed_research.sdk as managed_research_sdk
import managed_research.transport as transport
from managed_research import SmrControlClient


def test_top_level_public_exports_remain_available() -> None:
    assert managed_research.__version__
    assert managed_research.SmrControlClient is SmrControlClient
    assert "SmrControlClient" in managed_research.__all__
    assert "SmrProject" in managed_research.__all__


def test_generated_model_exports_cover_public_domains() -> None:
    assert {
        "SmrApproval",
        "SmrArtifact",
        "SmrCapabilities",
        "SmrIntegrationStatus",
        "SmrLinearTeam",
        "SmrLinearTeamListing",
        "SmrOAuthStart",
        "SmrProject",
        "SmrProjectStatusSnapshot",
        "SmrProviderKeyStatus",
        "SmrQuestion",
        "SmrRun",
        "SmrRunEconomics",
        "SmrRunLogArchive",
    }.issubset(set(generated_models.__all__))


def test_sdk_namespace_exports_are_public() -> None:
    assert {
        "ApprovalsAPI",
        "ArtifactsAPI",
        "IntegrationsAPI",
        "LogsAPI",
        "ProjectsAPI",
        "RunsAPI",
        "SmrControlClient",
        "UsageAPI",
    }.issubset(set(managed_research_sdk.__all__))


def test_transport_exports_cover_helper_surface() -> None:
    assert {
        "BinaryPayloadPreview",
        "RetryPolicy",
        "SmrHttpTransport",
        "build_query_params",
        "extract_next_cursor",
        "preview_binary_payload",
    }.issubset(set(transport.__all__))
