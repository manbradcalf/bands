"""Read-only Flask dashboard for a .bands/ agent workspace."""

from bands.dashboard.app import create_app

__all__ = ["create_app"]
