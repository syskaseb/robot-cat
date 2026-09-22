"""Fail-closed integrity/readiness check; stdlib only, no FreeCAD required."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath

REQUIRED_GATES = frozenset({
    "geometry", "assembly", "fit", "petg", "loads", "electrical", "service",
})
STATES = {"pass", "fail", "open"}
READINESS = {"concept", "prototype", "test", "print-ready"}


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def repo_file(root: Path, value: str) -> Path:
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        raise ValueError(f"Invalid relative path: {value!r}")
    rel = PurePosixPath(value)
    if rel.is_absolute() or ".." in rel.parts:
        raise ValueError(f"Path escapes repository: {value}")
    path = (root / value).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError(f"Missing/outside file: {value}")
    return path


def verify(root: Path, manifest: dict, require_print_ready: bool = False) -> dict:
    errors = []
    if manifest.get("schema_version") != 1:
        errors.append("Unsupported schema_version")
    if manifest.get("readiness") not in READINESS:
        errors.append("Invalid readiness")
    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        errors.append("Nonempty files list required")
        files = []
    seen = set()
    for item in files:
        try:
            name, expected = item["path"], item["sha256"]
            if name in seen:
                raise ValueError(f"Duplicate file: {name}")
            seen.add(name)
            if not isinstance(expected, str) or len(expected) != 64 or any(c not in "0123456789abcdef" for c in expected):
                raise ValueError(f"Invalid SHA-256: {name}")
            if sha256(repo_file(root, name)) != expected:
                raise ValueError(f"Hash mismatch: {name}")
        except (ValueError, KeyError, TypeError, OSError) as exc:
            errors.append(str(exc))
    gates = manifest.get("gates", {})
    if not isinstance(gates, dict):
        gates = {}
        errors.append("gates must be an object")
    for gate in sorted(REQUIRED_GATES):
        entry = gates.get(gate, {})
        if not isinstance(entry, dict) or entry.get("status") not in STATES or not entry.get("reason"):
            errors.append(f"Missing/invalid gate: {gate}")
            continue
        if entry["status"] == "pass":
            evidence = entry.get("evidence", [])
            if not isinstance(evidence, list) or not evidence or any(p not in seen for p in evidence):
                errors.append(f"Passed gate needs hashed evidence: {gate}")
    ready = manifest.get("readiness") == "print-ready"
    if require_print_ready and not ready:
        errors.append("Checkpoint is not print-ready")
    if ready or require_print_ready:
        for gate in sorted(REQUIRED_GATES):
            entry = gates.get(gate, {})
            if not isinstance(entry, dict) or entry.get("status") != "pass":
                errors.append(f"Print gate not passed: {gate}")
    return {"integrity_ok": not errors, "readiness": manifest.get("readiness"),
            "files_checked": len(files), "errors": errors,
            "scope": "Integrity and declared gates only; not independent engineering certification."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--require-print-ready", action="store_true")
    args = parser.parse_args()
    report = verify(args.root, json.loads(args.manifest.read_text(encoding="utf-8")), args.require_print_ready)
    print(json.dumps(report, indent=2))
    return 0 if report["integrity_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
