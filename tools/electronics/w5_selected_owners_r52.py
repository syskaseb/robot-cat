"""Installed R52 construction, not the released/parked bank service pose.

Reuse the accepted owner recipe without running old checks or rebuilding E6.
Restore the installed TE ends, input routes, ties and fuse holders by stopping
the service recipe BEFORE its release operations. Apply only selected R52
native replacements. Never use the parked owner census as installed wiring.
"""
from pathlib import Path
import json
import runpy
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/electronics"))
sys.path.insert(0, str(ROOT / "tools/cad"))
from servo_fuse_inputs_r1 import sha, save


def receive():
    import FreeCAD
    import Part
    source = ROOT / "tools/electronics/servo_fuse_bank_fixed_rr_lift_r22.py"
    namespace = runpy.run_path(str(source), run_name="installed_owner_definition")
    code = namespace["code"]
    code = code[:code.index("    omitted=[]")]
    # Remove only filesystem operations/check-execution guards in this receiver.
    code = code.replace("OUT.mkdir(parents=True,exist_ok=True)", "None")
    code = code.replace("assert not (OUT/'checks.json').exists(),'Preserve result'", "pass")
    code = code.replace("assert not (out / 'checks.json').exists(), 'Preserve completed results'", "pass")
    # The nested clip receiver has its own existing-output guard; replace in its
    # source text before compilation, without altering any owner construction.
    marker = "code=loader.read_text(encoding='utf-8');"
    code = code.replace(marker, marker + "code=code.replace(\"assert not (out / 'checks.json').exists(), 'Preserve completed results'\",'pass');")
    code += "    return owners,pins,module\n"
    context = dict(__file__=str(source), __name__="installed_receiver")
    exec(compile(code, str(source), "exec"), context)
    owners, pins, module = context["main"]()

    def load(rel):
        pins[rel] = sha(ROOT / rel)
        return Part.read(str(ROOT / rel))

    replacements = {
        "CandidateDeck": "servo-fuse-left-mount-service-native-r7/Deck_WORLD.brep",
        "BankRight": "servo-fuse-bank-inner-feed-service-r1/BankRight_WORLD.brep",
        "BankLeft": "servo-fuse-left-mount-service-native-r7/BankLeft_WORLD.brep",
        "Cover": "servo-fuse-cover-offset-mount-native-r3/Cover_WORLD.brep",
        "FixedGuard": "servo-fuse-guard-fixed-service-r1/Guard_WORLD.brep",
        "hardware/electronics/full-cat/servo-fuse-cover-neighbors-r1/CoverBracket_-84_-1":
            "servo-fuse-cover-offset-mount-native-r3/Bracket_WORLD.brep",
    }
    module.pop("FRReturnGuard")
    for key in list(module):
        if key.startswith("FRHardware/"):
            del module[key]
    owners.update(module)
    for key, rel in replacements.items():
        owners[key] = load("hardware/cad/studies/" + rel)
    for role in ("Screw0", "Screw1", "Nut0", "Nut1"):
        owners["FixedGuardHardware/" + role] = load(
            "hardware/electronics/full-cat/servo-fuse-guard-fixed-deck-r3/" + role + "_CANDIDATE.brep")
    rel = "hardware/electronics/full-cat/servo-fuse-p-wago-retention-r3/checks.json"
    pins[rel] = sha(ROOT / rel)
    wago = json.loads((ROOT / rel).read_text(encoding="utf-8"))
    assert wago["static_contacts"] == 0 and not wago["errors"]
    for row in wago["blocks"]:
        for rel in row["geometry"]:
            owners["PWagoTie/" + Path(rel).stem] = load(rel)
    selection = "hardware/manufacturing/one-batch-prototype-r52/selection.json"
    pins[selection] = sha(ROOT / selection)
    s = json.loads((ROOT / selection).read_text(encoding="utf-8"))
    assert s["local_fuse_bank_complete"] and not s["W5_complete"]
    # Every direct selected native replacement is pinned by the accepted lift
    # proof. Imported recipe hashes are retained separately for traceability.
    proofrel = "hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r22/checks.json"
    pins[proofrel] = sha(ROOT / proofrel)
    proof = json.loads((ROOT / proofrel).read_text(encoding="utf-8"))
    assert not proof["hits"] and not proof["errors"]
    for key, rel in replacements.items():
        path = "hardware/cad/studies/" + rel
        assert pins[path] == proof["source_sha256"][path], path
    assert sum(k.endswith("_ATO_DESIGN") for k in owners) == 12
    assert sum(k.rsplit("/", 1)[-1].startswith("F_") and
               k.endswith(("_IN_DESIGN", "_OUT_DESIGN")) for k in owners) == 24
    assert sum("release_0.0_W" in k for k in owners) == 12
    assert not any("release_1.0_W" in k for k in owners)
    pins[Path(__file__).relative_to(ROOT).as_posix()] = sha(Path(__file__))
    return owners, pins


def main():
    from datetime import datetime, timezone
    import FreeCAD
    import Part
    start = datetime.now(timezone.utc)
    out = ROOT / "hardware/electronics/full-cat/w5-installed-r52"
    out.mkdir(parents=True, exist_ok=True)
    assert not (out / "owners.json").exists(), "Keep the completed cache"
    owners, pins = receive()
    rows = []
    for index, (key, shape) in enumerate(owners.items()):
        assert not shape.isNull(), key
        rows.append(dict(key=key, child_index=index,
                         bounds_mm=[getattr(shape.BoundBox, n) for n in
                                    ("XMin", "YMin", "ZMin", "XMax", "YMax", "ZMax")]))
    compound = Part.makeCompound(list(owners.values()))
    compound.exportBrep(str(out / "installed.brep"))
    assert len(Part.read(str(out / "installed.brep")).childShapes()) == len(rows)
    end = datetime.now(timezone.utc)
    save(out / "owners.json", dict(status="INSTALLED_R52_CACHE_NOT_FULL_ROBOT_PASS",
         rows=rows, geometry="installed.brep", geometry_sha256=sha(out / "installed.brep"),
         source_sha256=pins, started_utc=start.isoformat(),
         finished_utc=end.isoformat(), worker_wall_seconds=(end-start).total_seconds(),
         physical_pass=False, W5_complete=False))
    print(json.dumps(dict(owners=len(rows), elapsed_seconds=(end-start).total_seconds())), flush=True)


def pack_initial_cache():
    """Consolidate only this task's initial disposable cache, never CAD sources."""
    import FreeCAD
    import Part
    out = ROOT / "hardware/electronics/full-cat/w5-installed-r52"
    receipt = json.loads((out / "owners.json").read_text(encoding="utf-8"))
    assert "geometry" not in receipt
    files = [out / row["file"] for row in receipt["rows"]]
    assert all(p.resolve().parent == out.resolve() and p.name.startswith("owner_")
               and p.suffix == ".brep" for p in files)
    assert all(sha(p) == row["sha256"] for p, row in zip(files, receipt["rows"]))
    shapes = [Part.read(str(p)) for p in files]
    target = out / "installed.brep"
    assert not target.exists()
    Part.makeCompound(shapes).exportBrep(str(target))
    reopened = Part.read(str(target)).childShapes()
    assert len(reopened) == len(shapes)
    assert all(abs(a.Volume-b.Volume) < 1e-5 for a, b in zip(shapes, reopened))
    for index, row in enumerate(receipt["rows"]):
        row.pop("file"); row.pop("sha256"); row["child_index"] = index
    receipt.update(geometry=target.name, geometry_sha256=sha(target))
    receipt["source_sha256"][Path(__file__).relative_to(ROOT).as_posix()] = sha(Path(__file__))
    save(out / "owners.json", receipt)
    # These 889 disposable files were generated by the initial cache run in
    # this turn. Their byte-identical topology is now in the verified compound.
    for p in files:
        p.unlink()
    print(json.dumps(dict(packed=len(shapes), files_remaining=2)), flush=True)


def cached():
    import FreeCAD
    import Part
    out = ROOT / "hardware/electronics/full-cat/w5-installed-r52"
    receipt = json.loads((out / "owners.json").read_text(encoding="utf-8"))
    path = out / receipt["geometry"]
    assert sha(path) == receipt["geometry_sha256"]
    pieces = Part.read(str(path)).childShapes()
    assert len(pieces) == len(receipt["rows"])
    return {row["key"]: pieces[row["child_index"]] for row in receipt["rows"]}, receipt


if __name__ == "__main__":
    pack_initial_cache() if "--pack-initial" in sys.argv else main()
