"""Services module for backend application."""
from app.services.state_store import DaprStateStore, get_state_store

__all__ = ["DaprStateStore", "get_state_store"]
