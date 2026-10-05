"""Allocate hip-root rear material from exact per-solid sections and witnesses.

Do not move a rejected root blindly. Determine actual case/carrier surfaces
within the strap lane and actual neighboring frame intersections for all hips.
"""
import json
from datetime import datetime,timezone
from pathlib import Path
import w5_source_hip_grips as H
from check_main_p0_placement import SavedShapes,prop
from w5_selected_owners_r52 import cached
from servo_fuse_inputs_r1 import save,sha
ROOT=H.ROOT;OUT=H.BASE/'w5-hip-root-section-allocation-r1'


def main():
    import FreeCAD as A,Part
    start=datetime.now(timezone.utc);assert not (OUT/'plan.json').exists()
    receipt=json.loads((H.OUT/'checks.json').read_text(encoding='utf-8'))
    bp=json.loads((H.OUT/'blueprint.json').read_text(encoding='utf-8'))
    profile=json.loads(H.FULL.read_text(encoding='utf-8'))
    source=json.loads((H.BASE/'w5-leg-source-map-r1/interface.json').read_text(encoding='utf-8'))
    r=SavedShapes();objects=r.doc(H.M.ENTRY);owners,cache=cached()
    def box(b):return Part.makeBox(*(b[i+3]-b[i] for i in range(3)),A.Vector(*b[:3]))
    def bounds(s):return [getattr(s.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]
    proposed,spec=H.proposed(A,Part);rows=[];geometry=[]
    for row in bp['rows']:
        mapping=next(p for p in source['looms'] if p['loom']==row['loom'])
        pose=r.placement(objects['Rigid_'+mapping['pcb']])*r.placement(objects[mapping['pcb']])
        full=next(p for p in profile['rows'] if p['loom']==row['loom'])
        slab=box([.15,-35,-25,3.05,15,25]);sections=[]
        for owner in full['complete_case_parts']+full['carrier_and_PCB']:
            s=owners[owner['name']].copy();s.Placement=pose.inverse()*s.Placement
            for solid in s.Solids:
                c=solid.common(slab)
                if c.Volume>1e-6:sections.append(dict(owner=owner['name'],label=owner['label'],bounds_PCB_mm=bounds(c),mm3=c.Volume))
        conflicts=[]
        for hit in receipt['hits']:
            if not hit['part'].startswith(row['loom']):continue
            role=hit['part'][3:]
            if hit['owner']==row['loom']+'Clip':other=proposed['Clip']
            else:
                other=owners[hit['owner']].copy();other.Placement=pose.inverse()*other.Placement
            for i,solid in enumerate(proposed[role].Solids):
                for other_solid in other.Solids:
                    if not solid.BoundBox.intersect(other_solid.BoundBox):continue
                    c=solid.common(other_solid)
                    if c.Volume>1e-6:
                        conflicts.append(dict(role=role,role_solid=i,owner=hit['owner'],mm3=c.Volume,bounds_PCB_mm=bounds(c)))
                        w=c.copy();w.Placement=pose*w.Placement;geometry.append(w)
        rows.append(dict(loom=row['loom'],strap_lane_x_mm=[.15,3.05],own_material_sections=sections,actual_conflicts=conflicts))
        print('HIP_ROOT_SECTION',row['loom'],sections,conflicts,flush=True)
    OUT.mkdir(parents=True,exist_ok=True);geo=OUT/'CONFLICT_WITNESSES_WORLD.brep';Part.makeCompound(geometry).exportBrep(str(geo))
    finish=datetime.now(timezone.utc)
    pins=[Path(__file__),Path(H.__file__),H.OUT/'checks.json',H.OUT/'blueprint.json',H.FULL,
        H.BASE/'w5-installed-r52/owners.json',H.BASE/'w5-installed-r52'/cache['geometry']]
    save(OUT/'plan.json',dict(status='FOUR_HIP_ACTUAL_STRAP_LANE_AND_CONFLICT_SECTIONS_RECEIVED',rows=rows,
        bounds_are_conservative_allocation_not_collision_verdict=True,
        selected=False,W1_complete=False,W5_complete=False,physical_pass=False,
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds(),
        source_sha256={**r.hashes,**{p.relative_to(ROOT).as_posix():sha(p) for p in pins}},files={geo.relative_to(ROOT).as_posix():sha(geo)}))


if __name__=='__main__':main()
