"""Public error types for Managed Research."""


class SmrApiError(RuntimeError):
    """Raised when the SMR API returns a non-success response."""


__all__ = ["SmrApiError"]
