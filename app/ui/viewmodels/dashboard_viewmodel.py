from __future__ import annotations

from app.core.services.persistence_service import PersistenceService


class DashboardViewModel:
    def __init__(self, persistence_service: PersistenceService):
        self.persistence_service = persistence_service

    def get_world_count(self) -> int:
        return len(self.persistence_service.list_worlds())

from __future__ import annotations

from app.core.services.persistence_service import PersistenceService


class DashboardViewModel:
    def __init__(self, persistence_service: PersistenceService):
        self.persistence_service = persistence_service

    def get_world_count(self) -> int:
        return len(self.persistence_service.list_worlds())

    def get_summary(self) -> str:
        world_count = self.get_world_count()
        if world_count == 0:
            return """Welcome to your D&D World Simulator! 🎲

🚀 Getting Started:
• Create your first world in the "Worlds" section
• Use the Map view to visualize geography
• Take snapshots to save your progress
• Export worlds for your campaigns

Your adventure awaits!"""
        else:
            return f"""Welcome back to your D&D World Simulator! 🎲

📊 Current Status:
• {world_count} world{'s' if world_count != 1 else ''} created
• Ready for simulation and exploration

💡 Quick Actions:
• View and manage worlds in the "Worlds" section
• Explore maps and relationships visually
• Create snapshots to preserve important states
• Export campaign-ready content

Let's continue building your fantasy world!"""