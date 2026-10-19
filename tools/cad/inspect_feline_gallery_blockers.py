"""Receive exact witnesses of the ONE frozen gallery's four external holds.

No candidate sweep or new geometry. Read current archived world once, keep
all changed-interface witnesses and full output-kit membership together.
"""
import json,zipfile,hashlib,time,os,sys,math
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_common_space_context import current
from feline_atomic_save import save_json


def bounds(s):
    b=s.BoundBox;return [[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]]


def main():
    if '--Pi-restraint-space' in sys.argv:return pi_restraint_space()
    if '--D-diagonal' in sys.argv:return receive_D_diagonal()
    tick=time.monotonic();source=OUT/'n01-service-gallery-core-received.json';d=json.loads(source.read_text())
    df=OUT/'n01-service-gallery-world-diagnostic.json';diag=json.loads(df.read_text())
    assert diag['critical_phase_complete'] and len(diag['failures'])==4 and not diag['errors']
    arc=ROOT/d['bundle'];assert sha(arc)==d['bundle_sha256'];wanted={r['a'] for r in diag['failures']};actors={}
    with zipfile.ZipFile(arc) as z:
        for row in d['geometry']:
            if row['name'] not in wanted:continue
            raw=z.read(row['entry']);assert hashlib.sha256(raw).hexdigest()==row['sha256'];s=Part.Shape();s.importBrepFromString(raw.decode());actors[row['name']]=s
    world,parts,meta,pins,docs=current()
    for name,value in pins.items():assert d['source_sha256'][name]==value,name
    result=dict(status='EXACT_FROZEN_GALLERY_SHARED_WITNESSES',source_sha256={**pins,source.relative_to(ROOT).as_posix():sha(source),df.relative_to(ROOT).as_posix():sha(df)},
        witnesses=[],F_PWM_whole_output_kit={},N01_complete=False,physical_pass=False,no_new_geometry=True)
    for row in diag['failures']:
        s,t=actors[row['a']],parts[row['b']];assert s.isValid() and t.isValid() and s.Solids and t.Solids
        common=s.copy().common(t.copy());assert common.isNull() or common.isValid();gap,points,_=s.distToShape(t)
        result['witnesses'].append(dict(a=row['a'],b=row['b'],actor_bounds_mm=bounds(s),fixed_bounds_mm=bounds(t),
            gap_mm=gap,common_mm3=common.Volume,common_bounds_mm=bounds(common) if common.Volume>1e-6 else None,
            common_centres_mm=[list(q.CenterOfMass) for q in common.Solids],closest_pairs_mm=[[list(a),list(b)] for a,b in points[:2]]))
    for n,s in parts.items():
        if meta[n].get('group')=='F_PWM_whole':result['F_PWM_whole_output_kit'][n]=dict(kind=meta[n].get('kind'),bounds_mm=bounds(s),rotate_whole_output=n.endswith(('out_first_bend','out_after_turn_grip')) or ':End1:' in n)
    result['worker_seconds']=round(time.monotonic()-tick,3);save_json(OUT/'n01-service-gallery-world-witnesses.json',result)
    print(json.dumps(result['witnesses']),flush=True);print('SECONDS',result['worker_seconds'],flush=True)


def pi_restraint_space():
    """Read all seven lands, real bolt axes and nearby retained owners once.

    Bounds are only planning datums/proximity, NEVER collision evidence.
    No new candidate, changed geometry, native save or loop of poses.
    """
    tick=time.monotonic();source=OUT/'n01-tail-supported-gallery-r2-canonical-core-received.json';d=json.loads(source.read_text())
    assert d['status']=='LONG_RETURN_CORE_RECEIVED_WORLD_OPEN' and not d['failures'] and not d['errors']
    arc=ROOT/d['bundle'];assert sha(arc)==d['bundle_sha256'];actors={};roles={}
    with zipfile.ZipFile(arc) as z:
        for row in d['geometry']:
            raw=z.read(row['entry']);assert hashlib.sha256(raw).hexdigest()==row['sha256']
            s=Part.Shape();s.importBrepFromString(raw.decode());actors[row['name']]=s;roles[row['name']]=row['role']
    world,parts,meta,pins,docs=current()
    for n,h in pins.items():assert d['source_sha256'][n]==h,n
    fixed={n:s for n,s in parts.items() if meta[n].get('group')!='PiUpper' and meta[n].get('role')!='BUS' and not n.startswith('CurrentBUS:')}
    for n in d['recipe'].get('fixed_replaced_names',[]):fixed.pop(n)
    fixed.update(actors)
    def near_land(s,ends):
        #12mm allocation neighborhood, NOT contact classification.
        b=s.BoundBox;lo=[min(p[i] for p in ends)-12 for i in range(3)];hi=[max(p[i] for p in ends)+12 for i in range(3)]
        return b.XMax>=lo[0] and b.XMin<=hi[0] and b.YMax>=lo[1] and b.YMin<=hi[1] and b.ZMax>=lo[2] and b.ZMin<=hi[2]
    lands=[]
    for row in d['recipe']['new_Pi_full_ends']:
        lands.append(dict(**row,nearby_owner_datums=[dict(name=n,bounds_mm=bounds(s)) for n,s in fixed.items() if near_land(s,row['full9_mm'])]))
    anchors=[dict(name=n,bounds_mm=bounds(s),cylinders=[dict(radius_mm=f.Surface.Radius,axis=list(f.Surface.Axis),centre_mm=list(f.Surface.Center)) for f in s.Faces if isinstance(f.Surface,Part.Cylinder)]) for n,s in actors.items() if n.startswith('Ref_Material_Pi4') and 'PCB' not in n]
    rootparts=[dict(name=n,bounds_mm=bounds(s)) for n,s in fixed.items() if n.startswith('CurrentFoundation:') or n==d['recipe']['frame_actor']]
    result=dict(status='SEVEN_PI_RESTRAINTS_SHARED_DATUMS_NOT_FIT',lands=lands,actual_Pi_fastener_datums=anchors,retained_root_datums=rootparts,
        source_sha256={**pins,source.relative_to(ROOT).as_posix():sha(source),arc.relative_to(ROOT).as_posix():sha(arc)},
        nearby_bounds_are_not_collision_proof=True,N01_complete=False,physical_pass=False,no_new_geometry=True,worker_seconds=round(time.monotonic()-tick,3))
    save_json(OUT/'n01-Pi-seven-restraints-shared-datums.json',result)
    print(json.dumps(dict(status=result['status'],lands=len(lands),fastener_parts=len(anchors),root_parts=len(rootparts),seconds=result['worker_seconds'])),flush=True)


def receive_D_diagonal():
    from feline_fore_power_pair import SolidQueries,pair_spacing
    from feline_solid_distance import bbox_lower_bound
    from receive_feline_global_case_candidates import placement
    from plan_feline_usb_service_bight import outer_margin
    tick=time.monotonic();dest=OUT/'n01-gallery-D-diagonal-received.json';assert not dest.exists()
    source=OUT/'n01-service-gallery-core-received.json';d=json.loads(source.read_text());arc=ROOT/d['bundle'];assert sha(arc)==d['bundle_sha256']
    actors={};records={}
    with zipfile.ZipFile(arc) as z:
        for row in d['geometry']:
            raw=z.read(row['entry']);assert hashlib.sha256(raw).hexdigest()==row['sha256'];s=Part.Shape();s.importBrepFromString(raw.decode());actors[row['name']]=s;records[row['name']]=row
    n='CurrentBUS:BUS.D';s=actors.pop(n)
    caps=[f for f in s.Faces if isinstance(f.Surface,Part.Plane) and abs(f.Area-math.pi*1.55**2)<1e-4];assert len(caps)==2
    q=max(caps,key=lambda f:f.CenterOfMass.z).CenterOfMass;rot=A.Rotation(A.Vector(0,0,1),-45)
    transform=A.Placement(q-rot.multVec(q),rot);s.Placement=transform*s.Placement
    world,parts,meta,pins,docs=current()
    for key,value in pins.items():assert d['source_sha256'][key]==value,key
    pose=d['recipe']['BUS_relative_placement'];bt=A.Placement(A.Vector(*pose['base_mm']),A.Rotation(*pose['quaternion']));inverse=world.bus['inverse']*bt.inverse()
    fixed={k:t for k,t in parts.items() if meta[k].get('group')!='PiUpper' and meta[k].get('role')!='BUS' and not k.startswith('CurrentBUS:')}
    targets={**fixed,**actors};query=SolidQueries();pairs=[]
    outer=Part.Shape();outer.read(str(ROOT/d['recipe']['outer_file']));outside=outer_margin(s,outer)
    for m,t in targets.items():
        row=meta.get(m,{}) if m in fixed else dict(kind='wire' if records[m]['role'] in ('PiWire','USB','BUSWireNew') else 'proposal_material')
        minimum=pair_spacing(n,{'kind':'wire'},m,row)
        if bbox_lower_bound(s.BoundBox,t.BoundBox)>=minimum:continue
        if not t.Solids:r=dict(ok=False,reason='Curve-only owner, not a solid collision claim')
        else:
            gap=query.distance(s,t);r=dict(ok=gap>=minimum-1e-6,gap_mm=gap,minimum_mm=minimum)
            if m=='CurrentBUS:H5MatingReserve':
                common=s.copy().common(t.copy());assert common.isNull() or common.isValid();r.update(ok=common.Volume<1e-5,intended_mating_common_mm3=common.Volume)
        pairs.append(dict(target=m,**r))
    # Invalid cached BUS25 is never queried. Its valid original is pinned.
    a=s.copy();a.Placement=inverse*a.Placement;gap=query.distance(a,world.bus['original'])
    pairs.append(dict(target=world.bus['name'],ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25))
    for p in world.motion:
        if bbox_lower_bound(s.BoundBox,A.BoundBox(*p['bounds'][0],*p['bounds'][1]))>=1.25:continue
        a=s.copy();a.Placement=placement(p['r'],p['t']).inverse()*a.Placement;gap=query.distance(a,world.rest[p['name']])
        pairs.append(dict(target=p['name'],pose=p['pose'],ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25))
    failures=[r for r in pairs if not r['ok']];file=dest.with_suffix('.brep');s.exportBrep(str(file))
    result=dict(status='D_DIAGONAL_FULL_WIRE_RECEIVED_OTHER_LAYOUT_HOLDS_OPEN' if outside['ok'] and not failures else 'D_DIAGONAL_WITNESSES_RECEIVED_NOT_INFEASIBILITY',
        source_sha256={**pins,source.relative_to(ROOT).as_posix():sha(source),arc.relative_to(ROOT).as_posix():sha(arc)},
        whole_wire_rotation_Z_deg=-45,retained_start_cap_mm=list(q),outer=outside,checks=pairs,failures=failures,
        unchanged_G_and_other_cables_not_rechecked=True,other_three_gallery_holds_still_OPEN=True,
        BRep=file.relative_to(ROOT).as_posix(),BRep_sha256=sha(file),N01_complete=False,physical_pass=False,worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,result);print(json.dumps(dict(status=result['status'],seconds=result['worker_seconds'],checks=len(pairs),failures=failures,outer=outside)),flush=True)


if __name__=='__main__':print('WORKER_PID',os.getpid(),flush=True);main()
