from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.core.services.import_export_service import ImportExportService
from app.core.services.persistence_service import PersistenceService
from app.data.jsonio.schema import JsonPackage
from app.domain.models.structure import World


@dataclass
class SnapshotRecord:
    id: str
    name: str
    description: str
    created_at: datetime
    file_path: Path


class SnapshotManager:
    def __init__(
        self,
        snapshot_dir: Path,
        persistence_service: PersistenceService,
        import_export_service: ImportExportService,
    ):
        self.snapshot_dir = snapshot_dir
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
        self.persistence_service = persistence_service
        self.import_export_service = import_export_service

    def create_snapshot(self, world_id: str, name: str, description: str = "") -> SnapshotRecord:
        world = self.persistence_service.load_world(world_id)
        if world is None:
            raise ValueError(f"World {world_id} not found")

        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        snapshot_id = f"snapshot-{timestamp}-{world.id}"
        filename = f"{snapshot_id}.json"
        path = self.snapshot_dir / filename
        package_path = self.snapshot_dir / f"{snapshot_id}.package.json"

        self.import_export_service.export_full_world(world.id, package_path)
        envelope = {
            "snapshot_id": snapshot_id,
            "name": name,
            "description": description,
            "created_at": datetime.utcnow().isoformat(),
            "package_path": str(package_path),
        }
        path.write_text(json.dumps(envelope, indent=2), encoding="utf-8")
        return SnapshotRecord(id=snapshot_id, name=name, description=description, created_at=datetime.utcnow(), file_path=path)

    def list_snapshots(self) -> list[SnapshotRecord]:
        records: list[SnapshotRecord] = []
        for path in sorted(self.snapshot_dir.glob("snapshot-*.json")):
            try:
                raw = json.loads(path.read_text(encoding="utf-8"))
                records.append(
                    SnapshotRecord(
                        id=raw["snapshot_id"],
                        name=raw.get("name", path.stem),
                        description=raw.get("description", ""),
                        created_at=datetime.fromisoformat(raw["created_at"]),
                        file_path=path,
                    )
                )
            except Exception:
                continue
        return records

    def load_snapshot_package(self, snapshot_id: str) -> Optional[JsonPackage]:
        for record in self.list_snapshots():
            if record.id == snapshot_id:
                raw = json.loads(record.file_path.read_text(encoding="utf-8"))
                package_path = Path(raw["package_path"])
                if package_path.exists():
                    return JsonPackage.from_json(package_path.read_text(encoding="utf-8"))
        return None

    def restore_snapshot(self, snapshot_id: str, overwrite: bool = True) -> World:
        for record in self.list_snapshots():
            if record.id != snapshot_id:
                continue
            raw = json.loads(record.file_path.read_text(encoding="utf-8"))
            package_path = Path(raw["package_path"])
            if not package_path.exists():
                raise ValueError(f"Snapshot package file missing: {package_path}")
            return self.import_export_service.import_world(package_path, overwrite=overwrite)
        raise ValueError(f"Snapshot {snapshot_id} not found")
