"""Allocate a common positive-X hip strap lane using actual material sweeps.

Only strap/head sweeps, not trial placements. Existing cover is excluded by
ownership and X; separate frame and all other P0 parts constrain the lane.
"""
from datetime import datetime,timezone
from pathlib import Path
import json
import w5_source_hip_grips as H
from check_main_p0_placement import SavedShapes,prop
from w5_selected_owners_r52 import cached
from w5_exact_separation import separated
from servo_fuse_inputs_r1 import save,sha
ROOT=H.ROOT;OUT=H.BASE/'w5-hip-band-lane-plan-r1'


def main():
    import FreeCAD as A,Part
    start=datetime.now(timezone.utc);assert not (OUT/'plan.json').exists()
    r=SavedShapes();objects=r.doc(H.M.ENTRY);owners,cache=cached()
    members={x.get('value') for x in prop(objects['RobotCatAssembly24'],'Group').findall('.//Link')}
    wanted=set()
    for wrapper in members:
        if not wrapper.startswith('Rigid_'):continue
        links=prop(objects[wrapper],'Group');children=links.findall('.//Link') if links is not None else []
        if len(children)==1:wanted.add(children[0].get('value'))
    owners={n:s for n,s in owners.items() if n in wanted}
    spec=json.loads((H.OUT/'blueprint.json').read_text(encoding='utf-8'))['specification']
    source=json.loads((H.BASE/'w5-leg-source-map-r1/interface.json').read_text(encoding='utf-8'))
    def box(b):return Part.makeBox(*(b[i+3]-b[i] for i in range(3)),A.Vector(*b[:3]))
    domain=[-.5,15.8];sweeps=[]
    for i,b in enumerate(spec['body_band_boxes_mm']):
        bb=list(b);bb[0],bb[3]=domain;sweeps.append((f'Band{i}',box(bb),1.25))
    bb=list(spec['body_head_box_mm']);bb[0],bb[3]=domain;sweeps.append(('Head',box(bb),2.25))
    hits=[];errors=[];intervals=[];pairs=0
    for row in source['looms']:
        if not row['loom'].endswith('1'):continue
        pose=r.placement(objects['Rigid_'+row['pcb']])*r.placement(objects[row['pcb']])
        for role,shape,hw in sweeps:
            world=shape.copy();world.Placement=pose*world.Placement
            for name,t in owners.items():
                if not world.BoundBox.intersect(t.BoundBox):continue
                for solid in t.Solids:
                    if not world.BoundBox.intersect(solid.BoundBox) or separated(world,solid):continue
                    pairs+=1
                    try:
                        c=world.common(solid)
                        if c.Volume<=1e-6:continue
                        c.Placement=pose.inverse()*c.Placement;b=c.BoundBox
                        hits.append(dict(loom=row['loom'],role=role,owner=name,actual_common_mm3=c.Volume,
                            conservative_contact_projection_mm=[b.XMin,b.XMax]))
                        intervals.append([b.XMin-hw-.2,b.XMax+hw+.2])
                    except Exception as ex:errors.append(str(ex))
        print('HIP_BAND_LANE',row['loom'],pairs,len(hits),flush=True)
    allowed=[[domain[0]+1.45,domain[1]-2.45]]
    for lo,hi in sorted(intervals):
        pieces=[]
        for a,b in allowed:
            if hi<=a or lo>=b:pieces.append([a,b])
            else:
                if lo>a:pieces.append([a,min(b,lo)])
                if hi<b:pieces.append([max(a,hi),b])
        allowed=pieces
    allowed=[p for p in allowed if p[1]-p[0]>.5]
    chosen=sum(max(allowed,key=lambda p:p[1]-p[0]))/2 if allowed and not errors else None
    finish=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True)
    pins=[Path(__file__),H.OUT/'checks.json',H.OUT/'blueprint.json',H.M.ENTRY,H.BASE/'w5-installed-r52/owners.json',H.BASE/'w5-installed-r52'/cache['geometry']]
    save(OUT/'plan.json',dict(status='COMMON_HIP_STRAP_LANE_ALLOCATED' if chosen is not None else 'COMMON_HIP_STRAP_LANE_BLOCKED',
        selected_axis_x_PCB_mm=chosen,allowed_intervals_mm=allowed,actual_witnesses=hits,errors=errors,pairs=pairs,
        projection_is_conservative_allocation_not_collision=True,root_reconstruction_required=True,
        selected=False,W1_complete=False,W5_complete=False,physical_pass=False,
        source_sha256={**r.hashes,**{p.relative_to(ROOT).as_posix():sha(p) for p in pins}},
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds()))
    print('HIP_BAND_LANE_RECEIVED',chosen,allowed,flush=True)


if __name__=='__main__':main()
