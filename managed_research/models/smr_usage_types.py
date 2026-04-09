"""Public SMR usage-type enum."""

from __future__ import annotations

from enum import StrEnum


class SmrUsageType(StrEnum):
    INFERENCE = "inference"
    METERED_TOOL = "metered_tool"
    METERED_INFRA = "metered_infra"
    SANDBOX = "sandbox"
    CODING_AGENT = "coding_agent"
    RESEARCH = "research"
    OTHER = "other"


SMR_USAGE_TYPE_VALUES: tuple[str, ...] = tuple(value.value for value in SmrUsageType)


def coerce_smr_usage_type(
    value: SmrUsageType | str | None,
    *,
    field_name: str = "usage_type",
) -> SmrUsageType | None:
    if value is None:
        return None
    if isinstance(value, SmrUsageType):
        return value
    normalized = str(value).strip()
    if not normalized:
        return None
    try:
        return SmrUsageType(normalized)
    except ValueError as exc:
        raise ValueError(
            f"{field_name} must be one of: {', '.join(SMR_USAGE_TYPE_VALUES)}"
        ) from exc


__all__ = ["SMR_USAGE_TYPE_VALUES", "SmrUsageType", "coerce_smr_usage_type"]
