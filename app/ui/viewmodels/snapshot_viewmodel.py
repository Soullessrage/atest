from __future__ import annotations

from pathlib import Path
from typing import List

from app.core.application import ApplicationContext
from app.data.snapshots.manager import SnapshotRecord
from app.domain.models.structure import World


class SnapshotViewModel:
    def __init__(self, context: ApplicationContext):
        self.context = context

    def list_snapshots(self) -> List[SnapshotRecord]:
        return self.context.snapshot_manager.list_snapshots()

    def create_snapshot(self, world_id: str, name: str, description: str = "") -> SnapshotRecord:
        return self.context.snapshot_manager.create_snapshot(world_id, name, description)

    def restore_snapshot(self, snapshot_id: str, overwrite: bool = True) -> World:
        return self.context.snapshot_manager.restore_snapshot(snapshot_id, overwrite=overwrite)

    def available_worlds(self) -> List[World]:
        return self.context.persistence_service.list_worlds()
