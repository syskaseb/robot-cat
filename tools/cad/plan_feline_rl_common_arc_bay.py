"""Retain the actual RL source seam; support the first9 ON the common arc."""
import math
import numpy as np
import FreeCAD as A
import Part
from plan_feline_n01_shared import pipe
from receive_feline_global_case_candidates import placement


def construct(ends,profiles,parent):
    rows=[r for r in ends if r['group']=='NineWireCuffRL'];assert len(rows)==9
    centre=np.mean([r['point_mm'] for r in rows],axis=0);assert np.allclose(centre,[117.5,50,70])
    d=np.array([-1.,0,0]);normal=np.array([0.,-1,0]);actors={};recipes={}
    for r in rows:
        p=np.array(r['point_mm']);R=16-(p[1]-50)*-1
        at=lambda t:p+R*(math.sin(t)*d+(1-math.cos(t))*normal)
        q=at(math.pi/2);tip=q+10*normal;radius=profiles[r['portion_id']]['project_radius_mm']
        parts=[dict(kind='arc',start=p.tolist(),mid=at(math.pi/4).tolist(),end=q.tolist(),radius_mm=float(R),length_mm=float(R*math.pi/2)),
               dict(kind='line',start=q.tolist(),end=tip.tolist(),length_mm=10.)]
        assert R>=profiles[r['portion_id']]['minimum_project_R_mm']-1e-7
        name='RLArc:'+r['id'];actors[name]=pipe(parts,radius)
        recipes[name]=dict(end_id=r['id'],wire=r['wire'],parts=parts,radius_mm=radius,
            original_source_mm=r['point_mm'],original_source_axis=r['departure_axis'],
            first9_arclength_mm=[0,9],exit_mm=tip.tolist(),exit_axis=normal.tolist(),
            moving900_not_qualified=True)
    angle=10.5/12.4
    def sector(r0,r1,z0,z1):
        p=lambda r,t:A.Vector(117.5-r*math.sin(t),34+r*math.cos(t),z0)
        es=[Part.Arc(p(r0,0),p(r0,angle/2),p(r0,angle)).toShape(),Part.makeLine(p(r0,angle),p(r1,angle)),
            Part.Arc(p(r1,angle),p(r1,angle/2),p(r1,0)).toShape(),Part.makeLine(p(r1,0),p(r0,0))]
        return Part.Face(Part.Wire(es)).extrude(A.Vector(0,0,z1-z0))
    guide=sector(8.7,23.3,62.7,64.7).multiFuse([sector(8.7,10.7,62.7,75.3),sector(21.3,23.3,62.7,75.3)])
    def box(lo,hi):return Part.makeBox(*(b-a for a,b in zip(lo,hi)),A.Vector(*lo))
    t=.3;forward=np.array([-math.cos(t),-math.sin(t),0]);inward=np.array([math.sin(t),-math.cos(t),0])
    tf=placement(np.column_stack((forward,inward,[0,0,1])),[117.5-16*math.sin(t),34+16*math.cos(t),70])
    band=box([-1.25,-8.65,-8.65],[1.25,8.65,6.65]).cut(box([-1.5,-7.45,-7.45],[1.5,7.45,5.45]))
    head=box([-2.5,8.65,-3.65],[2.5,12.95,1.65])
    band.Placement=tf*band.Placement;head.Placement=tf*head.Placement
    assert abs(head.Volume-5*4.3*5.3)<1e-6
    # Root on the source side of the loop, into the existing grounded rail
    # branch. Keep the complete loop/head and its curved tightening channel.
    # The retained G_TAIL case ends atZ68.345; its adhesive pad is not
    # a root to squeeze through. Bridge ABOVE the full case with1.25air.
    bridge_bottom=math.ceil((68.345+1.25)*10)/10
    # Use the rail branch's near faceX121 with1mm positive overlap, not
    # its far adhesive faceX123. That far face approaches the retained
    # full G_TAIL bandX123.55; near-face landing leaves1.55mm, not a waiver.
    bridge=box([116,55,bridge_bottom],[122,57,bridge_bottom+2])
    guide=guide.fuse(bridge).cut(band.makeOffsetShape(.2,1e-5,join=2)).removeSplitter()
    def clone(s):
        c=Part.Shape();c.importBrepFromString(s.exportBrepToString());return c
    joint=clone(guide).common(clone(parent)).Volume
    whole=clone(guide).fuse(clone(parent))
    assert joint>1e-5 and whole.isValid() and len(whole.Solids)==1,('RL parent joint',joint)
    actors.update(RLArcGuide=guide,RLArcBand=band,RLArcHead=head)
    assert all(s.isValid() and len(s.Solids)==1 for s in actors.values())
    return actors,dict(recipes=recipes,parent='GTAILRoot:rail_branch',parent_joint_mm3=joint,
        bridge_bounds_mm=[[116,55,bridge_bottom],[122,57,bridge_bottom+2]],first9_supported_on_arc=True,
        original_source_seams_and_motor_contacts_unchanged=True,full_loop_clearance_mm=.2,
        N01_complete=False,physical_pass=False,native_changed=False,whole123_not_received=True)


def package(actors,plan,parent,ends,profiles,base,changed,outer,motion):
    import hashlib,json,time,zipfile
    from pathlib import Path
    from check_main_p0_placement import ROOT,sha
    from plan_feline_layout import OUT
    from feline_atomic_save import save_json
    from plan_feline_usb_service_bight import outer_margin
    tick=time.monotonic();assert not changed['failures']
    checks={k:v for k,v in base['checks'].items() if 'RLArcGuide' not in k.split('|')}
    # These three rows are insulated wires against their OWN full nylon
    # closure. Correct the missing nylon type, retaining the actual gaps.
    for k in base['failures']:
        a,b=k.split('|')
        if b=='RLArcBand' and a in plan['recipes']:
            r=checks[k];checks[k]={**r,'minimum_mm':.2,'ok':r['gap_mm']>=.2-1e-6,'own_insulated_wire_to_full_nylon':True}
    checks.update(changed['checks'])
    for n,s in actors.items():
        if n=='RLArcGuide':continue
        gap=s.distToShape(parent)[0];checks[n+'|'+plan['parent']]=dict(gap_mm=gap,minimum_mm=1.25,ok=gap>=1.25-1e-6)
        minimum=.15 if n in plan['recipes'] or n=='RLArcBand' else .2
        gap=s.distToShape(actors['RLArcGuide'])[0]
        checks[n+'|RLArcGuide']=dict(gap_mm=gap,minimum_mm=minimum,ok=gap>=minimum-1e-6)
    outside={n:outer_margin(s,outer) for n,s in actors.items()}
    assert all(r['ok'] for r in checks.values()) and all(r['ok'] for r in outside.values())
    zbound=min(s.BoundBox.ZMin for s in actors.values())-max(r['bounds'][1][2] for r in motion)
    assert zbound>1.25 and {r['pose'] for r in motion}==set(range(36))
    path=OUT/'n01-RL9-common-arc-rooted-space.json';archive=path.with_suffix('.breps.zip');geometry=[]
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for n,s in {**actors,'Input:parent':parent}.items():
            raw=s.exportBrepToString().encode();entry=str(len(geometry))+'.brep';z.writestr(entry,raw)
            geometry.append(dict(name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    rows=[r for r in ends if r['group']=='NineWireCuffRL']
    specs={r['portion_id']:{k:profiles[r['portion_id']][k] for k in ('project_radius_mm','minimum_project_R_mm')} for r in rows}
    result=dict(status='RL9_CURVED_SOURCE_ROOTED_STATIC_SAMPLE36_RECEIVED_MOVING900_OPEN',
        N01_complete=False,physical_pass=False,native_changed=False,whole123_not_received=True,
        plan=plan,checks=checks,outer=outside,constructor_rows=rows,constructor_profiles=specs,
        sampled36_leg_vertical_separation_lower_bound_mm=zbound,
        full_moving_wire_and_head_tail_motion_NOT_received=True,
        geometry=geometry,bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),
        source_sha256={**changed['source_sha256'],Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
        worker_seconds=round(time.monotonic()-tick,3))
    save_json(path,result);return result
