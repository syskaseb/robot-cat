"""Create an explicitly non-production integrity manifest for the AUX pilot."""
from pathlib import Path
import json

from release_check import sha256, verify
from pilot import MODULES

ROOT = Path(__file__).resolve().parents[2]


def main():
    cad = ROOT / "hardware/cad"
    evidence_names = ["geometry.json", "native-motion.json", "parameter-update.json",
                      "relocation.json", "fasteners-smoke.json", "link-map.json",
                      "display.json", "tests.json", "whole-cat.png"]
    evidence = [cad / "validation" / name for name in evidence_names]
    files = [cad / "parameters/RobotParameters.FCStd", cad / "assembly/RobotCat.FCStd"]
    files += [cad / "modules" / (name + ".FCStd") for name in MODULES]
    files += evidence + [cad / "toolchain.json"]
    files += [ROOT / "tools/freecad/skorupa" / name for name in ["aux35.py", "inheritance30.py"]]
    files += [ROOT / "hardware/skorupa/v35" / name for name in [
        "assembly-plan.json", "Kot_v35_ZASILANIE_AUX.FCStd", "AuxPower35.FCStd"]]
    files += [ROOT / "hardware/bom/aux-pilot.json", ROOT / ".gitattributes"]
    files += sorted((ROOT / "tools/cad").glob("*.py"))
    files += sorted((ROOT / ".agents/skills").glob("*/SKILL.md"))
    bom = json.loads((ROOT / "hardware/bom/aux-pilot.json").read_text())
    ids = [p["id"] for p in bom["parts"]]
    assert len(ids) == len(set(ids)), "Duplicate part identities"
    instances = []
    for part in bom["parts"]:
        assert part["quantity"] == len(part["assembly_names"]), part["id"]
        instances.extend(part["assembly_names"])
    instances += bom["mating_parts_not_counted_again"]
    link_map = json.loads((cad / "validation/link-map.json").read_text())
    assert len(instances) == len(set(instances)) == 18
    assert set(instances) == {row["component"] for row in link_map["links"]}
    native = json.loads((cad / "validation/native-motion.json").read_text())
    geometry = json.loads((cad / "validation/geometry.json").read_text())
    relocation = json.loads((cad / "validation/relocation.json").read_text())
    parameters = json.loads((cad / "validation/parameter-update.json").read_text())
    target = cad / "assembly/RobotCat.FCStd"
    assert native["assembly_sha256"] == geometry["assembly_sha256"] == sha256(target)
    assert relocation["passed"] and parameters["restored"]
    for name, digest in relocation["file_sha256"].items():
        assert sha256(cad / name) == digest, name
    assert parameters["parameter_sha256"] == sha256(cad / "parameters/RobotParameters.FCStd")
    for name, digest in parameters["module_sha256"].items():
        assert sha256(cad / "modules" / (name + ".FCStd")) == digest, name
    for name, digest in native["module_sha256"].items():
        assert sha256(cad / "modules" / (name + ".FCStd")) == digest, name
    manifest = {
        "schema_version": 1, "checkpoint": "modular-aux-pilot", "readiness": "prototype",
        "baseline_commit": "6033edca1519dcc0cfa9e9dce4bf6cb1bc08f964",
        "scope": "18 linked AUX components; 302 inherited snapshots. No print approval or new hardware tag.",
        "files": [{"path": p.relative_to(ROOT).as_posix(), "sha256": sha256(p)} for p in files],
        "checks": {"linked_parts": 18, "compared_parts": 320, "native_frames": len(native["frames"]),
                   "parameter_test": "2.4 to 2.6 mm clearance, restored", "relocation": "fresh process"},
        "gates": {
            "geometry": {"status": "fail", "reason": "Inherited strict shell BOP failure remains; migration equivalence is a different test."},
            "assembly": {"status": "open", "reason": "Native kinematics checked; 29 TEMP locks and unfinished head/horn remain."},
            "fit": {"status": "open", "reason": "No physical PETG/insert/bearing fit measurements."},
            "petg": {"status": "open", "reason": "Printer profile, orientation validation and material trials not approved."},
            "loads": {"status": "open", "reason": "Continuous servo torque, thermal limits and PETG creep unresolved."},
            "electrical": {"status": "open", "reason": "Harness, connector/current and thermal verification unfinished."},
            "service": {"status": "open", "reason": "Battery service, rear bolt access and complete assembly sequence unresolved."}
        }
    }
    result = verify(ROOT, manifest)
    assert result["integrity_ok"], result
    assert not verify(ROOT, manifest, True)["integrity_ok"]
    out = ROOT / "hardware/releases/modular-pilot.json"
    out.write_text(json.dumps(manifest, indent=2), encoding="utf-8", newline="\n")
    print(json.dumps({"manifest": str(out), "files": len(files), "readiness": "prototype"}))


if __name__ == "__main__":
    main()
