"""One whole5-mouth restraint plan on the two existing U1 bolt axes.

Keep the proven nine upper seats. Four complete selected T18I envelopes
retain five separately backed9mm lands (the E2 pair has one common band).
Hollow printed stand-offs use the current PCB/arm datums and metal hardware;
no extra PCB holes, new purchased parts or unsupported native-N03 claims.
"""
import copy,gzip,hashlib,json,math,time,zipfile
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


def construct(fixed,root_clearance=False):
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
    fore=joined([box([-7.19,2,-30],[-5.19,27.47,-28]),box([-7.19,25.47,-30],[.38,27.47,-28])])
    if root_clearance:
        # The complete left head occupies X-7.12..-2.82, not empty space
        # next to the insulation. Root outside it, connect beyond its axial
        # end, and touch only the outer .75mm strip of the2mm saddle wall.
        fore=joined([box([-11.62,2,-30],[-9.62,27.47,-28]),
                     box([-11.62,1,-30],[-7.39,3,-28]),
                     box([-11.62,25.47,-30],[-.87,27.47,-28])])
    add('U1Relief:ForeRoot',fore,'PETG','fore')
    add('U1Relief:RearRoot',joined([box([28.37,2,-30],[30.37,27.47,-28]),
        box([8.81 if root_clearance else 7.56,25.47,-30],[30.37,27.47,-28]),box([6.27 if root_clearance else 5.02,1.47,-30],[30.37,3.47,-28]),
        box([28.37,2,-30],[30.37,7.825,-28]),box([28.37,5.825,-30],[46.5,7.825,-28]),
        box([44.5,-1.925,-30],[46.5,7.825,-28])]),'PETG','rear')
    return actors,metadata,dict(specs=specs,updates=updates,print_groups=pg,intended_insulation_mates=mates,lands=lands,
        PCB_arm_bearings=bearings,source_file=src.relative_to(ROOT).as_posix(),source_sha256={src.relative_to(ROOT).as_posix():sha(src),Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
        selected_T18I=4,printed_standoffs_not_extra_purchased_parts=2,source_wire_count=5,prefixes_not_complete225mm_Molex=True,
        separate_land_for_each_wire=True,roots_outside_whole_heads_and_own_jackets=root_clearance,N01_complete=False,native_changed=False,physical_pass=False)


def peripheral_construct(fixed,coupled=False):
    """After two pin-field rejections, move the WHOLE three-wire grip outside.

    One3-way open V-comb and flat pressure lid, not three heads underneath
    populated pads. Same selected HELU/R12.6; B2 bare form clocks round its
    own through-hole, B3 strip gains .3mm to give equal clamp heights.
    """
    actors,meta,r=construct(fixed,True)
    for n in list(actors):
        if n.startswith(('U1Relief:XS13:','U1Relief:XS23:','U1Relief:XS33:')) or n in ('U1Relief:ForeRoot','U1Relief:RearRoot'):
            actors.pop(n);meta.pop(n)
    r['print_groups']={k:[n for n in v if n in actors] for k,v in r['print_groups'].items()}
    r['intended_insulation_mates']={k:v for k,v in r['intended_insulation_mates'].items() if k in actors}
    def add(n,s,kind,group):
        assert s.isValid() and len(s.Solids)==1,n
        actors[n]=s;meta[n]=dict(kind=kind,print_group=group)
        if kind=='PETG':r['print_groups'][group].append(n)
    R=12.6;z=-28.55;centres=[-1.03,3.97,8.97]
    for w,x in zip(('XS13','XS23','XS33'),centres):
        eid=w+'/extra/start';s=r['specs'][eid];bare=copy.deepcopy(s['bare_parts']);p=A.Vector(*s['parts'][0]['start'])
        if w=='XS23':
            pad=A.Vector(*s['pad_world_mm']);rot=A.Rotation(A.Vector(0,0,1),180)
            for q in bare:
                for key in ('start','mid','end'):
                    if key in q:q[key]=list(pad+rot.multVec(A.Vector(*q[key])-pad))
            p=pad+rot.multVec(p-pad)
        sourcez=z-2 if coupled and w=='XS23' else z
        if abs(p.z-sourcez)>1e-6:
            dz=sourcez-p.z
            for key in ('start','mid','end'):bare[0][key][2]+=dz
            bare[1]['start'][2]+=dz;p.z=sourcez
        parts=[];t=A.Vector(0,1,0);offset=x-p.x
        if abs(offset)>1e-6:
            n=A.Vector(1 if offset>0 else -1,0,0);angle=math.acos(1-abs(offset)/(2*R))
            def turn(q,t,n):
                at=lambda a:q+t*(R*math.sin(a))+n*(R*(1-math.cos(a)))
                end=at(angle);parts.append(dict(kind='arc',start=list(q),mid=list(at(angle/2)),end=list(end),radius_mm=R));return end
            q=turn(p,t,n);d=t*math.cos(angle)+n*math.sin(angle);normal=t*math.sin(angle)-n*math.cos(angle)
            p=turn(q,d,normal)
        if coupled and w=='XS23':
            # Adjacent bare arcs at2.54mm pad pitch cannot share one source
            # plane with2.1mm jackets at the retained1.25mm margin. Put the
            # ENTIRE middle formed tail2mm below, then twoR12.6 arcs rise
            # to the common pressure plane. No smaller bare-wire gap.
            angle=math.acos(1-2/(2*R));n=A.Vector(0,0,1)
            def rise(q,t,n):
                at=lambda a:q+t*(R*math.sin(a))+n*(R*(1-math.cos(a)))
                end=at(angle);parts.append(dict(kind='arc',start=list(q),mid=list(at(angle/2)),end=list(end),radius_mm=R));return end
            q=rise(p,t,n);d=t*math.cos(angle)+n*math.sin(angle);normal=t*math.sin(angle)-n*math.cos(angle)
            p=rise(q,d,normal);assert abs(p.z-z)<1e-6
        assert abs(p.x-x)<1e-6 and p.y<40
        parts.extend([dict(kind='line',start=list(p),end=[x,40,z]),dict(kind='line',start=[x,40,z],end=[x,49,z])])
        s.update(parts=parts,bare_parts=bare,source_basis='Whole3 fan to common outside-PCB V-clamp, same named pad/R12.6/profile; B2 clock/B3 project strip budget')
        for kind,rows,rad in (('jacket',parts,1.05),('bare',bare,s['bare_radius_mm'])):
            n='U1Five:'+w+':'+kind;actors[n]=pipe(rows,rad);assert actors[n].isValid()
        r['updates'][eid].update(jacket_routing_point_mm=parts[0]['start'],routing_exit_mm=[x,49,z],routing_exit_axis=[0,1,0],
            jacket_grip9_mm=[[x,40,z],[x,49,z]],source_prefix_length_mm=sum(__import__('feline_source_saddles').segment(q).Length for q in parts),
            routing_boundary_status='WHOLE_THREE_PERIPHERAL_FAN_AND_COMMON9MM_CLAMP_NOT_RECEIVED')
        r['lands'][w]=dict(grip9_mm=[[x,40,z],[x,49,z]],pad='U1Relief:XSbundle:pad',lid='U1Relief:XSbundle:lid',
            band='U1Relief:XSbundle:band',individual_V9_and_equal_height_pressure_land=True)
    rad=1.05;vertex=z-rad*math.sqrt(2);bottom=vertex-2;lidbottom=z+rad;lidtop=lidbottom+2
    x0=centres[0]-rad*math.sqrt(2)-2;x1=centres[-1]+rad*math.sqrt(2)+2
    pad=joined([box([x0,40,bottom],[x1,49,z]),box([x0,40,z],[x0+2,49,lidbottom]),box([x1-2,40,z],[x1,49,lidbottom])])
    for x in centres:
        h=rad*math.sqrt(2)+.01;points=[A.Vector(x-h,39.99,z+.01),A.Vector(x,39.99,vertex),A.Vector(x+h,39.99,z+.01)]
        pad=pad.cut(Part.Face(Part.makePolygon(points+[points[0]])).extrude(A.Vector(0,9.02,0)))
    add('U1Relief:XSbundle:pad',pad,'PETG','fore')
    add('U1Relief:XSbundle:lid',box([x0,40,lidbottom],[x1,49,lidtop]),'PETG_lid','lid')
    band=box([x0-1.2,43.25,bottom-1.2],[x1+1.2,45.75,lidtop+1.2]).cut(box([x0,43.15,bottom],[x1,45.85,lidtop]))
    add('U1Relief:XSbundle:band',band,'T18I','fore')
    add('U1Relief:XSbundle:head',box([x1+1.2,42,(bottom+lidtop)/2-2.65],[x1+5.5,47,(bottom+lidtop)/2+2.65]),'T18I','fore')
    for suffix in ('pad','lid'):r['intended_insulation_mates']['U1Relief:XSbundle:'+suffix]=['U1Five:'+w+':jacket' for w in ('XS13','XS23','XS33')]
    y0=(fixed['Factory:W041'].BoundBox.YMax+1.25+38.75)/2;assert y0>=fixed['Factory:W041'].BoundBox.YMax+1.25 and y0+2<=40.75
    landing_faces=[f for f in fixed['LowerBay:ForePanel'].Faces if type(f.Surface).__name__=='Plane'
                   and abs(f.normalAt(0,0).z)>.99 and abs(f.CenterOfMass.z+42)<1e-5
                   and f.BoundBox.YMin>=28-1e-5 and f.Area>100]
    assert len(landing_faces)==1,'Locate the actual north floor land, not ForePanel bbox'
    landing_xmax=landing_faces[0].BoundBox.XMax
    columns=[]
    for a,b in ((x0,x0+2),(x1-2,x1)):
        # The north floor ends atX7.5 here. Extend the low right foot onto
        # that REAL face instead of leaving a post above an empty corner.
        columns.extend([box([a,y0,-43.3],[b,y0+2,lidbottom]),box([min(a-1,landing_xmax-2),y0-2,-43.3],[b+1,y0+2,-41.3])])
    root=joined(columns[:2]).fuse(joined(columns[2:]))
    # Two separate posts intentionally join through the common pad AND floor;
    # do not fake1Solid for their isolated union.
    for i,column in enumerate((joined(columns[:2]),joined(columns[2:]))):
        assert column.common(fixed['LowerBay:ForePanel']).Volume>5.,'Actual ForePanel foot missing'
        add('U1Relief:ForePost'+str(i),column,'PETG','fore')
    if coupled:
        r['named_grip_air_gaps']={f'U1Relief:ForePost{i}':['U1Five:'+w+':jacket' for w in ('XS13','XS23','XS33')] for i in (0,1)}
        r['named_structural_mates']={f'U1Relief:ForePost{i}':['U1Relief:XSbundle:lid'] for i in (0,1)}
    root=joined([box([28.37,3.2,-30],[30.37,7.825,-28]),box([28.37,5.825,-30],[46.25,7.825,-28]),
                 box([44.25,-1.925,-30],[46.25,7.825,-28])])
    add('U1Relief:RearRoot',root,'PETG','rear')
    r.update(status='PERIPHERAL_THREE_V_CLAMP_PLUS_E2_PLAN_NOT_RECEIVED',selected_T18I=2,
        changed_cause='Whole3 grip outside occupied PCB pin shadow; direct ForePanel feet, no through-pin long rails',
        common_V90_nominal_wire_radius_mm=rad,V_web_top_mm=5-2*rad*math.sqrt(2),V_floor_mm=2,
        clamp_pull_fit_and_lid_pressure_phase2=True,no_selected_bought_SKU_change=True,
        adjacent_bare_source_plane_coupled=coupled,foreign_and_bare_wire_margin_NOT_reduced=True)
    return actors,meta,r


def save(fixed,root_clearance=False,peripheral=False,coupled=False):
    tick=time.monotonic();actors,meta,r=peripheral_construct(fixed,coupled) if peripheral else construct(fixed,root_clearance)
    dest=OUT/('n01-U1-peripheral-coupled-plan.json' if coupled else 'n01-U1-peripheral-common-plan.json' if peripheral else 'n01-U1-common-restraints-rooted-plan.json' if root_clearance else 'n01-U1-common-restraints-plan.json');assert not dest.exists()
    archive=dest.with_suffix('.breps.zip');geometry=[]
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for n,s in actors.items():
            raw=s.exportBrepToString().encode();entry=str(len(geometry))+'.brep';z.writestr(entry,raw)
            geometry.append(dict(meta[n],name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    r.update(status='ONE_COMMON_U1_FIVE_RESTRAINTS_PLAN_WORLD_MOTION_ASSEMBLY_OPEN',geometry=geometry,
        bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),construction_worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,r);print(r['status'],len(actors),r['construction_worker_seconds'],flush=True);return r
