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

# _ci-ref-17328

# _ci-ref-32768

# _ci-ref-44517

# _ci-ref-44517

# _ci-ref-88172

# _ci-ref-98918

# _ci-ref-71249
