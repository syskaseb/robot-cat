"""Locate named USB conflicts on exact original path pieces, no new layout."""
import json,os,time
import FreeCAD as A
from feline_common_space_context import current
from receive_feline_positive_service_deck import usb_edges,pipe
from fit_feline_current_usb_space import planned_pi_transform
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from check_main_p0_placement import sha,ROOT
from pathlib import Path


def main():
    tick=time.monotonic();dest=OUT/'n01-positive-service-deck-USB-witnesses.json'
    assert not dest.exists()
    world,parts,meta,pins,docs=current()
    plan=OUT/'n01-common-upper-deck-underpass-usb-plan.json'
    c=json.loads(plan.read_text())['candidate']
    contract=json.loads((OUT/'n01-physical-cable-contract.json').read_text())['usb']
    tf=planned_pi_transform(c['pose'],parts['Ref_Material_Pi4NominalPCB_0_0'].BoundBox.Center)
    es,proof,bus=usb_edges(c,contract)
    names=['PiBudget:Ethernet','PiBudget:UnlabelledTopComponentsBudget']
    result=dict(status='RUNNING_NAMED_USB_WITNESSES',source_sha256={**pins,plan.relative_to(ROOT).as_posix():sha(plan),Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},targets={},pieces=[],N01_complete=False)
    for n in names:
        s=parts[n].copy();s.Placement=tf*s.Placement
        result['targets'][n]=dict(bounds_mm=[[s.BoundBox.XMin,s.BoundBox.YMin,s.BoundBox.ZMin],[s.BoundBox.XMax,s.BoundBox.YMax,s.BoundBox.ZMax]])
        for i,e in enumerate(es):
            # Distance to the centreline gives exact clearance to a circular
            # swept jacket when larger than its radius; penetration stays hold.
            g,pts,info=e.distToShape(s)
            if g>3.75:continue
            result['pieces'].append(dict(target=n,piece=i,axis_gap_mm=g,jacket_gap_upper_estimate_mm=g-2.5,
                closest_mm=[[list(a),list(b)] for a,b in pts],edge_length_mm=e.Length))
            save_json(dest,result)
    result.update(status='NAMED_USB_PIECES_LOCATED_NOT_NEW_GEOMETRY',seconds=round(time.monotonic()-tick,3));save_json(dest,result)
    print(json.dumps(result['pieces']),flush=True)


if __name__=='__main__':print('WORKER_PID',os.getpid(),flush=True);main()
