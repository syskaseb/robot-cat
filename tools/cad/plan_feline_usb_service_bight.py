"""One whole spatial service bight, not another local spiral offset.

Use previously received underhung Pi pose and cached closed cells; four
analytic biarcs join BOTH full ends through one shared bay. Hard length/R
gates precede occupancy. No native changes or N01/physical acceptance.
"""
import io,json,math,time,zipfile,hashlib,os,sys
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from scipy.ndimage import distance_transform_edt,map_coordinates
from scipy.optimize import brentq
from scipy.spatial import cKDTree
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from feline_signed_voxels import deposit
from fit_feline_current_usb_space import pi_prefix,bus_prefix,biarc_join


def middle(p,t,q,u,w,v,sample=False):
    a=biarc_join(p,t,w,v,1.,sample);b=biarc_join(w,v,q,u,1.,sample)
    if a is None or b is None:return None
    return dict(arcs=a['arcs']+b['arcs'],length_mm=a['length_mm']+b['length_mm'],minimum_R_mm=min(a['minimum_R_mm'],b['minimum_R_mm']))


def outer_margin(shape,outer):
    assert outer.isValid() and outer.Solids and shape.isValid() and shape.Solids
    cut=shape.copy().cut(outer);assert cut.isNull() or cut.isValid()
    # A shell is intentionally not a SolidQueries operand. Here the shell
    # surface is exactly the required boundary-distance target.
    gap=float(shape.distToShape(outer.Shells[0])[0])
    return dict(ok=cut.Volume<1e-5 and gap>=3.25-1e-6,outside_mm3=cut.Volume,gap_mm=gap,minimum_mm=3.25)


def best_recipe(doc):
    usb=json.loads((OUT/'n01-physical-cable-contract.json').read_text())['usb'];b=doc['best']
    p,t,first,PL=pi_prefix(doc['Pi_pose']['USB_mouth_mm'],math.pi/2,b['Pi_clock_rad'])
    q,bt,last,BL=bus_prefix(usb['bus_jacket_mouth_mm'],math.pi/2,b['BUS_clock_rad'])
    j=middle(p,t,q,-bt,np.array(b['waypoint_mm']),np.array(b['tangent']),True)
    samples=np.vstack([first,*[r['points_mm'][::-1] if r['reverse'] else r['points_mm'] for r in j['arcs']],last[::-1]])
    return j,first,last,samples


def diagnose():
    source=OUT/'n01-spatial-service-bight-usb-plan.json';d=json.loads(source.read_text());j,first,last,points=best_recipe(d)
    sf=OUT/'n01-current-signed-space.json';old=json.loads(sf.read_text());fp=ROOT/old['field'];arc=ROOT/old['voxel_source_archive']
    # Owner names come from cached closed source cells. A supersetted mask
    # witness is NOT a positive Boolean contact or global infeasibility.
    with np.load(fp,allow_pickle=False) as f:
        origin=f['origin_mm'];fields={n:f[n] for n in ('rigid_signed_distance','motion36_signed_distance','outer_distance')}
    witnesses=[]
    for name,f in fields.items():
        gaps=map_coordinates(f,(points-origin).T,order=1,mode='constant',cval=-100);i=int(np.argmin(gaps))
        witnesses.append(dict(field=name,point_mm=points[i].tolist(),old_field_gap_mm=float(gaps[i]),occupied_mask_owners=[]))
    with zipfile.ZipFile(arc) as z:
        for name,row in old['parts'].items():
            if not name.startswith('Static:'):continue
            raw=z.read(row['entry']);assert hashlib.sha256(raw).hexdigest()==row['sha256']
            with np.load(io.BytesIO(raw),allow_pickle=False) as f:origin=f['origin'];mask=f['occupied']
            for w in witnesses:
                v=np.rint(np.array(w['point_mm'])-origin).astype(int)
                if np.all(v>=0) and np.all(v<mask.shape) and mask[tuple(v)]:w['occupied_mask_owners'].append(name)
    result=dict(status='SERVICE_BIGHT_CACHED_OWNER_WITNESSES_NOT_CONTACT_PROOF',source=source.relative_to(ROOT).as_posix(),source_sha256=sha(source),witnesses=witnesses,
        middle={k:v for k,v in j.items() if k!='arcs'},arcs=[{k:v for k,v in r.items() if k!='points_mm'} for r in j['arcs']],N01_complete=False)
    save_json(OUT/'n01-service-bight-mask-witnesses.json',result);print(json.dumps(result),flush=True)


def underbank_candidate(phi,L,pose,usb,sample=True,plateau=False):
    p=np.array(pose['USB_mouth_mm']);t=np.array([-1.,0,0]);steps=[];points=[p.copy()]
    def line(length):
        nonlocal p
        if length< -1e-7:return False
        if length<1e-8:return True
        q=p+length*t;steps.append(dict(kind='line',start=p.tolist(),end=q.tolist(),length_mm=length))
        if sample:points.extend(p+v*(q-p) for v in np.linspace(0,1,max(2,int(math.ceil(length/.2))+1))[1:])
        p=q;return True
    def turn(n,angle):
        nonlocal p,t
        n=np.array(n);assert abs(n@t)<1e-7
        at=lambda a:p+30*math.sin(a)*t+30*(1-math.cos(a))*n
        q=at(angle);steps.append(dict(kind='arc',start=p.tolist(),tangent=t.tolist(),normal=n.tolist(),R_mm=30.,angle_rad=angle,length_mm=30*angle))
        if sample:points.extend(at(v) for v in np.linspace(0,angle,max(2,int(math.ceil(30*angle/.2))+1))[1:])
        p=q;t=math.cos(angle)*t+math.sin(angle)*n
    b=np.array([0.,-math.sin(phi),-math.cos(phi)])
    line(12);Pi_grip=[(np.array(pose['USB_mouth_mm'])+[-3,0,0]).tolist(),p.tolist()]
    if plateau:
        # Cross the bank/frame gap HORIZONTALLY: diagonal source chords
        # cannot pass both bank bottom55 and side-frame top38.52. This
        # changes the whole departure topology, not its scalar position.
        turn([0,0,-1],phi);turn([0,-1,0],math.pi/2)
        turn([0,0,-1],math.pi/2);line(L);turn([1,0,0],math.pi/2)
    else:turn(b,math.pi/2);line(L);turn([1,0,0],math.pi/2)
    if not line(usb['bus_jacket_mouth_mm'][0]-30-p[0]):return None
    turn([0,0,1],math.pi/2)
    target=np.array(usb['bus_jacket_mouth_mm'])+[0,-42,-30]
    shift=target[1]-p[1];angle=math.acos(1-abs(shift)/60) if abs(shift)<120 else math.nan
    if not math.isfinite(angle):return None
    if angle>1e-8:
        normal=np.array([0.,math.copysign(1.,shift),0]);turn(normal,angle)
        normal=np.array([0,0,1.])-math.cos(angle)*t;normal/=np.linalg.norm(normal);turn(normal,angle)
    if not line(target[2]-p[2]):return None
    assert np.linalg.norm(p-target)<1e-6
    # Reverse the BUS's12mm straight plus R30 downwards bend. The full9
    # land is BEFORE the bend; no additional grip or factory wire invented.
    turn([0,1,0],math.pi/2);line(12)
    assert np.linalg.norm(p-usb['bus_jacket_mouth_mm'])<1e-6 and np.allclose(t,[0,1,0])
    return dict(Pi_pose=pose,phi_deg=math.degrees(phi),side_straight_mm=L,steps=steps,samples=np.array(points),
        whole_external_length_mm=sum(r['length_mm'] for r in steps),R_mm=30.,Pi_full9_mm=Pi_grip,
        BUS_full9_mm=[(np.array(usb['bus_jacket_mouth_mm'])+[0,-12,0]).tolist(),(np.array(usb['bus_jacket_mouth_mm'])+[0,-3,0]).tolist()])


def plan_underbank():
    tick=time.monotonic();src=OUT/'n01-spatial-service-bight-usb-plan.json';prior=json.loads(src.read_text());pose=prior['Pi_pose'];usb=json.loads((OUT/'n01-physical-cable-contract.json').read_text())['usb']
    plateau='--frame-bank-gap-U' in sys.argv
    dest=OUT/('n01-frame-bank-gap-side-U-usb-plan.json' if plateau else 'n01-underbank-side-U-usb-plan.json');assert not dest.exists();candidates=[]
    angles=[82.5] if plateau else np.linspace(18,36,37)
    for phi in np.radians(angles):
        found=[]
        for L in (np.linspace(0,100,101) if plateau else np.linspace(20,130,111)):
            c=underbank_candidate(float(phi),float(L),pose,usb,False,plateau)
            if c:found.append((L,c['whole_external_length_mm']-452))
        for (a,da),(b,db) in zip(found,found[1:]):
            if da*db>0 or b-a>1.00001:continue
            try:root=brentq(lambda x:underbank_candidate(float(phi),x,pose,usb,False,plateau)['whole_external_length_mm']-452,a,b,xtol=1e-10)
            except TypeError:continue # invalid interior breaks a bracket; NOT infeasibility
            c=underbank_candidate(float(phi),root,pose,usb,True,plateau);points=c.pop('samples')
            along=np.r_[0,np.cumsum(np.linalg.norm(np.diff(points,axis=0),axis=1))];pairs=cKDTree(points).query_pairs(5.5,output_type='ndarray')
            bad=pairs[np.abs(along[pairs[:,0]]-along[pairs[:,1]])>12] if len(pairs) else pairs
            c.update(sampled_self_clear=not len(bad),bounds_mm=[points.min(0).tolist(),points.max(0).tolist()])
            if len(bad):continue
            # Necessary gross contour bounds only. True rounded skin, all
            # parts and36motion still need exact qualification.
            floor=float(points[:,2].min()+48-5.75);side=float(100-abs(points[:,1]).max()-5.75)
            c['gross_floor_side_residual_mm']=min(floor,side)
            candidates.append(c)
    candidates.sort(key=lambda c:c['gross_floor_side_residual_mm'],reverse=True)
    result=dict(status='UNDERBANK_SIDE_U_MATH_CANDIDATES_EXACT_GATES_OPEN' if candidates else 'UNDERBANK_SIDE_U_NO_MATH_CANDIDATE',
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (src,OUT/'n01-physical-cable-contract.json',Path(__file__))},candidate=candidates[0] if candidates else None,
        alternatives=[{k:c[k] for k in ('phi_deg','side_straight_mm','bounds_mm','gross_floor_side_residual_mm')} for c in candidates],worker_seconds=round(time.monotonic()-tick,3),
        N01_complete=False,selected=False,physical_pass=False,both_full9_grips_before_bends=True,individual_radii_not_reduced=True)
    save_json(dest,result);print(json.dumps({k:result[k] for k in ('status','worker_seconds','alternatives')}),flush=True)


def receive_best():
    from feline_common_space_context import current,is_jacket
    from receive_feline_positive_service_deck import circle_arc,pipe
    from feline_fore_power_pair import SolidQueries,pair_spacing
    from feline_solid_distance import bbox_lower_bound
    tick=time.monotonic();plateau='--receive-frame-bank-gap' in sys.argv;under='--receive-underbank' in sys.argv or plateau;source=OUT/('n01-frame-bank-gap-side-U-usb-plan.json' if plateau else 'n01-underbank-side-U-usb-plan.json' if under else 'n01-spatial-service-bight-usb-plan.json');doc=json.loads(source.read_text())
    usb=json.loads((OUT/'n01-physical-cable-contract.json').read_text())['usb'];edges=[]
    def prefix(mouth,d,clock):
        n=np.array([0,math.cos(clock),math.sin(clock)]) if d[0] else np.array([math.cos(clock),0,math.sin(clock)])
        p=np.array(mouth);d=np.array(d);land=p+3*d;end=land+30*d+30*n
        return [Part.makeLine(A.Vector(*p),A.Vector(*land)),circle_arc(land,d,n,30,math.pi/2),Part.makeLine(A.Vector(*end),A.Vector(*(end+9*n)))]
    if under:
        for r in doc['candidate']['steps']:
            edges.append(Part.makeLine(A.Vector(*r['start']),A.Vector(*r['end'])) if r['kind']=='line' else circle_arc(r['start'],r['tangent'],r['normal'],30,r['angle_rad']))
    else:
        j,first,last,points=best_recipe(doc);b=doc['best'];edges+=prefix(doc['Pi_pose']['USB_mouth_mm'],[-1,0,0],b['Pi_clock_rad'])
        for a in j['arcs']:
            e=circle_arc(a['start_mm'],a['start_tangent'],a['normal'],a['R_mm'],a['angle_rad'])
            if a['reverse']:e.reverse()
            edges.append(e)
        for e in prefix(usb['bus_jacket_mouth_mm'],[0,-1,0],b['BUS_clock_rad'])[::-1]:e=e.copy();e.reverse();edges.append(e)
    shape,path=pipe(edges,2.5);assert abs(path.Length-452)<1e-6
    world,parts,meta,pins,docs=current();own={n for n in parts if meta[n].get('group')=='PiUpper'}
    for n in own:parts.pop(n)
    lower=json.loads((OUT/'n01-usb-fore-lower-deck-space.json').read_text())
    for n in lower['changed_owners']:parts[n]=parts[n].copy();parts[n].translate(A.Vector(0,0,-8))
    priorfile=OUT/'n01-fore-coil-service-deck-received.json';prior=json.loads(priorfile.read_text());bundle=ROOT/prior['changed_geometry_archive']
    with zipfile.ZipFile(bundle) as z:
        for row in prior['geometry']:
            if row['role']!='PiRigid':continue
            raw=z.read(row['entry']);assert hashlib.sha256(raw).hexdigest()==row['sha256'];s=Part.Shape();s.importBrepFromString(raw.decode());parts[row['name']]=s;meta[row['name']]=dict(kind='project_rigid_Pi_budget')
    for n in list(parts):
        if n.startswith('CurrentBUS:USB_C') and is_jacket(n,meta[n]):parts.pop(n)
    query=SolidQueries();dest=OUT/('n01-frame-bank-gap-whole-usb-received.json' if plateau else 'n01-underbank-side-U-whole-usb-received.json' if under else 'n01-service-bight-whole-usb-received.json')
    previous=None
    if dest.exists():
        assert '--resume-empty-shell-error' in sys.argv
        previous=json.loads(dest.read_text());assert previous['errors']==["AssertionError('Invalid source is not clearance')"] and not previous['checks']
        own=Path(__file__).relative_to(ROOT).as_posix();newpins={**pins,**{p.relative_to(ROOT).as_posix():sha(p) for p in (source,priorfile,bundle,Path(__file__))}}
        assert all(p==own or h==newpins[p] for p,h in previous['source_sha256'].items())
    piece_bounds=[]
    for e in edges:
        b=e.BoundBox;piece_bounds.append(A.BoundBox(b.XMin-2.50001,b.YMin-2.50001,b.ZMin-2.50001,b.XMax+2.50001,b.YMax+2.50001,b.ZMax+2.50001))
    near=lambda b:any(bbox_lower_bound(p,b)<1.25 for p in piece_bounds)
    result=dict(status='RUNNING_SERVICE_BIGHT_ACTUAL_PAIRS',source_sha256={**pins,**{p.relative_to(ROOT).as_posix():sha(p) for p in (source,priorfile,bundle,Path(__file__))}},
        length_mm=path.Length,volume_mm3=shape.Volume,expected_volume_mm3=math.pi*2.5**2*452,checks={},failures=[],errors=[],selected=False,N01_complete=False,
        Pi_new_seven_prefixes_roots_full_grips_head_motion_capacity_and_enclosure_OPEN=True,host_mouth_fit_OPEN=['PiBudget:USB_A_data_boot','CurrentBUS:USB_C_Overmould'],
        broadphase='Union of whole axis EDGE boxes inflated by actual2.50001radius; empty global bbox never a collision')
    def save():result['worker_seconds']=round(time.monotonic()-tick,3);save_json(dest,result)
    if previous:result.update(previous_empty_shell_error_receipt=previous,only_controller_shell_distance_fix=True,no_completed_exact_pairs_replayed=True)
    else:
        with zipfile.ZipFile(dest.with_suffix('.breps.zip'),'x',zipfile.ZIP_DEFLATED) as z:z.writestr('USB500.brep',shape.exportBrepToString())
    result['geometry_bundle_sha256']=sha(dest.with_suffix('.breps.zip'))
    try:
        outer=Part.Shape();outer.read(str(OUT/'n01-six-source-shared-lanes.outer.brep'));r=outer_margin(shape,outer)
        result['checks']['outer']=r
        if not r['ok']:result['failures'].append(dict(owner='outer',**r))
        save()
        for n,s in parts.items():
            if not near(s.BoundBox):continue
            if n in ('PiBudget:USB_A_data_boot','CurrentBUS:USB_C_Overmould'):continue # source contact only; full host fit OPEN
            if not s.Solids:r=dict(ok=False,reason='Existing curve-only reservation; not actual solid collision')
            else:
                q=shape
                if n==world.bus['name']:q=shape.copy();q.Placement=world.bus['inverse']*q.Placement;s=world.bus['original']
                minimum=pair_spacing('USB500:whole',dict(kind='proposal_wire'),n,meta[n]);gap=query.distance(q,s);r=dict(ok=gap>=minimum-1e-6,gap_mm=gap,minimum_mm=minimum)
            result['checks'][n]=r
            if not r['ok']:result['failures'].append(dict(owner=n,**r))
            save()
            if time.monotonic()-tick>220:raise TimeoutError('Completed exact pairs saved, not full verdict')
        from receive_feline_global_case_candidates import placement
        for p in world.motion:
            if not near(A.BoundBox(*p['bounds'][0],*p['bounds'][1])):continue
            q=shape.copy();q.Placement=placement(p['r'],p['t']).inverse()*q.Placement;gap=query.distance(q,world.rest[p['name']]);r=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25)
            name='Motion:'+p['name']+':'+str(p['pose']);result['checks'][name]=r
            if not r['ok']:result['failures'].append(dict(owner=name,**r))
            save()
            if time.monotonic()-tick>220:raise TimeoutError('Completed exact pairs saved, not full verdict')
        result['status']='SERVICE_BIGHT_FIXED_PARTS_RECEIVED_OTHER_GATES_OPEN' if not result['failures'] else 'SERVICE_BIGHT_NAMED_INTERFACES_OPEN'
    except Exception as exc:result['errors'].append(repr(exc));result['status']='SERVICE_BIGHT_PARTIAL_OR_ERROR'
    save();print(json.dumps(dict(status=result['status'],seconds=result['worker_seconds'],pairs=len(result['checks']),failures=result['failures'],errors=result['errors'])),flush=True)


def receive_two_level_pi():
    """Whole occupied rigid Pi below a separately allocated service layer.

    Not a third offset of the old coil: components face DOWN below91mm PCB,
    the central USB service bay is100.7mm. Real connector boots move together.
    Seven new flexible ends, roots and whole USB remain explicit OPEN gates.
    """
    from feline_common_space_context import current
    from feline_fore_power_pair import SolidQueries,pair_spacing
    from feline_solid_distance import bbox_lower_bound
    coupled='--coupled-two-level' in sys.argv
    tick=time.monotonic();dest=OUT/('n01-coupled-Pi-BUS-two-level-received.json' if coupled else 'n01-two-level-Pi-rigid-received.json');assert not dest.exists()
    world,parts,meta,pins,docs=current();priorfile=OUT/'n01-fore-coil-service-deck-received.json';prior=json.loads(priorfile.read_text());bundle=ROOT/prior['changed_geometry_archive'];assert sha(bundle)==prior['changed_geometry_archive_sha256']
    own={n for n in parts if meta[n].get('group')=='PiUpper'};fixed={n:s for n,s in parts.items() if n not in own};changed={}
    offset=A.Vector(-2.5,-12,-11 if coupled else -13);roles={}
    with zipfile.ZipFile(bundle) as z:
        for row in prior['geometry']:
            if row['role']!='PiRigid':continue
            raw=z.read(row['entry']);assert hashlib.sha256(raw).hexdigest()==row['sha256'];s=Part.Shape();s.importBrepFromString(raw.decode());s.translate(offset);assert s.isValid() and s.Solids
            changed[row['name']]=s;roles[row['name']]='PiRigid'
    retired=[];bus_move=None;bus_source=None;bus_inverse=None
    if coupled:
        # BUS components face the rear, not the Pi. Move the COMPLETE board,
        # occupied H5 and USB mouths and existing source leads together.
        # Old printed full backplate/arms are explicitly not carried over:
        # a new rear-side edge frame requires its own constructive root gate.
        rot=A.Rotation(A.Vector(0,0,1),180);pivot=A.Vector(126,0,75);bus_move=A.Placement(pivot+A.Vector(5,0,0)-rot.multVec(pivot),rot)
        keep={'CurrentBUS:H5MatingReserve','CurrentBUS:USB_C_Overmould','CurrentBUS:DGSharedRelief'}
        for n in list(fixed):
            if meta[n].get('role')!='BUS' and not n.startswith('CurrentBUS:'):continue
            if n.startswith('CurrentBUS:') and meta[n].get('kind') not in ('wire','actual_wire') and n not in keep:
                retired.append(n);fixed.pop(n);continue
            s=fixed.pop(n).copy()
            if n==world.bus['name']:
                # This world-posed cache is only a BROADPHASE bbox proxy.
                # Never query/repair it. All exact queries use the VALID
                # original with the OTHER operand inverse-placed instead.
                bus_source=world.bus['original'];assert bus_source.isValid() and bus_source.Solids
                bus_inverse=world.bus['inverse']*bus_move.inverse()
            s.Placement=bus_move*s.Placement
            if n!=world.bus['name']:assert s.isValid() and s.Solids,n
            changed[n]=s;roles[n]='BUSRigid'
    lowerfile=OUT/'n01-usb-fore-lower-deck-space.json';lower=json.loads(lowerfile.read_text())
    for n in lower['changed_owners']:fixed[n]=fixed[n].copy();fixed[n].translate(A.Vector(0,0,-8))
    pose=dict(prior['Pi_pose']);pose['target_PCB_centre_mm']=[83.5,-10.,93. if coupled else 91.];pose['USB_mouth_mm']=(np.array(pose['USB_mouth_mm'])+np.array(list(offset))).tolist()
    outer=Part.Shape();outer.read(str(OUT/'n01-six-source-shared-lanes.outer.brep'));query=SolidQueries()
    result=dict(status='RUNNING_TWO_LEVEL_WHOLE_PI_RIGID',source_sha256={**pins,**{p.relative_to(ROOT).as_posix():sha(p) for p in (priorfile,bundle,lowerfile,Path(__file__))}},
        Pi_pose=pose,PCB_Z_mm=pose['target_PCB_centre_mm'][2],planned_USB_bay_Z_mm=103. if coupled else 100.7,changed_parts=list(changed),checks={},failures=[],errors=[],
        BUS_whole_relative_pose='180deg Z about[126,0,75] then+5X' if coupled else None,retired_printed_BUS_supports=retired,
        BUS_rear_edge_frame_and_all_retention_roots_OPEN=coupled,
        selected=False,N01_complete=False,physical_pass=False,seven_flexible_ends_full_USB_root_and_service_OPEN=True)
    archive=dest.with_suffix('.breps.zip');result['geometry']=[]
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
        for i,(name,s) in enumerate(changed.items()):
            original=bus_source if coupled and name==world.bus['name'] else s
            raw=original.exportBrepToString().encode();entry=str(i)+'.brep';z.writestr(entry,raw);row=dict(name=name,entry=entry,sha256=hashlib.sha256(raw).hexdigest(),role=roles[name])
            if coupled and name==world.bus['name']:row.update(stored_in_valid_original_frame=True,world_to_original_matrix=bus_inverse.toMatrix().A,world_bbox_proxy_never_used_for_exact_query=True)
            result['geometry'].append(row)
    result['changed_geometry_archive']=archive.relative_to(ROOT).as_posix();result['changed_geometry_archive_sha256']=sha(archive)
    def save():result['worker_seconds']=round(time.monotonic()-tick,3);save_json(dest,result)
    save()
    try:
        for name,s in changed.items():
            if coupled and name==world.bus['name']:
                q=outer.copy();q.Placement=bus_inverse*q.Placement;r=outer_margin(bus_source,q)
            else:r=outer_margin(s,outer)
            result['checks'][name+'|outer']=r
            if not r['ok']:result['failures'].append(dict(a=name,b='outer',**r))
            targets={**fixed,**{n:t for n,t in changed.items() if roles[n]!=roles[name]}}
            for n,t in targets.items():
                if bbox_lower_bound(s.BoundBox,t.BoundBox)>=1.25:continue
                if not t.Solids:r=dict(ok=False,reservation_only=True,reason='Curve-only existing source, not material contact')
                else:
                    q=s
                    if coupled and name==world.bus['name']:
                        q=t.copy();q.Placement=bus_inverse*q.Placement;t=bus_source
                    elif n==world.bus['name']:
                        q=s.copy();q.Placement=(bus_inverse if coupled else world.bus['inverse'])*q.Placement;t=bus_source if coupled else world.bus['original']
                    minimum=pair_spacing(name,meta.get(name,{}),n,meta.get(n,{}))
                    gap=query.distance(q,t);r=dict(ok=gap>=minimum-1e-6,gap_mm=gap,minimum_mm=minimum)
                result['checks'][name+'|'+n]=r
                if not r['ok']:result['failures'].append(dict(a=name,b=n,**r))
                if time.monotonic()-tick>190:raise TimeoutError('Completed rigid-pose pairs saved')
            save()
        result['status']='TWO_LEVEL_PI_RIGID_RECEIVED_FLEX_ROOTS_USB_OPEN' if not result['failures'] else 'TWO_LEVEL_PI_NAMED_INTERFACES_OPEN'
    except Exception as exc:result['errors'].append(repr(exc));result['status']='TWO_LEVEL_PI_PARTIAL_OR_ERROR'
    save();print(json.dumps(dict(status=result['status'],seconds=result['worker_seconds'],pairs=len(result['checks']),failures=result['failures'],errors=result['errors'])),flush=True)


def rear_coil(turns,sample=False):
    """Fixed R35 rear bay with smooth axial separation, not a flat coil.

    x is cubic smoothstep; yz is a circle. A conservative continuous
    curvature bound follows |v cross a| <= |v||a| and |v| >= R*T.
    """
    R=35.;C=71.2;T=2*math.pi*turns
    phi=math.asin((98.7-C)/math.hypot(R,39))-math.atan2(39,R)
    u,w=np.polynomial.legendre.leggauss(32);u=(u+1)/2
    length=float(np.sum(w*np.sqrt((54*u*(1-u))**2+(R*T)**2))/2)
    at=lambda u:np.array([145-9*(3*u*u-2*u*u*u),R*math.cos(phi-T*u),C+R*math.sin(phi-T*u)])
    beta=phi-T;tangent=np.array([0.,math.sin(beta),-math.cos(beta)])
    return dict(start=at(0),end=at(1),tangent=tangent,length=length,
        continuous_minimum_R_lower_bound_mm=1/math.sqrt(1/R**2+(54/(R**2*T**2))**2),
        points=np.array([at(v) for v in np.linspace(0,1,401)]) if sample else None,phase=phi)


def plan_rear_bay():
    """ONE shared architecture's whole-length constructor gate, no world PASS."""
    tick=time.monotonic();dest=OUT/'n01-rear-service-bay-whole-usb-plan.json';assert not dest.exists()
    files=[OUT/'n01-physical-cable-contract.json',OUT/'n01-active-Pi-BUS-datums.json',
           OUT/'n01-fore-coil-service-deck-received.json',OUT/'n01-usb-fore-lower-deck-space.json',Path(__file__)]
    usb=json.loads(files[0].read_text())['usb'];bus=np.array(usb['bus_jacket_mouth_mm']);q=bus+[0,-12,0];incoming=np.array([0.,1,0])
    base=rear_coil(1);phi=base['phase'];bend=np.array([0.,math.sin(phi),-math.cos(phi)])
    my=35*math.cos(phi)-39*math.sin(phi);mouth=np.array([112.,my,98.7]);first=mouth+[3,0,0]
    arcend=first+[30,0,0]+30*bend;landend=arcend+9*bend
    assert np.linalg.norm(landend-base['start'])<1e-8
    prefix_length=12+30*math.pi/2
    result=dict(status='RUNNING_REAR_SHARED_BAY_LENGTH_GATE',source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in files},
        Pi_PCB_centre_mm=[40.5,my-19.39,104],Pi_USB_mouth_mm=mouth.tolist(),Pi_departure_axis=[1,0,0],
        source_first3_mm=[mouth.tolist(),first.tolist()],source_R30_bend_unit=bend.tolist(),
        source_full9_mm=[arcend.tolist(),landend.tolist()],BUS_full9_after_first3_mm=[(bus+[0,-3,0]).tolist(),q.tolist()],
        BUS_whole_pose_unchanged=True,whole_FR_P_RR_P_kit_translation_mm=[0,0,-8],
        rear_bay=dict(R_mm=35.,centre_YZ_mm=[0,71.2],start_X_mm=145,end_X_mm=136,axial_profile='9mm cubic smoothstep'),
        target_jacket_mm=452,minimum_fixed_R_mm=30,tested=0,length_roots=0,hard_R30_survivors=0,
        sampled_self_clear=0,candidate=None,best_minimum_R_mm=0,selected=False,N01_complete=False,physical_pass=False,
        all_actual_parts_root_tool_motion_and_true_outer_gates_OPEN=True)
    ratios=np.logspace(-2,2,61)
    for turns in np.linspace(1.,1.5,101):
        c=rear_coil(turns);previous=None
        def join(r):return biarc_join(c['end'],c['tangent'],q,incoming,r,False)
        def total(j):return prefix_length+c['length']+j['length_mm']+12
        for ratio in ratios:
            j=join(ratio);result['tested']+=1
            if j is None:previous=None;continue
            delta=total(j)-452
            if previous is not None and delta*previous[1]<0:
                try:root=brentq(lambda r:total(join(r))-452,previous[0],ratio,xtol=1e-10);j=join(root)
                except (ValueError,TypeError,ZeroDivisionError):previous=(ratio,delta);continue
                result['length_roots']+=1;radius=min(30,c['continuous_minimum_R_lower_bound_mm'],j['minimum_R_mm'])
                result['best_minimum_R_mm']=max(result['best_minimum_R_mm'],radius)
                if radius<30-1e-7:previous=(ratio,delta);continue
                result['hard_R30_survivors']+=1;c=rear_coil(turns,True);j=biarc_join(c['end'],c['tangent'],q,incoming,root,True)
                ang=np.linspace(0,math.pi/2,100);pre=first+30*np.sin(ang[:,None])*[1,0,0]+30*(1-np.cos(ang[:,None]))*bend
                pts=np.vstack([mouth,first,pre,np.linspace(arcend,landend,20),c['points'],
                    *[r['points_mm'][::-1] if r['reverse'] else r['points_mm'] for r in j['arcs']],np.linspace(q,bus,25)])
                along=np.r_[0,np.cumsum(np.linalg.norm(np.diff(pts,axis=0),axis=1))];pairs=cKDTree(pts).query_pairs(5.2,output_type='ndarray')
                if len(pairs) and np.any(np.abs(along[pairs[:,0]]-along[pairs[:,1]])>12):previous=(ratio,delta);continue
                result['sampled_self_clear']+=1
                if np.any(pts.min(axis=0)<np.array([-141.5,-100,-48])+5.75) or np.any(pts.max(axis=0)>np.array([183.5,100,112])-5.75):previous=(ratio,delta);continue
                result['candidate']=dict(turns=float(turns),tail_ratio=root,whole_length_mm=total(j),minimum_R_mm=radius,
                    coil_continuous_R_lower_bound_mm=c['continuous_minimum_R_lower_bound_mm'],tail_arcs=[{k:v for k,v in r.items() if k!='points_mm'} for r in j['arcs']],
                    coil_length_mm=c['length'],points_mm=pts.tolist(),sampled_self_clear_NOT_continuous_proof=True)
                break
            previous=(ratio,delta)
        if result['candidate']:break
    result.update(status='REAR_BAY_WHOLE_MATH_PROPOSAL_WORLD_OPEN' if result['candidate'] else 'REAR_BAY_LENGTH_JOIN_REJECTED_NOT_GLOBAL_INFEASIBILITY',worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,result);print(json.dumps({k:v for k,v in result.items() if k not in ('source_sha256','candidate')}),flush=True)
    if result['candidate']:print(json.dumps({k:v for k,v in result['candidate'].items() if k not in ('points_mm','tail_arcs')}),flush=True)


def plan_joint_rear_bay(tail_mm=12):
    """Analytic shared receiver: BUS moves as a WHOLE with its occupied ends.

    No further tail ratio search. Full cable closes by a tangent12mm BUS
    land; derive board placement from the actual PCB datum and USB mouth.
    """
    from scipy.interpolate import make_interp_spline
    from feline_cubic_curvature import extrema
    from receive_feline_positive_service_deck import circle_arc,pipe
    tick=time.monotonic();dest=OUT/('n01-joint-rear-boot-budget-plan.json' if tail_mm>12 else 'n01-joint-rear-service-bay-plan.json');assert not dest.exists()
    files=[OUT/'n01-physical-cable-contract.json',OUT/'n01-active-Pi-BUS-datums.json',
           OUT/'n01-fore-coil-service-deck-received.json',OUT/'n01-usb-fore-lower-deck-space.json',Path(__file__)]
    usb=json.loads(files[0].read_text())['usb'];datums=json.loads(files[1].read_text())
    bus_datum=np.mean([f['centre_mm'] for f in datums['boards'][1]['large_plane_faces']],axis=0)
    oldmouth=np.array(usb['bus_jacket_mouth_mm'])
    R=36.5;cy=-12.;cz=69.7;x0=145.;x1=136.+oldmouth[0]-bus_datum[0];D=x0-x1
    phi=math.asin((98.7-cz)/math.hypot(R,39))+math.atan2(39,R)
    bend=np.array([0.,-math.sin(phi),math.cos(phi)])
    my=cy+R*math.cos(phi)+39*math.sin(phi);mouth=np.array([112.,my,98.7]);first=mouth+[3,0,0]
    arcend=first+[30,0,0]+30*bend;landend=arcend+9*bend
    nodes,weights=np.polynomial.legendre.leggauss(48);u=(nodes+1)/2
    length=lambda turns:float(np.sum(weights*np.sqrt((6*D*u*(1-u))**2+(R*2*math.pi*turns)**2))/2)
    assert tail_mm>=12
    prefix=12+30*math.pi/2;turns=brentq(lambda t:prefix+length(t)+tail_mm-452,1.,2.,xtol=1e-12);T=turns*2*math.pi
    at=lambda u:np.array([x0-D*(3*u*u-2*u*u*u),cy+R*math.cos(phi+T*u),cz+R*math.sin(phi+T*u)])
    derivative=lambda u:np.array([-6*D*u*(1-u),-R*T*math.sin(phi+T*u),R*T*math.cos(phi+T*u)])
    assert np.linalg.norm(at(0)-landend)<1e-8
    t=derivative(1);t/=np.linalg.norm(t);newmouth=at(1)+tail_mm*t
    angle=math.degrees(math.atan2(t[2],t[1]));rot=A.Rotation(A.Vector(1,0,0),angle)
    tf=A.Placement(A.Vector(*newmouth)-rot.multVec(A.Vector(*oldmouth)),rot)
    newdatum=tf.multVec(A.Vector(*bus_datum));assert abs(newdatum.x-136)<1e-7
    v=np.linspace(0,1,401);points=np.array([at(z) for z in v])
    spline=make_interp_spline(v,points,k=3,bc_type=([(1,derivative(0))],[(1,derivative(1))]))
    curvature=extrema(spline.t,spline.c);assert curvature['regular'] and curvature['minimum_radius_mm']>=30
    knots,mults=np.unique(spline.t,return_counts=True);curve=Part.BSplineCurve()
    curve.buildFromPolesMultsKnots([A.Vector(*p) for p in spline.c],mults.tolist(),knots.tolist(),False,3)
    edges=[Part.makeLine(A.Vector(*mouth),A.Vector(*first)),circle_arc(first,[1,0,0],bend,30,math.pi/2),
        Part.makeLine(A.Vector(*arcend),A.Vector(*landend)),curve.toShape(),Part.makeLine(A.Vector(*at(1)),A.Vector(*newmouth))]
    shape,path=pipe(edges,2.5);assert abs(path.Length-452)<1e-4
    ang=np.linspace(0,math.pi/2,101);pre=first+30*np.sin(ang[:,None])*[1,0,0]+30*(1-np.cos(ang[:,None]))*bend
    pts=np.vstack([mouth,first,pre,np.linspace(arcend,landend,30),points,np.linspace(at(1),newmouth,30)])
    along=np.r_[0,np.cumsum(np.linalg.norm(np.diff(pts,axis=0),axis=1))];pairs=cKDTree(pts).query_pairs(5.2,output_type='ndarray')
    selfbad=bool(len(pairs) and np.any(np.abs(along[pairs[:,0]]-along[pairs[:,1]])>12))
    result=dict(status='JOINT_REAR_WHOLE_USB_CONSTRUCTOR_RECEIVED_WORLD_OPEN' if not selfbad else 'JOINT_REAR_USB_SAMPLED_SELF_CONTACT_REJECTED',
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in files},selected=False,N01_complete=False,physical_pass=False,
        Pi_PCB_centre_mm=[40.5,my-19.39,104.],Pi_USB_mouth_mm=mouth.tolist(),Pi_departure_axis=[1,0,0],
        whole_FR_P_RR_P_translation_mm=[0,0,-8],source_first3_mm=[mouth.tolist(),first.tolist()],
        source_R30_bend_unit=bend.tolist(),source_full9_mm=[arcend.tolist(),landend.tolist()],
        BUS_first3_and_full9_mm=[newmouth.tolist(),(newmouth-3*t).tolist(),(newmouth-12*t).tolist()],
        allocated_BUS_outside_tangent_mm=tail_mm,minimum_3plus9_is_not_a_maximum=True,
        BUS_relative_placement=dict(rotation_X_deg=angle,translation_mm=list(tf.Base)),
        BUS_actual_source_PCB_datum_mm=bus_datum.tolist(),BUS_target_PCB_datum_mm=list(newdatum),
        BUS_new_mouth_mm=newmouth.tolist(),BUS_new_departure_axis=(-t).tolist(),
        coil=dict(R_mm=R,centre_YZ_mm=[cy,cz],start_X_mm=x0,end_X_mm=x1,turns=turns,phase=phi,
            spline_knots=spline.t.tolist(),spline_controls_mm=spline.c.tolist(),
            analytic_continuous_R_bound_mm=1/math.sqrt(1/R**2+(6*D/(R**2*T**2))**2),
            minimum_spline_R_mm=curvature['minimum_radius_mm']),
        USB_length_mm=path.Length,USB_valid=shape.isValid(),USB_solids=len(shape.Solids),USB_volume_mm3=shape.Volume,
        sampled_self_contact=selfbad,sampled_clearance_is_not_continuous_proof=True,
        points_mm=pts.tolist(),all_actual_world_root_tools_motion_and_true_skin_OPEN=True,
        worker_seconds=round(time.monotonic()-tick,3))
    raw=shape.exportBrepToString().encode();bundle=dest.with_suffix('.breps.zip')
    with zipfile.ZipFile(bundle,'x',zipfile.ZIP_DEFLATED) as z:z.writestr('USB500.brep',raw)
    result.update(bundle=bundle.relative_to(ROOT).as_posix(),bundle_sha256=sha(bundle),USB_brep_sha256=hashlib.sha256(raw).hexdigest())
    save_json(dest,result);print(json.dumps({k:v for k,v in result.items() if k not in ('source_sha256','points_mm','coil')}),flush=True)


def receive_rear_bridge_gate():
    """Cheap actual-material gate BEFORE loading the full changed scene."""
    from feline_fore_power_pair import SolidQueries
    from receive_feline_positive_service_deck import open_grip
    tick=time.monotonic();file=OUT/'n01-joint-rear-service-bay-plan.json';p=json.loads(file.read_text())
    bundle=ROOT/p['bundle'];assert sha(bundle)==p['bundle_sha256']
    with zipfile.ZipFile(bundle) as z:raw=z.read('USB500.brep')
    assert hashlib.sha256(raw).hexdigest()==p['USB_brep_sha256'];wire=Part.Shape();wire.importBrepFromString(raw.decode())
    # Full selected strap needs3.8mm transverse space plus1.25mm rigid gap.
    # Translate the ENTIRE coupled planning unit before any world acceptance,
    # keeping source/receiver positions,452length,R and axial separation alike.
    delta=A.Vector(-2,0,0);wire.translate(delta);actors={'USB500:whole':wire}
    start=np.array(p['source_full9_mm'][0])+np.array(list(delta));t=np.diff(np.array(p['source_full9_mm']),axis=0)[0];t/=np.linalg.norm(t)
    side=np.array([0.,-t[2],t[1]])
    for name,s in open_grip(start,t,side,4.5).items():actors['USBSourceGrip:'+name]=s
    sourcefiles=[OUT/n for n in ('n01-full-material-scene.json','n01-lower-bay-world-probe.json','n01-common-restraint-world-probe.json','n01-remaining-selected-inventory.json')]
    targets={};sources={};pins={file.relative_to(ROOT).as_posix():sha(file),bundle.relative_to(ROOT).as_posix():sha(bundle)}
    for f in sourcefiles:
        d=json.loads(f.read_text());b=ROOT/d['bundle'];assert sha(b)==d['bundle_sha256']
        pins[f.relative_to(ROOT).as_posix()]=sha(f);pins[b.relative_to(ROOT).as_posix()]=sha(b)
        with zipfile.ZipFile(b) as z:
            for r in d['parts']:
                if not any(k in r['name'] for k in ('tail_TailBridge29','tail_MG92BMount29')):continue
                if r.get('placed_current') is False:continue
                blob=z.read(r['entry']);assert hashlib.sha256(blob).hexdigest()==r['sha256']
                s=Part.Shape();s.importBrepFromString(blob.decode());assert s.isValid() and s.Solids
                targets[r['name']]=s;sources[r['name']]=r
    assert len(targets)==2,tuple(targets)
    q=SolidQueries();checks=[]
    for n,s in actors.items():
        for m,b in targets.items():
            gap=q.distance(s,b);row=dict(a=n,b=m,gap_mm=gap,minimum_mm=1.25,ok=gap>=1.25-1e-6)
            if gap<1e-8:
                common=s.copy().common(b.copy());assert common.isNull() or common.isValid();row['positive_common_mm3']=common.Volume
            checks.append(row)
    result=dict(status='REAR_BRIDGE_CHANGED_INTERFACE_GATE_CLEAR_OTHER_GATES_OPEN' if all(r['ok'] for r in checks) else 'REAR_BRIDGE_ACTUAL_MATERIAL_OR_MARGIN_REJECTED',
        source_sha256=pins,source_records=sources,coupled_whole_unit_translation_mm=list(delta),checks=checks,
        selected=False,N01_complete=False,physical_pass=False,worker_seconds=round(time.monotonic()-tick,3),
        full_world_Pi_BUS_other_grips_motion_roots_OPEN=True)
    save_json(OUT/'n01-joint-rear-bridge-gate.json',result);print(json.dumps(result),flush=True)


def plan_rear_bridge_frame():
    """One two-flank load-path proposal, retaining actual mounting patches.

    N01 material planning only; no native manufacturing/strength release.
    """
    tick=time.monotonic();file=OUT/'n01-remaining-selected-inventory.json';d=json.loads(file.read_text())
    row=next(r for r in d['parts'] if 'tail_TailBridge29' in r['name']);b=ROOT/d['bundle'];assert sha(b)==d['bundle_sha256']
    with zipfile.ZipFile(b) as z:raw=z.read(row['entry'])
    assert hashlib.sha256(raw).hexdigest()==row['sha256'];old=Part.Shape();old.importBrepFromString(raw.decode())
    def box(lo,hi):return Part.makeBox(*(np.array(hi)-lo),A.Vector(*lo))
    # Entire middle path is replaced; no point-witness slot or hole relocation.
    opening=box([128,-50,50],[149,50,70]);keepers=old.cut(opening)
    wings={};rails={};joints=[]
    for sign in (-1,1):
        yl,yh=sorted((24*sign,36*sign));rl,rh=sorted((30*sign,36*sign))
        wings['front'+str(sign)]=box([108,yl,57.52],[128,yh,60.52])
        wings['rear'+str(sign)]=box([149,yl,56],[195,yh,59])
        rails[str(sign)]=box([124,rl,56],[153,rh,62])
        for side in ('front','rear'):
            w=wings[side+str(sign)];joint=w.copy().common(keepers.copy());assert joint.isValid() and joint.Volume>5
            joints.append(dict(a=side+'wing'+str(sign),b='retained_mounting_patch',positive_common_mm3=joint.Volume))
            joint=w.copy().common(rails[str(sign)].copy());assert joint.isValid() and joint.Volume>5
            joints.append(dict(a='flankrail'+str(sign),b=side+'wing'+str(sign),positive_common_mm3=joint.Volume))
    new=keepers.multiFuse([*wings.values(),*rails.values()]).removeSplitter();assert new.isValid() and len(new.Solids)==1
    missing=keepers.copy().cut(new.copy());assert missing.isNull() or missing.isValid();assert missing.Volume<1e-6
    holes=[]
    for face in old.Faces:
        surf=face.Surface
        if type(surf).__name__!='Cylinder' or abs(surf.Axis.z)<.999 or surf.Radius>2:continue
        p=surf.Center;tool=Part.makeCylinder(surf.Radius,20,A.Vector(p.x,p.y,50));fill=new.copy().common(tool)
        assert fill.isNull() or fill.isValid();assert fill.Volume<1e-5
        holes.append(dict(axis_world_XY_mm=[p.x,p.y],radius_mm=surf.Radius,filled_mm3=fill.Volume))
    assert len(holes)==8
    usbfile=OUT/'n01-joint-rear-service-bay-plan.json';u=json.loads(usbfile.read_text());archive=ROOT/u['bundle'];assert sha(archive)==u['bundle_sha256']
    with zipfile.ZipFile(archive) as z:raw=z.read('USB500.brep')
    assert hashlib.sha256(raw).hexdigest()==u['USB_brep_sha256'];wire=Part.Shape();wire.importBrepFromString(raw.decode());wire.translate(A.Vector(-2,0,0))
    gap=float(new.distToShape(wire)[0]);common=new.copy().common(wire.copy());assert common.isNull() or common.isValid()
    result=dict(status='TWO_FLANK_BRIDGE_LOCAL_PLAN_RECEIVED_WORLD_OPEN' if gap>=1.25 else 'TWO_FLANK_BRIDGE_CHANGED_INTERFACE_REJECTED',
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (file,b,usbfile,archive,Path(__file__))},
        replaced_owner=row['name'],source_record=row,original_mounting_patches_retained=True,
        original_P0_four_D2p6_and_tail_four_D3p4_axes=holes,kept_material_missing_mm3=missing.Volume,
        joints=joints,new_valid=new.isValid(),new_solids=len(new.Solids),new_volume_mm3=new.Volume,
        USB_whole_gap_mm=gap,USB_positive_common_mm3=common.Volume,
        planned_flank_rail_absY_mm=[30,36],planning_print_bbox_mm=[87,72,6],
        new_material_vs_all_world_motion_tools_OPEN=True,native_N03_and_strength_OPEN=True,
        selected=False,N01_complete=False,physical_pass=False,worker_seconds=round(time.monotonic()-tick,3))
    dest=OUT/'n01-two-flank-tail-bridge-plan.json';assert not dest.exists();bundle=dest.with_suffix('.breps.zip')
    with zipfile.ZipFile(bundle,'x',zipfile.ZIP_DEFLATED) as z:
        for name,s in (('new_bridge.brep',new),('retained_mounting_patches.brep',keepers)):
            raw=s.exportBrepToString().encode();z.writestr(name,raw);result[name+'_sha256']=hashlib.sha256(raw).hexdigest()
    result.update(bundle=bundle.relative_to(ROOT).as_posix(),bundle_sha256=sha(bundle));save_json(dest,result)
    print(json.dumps(result),flush=True)


def complete_source_station_groups(source,metadata):
    """Recover complete station units, never a hand-picked subset of a pose."""
    rows=[r for r in source['geometry'] if r['name'].startswith('Station:')]
    groups={r['role'] for r in rows}
    assert groups==set(source['moved_positive_WAGO_groups'])
    for group in groups:
        expected={r['name'] for r in rows if r['role']==group}
        actual={n for n,r in metadata.items() if r.get('group')==group}
        assert expected==actual,(group,expected-actual,actual-expected)
    return groups


def fpwm_after_turn_carrier(include_arm=True):
    """One planning carrier, unchanged bought case and existing full9 lands.

    Tie envelopes are selected T18 planning budgets, not supplier fit claims.
    Complete strap channels leave a continuous rear wall; no witness cutout.
    """
    def box(lo,hi):return Part.makeBox(*(np.array(hi)-lo),A.Vector(*lo))
    backbone=box([119.2,53,4],[122.2,79,94])
    pads=[];ties={};channels=[];lands=[]
    for tag,z in [('in',5.6),('out',90.4)]:
        pad=box([117.55,53.6,z-1.65],[119.55,62.6,z+1.65]);pads.append(pad)
        outside=box([113.25,56.85,z-2.85],[120.75,59.35,z+2.85])
        inside=box([114.45,56.75,z-1.65],[119.55,59.45,z+1.65])
        ties[tag+':band_budget']=outside.cut(inside)
        ties[tag+':head_budget']=box([108.95,55.6,z-2.65],[113.25,60.6,z+2.65])
        channels.append(box([119,56.65,z-3.05],[120.95,59.55,z+3.05]))
        lands.append(dict(end=tag,start_mm=[116,62.6,z],end_mm=[116,53.6,z],length_mm=9,radius_mm=1.55))
    outside=box([111.6,70.6,60.25],[123.4,79.4,62.75])
    inside=box([112.8,71.8,60.15],[122.2,78.2,62.85])
    ties['case:band_budget']=outside.cut(inside)
    ties['case:head_budget']=box([123.4,72.35,59],[127.7,77.65,64])
    channels.append(box([119,70.4,60.05],[122.4,79.6,62.95]))
    def section(x,y,z):
        return Part.makePolygon([A.Vector(x-1.5,y,z-2),A.Vector(x+1.5,y,z-2),A.Vector(x+1.5,y,z+2),A.Vector(x-1.5,y,z+2),A.Vector(x-1.5,y,z-2)])
    arm=Part.makeLoft([section(121,65,56),section(126,32,60)],True,True)
    carrier=backbone.multiFuse([*pads,*([arm] if include_arm else [])]).cut(Part.makeCompound(channels)).removeSplitter()
    assert carrier.isValid() and len(carrier.Solids)==1
    assert all(s.isValid() and len(s.Solids)==1 for s in ties.values())
    return carrier,ties,dict(lands=lands,selected_ties=3,additional_case_tie_stock_not_yet_allocated=True,
        full_factory_curves_unchanged=True,continuous_backwall_mm=1.25,
        provisional_PETG_strength_and_delivered_fit_OPEN=True)


def plan_fpwm_after_turn_carrier():
    from feline_fore_power_pair import SolidQueries
    tick=time.monotonic();src=OUT/'n01-shared54-current.json';d=json.loads(src.read_text());bundle=ROOT/d['bundle']
    assert sha(bundle)==d['bundle_sha256'];parts={};records={}
    with zipfile.ZipFile(bundle) as z:
        for r in d['parts']:
            if r.get('group')!='F_PWM_whole':continue
            raw=z.read(r['entry']);assert hashlib.sha256(raw).hexdigest()==r['sha256']
            s=Part.Shape();s.importBrepFromString(raw.decode());parts[r['name']]=s;records[r['name']]=r
    retired=[n for n in parts if ':End0:' in n or ':End1:' in n]
    assert len(retired)==6
    carrier,ties,info=fpwm_after_turn_carrier();q=SolidQueries();checks=[]
    for n,s in parts.items():
        if n in retired:continue
        gap=q.distance(carrier,s);common=carrier.copy().common(s.copy());assert common.isNull() or common.isValid()
        contact=n.endswith((':case',':in_after_turn_grip',':out_after_turn_grip'))
        boundary=None
        if n.endswith((':in_first_bend',':out_first_bend')):
            # The factory bend and full9 land share a tangent endpoint. The
            # pad touches that endpoint, but must not penetrate the bend.
            distance=carrier.distToShape(s);witnesses=[[list(a),list(b)] for a,b in distance[1]]
            contact=bool(witnesses) and all(abs(p[1]-62.6)<1e-5 and abs(p[0]-117.55)<1e-5 for pair in witnesses for p in pair)
            boundary=dict(method='Exact tangent seam of unchanged factory bend and full9 land',witness_pairs_mm=witnesses)
        checks.append(dict(a='F_PWM:common_carrier',b=n,gap_mm=gap,common_mm3=common.Volume,
            intentional_case_or_full9_pad_contact=contact,tangent_boundary_evidence=boundary,ok=common.Volume<1e-5 and (contact or gap>=1.25-1e-6)))
    for tag,tie in ties.items():
        for name,material in {'carrier':carrier,**{n:s for n,s in parts.items() if n not in retired}}.items():
            common=tie.copy().common(material.copy());assert common.isNull() or common.isValid()
            checks.append(dict(a=tag,b=name,common_mm3=common.Volume,ok=common.Volume<1e-5,
                method='Whole selected strap envelope must not occupy carrier or bought material; contacts allowed'))
    bf=OUT/'n01-two-flank-tail-bridge-plan.json';b=json.loads(bf.read_text());bb=ROOT/b['bundle'];assert sha(bb)==b['bundle_sha256']
    with zipfile.ZipFile(bb) as z:raw=z.read('new_bridge.brep')
    assert hashlib.sha256(raw).hexdigest()==b['new_bridge.brep_sha256'];bridge=Part.Shape();bridge.importBrepFromString(raw.decode())
    joint=carrier.copy().common(bridge.copy());assert joint.isValid() and joint.Volume>5
    result=dict(status='F_PWM_AFTER_TURN_CARRIER_LOCAL_PLAN_RECEIVED' if all(r['ok'] for r in checks) else 'F_PWM_AFTER_TURN_CARRIER_LOCAL_REJECTED',
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (src,bundle,bf,bb,Path(__file__))},
        retired_old_printed_grips_only=retired,unchanged_factory_records={n:r for n,r in records.items() if n not in retired},
        carrier_valid=True,carrier_solids=1,positive_frame_joint_mm3=joint.Volume,checks=checks,**info,
        selected=False,N01_complete=False,physical_pass=False,whole_world_motion_tools_OPEN=True,
        worker_seconds=round(time.monotonic()-tick,3))
    dest=OUT/'n01-fpwm-after-turn-carrier-plan-v3.json';assert not dest.exists();arc=dest.with_suffix('.breps.zip')
    result['geometry']=[]
    with zipfile.ZipFile(arc,'x',zipfile.ZIP_DEFLATED) as z:
        for n,s in {'carrier':carrier,**ties}.items():
            raw=s.exportBrepToString().encode();entry=n.replace(':','_')+'.brep';z.writestr(entry,raw)
            result['geometry'].append(dict(name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    result.update(bundle=arc.relative_to(ROOT).as_posix(),bundle_sha256=sha(arc));save_json(dest,result)
    print(json.dumps(dict(status=result['status'],seconds=result['worker_seconds'],checks=checks,joint_mm3=joint.Volume)),flush=True)


def receive_joint_rear_layout():
    """One coupled static/motion receipt. Save and stop at an actual blocker."""
    from feline_common_space_context import current
    from feline_fore_power_pair import SolidQueries,pair_spacing
    from feline_solid_distance import bbox_lower_bound
    from receive_feline_positive_service_deck import open_grip,intentional_mate
    from receive_feline_global_case_candidates import placement
    afterturn='--fpwm-after-turn' in sys.argv
    quarter='--bus-quarter-clock' in sys.argv
    powerlane='--pi-power-common-lane' in sys.argv
    collect='--collect-layout-conflicts' in sys.argv
    shared='--shared-critical-plan' in sys.argv
    resume='--resume-conflicts' in sys.argv
    tick=time.monotonic();dest=OUT/('n01-shared-Pi-fpwm-critical-plan.json' if shared else 'n01-joint-rear-layout-common-power-conflicts.json' if collect else 'n01-joint-rear-layout-common-power-lane-received.json' if powerlane else 'n01-joint-rear-layout-quarter-clock-received.json' if quarter else 'n01-joint-rear-layout-after-turn-received.json' if afterturn else 'n01-joint-rear-layout-received.json');assert resume==dest.exists()
    previous=json.loads(dest.read_text()) if resume else None
    previous_sha=sha(dest) if resume else None
    planfile=OUT/'n01-joint-rear-service-bay-plan.json';p=json.loads(planfile.read_text())
    bridgefile=OUT/'n01-two-flank-tail-bridge-plan.json';bp=json.loads(bridgefile.read_text())
    forefile=OUT/'n01-fore-coil-service-deck-received.json';fore=json.loads(forefile.read_text())
    assert not fore['errors'] and fore['status']!='PARTIAL_COMMON_SERVICE_DECK_RECEIPT'
    sourcePi={r['name'] for r in fore['geometry'] if r['role'] in ('PiRigid','PiFlexible')}
    assert len(sourcePi)==35 and sum(r['role']=='PiFlexible' for r in fore['geometry'])==7
    assert not any(r.get('a') in sourcePi and r.get('b') in sourcePi for r in fore['failures'])
    world,parts,meta,pins,docs=current();query=SolidQueries();changed={};roles={};cm={};fixed=dict(parts)
    delta=A.Vector(-2,0,0);shift=np.array(list(delta))
    centre=A.Vector(*fore['Pi_pose']['target_PCB_centre_mm']);target=A.Vector(*p['Pi_PCB_centre_mm'])+delta
    spin=A.Rotation(A.Vector(0,0,1),180);pitf=A.Placement(target-spin.multVec(centre),spin)
    archive=ROOT/fore['changed_geometry_archive'];assert sha(archive)==fore['changed_geometry_archive_sha256']
    own_pi={n for n in parts if meta[n].get('group')=='PiUpper'}
    with zipfile.ZipFile(archive) as z:
        for r in fore['geometry']:
            if r['name'] not in sourcePi:continue
            raw=z.read(r['entry']);assert hashlib.sha256(raw).hexdigest()==r['sha256'];s=Part.Shape();s.importBrepFromString(raw.decode());s.Placement=pitf*s.Placement
            changed[r['name']]=s;roles[r['name']]='Pi';cm[r['name']]=dict(kind='wire' if r['role']=='PiFlexible' else 'reservation' if r['name'].startswith('PiBudget:') else 'proposal_material')
    for n in own_pi:fixed.pop(n)
    new_power_lands=[]
    if powerlane:
        from receive_feline_positive_service_deck import pipe,circle_arc
        for e in fore['new_Pi_endpoints']:
            power=e['id'].startswith(('W079/','W080/'))
            if not power and not shared:continue
            endpoint=next(r for r in docs['ends']['endpoints'] if r['id']==e['id'])
            n='PiPower:'+e['id'].split('/')[0] if power else 'PiGPIO:'+endpoint['endpoint']
            q=pitf.multVec(A.Vector(*e['point_mm']));t=pitf.Rotation.multVec(A.Vector(*e['axis']))
            b=A.Vector(0,1 if shared else -1,0) if power else A.Vector(1,1,0);b-=t*t.dot(b);b.normalize()
            start=q+t*e['first_mm'];end=start+t*e['R_mm']+b*e['R_mm'];tip=end+b*9
            edges=[Part.makeLine(q,start),circle_arc(list(start),list(t),list(b),e['R_mm'],math.pi/2),Part.makeLine(end,tip)]
            changed[n],path=pipe(edges,e['radius_mm'])
            new_power_lands.append(dict(name=n,source_mm=list(q),R_mm=e['R_mm'],first_mm=e['first_mm'],radius_mm=e['radius_mm'],full9_mm=[list(end),list(tip)],length_mm=path.Length))
    pose=p['BUS_relative_placement'];rot=A.Rotation(A.Vector(1,0,0),pose['rotation_X_deg']);bustf=A.Placement(A.Vector(*pose['translation_mm'])+delta,rot)
    if quarter:
        pivot=A.Vector(*p['BUS_new_mouth_mm'])+delta;clock=A.Rotation(A.Vector(*p['BUS_new_departure_axis']),90)
        bustf=A.Placement(pivot-clock.multVec(pivot),clock)*bustf
    bus_inverse=world.bus['inverse']*bustf.inverse();retired=[];backplate=None
    keep={'CurrentBUS:H5MatingReserve','CurrentBUS:USB_C_Overmould','CurrentBUS:DGSharedRelief','CurrentBUS:BUS_Backplate',*(f'CurrentBUS:BUS_Standoff{i}' for i in range(4))}
    for n in list(fixed):
        if meta[n].get('role')!='BUS' and not n.startswith('CurrentBUS:'):continue
        if n.startswith('CurrentBUS:') and meta[n].get('kind') not in ('wire','actual_wire') and n not in keep:
            retired.append(n);fixed.pop(n);continue
        s=fixed.pop(n).copy();s.Placement=bustf*s.Placement
        changed[n]=s;roles[n]='BUS';cm[n]=meta[n]
        if n=='CurrentBUS:BUS_Backplate':backplate=s
    assert backplate is not None
    station_groups=complete_source_station_groups(fore,meta)
    for n in list(fixed):
        if meta[n].get('group') in station_groups:
            s=fixed.pop(n).copy();s.translate(A.Vector(0,0,-8));changed[n]=s;roles[n]=meta[n]['group'];cm[n]=meta[n]
    if shared:
        fpwm_rotation=A.Rotation(A.Vector(0,1,0),90)
        fpwm_tf=A.Placement(A.Vector(95,75,48)-fpwm_rotation.multVec(A.Vector(116,75,48)),fpwm_rotation)
        factory=[n for n in fixed if meta[n].get('group')=='F_PWM_whole' and ':End0:' not in n and ':End1:' not in n]
        assert len(factory)==5
        for n in factory:
            s=fixed.pop(n).copy();s.Placement=fpwm_tf*s.Placement
            changed[n]=s;roles[n]='F_PWM_factory';cm[n]=meta[n]
    bundle=ROOT/p['bundle'];assert sha(bundle)==p['bundle_sha256']
    with zipfile.ZipFile(bundle) as z:raw=z.read('USB500.brep')
    assert hashlib.sha256(raw).hexdigest()==p['USB_brep_sha256'];s=Part.Shape();s.importBrepFromString(raw.decode());s.translate(delta)
    changed['USB500:whole']=s;roles['USB500:whole']='USB';cm['USB500:whole']=dict(kind='wire')
    bus_side=list(clock.multVec(A.Vector(1,0,0))) if quarter else [1,0,0]
    for tag,land,side in [('Pi',p['source_full9_mm'],None),('BUS',[p['BUS_first3_and_full9_mm'][1],p['BUS_first3_and_full9_mm'][2]],bus_side)]:
        start=np.array(land[0])+shift;axis=np.array(land[1])-land[0];axis/=np.linalg.norm(axis)
        if side is None:side=[0,-axis[2],axis[1]]
        for k,s in open_grip(start,axis,side,4.5).items():
            n='USBGrip:'+tag+':'+k;changed[n]=s;roles[n]='Grip:'+tag;cm[n]=dict(kind='proposal_material')
    bridgebundle=ROOT/bp['bundle'];assert sha(bridgebundle)==bp['bundle_sha256']
    with zipfile.ZipFile(bridgebundle) as z:raw=z.read('new_bridge.brep')
    assert hashlib.sha256(raw).hexdigest()==bp['new_bridge.brep_sha256'];bridge=Part.Shape();bridge.importBrepFromString(raw.decode())
    oldbridge=fixed.pop(bp['replaced_owner'])
    def box(lo,hi):return Part.makeBox(*(np.array(hi)-lo),A.Vector(*lo))
    rootparts=[box([137,26,58],[139.5,33,62]),box([137,26,60],[139.5,29,88]),box([137,26,85],[139.5,42,88])]
    root= rootparts[0].multiFuse(rootparts[1:]);assert root.isValid() and len(root.Solids)==1
    if quarter:
        # The old root cannot follow a module clock automatically. First
        # receive whole bought module/ports; a new load path remains OPEN.
        bj=pj=None;frame=bridge.copy()
    else:
        bj=root.copy().common(bridge.copy());pj=root.copy().common(backplate.copy())
        assert bj.isValid() and pj.isValid() and bj.Volume>5 and pj.Volume>5,(bj.Volume,pj.Volume)
        frame=bridge.multiFuse([root,backplate]).removeSplitter();assert frame.isValid() and len(frame.Solids)==1
    fpwm_local_pairs=set()
    if afterturn:
        cf=OUT/'n01-fpwm-after-turn-carrier-plan-v3.json';cp=json.loads(cf.read_text())
        assert cp['status']=='F_PWM_AFTER_TURN_CARRIER_LOCAL_PLAN_RECEIVED'
        carrier,ties,info=fpwm_after_turn_carrier(include_arm=not shared)
        for n in cp['retired_old_printed_grips_only']:assert fixed.pop(n) is not None
        if shared:
            carrier.Placement=fpwm_tf*carrier.Placement
            changed['HorizontalFPWMCarrier']=carrier;roles['HorizontalFPWMCarrier']='F_PWM_Carrier';cm['HorizontalFPWMCarrier']=dict(kind='proposal_material')
        else:
            frame=frame.fuse(carrier).removeSplitter();assert frame.isValid() and len(frame.Solids)==1
        for tag,s in ties.items():
            if shared:s.Placement=fpwm_tf*s.Placement
            n='F_PWM_shared:'+tag;changed[n]=s;roles[n]='F_PWM_Ties';cm[n]=dict(kind='proposal_material')
        fpwm_local_pairs={r['b'] for r in cp['checks'] if r['a']=='F_PWM:common_carrier' and r['ok']}
        pins[cf.relative_to(ROOT).as_posix()]=sha(cf)
    if not quarter:
        changed.pop('CurrentBUS:BUS_Backplate');roles.pop('CurrentBUS:BUS_Backplate');cm.pop('CurrentBUS:BUS_Backplate')
    changed['SharedRearFrame']=frame;roles['SharedRearFrame']='Frame';cm['SharedRearFrame']=dict(kind='proposal_material')
    deltaFrame=frame.copy().cut(oldbridge.copy());withoutPlate=frame if quarter else frame.copy().cut(backplate.copy())
    outer=Part.Shape();outer.read(str(OUT/'n01-six-source-shared-lanes.outer.brep'))
    pins.update({f.relative_to(ROOT).as_posix():sha(f) for f in (planfile,bridgefile,forefile,archive,bundle,bridgebundle,Path(__file__))})
    result=dict(status='RUNNING_ONE_JOINT_REAR_LAYOUT',source_sha256=pins,changed_parts=list(changed),
        retired_old_BUS_frame_roots=retired,root_positive_joints_mm3=[] if quarter else [bj.Volume,pj.Volume],checks={},failures=[],errors=[],
        BUS_quarter_clock_about_preserved_USB_mouth_and_tangent=quarter,new_BUS_load_path_OPEN=quarter,
        Pi_power_common_inboard_lane=[] if shared else new_power_lands,
        Pi_seven_full_ends_shared_plan=new_power_lands if shared else [],Pi_power_and_seven_port_common_carrier_OPEN=powerlane,
        whole_shared_critical_plan=shared,horizontal_F_PWM_new_load_path_OPEN=shared,
        moved_station_groups_recovered_from_full_source_recipe=fore['moved_positive_WAGO_groups'],
        GPIO_five_changed_internal_pairs_REQUIRE_recheck=shared,
        original_Pi35_internal_geometry_rigid_and_fore_receipt_reused=not powerlane,
        original_Pi_rigid_and_five_GPIO_internal_evidence_reused=not shared,changed_power_internal_pairs_REQUIRE_recheck=powerlane,
        BUS_valid_original_inverse_method=True,collect_all_conflicts_before_layout_revision=collect,
        seven_Pi_complete_restraints_still_require_shared_comb_space=True,
        selected=False,N01_complete=False,physical_pass=False,native_changed=False,
        shared123_capacity_other_roots_tools_and_full_head_motion_OPEN=True)
    if previous:
        # This resume changes only interruption/collection policy, not any
        # construction recipe. Pin every external geometry input and retain
        # exact completed pairs. Geometry changes must use a different receipt.
        def inputs(d):return {k:v for k,v in d.items() if k!=Path(__file__).relative_to(ROOT).as_posix()}
        assert inputs(previous['source_sha256'])==inputs(pins)
        for k in ('changed_parts','retired_old_BUS_frame_roots','BUS_quarter_clock_about_preserved_USB_mouth_and_tangent','Pi_power_common_inboard_lane'):
            assert previous[k]==result[k],k
        result['checks']=previous['checks'];result['failures']=previous['failures']
        result['resume_history']=previous.get('resume_history',[])+[dict(source_sha256=previous_sha,worker_seconds=previous['worker_seconds'],completed_pairs=len(previous['checks']),errors=previous['errors'])]
        result['unchanged_pair_reuse_after_control_only_resume']=True
    def save():result['worker_seconds']=round(time.monotonic()-tick,3);save_json(dest,result)
    def dist(n,s,m,t):
        if n==world.bus['name']:
            q=t.copy();q.Placement=bus_inverse*q.Placement;return query.distance(q,world.bus['original'])
        if m==world.bus['name']:
            q=s.copy();q.Placement=bus_inverse*q.Placement;return query.distance(q,world.bus['original'])
        return query.distance(s,t)
    def pair(n,m):
        key='|'.join(sorted((n,m)))
        if key in result['checks']:return
        s=changed[n];t=changed.get(m,fixed.get(m));minimum=pair_spacing(n,cm[n],m,cm.get(m,meta.get(m,{})))
        if n=='SharedRearFrame':s=withoutPlate if roles.get(m)=='BUS' else frame if m in changed else deltaFrame
        if m=='SharedRearFrame':t=withoutPlate if roles.get(n)=='BUS' else frame
        if bbox_lower_bound(s.BoundBox,t.BoundBox)>=minimum:return
        if not t.Solids:r=dict(ok=False,reason='Curve-only old physical harness gate, not material collision')
        else:
            result['pending_pair']=dict(a=n,b=m,started_worker_seconds=round(time.monotonic()-tick,3));save()
            carrier_owner='HorizontalFPWMCarrier' if shared else 'SharedRearFrame'
            gap=dist(n,s,m,t);mate=intentional_mate(n,m) or (afterturn and ((n==carrier_owner and m in fpwm_local_pairs) or (m==carrier_owner and (n.startswith('F_PWM_shared:') or n in fpwm_local_pairs)) or (n.startswith('F_PWM_shared:') and m in fpwm_local_pairs)))
            r=dict(ok=gap>=minimum-1e-6,gap_mm=gap,minimum_mm=minimum)
            if mate and gap<1e-6:
                common=s.copy().common(t.copy());assert common.isNull() or common.isValid()
                r.update(ok=common.Volume<1e-5,intended_project_mouth_contact_mm3=common.Volume,delivered_mating_fit_OPEN=True)
        result['checks'][key]=r
        result.pop('pending_pair',None)
        if not r['ok']:
            result['failures'].append(dict(a=n,b=m,**r));save()
            if not collect:raise RuntimeError('ACTUAL_INTERFACE_BLOCKER_SAVED')
        if time.monotonic()-tick>220:save();raise TimeoutError('Completed changed pairs retained; not infeasibility')
    save()
    try:
        for n in changed:
            if shared and roles[n]=='BUS' and not n.startswith('CurrentBUS:') and n not in ('Ref_Material_BUSsupplier0_0_0','Ref_Material_BUSsupplier18_0_0'):
                continue  # Gate entire planning core before microcomponent audit.
            if roles[n]=='BUS':
                for m in fixed:
                    if meta.get(m,{}).get('group')=='F_PWM_whole':pair(n,m)
        for n in changed:
            outerkey=n+'|outer'
            if shared and roles[n]=='BUS' and not n.startswith('CurrentBUS:') and n not in ('Ref_Material_BUSsupplier0_0_0','Ref_Material_BUSsupplier18_0_0'):
                continue
            if outerkey in result['checks']:r=result['checks'][outerkey]
            elif n==world.bus['name']:
                original_outer=outer.copy();original_outer.Placement=bus_inverse*original_outer.Placement
                r=outer_margin(world.bus['original'],original_outer)
                r['method']='Valid original supplier solid against inverse-placed actual outer'
            else:r=outer_margin(changed[n],outer)
            already=outerkey in result['checks'];result['checks'][outerkey]=r
            if not r['ok'] and not already:
                result['failures'].append(dict(a=n,b='outer',**r));save()
                if not collect:raise RuntimeError('ACTUAL_INTERFACE_BLOCKER_SAVED')
            for m in [*fixed,*changed]:
                newpower=powerlane and (n.startswith('PiPower:') or m.startswith('PiPower:') or (shared and (n.startswith('PiGPIO:') or m.startswith('PiGPIO:'))))
                if m==n or (m in changed and roles[m]==roles[n] and roles[n]!='USB' and not newpower):continue
                pair(n,m)
            save()
        result['status']='JOINT_REAR_WHOLE_LAYOUT_CONFLICTS_RECEIVED' if result['failures'] else 'CRITICAL_SHARED_LAYOUT_RECEIVED_OTHER_GATES_OPEN' if shared else 'JOINT_REAR_STATIC_RECEIVED_MOTION_ROOTS_CAPACITY_OPEN'
    except RuntimeError as exc:
        if str(exc)=='ACTUAL_INTERFACE_BLOCKER_SAVED':result['status']='JOINT_REAR_LAYOUT_NAMED_INTERFACE_REJECTED'
        else:result['errors'].append(repr(exc));result['status']='JOINT_REAR_LAYOUT_PARTIAL_ERROR'
    except Exception as exc:result['errors'].append(repr(exc));result['status']='JOINT_REAR_LAYOUT_PARTIAL_ERROR'
    save();print(json.dumps(dict(status=result['status'],seconds=result['worker_seconds'],pairs=len(result['checks']),failure_count=len(result['failures']),first_failures=result['failures'][:12],errors=result['errors'])),flush=True)


def receive_boot_intrinsic():
    """Full cable against full boot before a further world-layout attempt."""
    from feline_fore_power_pair import SolidQueries
    from feline_solid_distance import bbox_lower_bound
    tick=time.monotonic();pf=OUT/'n01-joint-rear-boot-budget-plan.json';p=json.loads(pf.read_text())
    sf=OUT/'n01-full-material-scene.json';source=json.loads(sf.read_text());archive=ROOT/source['bundle']
    assert sha(archive)==source['bundle_sha256'];wirefile=ROOT/p['bundle'];assert sha(wirefile)==p['bundle_sha256']
    with zipfile.ZipFile(wirefile) as z:raw=z.read('USB500.brep')
    assert hashlib.sha256(raw).hexdigest()==p['USB_brep_sha256'];wire=Part.Shape();wire.importBrepFromString(raw.decode());wire.translate(A.Vector(-2,0,0))
    pose=p['BUS_relative_placement'];tf=A.Placement(A.Vector(*pose['translation_mm'])+A.Vector(-2,0,0),A.Rotation(A.Vector(1,0,0),pose['rotation_X_deg']))
    names={'CurrentBUS:USB_C_Overmould','Ref_Material_BUSsupplier0_0_0','CurrentBUS:H5MatingReserve','CurrentBUS:DGSharedRelief','CurrentBUS:BUS_Backplate','CurrentBUS:BUS.D','CurrentBUS:BUS.G'}
    rows=[r for r in source['parts'] if r['name'] in names];assert len(rows)==len(names)
    checks=[];query=SolidQueries()
    with zipfile.ZipFile(archive) as z:
        for r in rows:
            raw=z.read(r['entry']);assert hashlib.sha256(raw).hexdigest()==r['sha256'];s=Part.Shape();s.importBrepFromString(raw.decode());s.Placement=tf*s.Placement
            assert s.isValid() and s.Solids
            minimum=.2 if r['name'].endswith(('BUS.D','BUS.G')) else 1.25
            lower=bbox_lower_bound(s.BoundBox,wire.BoundBox)
            if lower>=minimum:checks.append(dict(part=r['name'],ok=True,separation_lower_bound_mm=lower,minimum_mm=minimum,method='Bounding-box separation proof, not overlapping-box rejection'));continue
            gap=query.distance(wire,s);common=wire.copy().common(s.copy());assert common.isNull() or common.isValid()
            port=r['name']=='CurrentBUS:USB_C_Overmould'
            checks.append(dict(part=r['name'],gap_mm=gap,positive_common_mm3=common.Volume,
                minimum_mm=minimum,ok=common.Volume<1e-5 and (port or gap>=minimum-1e-6),port_face_contact_allowed=port))
    result=dict(status='USB_FULL_BOOT_CORE_INTRINSIC_CLEAR_WORLD_OPEN' if all(r['ok'] for r in checks) else 'USB_FULL_BOOT_CORE_INTRINSIC_REJECTED',
        source_sha256={f.relative_to(ROOT).as_posix():sha(f) for f in (pf,sf,archive,wirefile,Path(__file__))},checks=checks,
        selected=False,N01_complete=False,physical_pass=False,all_other_components_grips_roots_world_motion_OPEN=True,
        worker_seconds=round(time.monotonic()-tick,3))
    dest=OUT/'n01-joint-rear-boot-intrinsic-received.json';assert not dest.exists();save_json(dest,result)
    print(json.dumps(result),flush=True)


def main():
    if '--receive-boot-intrinsic' in sys.argv:return receive_boot_intrinsic()
    if '--joint-rear-boot-budget' in sys.argv:return plan_joint_rear_bay(30)
    if '--fpwm-after-turn-carrier' in sys.argv:return plan_fpwm_after_turn_carrier()
    if '--receive-joint-rear-layout' in sys.argv:return receive_joint_rear_layout()
    if '--rear-bridge-frame' in sys.argv:return plan_rear_bridge_frame()
    if '--rear-bridge-gate' in sys.argv:return receive_rear_bridge_gate()
    if '--joint-rear-service-bay' in sys.argv:return plan_joint_rear_bay()
    if '--rear-service-bay' in sys.argv:return plan_rear_bay()
    if '--diagnose-best' in sys.argv:return diagnose()
    if '--receive-best' in sys.argv:return receive_best()
    if '--under-bank-U' in sys.argv:return plan_underbank()
    if '--receive-underbank' in sys.argv:return receive_best()
    if '--frame-bank-gap-U' in sys.argv:return plan_underbank()
    if '--receive-frame-bank-gap' in sys.argv:return receive_best()
    if '--two-level-Pi' in sys.argv or '--coupled-two-level' in sys.argv:return receive_two_level_pi()
    tick=time.monotonic();dest=OUT/'n01-spatial-service-bight-usb-plan.json';assert not dest.exists()
    sf=OUT/'n01-current-signed-space.json';doc=json.loads(sf.read_text());fp=ROOT/doc['field'];arc=ROOT/doc['voxel_source_archive']
    assert sha(fp)==doc['field_sha256'] and sha(arc)==doc['voxel_source_archive_sha256']
    ps=OUT/'n01-whole-pi-rigid-ports-space.json';plan=json.loads(ps.read_text());pose=next(p for p in plan['proposals'] if p['orientation_index']==0)
    cp=OUT/'n01-physical-cable-contract.json';usb=json.loads(cp.read_text())['usb']
    # Source mask owners, not an erased Pi bounding box: other material in
    # the same cells MUST remain. Old flexible jackets remain in harness.
    own=set(plan['own_parts']);shift=json.loads((OUT/'n01-usb-fore-lower-deck-space.json').read_text())['changed_owners']
    with np.load(fp,allow_pickle=False) as f:
        origin=f['origin_mm'];occupied=np.zeros_like(f['rigid_occupied']);motion=f['motion36_signed_distance'];outer=f['outer_distance']
    with zipfile.ZipFile(arc) as z:
        for name,row in doc['parts'].items():
            if not name.startswith('Static:') or name[7:] in own:continue
            raw=z.read(row['entry']);assert hashlib.sha256(raw).hexdigest()==row['sha256']
            with np.load(io.BytesIO(raw),allow_pickle=False) as a:mask=a['occupied'];local=a['origin']
            if name[7:] in shift:local=local+[0,0,-8]
            # Keep ALL other static owners, including old harness, conservatively.
            deposit(occupied,mask,local,origin)
    signed=distance_transform_edt(~occupied).astype(np.float32);signed[occupied]=-distance_transform_edt(occupied)[occupied]
    src=OUT/'n01-fore-coil-service-deck-received.json';prior=json.loads(src.read_text());bundle=ROOT/prior['changed_geometry_archive'];assert sha(bundle)==prior['changed_geometry_archive_sha256']
    boxes=[]
    with zipfile.ZipFile(bundle) as z:
        for row in prior['geometry']:
            if row['role']!='PiRigid':continue
            raw=z.read(row['entry']);assert hashlib.sha256(raw).hexdigest()==row['sha256'];s=Part.Shape();s.importBrepFromString(raw.decode());bb=s.BoundBox
            boxes.append((row['name'],np.array([bb.XMin,bb.YMin,bb.ZMin]),np.array([bb.XMax,bb.YMax,bb.ZMax])))
    result=dict(status='RUNNING_SPATIAL_SERVICE_BIGHT',source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (sf,fp,arc,ps,cp,src,bundle,Path(__file__))},
        Pi_pose=pose,candidate=None,tested=0,length_roots=0,hard_R30_survivors=0,self_clear=0,whole_Pi_guard_clear=0,occupancy_survivors=0,best=None,
        selected=False,N01_complete=False,physical_pass=False,all_grip_roots_new_Pi_prefixes_and_exact_gates_OPEN=True,
        cached_owner_cells_reused=True,not_infeasibility_if_no_candidate=True)
    rng=np.random.default_rng(202610191632)
    # A bay/tangent is allocated jointly with both end clocks. No 360deg
    # coil, soft curvature penalty, or iterative world-axis cable offset.
    for i in range(3000):
        if time.monotonic()-tick>165:break
        ac=float(rng.choice([-math.pi/2,math.pi/2]));bc=float(rng.choice([math.pi,math.pi/2,-math.pi/2]))
        p,t,first,PL=pi_prefix(pose['USB_mouth_mm'],math.pi/2,ac)
        q,bt,last,BL=bus_prefix(usb['bus_jacket_mouth_mm'],math.pi/2,bc)
        v=rng.normal(size=3);v/=np.linalg.norm(v);yz=np.array([rng.uniform(-70,70),rng.uniform(-20,100)])
        previous=None
        for x in np.linspace(-90,130,12):
            w=np.r_[x,yz];j=middle(p,t,q,-bt,w,v);result['tested']+=1
            if j is None:previous=None;continue
            delta=j['length_mm']+PL+BL-452
            if previous is not None and delta*previous[1]<0:
                f=lambda xx:middle(p,t,q,-bt,np.r_[xx,yz],v)['length_mm']+PL+BL-452
                try:root=brentq(f,previous[0],x,xtol=1e-9)
                except (ValueError,TypeError):previous=(x,delta);continue
                j=middle(p,t,q,-bt,np.r_[root,yz],v);result['length_roots']+=1
                if j['minimum_R_mm']<30-1e-7:previous=(x,delta);continue
                result['hard_R30_survivors']+=1;j=middle(p,t,q,-bt,np.r_[root,yz],v,True)
                samples=np.vstack([first,*[r['points_mm'][::-1] if r['reverse'] else r['points_mm'] for r in j['arcs']],last[::-1]])
                along=np.r_[0,np.cumsum(np.linalg.norm(np.diff(samples,axis=0),axis=1))];pairs=cKDTree(samples).query_pairs(5.5,output_type='ndarray')
                if len(pairs) and np.any(np.abs(along[pairs[:,0]]-along[pairs[:,1]])>12):previous=(x,delta);continue
                result['self_clear']+=1;guard=samples[(along>3.8)&(along<along[-1]-3.8)];block=[]
                for name,lo,hi in boxes:
                    gap=float(np.linalg.norm(np.maximum(np.maximum(lo-guard,guard-hi),0),axis=1).min())
                    if gap<3.75:block.append(name)
                if block:previous=(x,delta);continue
                result['whole_Pi_guard_clear']+=1
                # Trilinear nominal signed samples are proposals, NOT exact
                # clearance or a continuous curve proof. All gates stay OPEN.
                coords=(guard-origin).T;gaps=[float(map_coordinates(f,coords,order=1,mode='constant',cval=-100).min()) for f in (signed,motion,outer)]
                residual=min(gaps[0]-3.75,gaps[1]-3.75,gaps[2]-5.75)
                brief=dict(waypoint_mm=[root,*yz.tolist()],tangent=v.tolist(),Pi_clock_rad=ac,BUS_clock_rad=bc,R_mm=min(30,j['minimum_R_mm']),length_mm=j['length_mm']+PL+BL,field_gaps_mm=gaps,residual_mm=residual)
                if result['best'] is None or residual>result['best']['residual_mm']:result['best']=brief
                if residual>=0:
                    result['occupancy_survivors']+=1;result['candidate']=dict(**brief,arcs=j['arcs'],Pi_prefix_samples_mm=first.tolist(),BUS_prefix_samples_mm=last.tolist());break
            previous=(x,delta)
        if result['candidate']:break
        if i%100==0:result['worker_seconds']=round(time.monotonic()-tick,3);save_json(dest,result)
    result.update(status='SERVICE_BIGHT_MATH_AND_SAMPLED_SPACE_PROPOSAL' if result['candidate'] else 'BOUNDED_SERVICE_BIGHT_NO_CANDIDATE_NOT_INFEASIBILITY',worker_seconds=round(time.monotonic()-tick,3));save_json(dest,result)
    print(json.dumps({k:result[k] for k in ('status','worker_seconds','tested','length_roots','hard_R30_survivors','self_clear','whole_Pi_guard_clear','best')}),flush=True)


if __name__=='__main__':print('WORKER_PID',os.getpid(),flush=True);main()
