"""One combined remaining support set: actual material before native export.

Preserved native parents are never overwritten. Only new material and its
interfaces are checked; current whole-body fanouts and physical fit stay open.
"""
import itertools,json,time,zipfile
from pathlib import Path
import FreeCAD as A
import Part
import build_complete_source_carriers as B
from build_front_fixed_port_clearance import placement
from diagnose_remaining_support_endpoints import transform,moved
from loom_land_port import build as port_build
from compact_loom_land_port import build as compact_build
from support_entry_port import build as entry_build
P=B.P
ANGLES=(-15,0,15)

def oriented(bounds,values=None):
    s=P.box(bounds)
    if values:s.Placement=placement(values)*s.Placement
    return s

def root_frame(choice):
    x=A.Vector(*choice['in_plane_axis']);z=A.Vector(*choice['outward_normal']);y=z.cross(x)
    c=A.Vector(*choice['plane_centre_world_mm']);m=A.Matrix()
    for j,v in enumerate((x,y,z,c),1):
        for i,q in enumerate(v,1):setattr(m,'A'+str(i)+str(j),q)
    return list(m.A)

def print_orientation(shape):
    options=[]
    for axis,base in ((A.Vector(1,0,0),0),(A.Vector(1,0,0),90),(A.Vector(0,1,0),90)):
        for yaw in range(0,91,15):
            rotation=A.Rotation(A.Vector(0,0,1),yaw)*A.Rotation(axis,base)
            q=moved(shape,A.Placement(A.Vector(),rotation));b=q.BoundBox
            size=[b.XLength,b.YLength,b.ZLength]
            options.append((max(size)+10<256,size[2],max(size),size,list(rotation.Q)))
    fits=[r for r in options if r[0]]
    best=min(fits,key=lambda r:(r[1],r[2])) if fits else min(options,key=lambda r:r[2])
    return dict(fits_with_5mm_brim=best[0],size_mm=best[3],rotation_quaternion=best[4],support_and_slicer_validation=False)

def allocation(paths,retention,roots,parents):
    shapes={};recipes={};bands={};bonds={};errors=[]
    lands={r['id']:r for g in roots['groups'] for r in g['lands']}
    for contract in roots['groups']:
        name=contract['id'];g=next(r for r in paths['groups'] if r['id']==name)
        selected=next(r for r in retention['groups'] if r['id']==name)
        pads=[];cuts=[]
        if name.endswith('KneeCarrier'):
            frame=root_frame(selected['root_choice'])
            pads.append(dict(name='CaseFoot',bounds_mm=[-5,-4,.2,5,4,6.2],placement=frame))
            bonds[name+'Bond']=oriented([-5,-4,0,5,4,.2],frame)
        for path in g['paths']:
            assert path['points_mm'],path['land_id']
            for i,(a,b) in enumerate(zip(path['points_mm'],path['points_mm'][1:])):
                v=[min(x,y)-h for x,y,h in zip(a,b,(2,3,2))]+[max(x,y)+h for x,y,h in zip(a,b,(2,3,2))]
                if not any(p['bounds_mm']==v and 'placement' not in p for p in pads):pads.append(dict(name='Arm'+str(len(pads)),bounds_mm=v))
        for port in selected['ports']:
            build=compact_build if port['recipe'].get('construction') else port_build
            actual=entry_build(lands[port['land_id']],port)
            recipe=actual['recipe'];frame=recipe['local_to_world']
            rank={'AxialApproach':-1,'ArrivalColumn':0,'AxialArmEntry':0,'BelowBandSlab':1,'NineMmLand':2}
            for row in sorted(recipe['pads'],key=lambda r:rank.get(r['name'],3)):
                pads.append(dict(name=port['land_id'].replace('/','')+row['name'],bounds_mm=row['bounds_mm'],placement=frame))
            cc=list(recipe['cuts']);r=recipe['ring_cut'];x,y,z,X,Y,Z=r['outer'];a,b,_,c,d,_=r['inner']
            cc += [[x,y,z,X,b,Z],[x,d,z,X,Y,Z],[x,b,z,a,d,Z],[c,b,z,X,d,Z]]
            cuts.extend(dict(bounds_mm=v,placement=frame) for v in cc)
            bands['Band_'+port['land_id']]=actual['band']
        parent=parents.get(contract.get('preserved_owner'))
        s=parent.copy() if parent else None
        for row in pads:
            q=oriented(row['bounds_mm'],row.get('placement'))
            s=q if s is None else s.fuse(q).removeSplitter()
        for row in cuts:s=s.cut(oriented(row['bounds_mm'],row.get('placement'))).removeSplitter()
        try:
            assert s.isValid() and len(s.Solids)==1 and not s.check(True),name
            if parent:assert parent.cut(s).Volume<1e-5,(name,'Would remove retained parent material')
        except (AssertionError,ValueError) as e:errors.append(dict(group=name,error=str(e)))
        shapes[name]=s
        recipes[name]=dict(pads=pads,cuts=cuts,preserved_owner=contract.get('preserved_owner'),owner_stage=contract['owner_stage'],root_choice=selected['root_choice'])
        print('combined support allocation',name,'solids',len(s.Solids),'valid',s.isValid(),flush=True)
    return shapes,recipes,bands,bonds,errors

def run(paths_file=None, output_file=None):
    tick=time.monotonic()
    files=[P.OUT/n for n in ('remaining-support-final-paths.json','remaining-retention-entry.json','remaining-loom-roots-plan.json','front-fixed-port-clearance-native.json','leg-source-near-member-plan.json')]
    if paths_file is not None:files[0]=Path(paths_file)
    paths,retention,roots,native,family=[json.loads(f.read_text()) for f in files]
    assert all(p['points_mm'] for g in paths['groups'] for p in g['paths']),'Do not fabricate missing paths'
    # Inputs of historical receipts may include earlier generator revisions;
    # geometry-bearing current sources are checked directly and pinned here.
    for f in files[1:]:
        rel=f.relative_to(P.ROOT).as_posix()
        if rel in paths['source_sha256']:assert P.SHA(f)==paths['source_sha256'][rel],rel
    reader=B.H.P.SavedShapes();targets,wires,archive,sf,hw=B.current_scene(reader)
    model=P.ROOT/native['native'];assert P.SHA(model)==native['native_sha256']
    af=P.ROOT/'hardware/simulation/p0/e6-leg-compatibility.json';axes=json.loads(af.read_text())['axes']
    zf=P.ROOT/'hardware/simulation/v35/inputs.zip'
    with zipfile.ZipFile(zf) as z:members=json.loads(z.read('geometry.json'))['components']
    membership={'P0_'+r['name']:tuple(r['stage'].split('_')[1:]) for r in members if r['stage'].startswith('Motion_')}
    for name in reader.doc(model):
        if not(name.endswith('SourceCarrier') or name.startswith('Ref_')):continue
        actual=name.removeprefix('Ref_');targets[actual]=reader.shape(model,name)
        if actual.endswith(('SourceCarrier','SourceCaseBond')):
            leg=actual.removesuffix('SourceCarrier').removesuffix('SourceCaseBond')
            code=next(r['cad_code'] for r in family['hips'] if r['physical_leg']==leg)
        else:code=next(r['cad_code'] for r in family['hips'] if r['loom']==actual.removesuffix('IndependentBand'))
        membership[actual]=(code,'Hip')
    shapes,recipes,bands,bonds,errors=allocation(paths,retention,roots,targets)
    result=dict(status='PARTIAL_COMBINED_SUPPORT_MATERIAL',errors=errors,contacts=[],recipes=recipes,
        selected=False,W5_complete=False,physical_pass=False,continuous_sweep_verified=False,
        source_sha256={f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in files+[af,zf,archive,sf,model,B.H.HEAD,hw,Path(__file__),Path(__file__).with_name('loom_land_port.py'),Path(__file__).with_name('compact_loom_land_port.py'),Path(__file__).with_name('support_entry_port.py')]},
        scope='36complete new lands/arms/four case feet against retained assembly and each other in coupled samples. Body core fanouts not yet allocated; not wholeW5.',
        print_allowance_each_mm=5)
    out=Path(output_file) if output_file is not None else P.OUT/'remaining-support-material.json'
    assert out.resolve()!=files[0].resolve(),'Output cannot replace the route contract'
    result['route_contract']=files[0].relative_to(P.ROOT).as_posix()
    def save():
        result['worker_seconds']=round(time.monotonic()-tick,3)
        out.write_text(json.dumps(result,indent=2)+'\n')
    if errors:result['status']='REJECTED_COMBINED_SUPPORT_ALLOCATION';save();return
    owners={g['id']:tuple(g['owner_stage'].split('_')[1:]) if g['owner_stage']!='Body' else (None,'Body') for g in roots['groups']}
    additions={}
    for name,s in shapes.items():
        parent=recipes[name]['preserved_owner']
        added=s.cut(targets[parent]).removeSplitter() if parent else s
        assert added.isValid(),name
        additions[name]=added;targets['NewSupport_'+name]=s;membership['NewSupport_'+name]=owners[name]
    for name,s in bonds.items():targets[name]=s;membership[name]=owners[name.removesuffix('Bond')]
    for name,s in bands.items():
        group=next(g for g in roots['groups'] if any(name=='Band_'+r['id'] for r in g['lands']))
        targets[name]=s;membership[name]=owners[group['id']]
    for sleeve in retention['sleeve_reservations']:
        axis=A.Vector(*sleeve['axis']);centre=A.Vector(*sleeve['centre_world_mm'])
        targets[sleeve['name']]=Part.makeCylinder(sleeve['diameter_project_mm']/2,sleeve['length_mm'],centre-axis*sleeve['length_mm']/2,axis)
        membership[sleeve['name']]=tuple(sleeve['owner_stage'].split('_')[1:])
    transforms={}
    for code in ('FL','FR','RL','RR'):
        for h,k,a in itertools.product(ANGLES,repeat=3):
            t=A.Placement()
            for stage,angle in zip(('Hip','Knee','Ankle'),(h,k,a)):
                ax=next(r for r in axes if r['code']==code and r['stage']==stage);p=A.Vector(*ax['pivot_mm']);r=A.Rotation(A.Vector(*ax['axis']),angle)
                t=t*A.Placement(p-r.multVec(p),r);transforms[code,h,k,a,stage]=t
    actual=[]
    for name,s in targets.items():
        code,stage=membership.get(name,(None,'Body'))
        poses=itertools.product(ANGLES,repeat=3) if stage=='Ankle' else ((h,k,0) for h,k in itertools.product(ANGLES,repeat=2)) if stage=='Knee' else ((h,0,0) for h in ANGLES) if code else [(0,0,0)]
        for h,k,a in poses:actual.append((name,moved(s,transforms[code,h,k,a,stage]) if code else s,code,stage,h,k,a))
    actual_wires=[(name,s,r,None,0,0) for name,(s,r) in wires.items()]
    for route in family['routes']:
        for h,k in itertools.product(ANGLES,repeat=2):
            w=P.wire(B.parts_for_loom(family,route['loom'],h,k,axes)+B.moved_parts(route['source_parts'],route['source'],h,k,axes))
            actual_wires.append((route['loom'],w,3,route['source']['cad_code'],h,k))
    bounds=B.ImmutableBounds();cache=B.PairReceipts(P.OUT/'remaining-support-material-pairs.json',bounds.near)
    result['groups']=[];checked=0
    for name,s in additions.items():
        code,stage=owners[name];contacts=[]
        poses=itertools.product(ANGLES,repeat=2) if stage=='Knee' else [(h,0) for h in ANGLES] if code else [(0,0)]
        for h,k in poses:
            q=moved(s,transforms[code,h,k,0,stage]) if code else s
            for other,t,oc,ost,hh,kk,aa in actual:
                if other in ('NewSupport_'+name,recipes[name]['preserved_owner'],name+'Bond'):continue
                if code and code==oc and (h!=hh or (stage=='Knee' and ost in ('Knee','Ankle') and k!=kk)):continue
                if not bounds.near(q,t,.001):continue
                checked+=1;gap,volume=cache.check(q,t)
                if volume>1e-5:contacts.append(dict(target=other,pose=[h,k],other_pose=[hh,kk,aa],volume_mm3=volume))
            for other,w,r,oc,hh,kk in actual_wires:
                if code and code==oc and (h!=hh or (stage=='Knee' and k!=kk)):continue
                if not bounds.near(q,w,r+.5+.001):continue
                checked+=1;gap,_=cache.check(q,w,0,r+.5)
                if gap<r+.5-1e-4:contacts.append(dict(target=other,pose=[h,k],other_pose=[hh,kk],gap_mm=gap,required_mm=r+.5))
        printing=print_orientation(shapes[name])
        if not printing['fits_with_5mm_brim']:errors.append(dict(group=name,error='No tested print orientation fits256with5mmbrim',printing=printing))
        result['groups'].append(dict(name=name,contacts=contacts,printing=printing,added_volume_mm3=s.Volume))
        result['contacts'] += [dict(group=name,**r) for r in contacts]
        result['pairs']=checked
        result['pair_reuse']=dict(computed=cache.computed,reused=cache.reused)
        cache.save();save()
        print('combined support material',name,'contacts',len(contacts),'pairs',checked,flush=True)
    result['status']='COMBINED_SUPPORT_MATERIAL_CLEAR_NATIVE_OPEN' if not result['contacts'] and not errors else 'REJECTED_COMBINED_SUPPORT_MATERIAL'
    save();print(json.dumps(dict(status=result['status'],contacts=len(result['contacts']),errors=errors,worker_seconds=result['worker_seconds'])),flush=True)
if __name__=='__main__':run()
