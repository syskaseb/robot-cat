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
    paths += sorted(folder.glob('w5-leg-lower-fanouts-r*/checks.json'))
    paths += sorted(folder.glob('w5-leg-escape-fanouts-r*/checks.json'))
    paths += sorted(folder.glob('w5-leg-outward-loops-r*/checks.json'))
    paths += sorted(folder.glob('w5-leg-joint-source-layout-r*/checks.json'))
    paths += sorted(folder.glob('w5-joint-source-carrier-native-r*/checks.json'))
    paths += sorted(folder.glob('w5-four-ground-returns-plan-r*/intent.json'))
    paths += sorted(folder.glob('w5-four-ground-returns-check-r*/checks.json'))
    paths += sorted(folder.glob('w5-ground-joint-preflight-r*/checks.json'))
    paths += sorted(folder.glob('w5-ground-entries-r*/checks.json'))
    paths += sorted(folder.glob('w5-ground-network-r*/checks.json'))
    paths += sorted(folder.glob('w5-space-plan-inputs-r*/space.json'))
    paths += sorted(folder.glob('w5-space-plan-inputs-r*/allocation.json'))
    paths += sorted(folder.glob('w5-space-plan-inputs-r*/reservations.json'))
    paths += sorted(folder.glob('w5-space-plan-inputs-r*/egress.json'))
    paths += sorted(folder.glob('w5-space-plan-inputs-r*/looms.json'))
    paths += sorted(folder.glob('w5-ground-facing-plan-r*/checks.json'))
    paths += sorted(folder.glob('w5-central-ground-routes-r*/checks.json'))
    paths += sorted(folder.glob('w5-leg-ground-*-plan-r*/egress.json'))
    paths += sorted(folder.glob('w5-leg-ground-upper-rail-r*/checks.json'))
    paths += sorted(folder.glob('w5-joint-upper-harness-r*/checks.json'))
    paths += sorted(folder.glob('w5-data-outward-r*/checks.json'))
    paths += sorted(folder.glob('w5-coupled-corridors-r*/checks.json'))
    paths += sorted(folder.glob('w5-central-space-solver-r*/checks.json'))
    paths += sorted(folder.glob('w5-central-outward-plan-r*/checks.json'))
    paths += sorted(folder.glob('w5-central-source-zone-r*/checks.json'))
    paths += sorted(folder.glob('w5-central-source-boundary-r*/checks.json'))
    paths += sorted(folder.glob('w5-central-orientation-plan-r*/checks.json'))
    paths += sorted(folder.glob('w5-central-restraint-dependencies-r*/checks.json'))
    paths += sorted(folder.glob('w5-central-joint-clearance-r*/checks.json'))
    paths += sorted(folder.glob('w5-central-battery-s-plan-r*/checks.json'))
    paths += sorted(folder.glob('w5-central-bridge-low-arc-r*/checks.json'))
    paths += sorted(folder.glob('w5-central-bridge-low-arc-r*/received-family.json'))
    paths += sorted(folder.glob('w5-central-shared-routes-r*/checks.json'))
    paths += sorted(folder.glob('w5-central-south-bridge-r*/checks.json'))
    paths += sorted(folder.glob('w5-central-remaining-routes-r*/checks.json'))
    paths += sorted(folder.glob('w5-bus-low-s-plan-r*/intent.json'))
    paths += sorted(folder.glob('w5-bus-low-s-material-r*/checks.json'))
    paths += sorted(folder.glob('w5-four-low-returns-r*/checks.json'))
    paths += sorted(folder.glob('w5-rear-aux-low-joint-r*/checks.json'))
    paths += sorted(folder.glob('w5-aux-side-loop-r*/checks.json'))
    paths += sorted(folder.glob('w5-aux-diagonal-loop-r*/checks.json'))
    paths += sorted(folder.glob('w5-central-received-joint-r*/received.json'))
    paths += sorted(folder.glob('w5-leg-length-ledger-r*/ledger.json'))
    paths += sorted(folder.glob('w5-branch-space-plan-r*/checks.json'))
    paths += sorted(folder.glob('w5-branch-joint-routes-r*/checks.json'))
    paths += sorted(folder.glob('w5-leg-end-preparation-r*/interface.json'))
    paths += sorted(folder.glob('w5-s1-source-layout-r*/intent.json'))
    paths += sorted(folder.glob('w5-s1-source-check-r*/checks.json'))
    paths += sorted(folder.glob('w5-source-inlet-joint-r*/checks.json'))
    paths += sorted(folder.glob('w5-source-platform-native-r*/checks.json'))
    paths += sorted(folder.glob('w5-source-carrier-native-r*/checks.json'))
    paths += sorted(folder.glob('w5-source-bank-passage-native-r*/checks.json'))
    paths += sorted(folder.glob('w5-source-cover-passages-native-r*/checks.json'))
    paths += sorted(folder.glob('w5-source-received-interface-r*/checks.json'))
    paths += sorted(folder.glob('w5-source-grips-native-r*/checks.json'))
    paths += sorted(folder.glob('w5-source-roof-native-r*/checks.json'))
    paths += sorted(folder.glob('w5-source-roof-service-r*/assembly.json'))
    paths += sorted(folder.glob('w5-source-family-service-r*/assembly.json'))
    paths += sorted(folder.glob('w5-source-cage-access-native-r*/checks.json'))
    paths += sorted(folder.glob('w5-source-cage-assembly-receive-r*/assembly.json'))
    paths += sorted(folder.glob('w5-source-material-contribution-r*/stock.json'))
    paths += sorted(folder.glob('w5-source-platform-native-r*/execution-observation.json'))
    paths += sorted(folder.glob('w5-source-platform-assembly-r*/assembly.json'))
    paths += sorted((ROOT / 'hardware/reference').glob('source-terminal-*/received.json'))
    paths += sorted(folder.glob('w5-psys-platform-preflight-r*/checks.json'))
    paths += sorted(folder.glob('w5-xa05-joint-repair-r*/checks.json'))
    paths += sorted(folder.glob('w5-xa05-native-r*/checks.json'))
    paths += sorted(folder.glob('w5-xa05-outer-support-r*/checks.json'))
    paths += sorted(folder.glob('w5-xa05-access-r*/checks.json'))
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
