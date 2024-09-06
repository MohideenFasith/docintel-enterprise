class DocIntelError(Exception):
    """Base class for domain errors."""


class DocumentNotFound(DocIntelError):
    pass


class DuplicateDocument(DocIntelError):
    pass


class InvalidDocument(DocIntelError):
    pass


class PermissionDenied(DocIntelError):
    pass


class RateLimitExceeded(DocIntelError):
    pass


class WorkflowNotFound(DocIntelError):
    pass

# _ci-ref-32789
