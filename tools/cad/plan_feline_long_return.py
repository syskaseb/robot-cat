"""Single longitudinal USB return over bank; shared Pi/BUS before detail.

One declared topology, no pose sweep, no world mask subtraction. Retain all
21 stations; no P_REAR relocation inherited from the rejected roof coil.
"""
import io,json,math,time,zipfile,hashlib,sys,os
import numpy as np
import FreeCAD as A
import Part
from scipy.interpolate import make_interp_spline
from scipy.optimize import brentq
from plan_feline_usb_service_bight import receive_roof_core,outer_margin
from receive_feline_positive_service_deck import pipe,circle_arc,open_grip,intentional_mate
from feline_cubic_curvature import extrema
from feline_fore_power_pair import SolidQueries,pair_spacing
from feline_solid_distance import bbox_lower_bound
from receive_feline_global_case_candidates import placement
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json


def usb_recipe():
    q=np.array([80.,32.85810963471377,98.7]);first=q+[15,0,0]
    a=first+[0,-60,0];b=a+[-140,0,0];c=b+[0,60,0];drop=12.
    nodes,weights=np.polynomial.legendre.leggauss(48);v=(nodes+1)/2
    length=lambda L:float(np.sum(weights*np.sqrt(L*L+(6*drop*v*(1-v))**2))/2)
    L=brentq(lambda L:15+60*math.pi+140+length(L)-452,90,120,xtol=1e-12)
    at=lambda u:c+np.array([L*u,0,-drop*(3*u*u-2*u*u*u)])
    derivative=lambda u:np.array([L,0,-6*drop*u*(1-u)])
    v=np.linspace(0,1,241);points=np.array([at(u) for u in v])
    spline=make_interp_spline(v,points,k=3,bc_type=([(1,derivative(0))],[(1,derivative(1))]))
    curvature=extrema(spline.t,spline.c);assert curvature['regular'] and curvature['minimum_radius_mm']>=30
    knots,mults=np.unique(spline.t,return_counts=True);curve=Part.BSplineCurve()
    curve.buildFromPolesMultsKnots([A.Vector(*p) for p in spline.c],mults.tolist(),knots.tolist(),False,3)
    es=[Part.makeLine(A.Vector(*q),A.Vector(*first)),circle_arc(first,[1,0,0],[0,-1,0],30,math.pi),
        Part.makeLine(A.Vector(*a),A.Vector(*b)),circle_arc(b,[-1,0,0],[0,1,0],30,math.pi),curve.toShape()]
    wire,path=pipe(es,2.5);assert abs(path.Length-452)<1e-5
    return wire,dict(Pi_mouth_mm=q.tolist(),Pi_full9_mm=[(q+[3,0,0]).tolist(),(q+[12,0,0]).tolist()],
        BUS_mouth_mm=at(1).tolist(),BUS_full9_mm=[(at(1)-[3,0,0]).tolist(),(at(1)-[12,0,0]).tolist()],
        USB_length_mm=path.Length,minimum_R_mm=min(30,curvature['minimum_radius_mm']),
        return_ramp_minimum_R_mm=curvature['minimum_radius_mm'],return_length_X_mm=L,
        fixed_U_radius_mm=30,main_straight_mm=140,return_drop_mm=drop)


def under_port_recipe():
    """Allocate an entire fixed plane BELOW all populated Pi port budgets.

    The first turn changes height, not the final9mm grip. The long return
    passes under USB-A, not through its envelope. The positive-Y lane avoids
    the retained S0 key/PWM occupied foreground of the negative-Y return.
    """
    q=np.array([80.,25.,98.7]);first=q+[15,0,0];R=32.;drop=17.2
    at=lambda u:first+np.array([R*math.sin(math.pi*u),R*(1-math.cos(math.pi*u)),-drop*(3*u*u-2*u*u*u)])
    deriv=lambda u:np.array([R*math.pi*math.cos(math.pi*u),R*math.pi*math.sin(math.pi*u),-6*drop*u*(1-u)])
    v=np.linspace(0,1,241);points=np.array([at(u) for u in v])
    spline=make_interp_spline(v,points,k=3,bc_type=([(1,deriv(0))],[(1,deriv(1))]))
    curvature=extrema(spline.t,spline.c);assert curvature['regular'] and curvature['minimum_radius_mm']>=30
    knots,mults=np.unique(spline.t,return_counts=True);curve=Part.BSplineCurve()
    curve.buildFromPolesMultsKnots([A.Vector(*p) for p in spline.c],mults.tolist(),knots.tolist(),False,3)
    edge=curve.toShape();a=at(1)
    # Actual received mould grows +22X from its jacket mouth. The initial
    # assumption left it overlapping Pi's other USB-A occupied envelope.
    # Allocate separate complete mating bays: Pi USB-A ends at54X; BUS
    # mould starts64X, giving10mm. Solve BOTH arm lengths, keep total452.
    target=64. if '--separate-mating-bays' in sys.argv else None
    main=(a[0]+452-15-edge.Length-math.pi*R-target)/2 if target is not None else 140.
    b=a+[-main,0,0];c=b+[0,-2*R,0]
    final=452-15-edge.Length-main-math.pi*R;assert final>=12
    mouth=c+[final,0,0]
    wire,path=pipe([Part.makeLine(A.Vector(*q),A.Vector(*first)),edge,
        Part.makeLine(A.Vector(*a),A.Vector(*b)),circle_arc(b,[-1,0,0],[0,-1,0],R,math.pi),
        Part.makeLine(A.Vector(*c),A.Vector(*mouth))],2.5)
    assert abs(path.Length-452)<1e-5
    return wire,dict(Pi_mouth_mm=q.tolist(),Pi_full9_mm=[(q+[3,0,0]).tolist(),(q+[12,0,0]).tolist()],
        BUS_mouth_mm=mouth.tolist(),BUS_full9_mm=[(mouth-[3,0,0]).tolist(),(mouth-[12,0,0]).tolist()],
        USB_length_mm=path.Length,minimum_R_mm=min(R,curvature['minimum_radius_mm']),
        descending_turn_minimum_R_mm=curvature['minimum_radius_mm'],final_exact_straight_mm=final,
        fixed_U_radius_mm=R,main_straight_mm=main,full_fixed_plane_Z_mm=81.5,
        allocated_BUS_mould_start_X_mm=target,actual_Pi_USB_A_front_end_X_mm=54.,
        seven_Pi_port_and_budget_space_preserved=True)


def build():
    sys.argv.append('--roof-layer30') if '--roof-layer30' not in sys.argv else None
    world,parts,meta,pins,docs,actors,roles,rows,inverse,outer,old,oldfile=receive_roof_core(True)
    pfile=OUT/'n01-roof-shared-layer30-plan.json';p=json.loads(pfile.read_text())
    oldpose=p['BUS_relative_placement'];oldbus=A.Placement(A.Vector(*oldpose['base_mm']),A.Rotation(*oldpose['quaternion']))
    under='--under-ports' in sys.argv;wire,recipe=under_port_recipe() if under else usb_recipe();mouth=np.array(recipe['BUS_mouth_mm'])
    dy=25.-32.85810963471377 if under else 0.;pi_delta=np.array([-30,dy,0])
    usbfile=OUT/'n01-physical-cable-contract.json';usb=json.loads(usbfile.read_text())['usb']
    matrix=np.column_stack([[0,0,1],[1,0,0],[0,1,0]]);rot=placement(matrix,[0,0,0]).Rotation
    bustf=A.Placement(A.Vector(*mouth)-rot.multVec(A.Vector(*usb['bus_jacket_mouth_mm'])),rot)
    busdelta=bustf*oldbus.inverse();baseline={};newends=[]
    for n in list(actors):
        s=actors[n]
        if roles[n] in ('PiRigid','PiWire'):s.translate(A.Vector(*pi_delta));baseline[n]=s.copy()
        elif roles[n]=='BUS':s.Placement=busdelta*s.Placement
        else:del actors[n];del roles[n];del rows[n]
    for e in old['new_Pi_full_ends']:
        n=e['name'];q=np.array(e['point_mm'])+pi_delta;t=np.array(e['axis']);power=n.startswith('PiPower:')
        if power:
            first=q+3*t;end=first+e['R_mm']*t+[0,0,-e['R_mm']];tip=end+[0,0,-9]
            actors[n],path=pipe([Part.makeLine(A.Vector(*q),A.Vector(*first)),circle_arc(first,t,[0,0,-1],e['R_mm'],math.pi/2),Part.makeLine(A.Vector(*end),A.Vector(*tip))],1.55)
        else:
            end=np.array(e['full9_mm'][0])+pi_delta;tip=np.array(e['full9_mm'][1])+pi_delta
        newends.append(dict(name=n,point_mm=q.tolist(),axis=t.tolist(),full9_mm=[end.tolist(),tip.tolist()],R_mm=e['R_mm']))
    actors['USB500:whole']=wire;roles['USB500:whole']='USB';rows['USB500:whole']={'kind':'wire'}
    for tag,land,side in [('Pi',recipe['Pi_full9_mm'],[0,0,1]),('BUS',recipe['BUS_full9_mm'],[0,-1,0])]:
        t=np.array(land[1])-land[0];t/=np.linalg.norm(t)
        for suffix,s in open_grip(land[0],t,side,4.5).items():
            n='USBGrip:'+tag+':'+suffix;actors[n]=s;roles[n]='Grip:'+tag;rows[n]={'kind':'proposal_material'}
    inverse=world.bus['inverse']*bustf.inverse()
    pins.update({f.relative_to(ROOT).as_posix():sha(f) for f in (oldfile,pfile,usbfile,ROOT/'tools/cad/plan_feline_long_return.py')})
    recipe.update(Pi_PCB_centre_mm=[8.5,13.46810963471377+dy,104],new_Pi_full_ends=newends,
        BUS_relative_placement=dict(base_mm=list(bustf.Base),quaternion=list(bustf.Rotation.Q)),
        full21_station_relocations=[],seven_full_Pi_grips_roots_tools_all123_OPEN=True)
    return world,parts,meta,pins,actors,roles,rows,inverse,outer,baseline,recipe


def frozen_core(previous):
    """Continue an interrupted receipt from exact archived bytes, no CAD rebuild."""
    from feline_common_space_context import current
    world,parts,meta,pins,docs=current()
    for name,value in previous['source_sha256'].items():
        if name in ('tools/cad/plan_feline_long_return.py','tools/cad/plan_feline_usb_service_bight.py'):continue
        assert sha(ROOT/name)==value,name
    pins=dict(previous['source_sha256']);pins['tools/cad/plan_feline_long_return.py']=sha(ROOT/'tools/cad/plan_feline_long_return.py')
    archive=ROOT/previous['bundle'];assert sha(archive)==previous['bundle_sha256'];actors={};roles={};rows={}
    with zipfile.ZipFile(archive) as z:
        for row in previous['geometry']:
            raw=z.read(row['entry']);assert hashlib.sha256(raw).hexdigest()==row['sha256']
            s=Part.Shape();s.importBrepFromString(raw.decode());assert s.isValid() and s.Solids
            n=row['name'];role=row['role'];actors[n]=s;roles[n]=role
            rows[n]=dict(meta[n]) if n in meta and role in ('BUS','MovedFPWM') else {'kind':'wire' if role in ('PiWire','USB','BUSWireNew') else 'reservation' if n.startswith('PiBudget:') else 'proposal_material'}
    recipe=previous['recipe'];p=recipe['BUS_relative_placement'];bt=A.Placement(A.Vector(*p['base_mm']),A.Rotation(*p['quaternion']))
    n=world.bus['name'];s=parts[n].copy();s.Placement=bt*s.Placement;actors[n]=s;roles[n]='BUS';rows[n]=meta[n]
    inverse=world.bus['inverse']*bt.inverse();outer=Part.Shape();outer.read(str(ROOT/recipe['outer_file']))
    # A timeout after the BUS actor loop cannot reopen unreceived Pi mating
    # evidence. Never replace its original ingress comparison with itself.
    for n in actors:
        if not n.startswith(('PiGPIO:','PiPower:')):continue
        housing='PiBudget:GPIO1992OccupiedHousing' if n.startswith('PiGPIO:') else 'PiBudget:RetainedK1474Boot'
        key='|'.join(sorted((n,housing)))
        if key not in previous['checks'] and recipe.get('r2_from_exact_received_frame_sha256'):
            p=OUT/'n01-tail-supported-gallery-core-received.json'
            assert previous['source_sha256'][p.relative_to(ROOT).as_posix()]==sha(p)
            original=json.loads(p.read_text());assert original['checks'][key]['ok']
            # The exact non-frame actor byte roundtrip is verified by main
            # BEFORE using this inherited ingress result in any receiver.
        else:assert key in previous['checks'],(n,'Source ingress must already be received')
    return world,parts,meta,pins,actors,roles,rows,inverse,outer,{},recipe


def main():
    if '--shared-constraints' in sys.argv:return shared_constraints()
    if '--world' in sys.argv:return receive_world()
    if '--diagnose' in sys.argv:return diagnose()
    tick=time.monotonic();name='n01-tail-supported-gallery-core-received.json' if '--supported-tail' in sys.argv else 'n01-service-gallery-core-received.json' if '--gallery' in sys.argv else 'n01-separated-port-bays-core-received.json' if '--separate-mating-bays' in sys.argv else 'n01-under-port-return-core-received.json' if '--under-ports' in sys.argv else 'n01-long-return-core-received.json'
    if '--keyed-feet' in sys.argv:name='n01-tail-supported-gallery-r2-core-received.json'
    canonical='--canonical-parent' in sys.argv
    if canonical:name='n01-tail-supported-gallery-r2-canonical-core-received.json'
    pi_carrier='--Pi-carrier' in sys.argv
    if pi_carrier:name='n01-shared-Pi-carrier-core-received.json'
    dest=OUT/name;resume='--resume-core' in sys.argv;assert resume==dest.exists()
    previous=json.loads(dest.read_text()) if resume else None
    if pi_carrier:
        from feline_shared_pi_carrier import build as selected_build
    elif '--supported-tail' in sys.argv:
        from feline_gallery_tail_support import build as selected_build
    elif '--gallery' in sys.argv:
        from feline_service_gallery import build as selected_build
    else:selected_build=build
    parent_raw={}
    if canonical and not previous:
        parentfile=OUT/'n01-tail-supported-gallery-core-received.json';parent=json.loads(parentfile.read_text())
        r2file=OUT/'n01-tail-supported-gallery-r2-core-received.json';r2=json.loads(r2file.read_text())
        parent['source_sha256']['tools/cad/feline_gallery_tail_support.py']=sha(ROOT/'tools/cad/feline_gallery_tail_support.py')
        world,parts,meta,pins,actors,roles,rows,inverse,outer,baseline,_=frozen_core(parent)
        recipe=r2['recipe'];ff=ROOT/recipe['frame_file'];assert sha(ff)==r2['source_sha256'][recipe['frame_file']]
        frame=Part.Shape();frame.read(str(ff));assert frame.isValid() and len(frame.Solids)==1;actors[recipe['frame_actor']]=frame
        parentzip=ROOT/parent['bundle'];assert sha(parentzip)==parent['bundle_sha256']
        with zipfile.ZipFile(parentzip) as z:
            for row in parent['geometry']:
                raw=z.read(row['entry']);assert hashlib.sha256(raw).hexdigest()==row['sha256']
                if row['name']!=recipe['frame_actor']:parent_raw[row['name']]=raw
        pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (parentfile,r2file,ff,ROOT/recipe['frame_delta_file'])})
        recipe=dict(recipe,exact_parent_bytes_passed_without_reserialization=True)
    else:world,parts,meta,pins,actors,roles,rows,inverse,outer,baseline,recipe=frozen_core(previous) if previous else selected_build()
    if pi_carrier and not previous:
        parent=json.loads((ROOT/recipe['immutable_parent_core_file']).read_text());pzip=ROOT/parent['bundle'];assert sha(pzip)==parent['bundle_sha256']
        with zipfile.ZipFile(pzip) as z:
            for row in parent['geometry']:
                if row['name'] not in recipe['Pi_unchanged_parent_actor_names']:continue
                raw=z.read(row['entry']);assert hashlib.sha256(raw).hexdigest()==row['sha256'];parent_raw[row['name']]=raw
    query=SolidQueries()
    archive=dest.with_suffix('.breps.zip');geometry=[]
    if previous:geometry=previous['geometry']
    with zipfile.ZipFile(archive,'r' if resume else 'x',zipfile.ZIP_DEFLATED) as z:
        for i,(n,s) in enumerate(actors.items()):
            if previous:continue  # SHA checked while loading frozen bytes above.
            # Cached BUS25 is invalid; retain exact inverse/original protocol.
            if n==world.bus['name']:continue
            assert s.isValid() and s.Solids,n
            raw=parent_raw[n] if n in parent_raw else s.exportBrepToString().encode();entry=f'{i}.brep'
            if resume:assert z.read(entry)==raw,n
            else:z.writestr(entry,raw)
            geometry.append(dict(name=n,role=roles[n],entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    result=dict(status='RUNNING_LONG_RETURN_CORE',source_sha256=pins,recipe=recipe,checks={},failures=[],errors=[],
        geometry=geometry,bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),
        current_world_outer_tools_montage_all123_OPEN=True,N01_complete=False,physical_pass=False,selected=False,native_changed=False)
    if ('--supported-tail' in sys.argv or pi_carrier) and not previous:
        priorfile=ROOT/recipe['immutable_parent_core_file'] if pi_carrier else OUT/('n01-tail-supported-gallery-core-received.json' if '--keyed-feet' in sys.argv else 'n01-service-gallery-core-received.json');old=json.loads(priorfile.read_text())
        before={r['name']:(r['sha256'],r['role']) for r in old['geometry']};after={r['name']:(r['sha256'],r['role']) for r in geometry}
        same={n for n,v in after.items() if before.get(n)==v}
        outer_key=recipe['outer_file'];same_outer=old['source_sha256'].get(outer_key)==pins[outer_key]
        for key,r in old['checks'].items():
            names=key.split('|')
            if '--keyed-feet' in sys.argv and any(x.startswith('DGGrip:') for x in names) and any(x.startswith('CurrentBUS:BUS.') for x in names):continue
            if len(names)!=2 or names[0] not in same:continue
            if names[1]=='outer':
                if not same_outer:continue
            elif names[1] not in same:continue
            elif 'minimum_mm' in r and r['minimum_mm']!=pair_spacing(names[0],rows[names[0]],names[1],rows[names[1]]):continue
            result['checks'][key]=r
            if not r['ok']:result['failures'].append(dict(a=names[0],b=names[1],**r))
        result['exact_unchanged_pair_reuse']=dict(source_sha256=sha(priorfile),same_actor_BRep_and_role_names=sorted(same),pairs=len(result['checks']),same_outer=same_outer)
    if previous:
        # Collection-only continuation: each archived geometric byte and the
        # complete recipe must match, so no renamed geometry inherits checks.
        assert previous['geometry']==geometry and previous['recipe']==recipe
        assert previous['bundle_sha256']==result['bundle_sha256']
        control_files={'tools/cad/plan_feline_long_return.py','tools/cad/plan_feline_usb_service_bight.py'}
        for name,value in previous['source_sha256'].items():
            if name not in control_files:assert pins[name]==value,name
        result.update(checks=previous['checks'],failures=previous['failures'],
            previous_runs=previous.get('previous_runs',[])+[dict(worker_seconds=previous['worker_seconds'],receipt_sha256=sha(dest),errors=previous['errors'])],
            unchanged_geometry_archive_and_complete_recipe_verified=True,geometry_resume_method='Exact SHA-pinned archive, no Boolean construction or serialization round trip')
    if '--keyed-feet' in sys.argv and not canonical and not result.get('exact_roundtrip_source_reuse'):
        # R2 edits ONLY the frame loaded from the prior archive. Its other
        # actors passed through import/export, which changes BRep encoding.
        # Prove that exact serialization roundtrip, rather than rerunning
        # hundreds of unchanged pairs or comparing only bounds/volume.
        priorfile=OUT/'n01-tail-supported-gallery-core-received.json';old=json.loads(priorfile.read_text())
        oldzip=ROOT/old['bundle'];assert sha(oldzip)==old['bundle_sha256']
        after={r['name']:r for r in geometry};same=set()
        with zipfile.ZipFile(oldzip) as z:
            for row in old['geometry']:
                n=row['name']
                if n==recipe['frame_actor'] or n not in after or after[n]['role']!=row['role']:continue
                raw=z.read(row['entry']);assert hashlib.sha256(raw).hexdigest()==row['sha256']
                s=Part.Shape();s.importBrepFromString(raw.decode())
                assert hashlib.sha256(s.exportBrepToString().encode()).hexdigest()==after[n]['sha256'],n
                same.add(n)
        for key,r in old['checks'].items():
            names=key.split('|')
            if len(names)!=2 or names[0] not in same or names[1]!='outer' and names[1] not in same:continue
            if any(x.startswith('DGGrip:') for x in names) and any(x.startswith('CurrentBUS:BUS.') for x in names):continue
            result['checks'][key]=r
        result['failures']=[dict(a=k.split('|')[0],b=k.split('|')[1],**v) for k,v in result['checks'].items() if not v['ok']]
        result['exact_roundtrip_source_reuse']=dict(source_sha256=sha(priorfile),unchanged_actor_count=len(same),only_changed_actor=recipe['frame_actor'],method='Exact old archive bytes -> identical imported/exported bytes; not bounds or volume equivalence')
    def save():result['worker_seconds']=round(time.monotonic()-tick,3);save_json(dest,result)
    def distance(n,s,m,t):
        if n==world.bus['name']:
            a=t.copy();a.Placement=inverse*a.Placement;return query.distance(world.bus['original'],a)
        if m==world.bus['name']:
            a=s.copy();a.Placement=inverse*a.Placement;return query.distance(a,world.bus['original'])
        return query.distance(s,t)
    try:
        for n,s in actors.items():
            if roles[n]!='BUS' or n.startswith('CurrentBUS:') or n=='Ref_Material_BUSsupplier0_0_0':
                key=n+'|outer'
                if key not in result['checks']:
                    if roles[n] in ('FrameNew','PiFrameNew'):
                        key='Pi_frame_delta_file' if roles[n]=='PiFrameNew' else 'frame_delta_file'
                        delta=Part.Shape();delta.read(str(ROOT/recipe[key]));r=outer_margin(delta,outer);r['scope']='Only added material inside torso; unchanged rooted source material retained'
                    else:r=outer_margin(s,outer)
                    result['checks'][key]=r
                    if not r['ok']:result['failures'].append(dict(a=n,b='outer',**r))
            for m,t in actors.items():
                if n==m or roles[n]==roles[m] and roles[n] not in ('PiWire','USB','BUSWireNew','PiHWNew'):continue
                key='|'.join(sorted((n,m)))
                if key in result['checks']:continue
                minimum=pair_spacing(n,rows[n],m,rows[m])
                if bbox_lower_bound(s.BoundBox,t.BoundBox)>=minimum:continue
                result['pending_pair']=[n,m];save();gap=distance(n,s,m,t)
                r=dict(ok=gap>=minimum-1e-6,gap_mm=gap,minimum_mm=minimum)
                if intentional_mate(n,m) and gap<1e-6:
                    common=s.copy().common(t.copy());assert common.isNull() or common.isValid()
                    r.update(ok=common.Volume<1e-5,mating_common_mm3=common.Volume)
                    wire=n if n.startswith(('PiPower:','PiGPIO:')) else m if m.startswith(('PiPower:','PiGPIO:')) else None
                    housing=m if wire==n else n
                    if wire and housing in ('PiBudget:GPIO1992OccupiedHousing','PiBudget:RetainedK1474Boot'):
                        before=baseline[wire].copy().common(actors[housing].copy());delta=common.copy().cut(before.copy()).Volume+before.copy().cut(common.copy()).Volume
                        r.update(ok=delta<1e-5,source_ingress_symmetric_difference_mm3=delta,project_budget_only_not_supplier_fit=True)
                if ('CurrentBUS:H5MatingReserve' in (n,m)) and (roles[n]=='BUSWireNew' or roles[m]=='BUSWireNew'):
                    common=s.copy().common(t.copy());assert common.isNull() or common.isValid();r.update(ok=common.Volume<1e-5,intended_H5_port_common_mm3=common.Volume)
                frame=recipe.get('frame_actor')
                if frame in (n,m):
                    other=m if n==frame else n
                    channel=other in ('CurrentBUS:BUS.D','CurrentBUS:BUS.G')
                    mate=other=='Ref_Material_BUSsupplier0_0_0' or other.startswith('DGGrip:') and other.endswith((':cap',':band'))
                    if channel or mate:
                        common=s.copy().common(t.copy());assert common.isNull() or common.isValid()
                        r.update(ok=common.Volume<1e-5 and (not channel or gap>=.149-1e-6),intended_supported_joint_common_mm3=common.Volume,
                            nominal_channel_clearance_mm=.15 if channel else None,physical_retention_not_qualified=True)
                if '--keyed-feet' in sys.argv and any(set((n,m))=={'CurrentBUS:BUS.'+tag,'DGGrip:'+tag+':cap'} for tag in ('D','G')):
                    common=s.copy().common(t.copy());assert common.isNull() or common.isValid()
                    r.update(ok=common.Volume<1e-5 and gap>=.149-1e-6,matching_split_cap_nominal_clearance_mm=.15,physical_retention_not_qualified=True)
                if 'USB500:whole' in (n,m) and any(x.startswith('USBGrip:') and x.endswith((':pad',':band')) for x in (n,m)):
                    common=s.copy().common(t.copy());assert common.isNull() or common.isValid();r.update(ok=common.Volume<1e-5,intended_pad_band_common_mm3=common.Volume)
                if pi_carrier:
                    ownframe=recipe['Pi_frame_actor'];other=m if n==ownframe else n if m==ownframe else None
                    if other and (other.startswith(('PiGPIO:','PiPower:','PiGrip:','Ref_Material_Pi4')) or other=='USB500:whole'):
                        common=s.copy().common(t.copy());assert common.isNull() or common.isValid()
                        channel=other.startswith(('PiGPIO:','PiPower:'))
                        r.update(ok=common.Volume<1e-5 and (not channel or gap>=.149-1e-6),planned_Pi_mount_or_jacket_mate_mm3=common.Volume,physical_fit_not_qualified=True)
                    hw=n if roles[n]=='PiHWNew' else m if roles[m]=='PiHWNew' else None
                    target=m if hw==n else n
                    if hw and (roles[target]=='PiHWNew' or target=='Ref_Material_Pi4NominalPCB_0_0'):
                        common=s.copy().common(t.copy());assert common.isNull() or common.isValid();r.update(ok=common.Volume<1e-5,selected_M2_same_actual_axis_mate_mm3=common.Volume)
                    if hw and target=='PiBudget:UnlabelledTopComponentsBudget':
                        r.update(ok=True,project_actual_mount_axis_keepout_not_supplier_component_geometry=True,delivery_fit_gate=True)
                result['checks'][key]=r;result.pop('pending_pair',None)
                if not r['ok']:result['failures'].append(dict(a=n,b=m,**r))
                save()
                if time.monotonic()-tick>220:raise TimeoutError('Bounded own core receipt; completed pairs saved')
        result['status']='LONG_RETURN_CORE_RECEIVED_WORLD_OPEN' if not result['failures'] else 'LONG_RETURN_CORE_CONFLICTS_RECEIVED'
    except Exception as exc:result['errors'].append(repr(exc));result['status']='LONG_RETURN_CORE_PARTIAL'
    save();print(json.dumps(dict(status=result['status'],seconds=result['worker_seconds'],checks=len(result['checks']),failures=result['failures'],errors=result['errors'])),flush=True)


def diagnose():
    under='--under-ports' in sys.argv
    gallery='--gallery' in sys.argv
    supported='--supported-tail' in sys.argv
    source=OUT/('n01-tail-supported-gallery-core-received.json' if supported else 'n01-service-gallery-core-received.json' if gallery else 'n01-under-port-return-core-received.json' if under else 'n01-long-return-core-received.json');d=json.loads(source.read_text())
    assert d['status']!='RUNNING_LONG_RETURN_CORE'
    arc=ROOT/d['bundle'];assert sha(arc)==d['bundle_sha256']
    names={r[k] for r in d['failures'] for k in ('a','b') if r[k]!='outer'}
    parts={}
    with zipfile.ZipFile(arc) as z:
        for row in d['geometry']:
            if row['name'] not in names:continue
            raw=z.read(row['entry']);assert hashlib.sha256(raw).hexdigest()==row['sha256']
            s=Part.Shape();s.importBrepFromString(raw.decode());parts[row['name']]=s
    result=dict(source_sha256=sha(source),actors={},pairs=[],no_new_geometry=True,N01_complete=False)
    for n,s in parts.items():
        bb=s.BoundBox;result['actors'][n]=[[bb.XMin,bb.YMin,bb.ZMin],[bb.XMax,bb.YMax,bb.ZMax]]
    for row in d['failures']:
        if row['b']=='outer':continue
        s,t=parts[row['a']],parts[row['b']];gap,points,_=s.distToShape(t)
        common=s.copy().common(t.copy());assert common.isNull() or common.isValid()
        result['pairs'].append(dict(a=row['a'],b=row['b'],gap_mm=gap,
            closest_pairs_mm=[[list(a),list(b)] for a,b in points[:2]],common_mm3=common.Volume))
    save_json(OUT/('n01-tail-supported-gallery-blocker-datums.json' if supported else 'n01-service-gallery-blocker-datums.json' if gallery else 'n01-under-port-return-blocker-datums.json' if under else 'n01-long-return-blocker-datums.json'),result);print(json.dumps(result),flush=True)


def receive_world():
    """Receive only external pairs of the frozen complete own-core archive."""
    from feline_common_space_context import current
    tick=time.monotonic();gallery='--gallery' in sys.argv
    source=OUT/('n01-tail-supported-gallery-r2-core-received.json' if '--keyed-feet' in sys.argv else 'n01-tail-supported-gallery-core-received.json' if '--supported-tail' in sys.argv else 'n01-service-gallery-core-received.json' if gallery else 'n01-separated-port-bays-core-received.json')
    if '--canonical-parent' in sys.argv:source=OUT/'n01-tail-supported-gallery-r2-canonical-core-received.json'
    if '--Pi-carrier' in sys.argv:source=OUT/'n01-shared-Pi-carrier-core-received.json'
    prior=json.loads(source.read_text());diagnostic='--diagnose-world' in sys.argv
    if diagnostic:
        # Collect a frozen whole hypothesis BEFORE correcting its separate
        # interfaces. This never accepts its known intrinsic margin hold.
        assert gallery and prior['status']=='LONG_RETURN_CORE_CONFLICTS_RECEIVED' and not prior['errors']
        assert len(prior['failures'])==1
        hold=prior['failures'][0];assert {hold['a'],hold['b']}=={'Ref_Material_BUSsupplier11_0_0','USBGrip:Pi:band'}
        assert hold['gap_mm']>1.2
    else:
        assert prior['status']=='LONG_RETURN_CORE_RECEIVED_WORLD_OPEN'
        assert not prior['failures'] and not prior['errors']
    name='n01-tail-supported-gallery-world-received.json' if '--supported-tail' in sys.argv else 'n01-service-gallery-world-diagnostic.json' if diagnostic else 'n01-service-gallery-world-received.json' if gallery else 'n01-separated-port-bays-world-received.json'
    if '--keyed-feet' in sys.argv:name='n01-tail-supported-gallery-r2-world-received.json'
    if '--canonical-parent' in sys.argv:name='n01-tail-supported-gallery-r2-canonical-world-received.json'
    if '--Pi-carrier' in sys.argv:name='n01-shared-Pi-carrier-world-received.json'
    dest=OUT/name;resume='--resume' in sys.argv;assert resume==dest.exists()
    world,parts,meta,pins,docs=current()
    for name,value in pins.items():assert prior['source_sha256'][name]==value,name
    archive=ROOT/prior['bundle'];assert sha(archive)==prior['bundle_sha256'];actors={};roles={};rows={}
    with zipfile.ZipFile(archive) as z:
        for row in prior['geometry']:
            raw=z.read(row['entry']);assert hashlib.sha256(raw).hexdigest()==row['sha256']
            s=Part.Shape();s.importBrepFromString(raw.decode());assert s.isValid() and s.Solids
            n=row['name'];actors[n]=s;roles[n]=row['role']
            rows[n]=dict(meta.get(n,{}),kind='wire' if row['role'] in ('PiWire','USB') else 'reservation' if n.startswith('PiBudget:') else meta.get(n,{}).get('kind','proposal_material'))
    pose=prior['recipe']['BUS_relative_placement'];bustf=A.Placement(A.Vector(*pose['base_mm']),A.Rotation(*pose['quaternion']))
    n=world.bus['name'];s=parts[n].copy();s.Placement=bustf*s.Placement;actors[n]=s;roles[n]='BUS';rows[n]=meta[n]
    inverse=world.bus['inverse']*bustf.inverse();fixed={n:s for n,s in parts.items() if meta[n].get('group')!='PiUpper' and meta[n].get('role')!='BUS' and not n.startswith('CurrentBUS:')}
    for n in prior['recipe'].get('fixed_replaced_names',[]):
        assert n in fixed,n;fixed.pop(n)
    frame_delta=None
    if prior['recipe'].get('frame_delta_file'):
        f=ROOT/prior['recipe']['frame_delta_file'];assert sha(f)==prior['recipe']['frame_delta_sha256'];frame_delta=Part.Shape();frame_delta.read(str(f))
    pi_frame_delta=None
    if prior['recipe'].get('Pi_frame_delta_file'):
        f=ROOT/prior['recipe']['Pi_frame_delta_file'];assert sha(f)==prior['recipe']['Pi_frame_delta_sha256'];pi_frame_delta=Part.Shape();pi_frame_delta.read(str(f))
    outerfile=ROOT/prior['recipe']['outer_file'] if gallery else OUT/'n01-six-source-shared-lanes.outer.brep'
    outer=Part.Shape();outer.read(str(outerfile));query=SolidQueries()
    # A containing solid inside the real outline is a sufficient POSITIVE
    # bound for every contained bought subpart. It is not a bbox contact test.
    supplier_names=[n for n in actors if n.startswith('Ref_Material_BUSsupplier')]
    envelope=A.BoundBox()
    for n in supplier_names:
        if n==world.bus['name']:
            b=world.bus['original'].BoundBox;to_world=inverse.inverse()
            for x in (b.XMin,b.XMax):
                for y in (b.YMin,b.YMax):
                    for z in (b.ZMin,b.ZMax):envelope.add(to_world.multVec(A.Vector(x,y,z)))
        else:envelope.add(actors[n].BoundBox)
    enclosure=Part.makeBox(envelope.XLength,envelope.YLength,envelope.ZLength,A.Vector(envelope.XMin,envelope.YMin,envelope.ZMin))
    supplier_outer_proof=outer_margin(enclosure,outer)
    result=dict(status='RUNNING_SEPARATED_PORT_BAYS_WORLD',source_sha256={**pins,source.relative_to(ROOT).as_posix():sha(source),archive.relative_to(ROOT).as_posix():sha(archive)},
        unchanged_own_core_reused=not diagnostic,intrinsic_spacing_holds=prior['failures'],diagnostic_not_layout_acceptance=diagnostic,
        all21_stations_preserved_without_relocation=True,checks={},failures=[],errors=[],completed_actors=[],critical_phase_complete=False,
        full_Pi_grips_roots_tools_all123_montage_OPEN=True,N01_complete=False,physical_pass=False,selected=False,native_changed=False)
    result['supplier_outer_enclosure_proof']=dict(**supplier_outer_proof,bounds_mm=[[envelope.XMin,envelope.YMin,envelope.ZMin],[envelope.XMax,envelope.YMax,envelope.ZMax]],
        actors=supplier_names,invalid_cached_part_bounds_replaced_by_transformed_valid_original_bounds=True,
        proof='Every bought BUS solid is contained in this box; box itself is contained in actual outer solid with required3.25mm. Not a contact test.')
    if frame_delta:
        result['frame_static_pair_scope']='Added carrier material only; old fixed mating interfaces retained. FULL frame is checked against all affected36 moving poses.'
        result['moved_whole_FPWM_output_case_isometry_proof']=prior['recipe']['FPWM_case_symmetry_difference_mm3']
    if resume:
        old=json.loads(dest.read_text());assert old['source_sha256']==result['source_sha256']
        result.update(checks=old['checks'],failures=old['failures'],completed_actors=old['completed_actors'],
            previous_runs=old.get('previous_runs',[])+[dict(worker_seconds=old['worker_seconds'],receipt_sha256=sha(dest),errors=old['errors'])])
    def save():result['worker_seconds']=round(time.monotonic()-tick,3);save_json(dest,result)
    critical=[n for n in actors if roles[n]!='BUS' or n.startswith('CurrentBUS:') or n=='Ref_Material_BUSsupplier0_0_0']
    # No actor/fixed solid is transformed in-place in this receiver. Cache
    # exact bounds ONCE, not thousands of repeated OCC evaluations per part.
    bounds_tick=time.monotonic();actor_bounds={n:s.BoundBox for n,s in actors.items()};fixed_bounds={n:s.BoundBox for n,s in fixed.items()}
    delta_bounds=frame_delta.BoundBox if frame_delta else None
    pi_delta_bounds=pi_frame_delta.BoundBox if pi_frame_delta else None
    motion_bounds=[A.BoundBox(*p['bounds'][0],*p['bounds'][1]) for p in world.motion]
    result['immutable_bound_cache']=dict(actors=len(actor_bounds),fixed=len(fixed_bounds),motion=len(motion_bounds),seconds=round(time.monotonic()-bounds_tick,3),geometry_not_mutated_in_place=True)
    priority=lambda n:0 if n=='USB500:whole' else 1 if roles[n]=='PiWire' else 2 if roles[n].startswith('Grip') else 3
    save()
    try:
        for phase,names in [('critical',sorted(critical,key=priority)),('remaining_supplier_parts',[n for n in actors if n not in critical])]:
            if phase!='critical' and result['failures']:break
            for n in names:
                if n in result['completed_actors']:continue
                s=actors[n]
                # All critical outer pairs were received as identical solids.
                if phase!='critical':
                    if n in supplier_names and supplier_outer_proof['ok']:
                        r=dict(ok=True,enclosing_solid_inside_real_outline=True,gap_lower_bound_mm=supplier_outer_proof['gap_mm'],minimum_mm=3.25)
                    elif n==world.bus['name']:
                        o=outer.copy();o.Placement=inverse*o.Placement;r=outer_margin(world.bus['original'],o)
                    else:r=outer_margin(s,outer)
                    result['checks'][n+'|outer']=r
                    if not r['ok']:result['failures'].append(dict(a=n,b='outer',**r))
                for m,t in fixed.items():
                    key=n+'|fixed:'+m
                    if key in result['checks']:continue
                    minimum=pair_spacing(n,rows[n],m,meta.get(m,{}))
                    tested=pi_frame_delta if roles[n]=='PiFrameNew' else frame_delta if roles[n]=='FrameNew' else s
                    bb=pi_delta_bounds if roles[n]=='PiFrameNew' else delta_bounds if roles[n]=='FrameNew' else actor_bounds[n]
                    if bbox_lower_bound(bb,fixed_bounds[m])>=minimum:continue
                    result['pending_pair']=[n,m];save()
                    if n in prior['recipe'].get('FPWM_moved_whole_output_names',[]) and m==prior['recipe'].get('FPWM_case_name'):
                        assert prior['recipe']['FPWM_case_symmetry_difference_mm3']<1e-5
                        r=dict(ok=True,unchanged_internal_factory_mate_reused_via_complete_output_isometry_and_case_invariance=True)
                    elif not t.Solids:r=dict(ok=False,reason='Existing curve-only route requires actual physical profile; not a material collision claim')
                    else:
                        if n==world.bus['name']:
                            a=t.copy();a.Placement=inverse*a.Placement;gap=query.distance(world.bus['original'],a)
                        else:gap=query.distance(tested,t)
                        r=dict(ok=gap>=minimum-1e-6,gap_mm=gap,minimum_mm=minimum)
                    result['checks'][key]=r;result.pop('pending_pair',None)
                    if not r['ok']:result['failures'].append(dict(a=n,b=m,**r))
                    save()
                    if time.monotonic()-tick>220:raise TimeoutError('Saved external pairs; resume same frozen archive')
                for pose,pose_bounds in zip(world.motion,motion_bounds):
                    if bbox_lower_bound(actor_bounds[n],pose_bounds)>=1.25:continue
                    key=n+'|motion:'+pose['name']+':'+str(pose['pose'])
                    if key in result['checks']:continue
                    tf=placement(pose['r'],pose['t']);result['pending_pair']=[n,key];save()
                    if n==world.bus['name']:
                        a=world.rest[pose['name']].copy();a.Placement=inverse*tf*a.Placement;gap=query.distance(world.bus['original'],a)
                    else:
                        a=s.copy();a.Placement=tf.inverse()*a.Placement;gap=query.distance(a,world.rest[pose['name']])
                    r=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25);result['checks'][key]=r;result.pop('pending_pair',None)
                    if not r['ok']:result['failures'].append(dict(a=n,b=pose['name'],pose=pose['pose'],**r))
                    save()
                    if time.monotonic()-tick>220:raise TimeoutError('Saved external motion pairs; resume same frozen archive')
                result['completed_actors'].append(n);save()
            if phase=='critical':result['critical_phase_complete']=True;save()
        result['status']='SEPARATED_PORT_BAYS_WORLD_CONFLICTS_RECEIVED' if result['failures'] else 'SEPARATED_PORT_BAYS_STATIC36MOTION_RECEIVED_ROOTS_TOOLS_CAPACITY_OPEN'
        if diagnostic:result['status']='DIAGNOSTIC_EXTERNAL_RECEIVED_INTRINSIC_HOLD_STILL_OPEN'
    except Exception as exc:result['errors'].append(repr(exc));result['status']='SEPARATED_PORT_BAYS_WORLD_PARTIAL'
    save();print(json.dumps(dict(status=result['status'],seconds=result['worker_seconds'],checks=len(result['checks']),failures=result['failures'][:18],failure_count=len(result['failures']),errors=result['errors'])),flush=True)


def shared_constraints():
    """Read ALL critical actor extents, before another constructor/receiver."""
    tick=time.monotonic();source=OUT/'n01-separated-port-bays-core-received.json';d=json.loads(source.read_text())
    arc=ROOT/d['bundle'];assert sha(arc)==d['bundle_sha256'];boxes={};holes={}
    with zipfile.ZipFile(arc) as z:
        for row in d['geometry']:
            n=row['name']
            if row['role'] not in ('PiRigid','PiWire') and not n.startswith('CurrentBUS:') and n!='Ref_Material_BUSsupplier0_0_0':continue
            raw=z.read(row['entry']);assert hashlib.sha256(raw).hexdigest()==row['sha256'];s=Part.Shape();s.importBrepFromString(raw.decode())
            bb=s.BoundBox;boxes[n]=[[bb.XMin,bb.YMin,bb.ZMin],[bb.XMax,bb.YMax,bb.ZMax]]
            if 'Standoff' in n:
                holes[n]=[dict(radius_mm=f.Surface.Radius,axis=list(f.Surface.Axis),centre_mm=list(f.Surface.Center)) for f in s.Faces if isinstance(f.Surface,Part.Cylinder)]
    fixed=OUT/'n01-upper-shared-sections.json';f=json.loads(fixed.read_text());world=OUT/'n01-separated-port-bays-world-received.json';w=json.loads(world.read_text())
    names={r['b'] for r in w['failures']}
    result=dict(status='SHARED_CONSTRAINT_TABLE_NO_NEW_GEOMETRY',source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (source,arc,fixed,world)},
        actor_bounds_mm=boxes,BUS_standoff_cylinder_datums=holes,
        conservative_fixed_cell_bounds_mm={n:b for n,b in f['upper_owner_cell_bounds_mm'].items() if n in names},
        original_recipe=d['recipe'],N01_complete=False,physical_pass=False,new_geometry=False,worker_seconds=round(time.monotonic()-tick,3))
    save_json(OUT/'n01-shared-upper-constraints.json',result)
    print(json.dumps(dict(seconds=result['worker_seconds'],BUS={n:b for n,b in boxes.items() if n.startswith('CurrentBUS:')},standoffs=holes)),flush=True)


if __name__=='__main__':print('WORKER_PID',os.getpid(),flush=True);main()
