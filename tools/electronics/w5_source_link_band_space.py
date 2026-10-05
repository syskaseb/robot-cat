"""Allocate one band plane from actual P0 material for all eight link grips.

Intersect complete swept strap/head boxes and extensible C-jaw rails with
actual saved BReps. Project those actual witnesses into forbidden station
intervals. This is conservative dimensional allocation, not bbox collisions
or trial placement of successive straps.
"""
from pathlib import Path
from datetime import datetime,timezone
import json
import w5_source_link_grips as L
from check_main_p0_placement import SavedShapes,prop
from w5_selected_owners_r52 import cached
from w5_exact_separation import separated
from servo_fuse_inputs_r1 import save,sha
ROOT=L.ROOT;OUT=L.BASE/'w5-source-link-band-space-r1'
RECEIPT=L.OUT/'checks.json';BLUEPRINT=L.OUT/'blueprint.json'


def main():
    import FreeCAD as A,Part
    start=datetime.now(timezone.utc);assert not (OUT/'plan.json').exists()
    previous=json.loads(RECEIPT.read_text(encoding='utf-8'))
    assert len(previous['hits'])==4 and not previous['errors']
    assert {h['part'][2:] for h in previous['hits']}=={'2BodyBand'}
    for rel,digest in {**previous['source_sha256'],**previous['files']}.items():
        assert sha(ROOT/rel)==digest,rel
    bp=json.loads(BLUEPRINT.read_text(encoding='utf-8'));spec=bp['specification']
    reader=SavedShapes();objects=reader.doc(L.M.ENTRY)
    members={x.get('value') for x in prop(objects['RobotCatAssembly24'],'Group').findall('.//Link')}
    wanted=set()
    for wrapper in members:
        if wrapper.startswith('Rigid_'):
            links=prop(objects[wrapper],'Group');children=links.findall('.//Link') if links is not None else []
            if len(children)==1:wanted.add(children[0].get('value'))
    owners,cache=cached();owners={n:s for n,s in owners.items() if n in wanted}
    source=json.loads((L.BASE/'w5-leg-source-map-r1/interface.json').read_text(encoding='utf-8'))
    domain=[-33.5,-1.7];station_margin=.2
    def box(b):return Part.makeBox(*(b[i+3]-b[i] for i in range(3)),A.Vector(*b[:3]))
    swept=[]
    for i,b in enumerate(spec['body_band_boxes_mm']):
        bb=list(b);bb[0],bb[3]=domain
        swept.append((f'Band{i}',box(bb),1.25))
    bb=list(spec['body_head_box_mm']);bb[0],bb[3]=domain
    swept.append(('BodyHead',box(bb),2.25))
    # Only these three rails expand toward the chosen strap station. Keep
    # the existing front foot/stem/arm and the received cable saddle datum.
    for name in ('TopJaw','BottomJaw','BackJaw'):
        bb=list(spec['root_boxes_mm'][name]);bb[0],bb[3]=domain[0],-4.7
        swept.append(('RootExtension'+name,box(bb),None))
    intervals=[];witnesses=[];errors=[];pairs=0;root_min=domain[0]
    for row in bp['rows']:
        mapping=next(r for r in source['looms'] if r['loom']==row['loom'])
        pose=reader.placement(objects['Rigid_'+mapping['pcb']])*reader.placement(objects[mapping['pcb']])
        for role,prototype,halfwidth in swept:
            world=prototype.copy();world.Placement=pose*world.Placement
            for name,t in owners.items():
                if not world.BoundBox.intersect(t.BoundBox):continue
                for solid in t.Solids:
                    if not world.BoundBox.intersect(solid.BoundBox) or separated(world,solid):continue
                    pairs+=1
                    try:
                        contact=world.common(solid)
                        if contact.Volume<=1e-6:continue
                        contact.Placement=pose.inverse()*contact.Placement
                        b=contact.BoundBox;x0,x1=b.XMin,b.XMax
                        witnesses.append(dict(loom=row['loom'],role=role,owner=name,mm3=contact.Volume,
                            actual_contact_projection_x_PCB_mm=[x0,x1]))
                        if halfwidth is None:root_min=max(root_min,x1+station_margin)
                        else:intervals.append([x0-halfwidth-station_margin,x1+halfwidth+station_margin])
                    except Exception as ex:errors.append(dict(loom=row['loom'],role=role,owner=name,error=str(ex)))
        print('LINK_BAND_SPACE',row['loom'],pairs,len(witnesses),len(errors),flush=True)
    # The body band must lie wholly on the expanded jaw, with a small land.
    allowed=[[max(domain[0]+1.45,root_min+1.45),domain[1]-1.45]]
    for lo,hi in sorted(intervals):
        pieces=[]
        for a,b in allowed:
            if hi<=a or lo>=b:pieces.append([a,b])
            else:
                if lo>a:pieces.append([a,min(b,lo)])
                if hi<b:pieces.append([max(a,hi),b])
        allowed=pieces
    allowed=[p for p in allowed if p[1]-p[0]>.5]
    selected=None if not allowed or errors else sum(max(allowed,key=lambda p:p[1]-p[0]))/2
    finish=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True)
    pins=[Path(__file__),Path(L.__file__),RECEIPT,BLUEPRINT,L.FULL,L.M.ENTRY,
          L.BASE/'w5-leg-source-map-r1/interface.json',L.BASE/'w5-installed-r52/owners.json',
          L.BASE/'w5-installed-r52'/cache['geometry']]
    save(OUT/'plan.json',dict(status='ONE_COMMON_LINK_BAND_PLANE_ALLOCATED' if selected is not None else 'LINK_BAND_ALLOCATION_BLOCKED',
        domain_x_PCB_mm=domain,actual_witnesses=witnesses,errors=errors,pairs=pairs,
        forbidden_station_intervals_mm=intervals,minimum_root_extension_x_mm=root_min,
        allowed_station_intervals_mm=allowed,selected_station_x_PCB_mm=selected,
        selected_root_xmin_mm=None if selected is None else min(-4.7,selected-1.45),
        station_clearance_design_mm=station_margin,whole_harness_motion_or_assembly_proof=False,
        planned_changes=['Extend only top/bottom/back C-jaw rails to the allocated shared band station.',
            'Move one body strap and its locking head coherently onto that land for all eight link-stage grips.',
            'Preserve front foot/stem/saddle, source lead and P0. Four hip roots remain independent.'],
        selected=False,W1_complete=False,W5_complete=False,physical_pass=False,
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds(),
        source_sha256={**reader.hashes,**{p.relative_to(ROOT).as_posix():sha(p) for p in pins}}))
    print('LINK_BAND_ALLOCATION',selected,allowed,flush=True)


if __name__=='__main__':main()
