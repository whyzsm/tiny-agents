from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ScanItem:
    name: str
    kind: str
    status: str
    source_path: Path
    entry_path: Path
    reason: str
    files: list[Path] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    secret_findings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "kind": self.kind,
            "status": self.status,
            "source_path": str(self.source_path),
            "entry_path": str(self.entry_path),
            "reason": self.reason,
            "files": [str(path) for path in self.files],
            "warnings": list(self.warnings),
            "secret_findings": list(self.secret_findings),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ScanItem":
        return cls(
            name=data["name"],
            kind=data["kind"],
            status=data["status"],
            source_path=Path(data["source_path"]),
            entry_path=Path(data["entry_path"]),
            reason=data["reason"],
            files=[Path(path) for path in data.get("files", [])],
            warnings=list(data.get("warnings", [])),
            secret_findings=list(data.get("secret_findings", [])),
        )


@dataclass
class ScanReport:
    SCHEMA_VERSION = 1

    generated_at: str
    roots: list[Path]
    items: list[ScanItem] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    schema_version: int = SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "generated_at": self.generated_at,
            "roots": [str(root) for root in self.roots],
            "items": [item.to_dict() for item in self.items],
            "warnings": list(self.warnings),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ScanReport":
        if data.get("schema_version") != cls.SCHEMA_VERSION:
            raise ValueError("Unsupported report schema version")
        return cls(
            generated_at=data["generated_at"],
            roots=[Path(root) for root in data.get("roots", [])],
            items=[ScanItem.from_dict(item) for item in data.get("items", [])],
            warnings=list(data.get("warnings", [])),
            schema_version=data["schema_version"],
        )
