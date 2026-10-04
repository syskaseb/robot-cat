"""Verify new W5 receipts only; do not audit/rebuild unchanged robot geometry."""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    folder = ROOT / 'hardware/electronics/full-cat'
    paths = [folder / 'w5-body-selected-r52/manifest.json',
             folder / 'w5-installed-r52/owners.json']
    paths += sorted(folder.glob('w5-front-return-r52-r*/checks.json'))
    paths += sorted(folder.glob('w5-g1-passage-native-r*/checks.json'))
    paths += sorted(folder.glob('w5-g1-passage-native-r*/execution-observation.json'))
    paths += sorted(folder.glob('w5-g1-saved-*/checks.json'))
    paths += sorted(folder.glob('w5-fl-return-r52-r*/checks.json'))
    pins, mismatches = {}, []
    for path in paths:
        receipt = json.loads(path.read_text(encoding='utf-8'))
        bindings = {**receipt.get('source_sha256', {}), **receipt.get('files', {})}
        if 'geometry' in receipt:
            bindings[(path.parent / receipt['geometry']).relative_to(ROOT).as_posix()] = receipt['geometry_sha256']
        for rel, value in bindings.items():
            if rel in pins and pins[rel] != value:
                mismatches.append(dict(path=rel, problem='conflicting new receipt hashes'))
            pins[rel] = value
    for rel, value in pins.items():
        path = ROOT / rel
        if not path.is_file() or digest(path) != value:
            mismatches.append(dict(path=rel, problem='missing or changed bytes'))
    print(json.dumps(dict(receipts=len(paths), pinned_sources=len(pins), mismatches=mismatches)), flush=True)
    return 1 if mismatches else 0


if __name__ == '__main__':
    sys.exit(main())
