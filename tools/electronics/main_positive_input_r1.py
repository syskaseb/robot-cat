"""One complete MAIN positive input candidate on selected R41.

Read cached current shapes, never recompute legacy E6. Exact FHAC0001ZXJ
lead and body dimensions are distinguished from a conservative closed-cover
project box. No circuit, purchase or printed part is selected by this screen.
"""
from datetime import datetime, timezone
from pathlib import Path
import json, sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools/cad'))
import body_ground_routes_r1 as M
OUT = ROOT/'hardware/electronics/full-cat/main-positive-input-r1'

def current_owners():
    import FreeCAD as A
    import Part
    import body_ground_front_shared_r3 as R
    import g1_exit_restraints_finish_r1 as G
    owners, hashes = R.current_owners()
    owners.pop('Deck_R40')
    path=ROOT/'hardware/cad/studies/g1-exit-restraints-finish-r1/Deck_WORLD.brep'
    shape=Part.Shape();shape.read(str(path));owners['Deck_R41']=shape
    hashes[path.relative_to(ROOT).as_posix()]=M.sha(path)
    _, bands=G.selected_shapes()
    owners.update(bands)
    return owners,hashes

def main():
    import FreeCAD as A
    import Part
    OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'placement-checks.json').exists(), 'Preserve completed evidence.'
    begin=datetime.now(timezone.utc)
    owners, hashes=current_owners()
    # Only closed holder envelope: exact length50 +/-1, cap20 +/-0.25,
    # socket17.2 +/-0.25. Height22 is an explicit project allowance, not
    # the open-cover21.2 dimension misrepresented as closed overall height.
    bbox=[-88,-29.85,109,-37,-12.15,131]
    holder=Part.makeBox(bbox[3]-bbox[0],bbox[4]-bbox[1],bbox[5]-bbox[2],A.Vector(*bbox[:3]))
    rows=[]
    for name,s in owners.items():
        if name=='Deck_R41':continue # intended seat contact; native mount not yet made
        for i,q in enumerate(s.Solids):
            if holder.BoundBox.intersect(q.BoundBox):
                rows.append(dict(owner=name,solid=i,hit_mm3=holder.common(q).Volume))
    hits=[r for r in rows if r['hit_mm3']>1e-5]
    end=datetime.now(timezone.utc)
    M.save(OUT/'placement-checks.json',dict(status='REJECTED' if hits else 'HOLDER_SITE_CLEAR_NEEDS_COMPLETE_WIRES_AND_MOUNT',
        holder_SKU='FHAC0001ZXJ',old_centre_xy_mm=[43,-58.5],candidate_bbox_mm=bbox,
        source='Littelfuse OL-FHAC0001ZXJ revL and 2012 transport catalogue p132',
        body_length_including_moulded_reliefs_mm=[49,51],factory_leads_A_B_mm=[84.5,94.5],
        delivered_bare_tips_C_D_mm=[4.35,8.35],factory_wire_AWG=16,
        closed_height_22mm_is_project_allowance=True,lead_OD_and_static_radius_unconfirmed=True,
        source_sha256=hashes,rows=rows,hits=hits,script_sha256=M.sha(Path(__file__)),
        W043_prefuse_blank_max_mm=50,W077_postfuse_blank_max_mm=100,W078_red_blank_max_mm=150,
        selected=False,W5_complete=False,physical_pass=False,
        started_utc=begin.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds()))
    holder.exportBrep(str(OUT/'F_PI_candidate_DESIGN.brep'))
    M.save(OUT/'owner-bboxes.json',{n:[s.BoundBox.XMin,s.BoundBox.YMin,s.BoundBox.ZMin,s.BoundBox.XMax,s.BoundBox.YMax,s.BoundBox.ZMax] for n,s in owners.items()})
    print(json.dumps(dict(hits=hits,pairs=len(rows))),flush=True)

if __name__=='__main__':main()
