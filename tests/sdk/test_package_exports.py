from managed_research.client import SmrControlClient as ClientViaCompat
from managed_research.errors import SmrApiError
from managed_research.sdk import SmrControlClient as ClientViaSdk


def test_sdk_and_compat_client_exports_resolve_same_type() -> None:
    assert ClientViaCompat is ClientViaSdk
    assert issubclass(SmrApiError, RuntimeError)
