"""One whole5-mouth restraint plan on the two existing U1 bolt axes.

Keep the proven nine upper seats. Four complete selected T18I envelopes
retain five separately backed9mm lands (the E2 pair has one common band).
Hollow printed stand-offs use the current PCB/arm datums and metal hardware;
no extra PCB holes, new purchased parts or unsupported native-N03 claims.
"""
import copy,gzip,hashlib,json,time,zipfile
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from receive_feline_rrp_shared_height import load
from receive_feline_global_case_candidates import placement
from feline_source_restraint_plan import box,joined
from feline_atomic_save import save_json
from plan_feline_n01_shared import pipe
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from plan_feline_usb_service_bight import outer_margin
from plan_feline_pi_root_access import profile_gap


def open_seat(start,axis,side,radius,halfheight=None):
    """Full flat land, actual T18I1.2x2.5 band and5x4.3x5.3 head."""
    p=np.array(start,float);t=np.array(axis,float);u=np.array(side,float);v=np.cross(t,u)
    assert abs(t@u)<1e-7 and abs(np.linalg.norm(v)-1)<1e-7
    tf=placement(np.column_stack((t,u,v)),p);h=radius if halfheight is None else halfheight
    def placed(lo,hi):s=box(lo,hi);s.Placement=tf*s.Placement;return s
    pad=placed([0,radius,-h],[9,radius+2,h])
    band=placed([3.25,-radius-1.2,-h-1.2],[5.75,radius+3.2,h+1.2]).cut(
        placed([3.15,-radius,-h],[5.85,radius+2,h]))
    head=placed([2,radius+3.2,-2.65],[7,radius+7.5,2.65])
    assert abs(head.Volume-5*4.3*5.3)<1e-5
    assert band.fuse(head).isValid() and len(band.fuse(head).Solids)==1
    return dict(pad=pad,band=band,head=head)


def construct(fixed):
    src=OUT/'n01-U1-remaining-five-coupled-plan.json';r=json.loads(src.read_text());actors=load(r)
    metadata={g['name']:dict(g) for g in r['geometry']};specs=copy.deepcopy(r['specs']);updates=copy.deepcopy(r['updates'])
    pcb=fixed['Ref_Material_PWM1608NominalPCB_0_0'];pg={'fore':[],'rear':[]};mates={};lands={}
    def add(n,s,kind,group,wires=()):
        assert s.isValid() and len(s.Solids)==1,n
        actors[n]=s;metadata[n]=dict(kind=kind,print_group=group,wires=list(wires))
        if kind=='PETG':pg[group].append(n)
    # These are longer prefixes of the SAME selected physical conductors,
    # not added cable blanks. XS23 has27.97mm in its original first straight.
    for eid,s in specs.items():
        w=s['wire'];parts=s['parts']
        if w=='XS23':parts[0]['end'][1]=parts[0]['start'][1]-12.;parts[0]['length_mm']=12.
        elif w.startswith('XP'):parts[-1]['end'][0]=45.;parts[-1]['length_mm']=45.-parts[-1]['start'][0]
        else:continue
        n='U1Five:'+w+':jacket';actors[n]=pipe(parts,s['radius_mm'])
        q=np.array(parts[-1]['end']);p=np.array(parts[-1]['start']);d=(q-p)/np.linalg.norm(q-p)
        updates[eid].update(routing_exit_mm=q.tolist(),routing_exit_axis=d.tolist(),jacket_grip9_mm=[(q-9*d).tolist(),q.tolist()])
    for w,side,group in (('XS13',[-1,0,0],'fore'),('XS23',[1,0,0],'rear'),('XS33',[1,0,0],'rear')):
        eid=w+'/extra/start';u=updates[eid];p,q=[np.array(a) for a in u['jacket_grip9_mm']];d=(q-p)/9
        kit=open_seat(p,d,side,1.05);prefix='U1Relief:'+w+':'
        for k,s in kit.items():add(prefix+k,s,'PETG' if k=='pad' else 'T18I',group,[w])
        lands[w]=dict(grip9_mm=[p.tolist(),q.tolist()],pad=prefix+'pad',band=prefix+'band')
        for k in ('pad','band'):mates[prefix+k]=[('U1Five:'+w+':jacket')]
    a=updates['XP02.module/extra/end'];b=updates['XP03.module/extra/end'];z=(a['routing_exit_mm'][2]+b['routing_exit_mm'][2])/2
    half=abs(a['routing_exit_mm'][2]-b['routing_exit_mm'][2])/2+.925
    kit=open_seat([36,-4.35,z],[1,0,0],[0,1,0],.925,half)
    for k,s in kit.items():
        n='U1Relief:E2pair:'+k;add(n,s,'PETG' if k=='pad' else 'T18I','rear',['XP02.module','XP03.module'])
        if k in ('pad','band'):mates[n]=['U1Five:XP02.module:jacket','U1Five:XP03.module:jacket']
    for w in ('XP02.module','XP03.module'):
        lands[w]=dict(grip9_mm=[[36,-4.35,updates[w+'/extra/end']['routing_exit_mm'][2]],[45,-4.35,updates[w+'/extra/end']['routing_exit_mm'][2]]],
                      pad='U1Relief:E2pair:pad',band='U1Relief:E2pair:band',common_band_separate_backed_land=True)
    bearings={}
    for i,group in ((0,'fore'),(1,'rear')):
        arm=fixed['StructureReserve:U1CarrierArm'+str(i)];x=arm.BoundBox.Center.x;y=2.;z0=arm.BoundBox.ZMax-.5;z1=pcb.BoundBox.ZMin
        s=Part.makeCylinder(2.4,z1-z0,A.Vector(x,y,z0)).cut(Part.makeCylinder(1.2,z1-z0+.02,A.Vector(x,y,z0-.01)))
        n='U1Relief:Stand'+str(i);add(n,s,'PETG',group)
        assert s.common(arm).Volume>1.,'No actual existing arm bearing'
        bearings[n]=dict(existing_axis_mm=[x,y],PCB_bearing_Z_mm=z1,arm_Z_mm=arm.BoundBox.ZMax,
            height_between_arm_and_PCB_mm=z1-arm.BoundBox.ZMax,shaft_clearance_radius_mm=1.2,no_new_hardware=True)
    add('U1Relief:ForeRoot',joined([box([-7.19,2,-30],[-5.19,27.47,-28]),box([-7.19,25.47,-30],[.38,27.47,-28])]),'PETG','fore')
    add('U1Relief:RearRoot',joined([box([28.37,2,-30],[30.37,27.47,-28]),
        box([7.56,25.47,-30],[30.37,27.47,-28]),box([5.02,1.47,-30],[30.37,3.47,-28]),
        box([28.37,2,-30],[30.37,7.825,-28]),box([28.37,5.825,-30],[46.5,7.825,-28]),
        box([44.5,-1.925,-30],[46.5,7.825,-28])]),'PETG','rear')
    return actors,metadata,dict(specs=specs,updates=updates,print_groups=pg,intended_insulation_mates=mates,lands=lands,
        PCB_arm_bearings=bearings,source_file=src.relative_to(ROOT).as_posix(),source_sha256={src.relative_to(ROOT).as_posix():sha(src),Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
        selected_T18I=4,printed_standoffs_not_extra_purchased_parts=2,source_wire_count=5,prefixes_not_complete225mm_Molex=True,
        separate_land_for_each_wire=True,N01_complete=False,native_changed=False,physical_pass=False)


def save(fixed):
    tick=time.monotonic();actors,meta,r=construct(fixed);dest=OUT/'n01-U1-common-restraints-plan.json';assert not dest.exists()
    archive=dest.with_suffix('.breps.zip');geometry=[]
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for n,s in actors.items():
            raw=s.exportBrepToString().encode();entry=str(len(geometry))+'.brep';z.writestr(entry,raw)
            geometry.append(dict(meta[n],name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    r.update(status='ONE_COMMON_U1_FIVE_RESTRAINTS_PLAN_WORLD_MOTION_ASSEMBLY_OPEN',geometry=geometry,
        bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),construction_worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,r);print(r['status'],len(actors),r['construction_worker_seconds'],flush=True);return r
