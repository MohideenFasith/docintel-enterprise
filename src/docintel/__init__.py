"""DocIntel Enterprise document intelligence service."""

from .main import create_app
from .service import DocumentService

__all__ = ["DocumentService", "create_app"]
