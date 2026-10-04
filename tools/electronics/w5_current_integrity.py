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
    paths += sorted(folder.glob('w5-bus-pair-r52-r*/checks.json'))
    paths += sorted(folder.glob('w5-bus-native-grips-r*/checks.json'))
    paths += sorted(folder.glob('w5-bus-native-grips-r*/execution-observation.json'))
    paths += sorted(folder.glob('w5-bus-band-preflight-r*/checks.json'))
    paths += sorted(folder.glob('w5-bus-assembly-r*/assembly.json'))
    paths += sorted(folder.glob('w5-leg-source-map-r*/interface.json'))
    paths += sorted(folder.glob('w5-leg-corridors-r*/checks.json'))
    paths += sorted(folder.glob('w5-leg-fanouts-r*/checks.json'))
    paths += sorted(folder.glob('w5-leg-end-preparation-r*/interface.json'))
    paths += sorted(folder.glob('w5-s1-source-layout-r*/intent.json'))
    paths += sorted(folder.glob('w5-s1-source-check-r*/checks.json'))
    paths += sorted(folder.glob('w5-psys-platform-preflight-r*/checks.json'))
    paths += sorted(folder.glob('w5-xa05-joint-repair-r*/checks.json'))
    paths += sorted((ROOT / 'hardware/manufacturing').glob('one-batch-prototype-r53/BUS-reconciliation.json'))
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
