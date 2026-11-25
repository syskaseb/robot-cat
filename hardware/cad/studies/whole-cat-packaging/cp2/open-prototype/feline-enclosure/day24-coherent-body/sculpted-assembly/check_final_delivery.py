"""Read back the digital body kit and its named first-fit checks."""
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from struct import Struct

PWD=Path(__file__).resolve().parent

def read(name):
    return json.loads((PWD/name).read_text("utf-8"))

def sha(full):
    return sha256(full.read_bytes()).hexdigest()

def review_triangles(path, row):
    data=path.read_bytes()
    count=int.from_bytes(data[80:84],"little")
    assert count==row["triangles"] and len(data)==84+50*count
    edges=Counter()
    winding=Counter()
    low=[float("inf")]*3
    high=[float("-inf")]*3
    for facet in Struct("<12fH").iter_unpack(memoryview(data)[84:]):
        a,b,c=facet[3:6],facet[6:9],facet[9:12]
        assert len({a,b,c})==3,path
        for start,end in ((a,b),(b,c),(c,a)):
            key=(start,end) if start<end else (end,start)
            edges[key]+=1
            winding[key]+=1 if start<end else -1
            for i,x in enumerate(start):
                low[i]=min(low[i],x)
                high[i]=max(high[i],x)
    assert set(edges.values())=={2} and not any(winding.values()),path
    assert abs(low[2])<.0001,path
    assert all(abs(b-a-d)<.0002 for a,b,d in zip(low,high,row["bounds_mm"])),path
    return {"oriented_edges":len(edges),"triangles":count,"sha256":sha(path)}


def run():
    native=read("native-readback.json")
    files=read("body-print-index.json")
    verified=read("verified-native.json")
    assert native["native_sha256"]==files["native_sha256"]==verified["native_assembly_sha256"]
    assert sha(PWD/native["document"])==native["native_sha256"]
    assert native["gui_pid"]==14076 and native["objects"]==640 and native["modified"] is False
    assert native["pending_operation"] is None
    assert all(sha(PWD/name)==pin for name,pin in native["views"].items())
    assert len(native["views"])==9
    assert (files["robot_stl"],files["robot_print_qty"],files["replacement_parts"],files["additional_parts"])==(62,82,9,1)
    assert len(files["source_retained"])==52
    assert len(files["parts"])==10
    assert all(sha(PWD/row["file"])==row["sha256"] and row["watertight"]
               and max(row["bounds_with_brim_and_supports_mm"])<=256
               for row in files["parts"])
    paths={p.relative_to(PWD).as_posix() for p in (PWD/"STL").glob("*.stl")}
    assert paths=={row["file"] for row in files["parts"]}
    meshes={row["file"]:review_triangles(PWD/row["file"],row) for row in files["parts"]}
    closure=read("final-two-closed-rays.json")["proof"]
    assert all(not row["uncovered"] for row in closure.values())
    same_rail=read("6ba6-rail-first-surfaces.json")
    assert all(p["object"] in ("H19_FrontFrame_Print","D24_FrontLowerShroud","E19_RearBase")
               for n in ("left","right") for p in same_rail[n])
    assert any(p["object"]=="WAVEGO_complete_126_source_solids" for p in same_rail["bottom"])
    anchors=read("front-split-anchors.json")
    assert all(p["rigid_conflict_mm3"]==0 for p in anchors["final_mesh_lift"])
    pi=read("front-pi-assembly.json")
    assert all(max(p["contact_mm3"])<.002 for p in pi["prewire_and_board_from_above_then_tilted_axial"])
    assert not read("b44-aft-final-receiver.json")["actual_bound_contact_sr"]
    assert not read("front-split-leg-final.json")["contacts"]
    csi=read("ab43-csi-delta.json")
    connector=read("ab43-pi-connector-access.json")
    rear=read("rear-refined-proof.json")
    assert {csi["native_sha256"],connector["native_sha256"],rear["native_sha256"]}=={native["native_sha256"]}
    assert connector["actual_seen_mesh_sha"]=={row["object"]:row["sha256"] for row in native["print_meshes"]}
    sections=csi["full_CSI"]
    poses={(0,0),(-20,-10),(-20,10),(20,-10),(20,10)}
    assert {(tuple(row["yaw_pitch"]),row["section"]) for row in sections}=={
        (pose,section) for pose in poses for section in ("moving","parked")}
    assert len(sections)==10 and all(not row["BRep_actual_hits"] and
        all(candidate["surface_contact"] is None for candidate in row["mesh_candidates"])
        for row in sections)
    insertion=connector["full_power_connector_approach"]
    assert len(insertion)==8 and insertion[-1]["withdrawal_from_USB_C_mm"]==0
    assert all(row["full_body_vs_Pi_mm3"]==0 and not any(row["full_body_common_mm3"].values())
               for row in insertion)
    assert not any(connector["open_CSI_access"]["occupied_open_approach_vs_prints_mm3"].values())
    rear_row=next(row for row in files["parts"] if row["source_name"]==rear["source"])
    assert rear_row["sha256"]==rear["sha256"] and rear["fractional_volume_error"]<.001
    evidence=("visual-assessment.md","native-readback.json","verified-native.json",
              "final-two-closed-rays.json","6ba6-rail-first-surfaces.json","front-split-anchors.json",
              "front-pi-assembly.json","b44-aft-final-receiver.json","front-split-leg-final.json",
              "ab43-csi-delta.json","ab43-pi-connector-access.json","ab43-grounding.json",
              "tail-final-positive.json","installed-access.json","S0-shell.json","rear-refined-proof.json")
    result={
        "verified_utc":datetime.now(timezone.utc).isoformat(),
        "native_path":native["document"],"native_sha256":native["native_sha256"],
        "gui":{"pid":native["gui_pid"],"objects":640,"saved":True,"pending_operation":None},
        "frozen_22_package_sha256":files["base_package_zip_sha256"],
        "reviewed_6ba6_sha256":native["reviewed_6ba6_sha256"],
        "inventory":{"existing_retained_files":52,"replacement_STLs":9,"added_front_mantle":1,
                     "unique_STLs":62,"quantity":82,"separate_coupon_required_before_rear_print":"FIT_S0"},
        "opaque_views_and_service_sha256":native["views"],
        "background_test":{k:{"rays":v["checked_background_pixels"],"remaining":len(v["uncovered"])}
                           for k,v in closure.items()},
        "rail_target":"side samples hit printed front/rear rail shadows; bottom sample sees the original frame",
        "CSI_occupied_regions":{"moving_and_parked_poses":len(poses),"contacts":0,"evidence":"ab43-csi-delta.json"},
        "Pi_with_open_covers":{"board_insertion_samples":len(pi["prewire_and_board_from_above_then_tilted_axial"]),
                               "complete_nominal_USB_C_insertion_samples":len(insertion),"contacts":0,
                               "CSI_full_open_latch_lane":True,"evidence":"ab43-pi-connector-access.json"},
        "rear_base_stl_fractional_volume_error":rear["fractional_volume_error"],
        "print_index_sha256":sha(PWD/"body-print-index.json"),
        "grounded_STLs":meshes,
        "evidence_sha256":{name:sha(PWD/name) for name in evidence},
        "print_max_envelope_mm":max(max(q["bounds_with_brim_and_supports_mm"]) for q in files["parts"]),
        "physical_pass":False,"actual_fit":None,"actual_cut":None,"actual_slack":None,
    }
    (PWD/"FINAL_CHECKS.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(result["native_sha256"],result["print_max_envelope_mm"],result["background_test"],flush=True)

if __name__=="__main__":
    run()
