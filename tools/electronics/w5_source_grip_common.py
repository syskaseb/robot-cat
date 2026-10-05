"""One removable source-clip proposal for12looms, no P0 or path changes.

The narrow root lane is derived from actual case/PCB/carrier profiles: PCB
ends at localX=-5, hip carrier begins atX=-1.0688. Clamp to CASE, never PCB.
Use one T18I around a captured U-root and one insulation strap at the saddle.
All dimensions/bent tie shapes are prototype reservations; no strength PASS.
"""
from pathlib import Path
from datetime import datetime,timezone
import json, math, sys
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics'),str(ROOT/'tools/cad')]
from servo_fuse_inputs_r1 import sha,save
from check_main_p0_placement import SavedShapes,prop
from check_p0_leg_geometry import world_shape
from w5_exact_separation import separated

BASE=ROOT/'hardware/electronics/full-cat';OUT=BASE/'w5-source-grip-common-r1'
PLAN=BASE/'w5-moving-grip-space-plan-r1/plan.json'
ENTRY=ROOT/'hardware/cad/assembly/RobotCatNarrowRimEars.FCStd'
TIE=ROOT/'hardware/reference/hellermann-11102370-2026-10-04/dimensions.json'


def proposed(A,Part):
    def box(b):return Part.makeBox(*(b[i+3]-b[i] for i in range(3)),A.Vector(*b[:3]))
    # U-jaws slide onto the case from the connector side, in the thin free
    # lane beyond the PCB edge. The back and two jaws provide angular capture;
    # a body strap prevents opening. No existing bolt stack is changed.
    xmin,xmax=-4.7,-1.7; ymin,ymax=-18.56,.507228358954493
    zinner=12.5617039077231;zouter=zinner+1.5
    boxes=dict(TopJaw=[xmin,ymin,zinner,xmax,ymax,zouter],
        BottomJaw=[xmin,ymin,-zouter,xmax,ymax,-zinner],
        BackJaw=[xmin,-.992771641045507,-zouter,xmax,ymax,zouter],
        RootStem=[xmin,-22,-13.3,xmax,-17.2,-1],
        SourceArm=[xmin,-50.5,-7,xmax,-21,-1],
        SaddleBeam=[-15.55,-53.5,-7,xmax,-47.5,1])
    roots=[box(b) for b in boxes.values()]
    cx,cy,cz=-11.55,-50.5,5
    roots.append(Part.makeCylinder(5.5,6,A.Vector(cx,cy-3,cz),A.Vector(0,1,0)))
    cutters=[Part.makeCylinder(3.05,8,A.Vector(cx,cy-4,cz),A.Vector(0,1,0)),box([cx-6,cy-4,cz,cx+6,cy+4,cz+7])]
    def half_ring(ri,ro,upper,clear=False):
        lo=cy-1.5 if clear else cy-1.25;h=3 if clear else 2.5
        ann=Part.makeCylinder(ro,h,A.Vector(cx,lo,cz),A.Vector(0,1,0)).cut(
            Part.makeCylinder(ri,h+.2,A.Vector(cx,lo-.1,cz),A.Vector(0,1,0)))
        hb=[cx-ro-.1,lo-.1,cz if upper else cz-ro-.1,cx+ro+.1,lo+h+.1,cz+ro+.1 if upper else cz]
        return ann.common(box(hb))
    cutters.extend([half_ring(5.25,6.95,False,True),half_ring(2.5,4.2,True,True)])
    bridges=[];slotboxes=[]
    for sign in (-1,1):
        xa,xb=(2.75,6.7) if sign>0 else (-6.7,-2.75)
        bridges.append(box([cx+xa,cy-1.25,cz-1.2,cx+xb,cy+1.25,cz]))
        xa,xb=(2.55,6.95) if sign>0 else (-6.95,-2.55)
        sb=[cx+xa,cy-1.5,cz-1.45,cx+xb,cy+1.5,cz+.25];slotboxes.append(sb);cutters.append(box(sb))
    clip=roots[0].multiFuse(roots[1:]).cut(Part.makeCompound(cutters))
    assert clip.isValid() and len(clip.Solids)==1,('clip',len(clip.Solids))
    body_boxes=[[-4.65,ymin,zouter,-2.15,ymax,zouter+1.2],
                [-4.65,ymin,-zouter-1.2,-2.15,ymax,-zouter],
                [-4.65,ymin-1.2,-zouter,-2.15,ymin,zouter],
                [-4.65,ymax,-zouter,-2.15,ymax+1.2,zouter]]
    body_head=[-6,-12.4,zouter+.6,-1.5,-7.6,zouter+4.1]
    cable_head=[cx+5.8,cy-2.25,cz-2.4,cx+9.3,cy+2.25,cz+2.4]
    parts=dict(Clip=clip,BodyBand=Part.makeCompound([box(b) for b in body_boxes]),BodyHead=box(body_head),
        CableBand=Part.makeCompound([half_ring(5.5,6.7,False),half_ring(2.75,3.95,True),*bridges]),CableHead=box(cable_head))
    spec=dict(root_boxes_mm=boxes,root_case_gap_mm=.2,root_wall_mm=1.5,root_lane_x_mm=[xmin,xmax],
        source_saddle_center_in_PCB_frame_mm=[cx,cy,cz],saddle_axis_local=[0,1,0],saddle_radii_mm=[3.05,5.5],
        saddle_length_mm=6,tie_corner_slots_mm=slotboxes,body_band_boxes_mm=body_boxes,
        body_head_box_mm=body_head,cable_head_box_mm=cable_head,
        body_aperture_diagonal_mm=math.hypot(ymax-ymin,2*zouter),
        nominal_rectangular_body_band_perimeter_mm=2*(ymax-ymin+2*zouter),
        beam_section_mm=[3,6],cable_root_pullout_and_PETG_creep_unknown=True,
        assembly='Before assembling the servo into P0, slip the U-root onto its case in the planned free lane. Fit one case/root strap, plug the unchanged factory lead, lay its insulation in the open saddle and fit one cable strap. Inspect PCB/shaft clearance and actual fit in phase2.',
        model_band_closure_and_case_conformity_provisional=True)
    return parts,spec


def main():
    import FreeCAD as A,Part
    start=datetime.now(timezone.utc);assert not (OUT/'checks.json').exists()
    plan=json.loads(PLAN.read_text(encoding='utf-8'));tie=json.loads(TIE.read_text(encoding='utf-8'))
    for rel,digest in plan['source_sha256'].items():assert sha(ROOT/rel)==digest,rel
    reader=SavedShapes();objects=reader.doc(ENTRY)
    members={x.get('value') for x in prop(objects['RobotCatAssembly24'],'Group').findall('.//Link')}
    local,spec=proposed(A,Part)
    assert spec['body_aperture_diagonal_mm']<tie['maximum_bundle_diameter_mm']
    assert spec['nominal_rectangular_body_band_perimeter_mm']+tie['head_length_mm']<tie['length_mm']
    OUT.mkdir(parents=True,exist_ok=True)
    # Use the existing pinned neighbor cache, including its already received
    # P0 bodies. Never read the heavy Shell35 BRep from E6 again.
    from w5_selected_owners_r52 import cached
    cached_shapes,cache=cached();wanted=set()
    for wrapper in sorted(members):
        if not wrapper.startswith('Rigid_'):continue
        links=prop(objects[wrapper],'Group')
        if links is None:continue
        child=links.findall('.//Link')
        if len(child)!=1:continue
        name=child[0].get('value')
        shape_property=prop(objects[name],'Shape')
        linked=prop(objects[name],'LinkedObject')
        if shape_property is None and linked is None:continue
        wanted.add(name)
    neighbors={name:s for name,s in cached_shapes.items() if name in wanted}
    assert all(row['case'] in neighbors for row in plan['looms'])
    proposals={};rows=[];hits=[];errors=[];pairs=0
    def check(label,s,name,t):
        nonlocal pairs
        if not s.BoundBox.intersect(t.BoundBox):return
        for a in s.Solids:
            for b in t.Solids:
                if not a.BoundBox.intersect(b.BoundBox) or separated(a,b):continue
                pairs+=1
                try:
                    c=a.common(b)
                    if c.Volume>1e-6:hits.append(dict(part=label,owner=name,mm3=c.Volume,
                        bounds_mm=[getattr(c.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]))
                except Exception as ex:errors.append(dict(part=label,owner=name,error=str(ex)))
    for row in plan['looms']:
        pcb=next(r['pcb'] for r in json.loads((BASE/'w5-leg-source-map-r1/interface.json').read_text(encoding='utf-8'))['looms'] if r['loom']==row['loom'])
        pose=reader.placement(objects['Rigid_'+pcb])*reader.placement(objects[pcb])
        for role,prototype in local.items():
            label=row['loom']+role;s=prototype.copy();s.Placement=pose*s.Placement;proposals[label]=s
            for name,t in neighbors.items():check(label,s,name,t)
        rows.append(dict(loom=row['loom'],root_case=row['case'],printed_part='SourceClipUniversal',
            source_grip_world_mm=list(pose.multVec(A.Vector(*spec['source_saddle_center_in_PCB_frame_mm']))),
            same_received_straight_lead=True,body_straps=1,insulation_straps=1))
        save(OUT/'progress.json',dict(last_loom=row['loom'],pairs=pairs,hits=hits,errors=errors,updated_utc=datetime.now(timezone.utc).isoformat()))
        print('SOURCE_GRIP_COMMON',row['loom'],'pairs',pairs,'hits',len(hits),'errors',len(errors),flush=True)
    for i,a in enumerate(rows):
        for b in rows[i+1:]:
            for ra in local:
                for rb in local:check(a['loom']+ra,proposals[a['loom']+ra],b['loom']+rb,proposals[b['loom']+rb])
    for row in rows:
        for role in ('BodyBand','BodyHead','CableBand','CableHead'):
            check(row['loom']+role,proposals[row['loom']+role],row['loom']+'Clip',proposals[row['loom']+'Clip'])
    geometry=OUT/'TWELVE_SOURCE_CLIPS_AND_STRAPS_PROPOSED_WORLD.brep'
    Part.makeCompound(list(proposals.values())).exportBrep(str(geometry))
    blueprint=OUT/'blueprint.json';save(blueprint,dict(specification=spec,roles=list(proposals),rows=rows,
        new_print_identity='SourceClipUniversal',print_quantity=12,T18I_installed=24,
        selected=False,native_complete=False,source_harness_and_joint_motion_pending=True,physical_pass=False))
    finish=datetime.now(timezone.utc)
    pins=[Path(__file__),PLAN,TIE,BASE/'w5-leg-source-map-r1/interface.json',ROOT/'tools/cad/check_main_p0_placement.py',ROOT/'tools/cad/check_p0_leg_geometry.py',
          ROOT/'tools/electronics/w5_selected_owners_r52.py',BASE/'w5-installed-r52/owners.json',BASE/'w5-installed-r52'/cache['geometry']]
    save(OUT/'checks.json',dict(status='ONE_SHARED_TWELVE_SOURCE_CLIP_STATIC_PROPOSAL',hits=hits,errors=errors,pairs=pairs,
        scope='Only12source clips and their straps vs saved P0 parts and each other. Fixed/body received wiring must still be included; not a whole-robot audit or motion qualification.',
        source_loom_body_pairs_and_motion_pending=True,P0_unchanged=True,wire_paths_unchanged=True,
        selected=False,native_complete=False,W1_complete=False,W5_complete=False,physical_pass=False,
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds(),
        source_sha256={**reader.hashes,**{p.relative_to(ROOT).as_posix():sha(p) for p in pins}},
        files={p.relative_to(ROOT).as_posix():sha(p) for p in [geometry,blueprint]}))


if __name__=='__main__':main()
