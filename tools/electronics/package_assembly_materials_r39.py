"""Replace five generic allowances by six exact materials; preserve R38 CAD."""
import copy
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/cad"))
from release_check import sha256, verify
PARENT = ROOT / "hardware/manufacturing/one-batch-prototype-r38"
BATCH = ROOT / "hardware/manufacturing/one-batch-prototype-r39"
OUT = ROOT / "hardware/electronics/full-cat/assembly-materials-k3-r1"
START = "2026-10-02T02:57:02+00:00"

def read(p):
    return json.loads(p.read_text(encoding="utf-8"))

def save(p, v):
    p.write_text(json.dumps(v, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

def build_payload(materials, selection, quantities):
    selection, quantities = copy.deepcopy(selection), copy.deepcopy(quantities)
    old_ids = set(materials["replaces_generic_ids"])
    assert len(old_ids) == 5 and len(materials["lines"]) == 6
    assert {r["id"] for r in quantities["lines"] if r["id"] in old_ids} == old_ids
    assert {r["replaces"] for r in materials["lines"]} == old_ids
    quantities["lines"] = [r for r in quantities["lines"] if r["id"] not in old_ids]
    recipe = (OUT / "materials.json").relative_to(ROOT).as_posix()
    for r in materials["lines"]:
        quantities["lines"].append(dict(id=r["id"], name=r["name"], planning_quantity=r["planning_quantity"],
            unit=r["unit"], source=recipe, manufacturer_sku=r["manufacturer_sku"], supplier_sku=r["supplier_sku"],
            manufacturer_url=r["manufacturer_url"], supplier_url=r["supplier_url"],
            purchase_pack_count=r["purchase_pack_count"], stock_per_pack=r["stock_per_pack"], stock_unit=r["stock_unit"],
            existing_working_allowance=r["existing_working_allowance"], unallocated_stock=r["unallocated_stock"],
            note=r["note"]))
    assert len({r["id"] for r in quantities["lines"]}) == len(quantities["lines"])
    quantities.update(line_count=len(quantities["lines"]), selected_prints=(BATCH/"selection.json").relative_to(ROOT).as_posix(),
        assembly_materials=recipe, K3_complete=False, W5_complete=False)
    # This is not a second tool kit or a whole-harness stock balance.
    quantities["missing_for_phase1"] = [
        "Five generic P0 material categories now have six exact SKU rows. Whole W5/tool compatibility/material census remains OPEN.",
        "R32 closed nominal F_PWM ends; source protection E3 and remaining W5 are not closed by a material kit.",
        "Resolve remaining generic K2 items and consolidate stock after all routes; no order release or physical PASS."]
    selection.update(parent_selection_sha256=sha256(PARENT/"selection.json"), assembly_materials=recipe,
        assembly_materials_sha256=sha256(OUT/"materials.json"), phase1_percent=70, K3_complete=False, W5_complete=False)
    return selection, quantities

def main():
    assert not (BATCH / "manifest.json").exists(), "Do not overwrite a pinned package"
    start = datetime.now(timezone.utc); tick = time.monotonic()
    parent = read(PARENT/"manifest.json")
    assert verify(ROOT, parent)["integrity_ok"]
    materials = read(OUT/"materials.json")
    selection, quantities = build_payload(materials, read(PARENT/"selection.json"), read(PARENT/"one-order-quantities.json"))
    assert quantities["line_count"] == 114 and selection["jobs"] == 71 and selection["installed_petg_parts"] == 110
    runs = []
    for pattern in ("test_assembly_materials_r39.py", "test_body_ground_bridge.py", "test_body_data_bridges_r3.py"):
        r = subprocess.run([sys.executable, "-X", "utf8", "-m", "unittest", "discover", "-s", "tools/electronics", "-p", pattern, "-v"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
        runs.append(dict(pattern=pattern, exit_code=r.returncode, output=r.stdout+r.stderr))
    save(OUT/"regression-run.json", dict(start_utc=start.isoformat(), measured_seconds=time.monotonic()-tick, runs=runs, physical_pass=False))
    assert all(r["exit_code"] == 0 for r in runs), runs
    BATCH.mkdir(exist_ok=True)
    save(BATCH/"selection.json", selection); save(BATCH/"one-order-quantities.json", quantities)
    summary = (OUT/"README.md").read_text(encoding="utf-8")
    (BATCH/"README.md").write_text(summary, encoding="utf-8", newline="\n")
    rejected = []
    for version in (1, 2):
        folder = ROOT/f"hardware/electronics/full-cat/body-ground-front-return-r{version}"
        c = read(folder/"checks.json")
        assert c["status"] == "REJECTED" and c["hits"]
        rejected.append(dict(version=version, checks=(folder/"checks.json").relative_to(ROOT).as_posix(), hits=c["hits"], selected=False))
    save(OUT/"rejected-W036.json", dict(status="TWO_BOUNDED_ATTEMPTS_REJECTED", selected=False, attempts=rejected,
        note="G1 alternate cage in diagnostic r2 is not a selected terminal-label change. Retain R38 interface precedence. No new wire or Deck selection."))
    end = datetime.now(timezone.utc)
    save(OUT/"work-time.json", dict(start_utc=START, end_utc=end.isoformat(), wall_seconds=(end-datetime.fromisoformat(START)).total_seconds(),
        kind="Two rejected W036 routes plus independent complete six-SKU assembly material kit and inherited package", active_robot_work_seconds=None, separately_measured_phases=False, physical_pass=False))
    pins = {r["path"]:r["sha256"] for r in parent["files"]}
    paths = [p for folder in (OUT, BATCH, ROOT/"hardware/electronics/full-cat/body-ground-front-return-r1", ROOT/"hardware/electronics/full-cat/body-ground-front-return-r2") for p in folder.iterdir() if p.is_file() and p.name not in ("manifest.json", "validation.json")]
    paths += [PARENT/"manifest.json", Path(__file__), Path(__file__).with_name("test_assembly_materials_r39.py"), Path(__file__).with_name("body_ground_front_return_r1.py"), Path(__file__).with_name("body_ground_front_return_r2.py")]
    for p in paths:
        rel = p.relative_to(ROOT).as_posix(); digest = sha256(p)
        assert rel not in pins or pins[rel] == digest, rel
        pins[rel] = digest
    m = copy.deepcopy(parent)
    m.update(phase1_percent=70, K3_complete=False, W5_complete=False, parent_pins_preserved=len(parent["files"]), files=[dict(path=p, sha256=h) for p,h in sorted(pins.items())])
    integrity = verify(ROOT, m); assert integrity["integrity_ok"], integrity
    save(BATCH/"manifest.json", m)
    save(BATCH/"validation.json", dict(integrity=integrity, parent_pins_preserved=len(parent["files"]), print_selection_unchanged=True, new_STL=0, replaced_generic_categories=5, exact_SKU_rows=6, quantity_lines=114, phase1_percent=70, K3_complete=False, W5_complete=False, physical_pass=False))
    print(json.dumps(dict(pins=len(pins), parent_pins=len(parent["files"]), quantity_lines=114, phase1_percent=70, new_STL=0, work_wall_seconds=(end-datetime.fromisoformat(START)).total_seconds())))

if __name__ == "__main__":
    main()
