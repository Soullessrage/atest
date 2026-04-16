import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional


EXPORT_PACKAGE_TYPES = [
    "world",
    "continent",
    "empire",
    "kingdom",
    "region",
    "settlement",
    "npc",
    "race",
    "event",
    "ruleset",
    "template",
]


class JsonPackage:
    def __init__(self, package_type: str, version: int, payload: Dict[str, Any]):
        if package_type not in EXPORT_PACKAGE_TYPES:
            raise ValueError(f"Unsupported package type: {package_type}")
        self.package_type = package_type
        self.version = version
        self.payload = payload

    def to_dict(self) -> Dict[str, Any]:
        return {
            "package_type": self.package_type,
            "version": self.version,
            "payload": self.payload,
        }

    def to_json(self, path: Optional[Path] = None, indent: int = 2) -> str:
        text = json.dumps(self.to_dict(), indent=indent, default=str)
        if path:
            path.write_text(text, encoding="utf-8")
        return text

    @classmethod
    def from_json(cls, source: str) -> "JsonPackage":
        data = json.loads(source)
        return JsonPackage(
            package_type=data["package_type"],
            version=data["version"],
            payload=data["payload"],
        )
