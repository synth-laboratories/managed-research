from managed_research.models.generated.v1 import (
    SmrCapabilities,
    SmrIntegrationStatus,
    SmrLinearTeamListing,
    SmrOAuthStart,
    SmrProject,
    SmrProjectStatusSnapshot,
    SmrProviderKeyStatus,
    SmrRunEconomics,
)


def test_project_from_dict_normalizes_optional_fields() -> None:
    project = SmrProject.from_dict(
        {
            "project_id": "proj_123",
            "org_id": 42,
            "name": "Demo",
            "archived": 0,
            "onboarding_state": {"step": "ready"},
            "execution": {"pool_id": "pool_1"},
        }
    )

    assert project.project_id == "proj_123"
    assert project.org_id == "42"
    assert project.archived is False
    assert project.execution["pool_id"] == "pool_1"


def test_project_status_snapshot_drops_non_object_entries() -> None:
    snapshot = SmrProjectStatusSnapshot.from_dict(
        {
            "project_id": "proj_123",
            "active_runs": [{"run_id": "run_1"}, "bad"],
            "active_actor_summaries": [{"actor_id": "actor_1"}, 7],
            "queue_backlog_counts": {"queued": "2", "running": 1},
        }
    )

    assert snapshot.active_runs == [{"run_id": "run_1"}]
    assert snapshot.active_actor_summaries == [{"actor_id": "actor_1"}]
    assert snapshot.queue_backlog_counts == {"queued": 2, "running": 1}


def test_run_economics_filters_non_object_entries() -> None:
    economics = SmrRunEconomics.from_dict(
        {
            "run_id": "run_123",
            "spend_entries": [{"cost_cents": 5}, "bad"],
            "egress_events": [{"bytes": 10}, None],
            "trace_artifact": {"artifact_id": "art_1"},
        }
    )

    assert economics.spend_entries == [{"cost_cents": 5}]
    assert economics.egress_events == [{"bytes": 10}]
    assert economics.trace_artifact == {"artifact_id": "art_1"}


def test_capabilities_from_dict_defaults_missing_flags_false() -> None:
    caps = SmrCapabilities.from_dict({"actor_status_schema_version": "v1"})

    assert caps.actor_status_schema_version == "v1"
    assert caps.supports_actor_control is False
    assert caps.supports_run_economics is False


def test_integration_status_from_dict_handles_optional_fields() -> None:
    status = SmrIntegrationStatus.from_dict(
        {
            "provider": "github",
            "status": "connected",
            "connected": 1,
            "project_id": "proj_123",
            "authorize_url": "https://example.test/oauth",
        }
    )

    assert status.provider == "github"
    assert status.status == "connected"
    assert status.connected is True
    assert status.project_id == "proj_123"


def test_oauth_start_and_provider_key_models_normalize_payloads() -> None:
    oauth = SmrOAuthStart.from_dict({"authorize_url": "https://example.test/start", "state": 7})
    provider_key = SmrProviderKeyStatus.from_dict(
        {
            "project_id": "proj_123",
            "provider": "openai",
            "funding_source": "user_connected",
            "configured": 1,
            "status": "configured",
        }
    )

    assert oauth.authorize_url == "https://example.test/start"
    assert oauth.state == "7"
    assert provider_key.configured is True
    assert provider_key.provider == "openai"


def test_linear_team_listing_supports_dict_and_list_payloads() -> None:
    from_dict_payload = SmrLinearTeamListing.from_payload(
        {"teams": [{"id": "team_1", "key": "ENG", "name": "Engineering"}]}
    )
    from_list_payload = SmrLinearTeamListing.from_payload(
        [{"team_id": "team_2", "key": "OPS", "name": "Operations"}]
    )

    assert from_dict_payload.teams[0].team_id == "team_1"
    assert from_list_payload.teams[0].team_id == "team_2"
