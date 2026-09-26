"""Domain exceptions. Adapters translate vendor errors into these."""


class OpsPilotError(Exception):
    """Base class for all OpsPilot errors."""


class InvalidRequestError(OpsPilotError):
    """The caller sent something we cannot process. Maps to HTTP 400."""


class RetryableError(OpsPilotError):
    """A transient dependency failure (throttling, timeout, 5xx). Safe to retry."""


class DependencyUnavailableError(OpsPilotError):
    """A dependency is failing and its circuit breaker is open. Maps to HTTP 503."""

    def __init__(self, dependency: str, retry_after_seconds: float) -> None:
        super().__init__(f"{dependency} is unavailable; retry in {retry_after_seconds:.0f}s")
        self.dependency = dependency
        self.retry_after_seconds = retry_after_seconds


class ConfigurationError(OpsPilotError):
    """Settings are invalid for the current stage."""
