import managed_research
import managed_research.sdk as managed_research_sdk
import managed_research.transport as transport
from managed_research import SmrControlClient


def test_top_level_public_exports_match_rewritten_surface() -> None:
    assert managed_research.__version__
    assert managed_research.SmrControlClient is SmrControlClient
    assert {
        "ProjectReadiness",
        "ProgressAPI",
        "RunProgress",
        "SmrControlClient",
        "WorkspaceInputsAPI",
        "WorkspaceInputsState",
        "WorkspaceUploadResult",
    }.issubset(set(managed_research.__all__))


def test_sdk_exports_cover_new_namespaces() -> None:
    assert {
        "ProgressAPI",
        "ProjectsAPI",
        "RunsAPI",
        "SmrControlClient",
        "WorkspaceInputsAPI",
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
