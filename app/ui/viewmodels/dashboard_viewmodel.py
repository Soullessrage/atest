from __future__ import annotations

from app.core.services.persistence_service import PersistenceService


class DashboardViewModel:
    def __init__(self, persistence_service: PersistenceService):
        self.persistence_service = persistence_service

    def get_world_count(self) -> int:
        return len(self.persistence_service.list_worlds())

    def get_summary(self) -> str:
        return f"Worlds: {self.get_world_count()}\nUse the sidebar to inspect worlds, run simulations, and export campaign content."