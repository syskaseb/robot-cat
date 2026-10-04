"""Compile the selected bank into the body wiring ledger without false W5.

Retain the 80 physical P0 wires/160 end identities. A qualified local fuse
output termination is NOT a qualified full moving servo lead. R52 receipt
precedence supersedes the obsolete R45 input-length candidates, not every
open robot wire. No purchases, physical continuity or invented cut lengths.
"""
from pathlib import Path
from datetime import datetime, timezone
import csv
import io
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/electronics"))
from servo_fuse_inputs_r1 import sha, save
OUT = ROOT / "hardware/electronics/full-cat/w5-body-selected-r52"


def compile_ledger():
    pins = {}
    def read(rel):
        pins[rel] = sha(ROOT / rel)
        return json.loads((ROOT / rel).read_text(encoding="utf-8"))
    selection = read("hardware/manufacturing/one-batch-prototype-r52/selection.json")
    base = read(selection["body_harness"])
    graph = read("hardware/electronics/power-platform/wiring-p0.json")
    electrical = read(selection["local_fuse_electrical"])
    stock = read(selection["local_fuse_stock"])
    inputs = read("hardware/electronics/full-cat/servo-fuse-lower-loop-materials-r1/materials.json")
    proof = read("hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r47/manifest.json")
    assert selection["local_fuse_bank_complete"] and not selection["W5_complete"]
    assert len(base["conductors"]) == len(graph["wires"]) == 80
    assert electrical["input_ends"] == electrical["output_ends"] == 12
    cuts = {row["wire"]: row["nominal_blank_mm"] for row in inputs["rows"]}
    assert len(cuts) == 12 and sum(cuts.values()) == 2880
    ends = {row["wire_id"]: row for row in electrical["ends"]}
    assert len(ends) == 24
    factory_pair_ids = {"W026", "W037", "W042", "W044", "W045", "W052", "W053"}
    graph_rows = {row["id"]: row for row in graph["wires"]}
    rows = []
    for source in base["conductors"]:
        g = graph_rows[source["id"]]
        assert (source["a"], source["b"], source["net"]) == (g["a"], g["b"], g["net"])
        assert len(source["ends"]) == 2
        row = {key: source[key] for key in ("id", "a", "b", "net", "group")}
        row.update(base_end_recipe=selection["body_harness"] + "#" + source["id"],
                   nominal_blank_mm=source.get("nominal_selected_blank_mm"),
                   full_route_prepared=source["current_selected_route_checked"],
                   route_recipe=source.get("selected_recipe"), actual_cut_mm=None,
                   phase2_physical_continuity_checked=False)
        if row["id"] in ends:
            end = ends[row["id"]]
            assert end["id"] in (row["a"], row["b"])
            row["selected_end_overlay"] = end
        if row["id"] in cuts:
            row.update(nominal_blank_mm=cuts[row["id"]], full_route_prepared=True,
                       route_recipe=selection["local_fuse_assembly"],
                       material="LAPP0107001 positive-marked black12AWG",
                       stock_identity=stock["LAPP0107001"]["quantity_id"],
                       bank_selection_proof="hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r47/manifest.json")
        if row["id"] in factory_pair_ids:
            contribution = next(q for q in stock["HELU23802"]["unique_roles"]
                                if q["id"] == row["id"] + "_extension")
            row.update(full_route_prepared=True, nominal_blank_mm=None,
                       route_recipe=selection["local_fuse_assembly"],
                       physical_segments="MTA factory lead + selected isolated extension; do not count as one HELU cable",
                       extension_blank_mm=contribution["blank_mm"],
                       factory_usable_length_assumed_mm=100,
                       factory_length_is_manufacturer_dimension=False)
        if row["id"] == "W041":
            rel = "hardware/electronics/full-cat/servo-fuse-front-source-ports-r2/W041_factory_direct_DESIGN.brep"
            assert any(q.get("path") == rel and q.get("sha256") == sha(ROOT / rel)
                       for q in proof.get("files", [])), "Selected proof must include the direct factory route"
            pins[rel] = sha(ROOT / rel)
            row.update(full_route_prepared=True, nominal_blank_mm=None,
                       route_recipe=selection["local_fuse_assembly"],
                       physical_segments="One retained MTA factory input lead; no extension or added splice",
                       factory_usable_length_assumed_mm=100,
                       factory_length_is_manufacturer_dimension=False)
        if source["group"] == "MOVING_SERVO_LOOMS":
            assert not row["full_route_prepared"], "Local termination must not close a moving leg loom"
        rows.append(row)
    assert len({r["id"] for r in rows}) == 80
    assert sum("selected_end_overlay" in r for r in rows) == 24
    assert sum(r["group"] == "MOVING_SERVO_LOOMS" for r in rows) == 36
    pending = [r["id"] for r in rows if not r["full_route_prepared"]]
    return dict(status="R52_LOCAL_BANK_MERGED_WHOLE_W5_OPEN", selected_parent="one-batch-prototype-r52",
                phase1_completed_count=15, phase1_total=20, phase1_percent=75,
                physical_P0_conductors=80, physical_P0_ends=160,
                current_body_route_rows_prepared=len(rows)-len(pending),
                route_rows_pending=pending, conductors=rows,
                source_sha256=pins,
                invariant="Coverage is a work list, not a new phase1 percentage or claim of full robot collision freedom",
                additional_W5_scope="Head/tail/Pi/AUX recipes retained by selection; balance pigtail must retain exact vendor pin mapping and unpowered fitting condition",
                W5_complete=False, K3_complete=False, physical_pass=False)


def main():
    start = datetime.now(timezone.utc)
    OUT.mkdir(parents=True, exist_ok=True)
    if (OUT / "interface.json").exists():
        assert "--refresh-own" in sys.argv, "Preserve saved receipts"
        old = json.loads((OUT / "interface.json").read_text(encoding="utf-8"))
        assert old["status"] == "R52_LOCAL_BANK_MERGED_WHOLE_W5_OPEN" and not old["W5_complete"]
    ledger = compile_ledger()
    end = datetime.now(timezone.utc)
    ledger.update(started_utc=start.isoformat(), finished_utc=end.isoformat(),
                  worker_wall_seconds=(end-start).total_seconds())
    save(OUT / "interface.json", ledger)
    stream = io.StringIO(newline="")
    writer = csv.writer(stream)
    writer.writerow(["wire", "from", "to", "group", "full_route_prepared", "nominal_blank_mm", "extension_blank_mm", "actual_cut_mm", "selected_fuse_end"])
    for r in ledger["conductors"]:
        writer.writerow([r["id"], r["a"], r["b"], r["group"], r["full_route_prepared"],
                         r["nominal_blank_mm"], r.get("extension_blank_mm", ""), "",
                         r.get("selected_end_overlay", {}).get("id", "")])
    (OUT / "wire-status.csv").write_text(stream.getvalue(), encoding="utf-8", newline="")
    paths = [OUT / "interface.json", OUT / "wire-status.csv", Path(__file__)]
    save(OUT / "manifest.json", dict(source_sha256=ledger["source_sha256"],
                                    files={p.relative_to(ROOT).as_posix(): sha(p) for p in paths}))
    print(json.dumps(dict(conductors=80, end_overlays=24, prepared=ledger["current_body_route_rows_prepared"],
                          pending=len(ledger["route_rows_pending"]), phase1_percent=75)), flush=True)


if __name__ == "__main__":
    main()
