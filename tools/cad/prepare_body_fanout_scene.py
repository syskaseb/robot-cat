"""Cache the current shared material and wire reservations for all36 fanouts.

Meshes and sampled poses guide planning only. Actual BRep qualification remains
required for the chosen complete layout. No native model is recomputed here.
"""
import itertools
import json
import time
import zipfile
from pathlib import Path
import FreeCAD as A
import numpy as np
import build_complete_source_carriers as B
from diagnose_remaining_support_endpoints import transform,moved
from resume_remaining_support_gate import cached_allocation

P=B.P
OUT=P.OUT
ANGLES=(-15,0,15)
LOW=np.array([-210.,-165.,-30.])
HIGH=np.array([190.,165.,155.])


def run():
    tick=time.monotonic()
    gatefile=OUT/'remaining-support-shared-material.json'
    gate=json.loads(gatefile.read_text())
    assert gate['status']=='COMBINED_SUPPORT_MATERIAL_CLEAR_NATIVE_OPEN'
    assert not gate['contacts'] and not gate['errors']
    for name,digest in gate['source_sha256'].items():assert P.SHA(P.ROOT/name)==digest,name
    native=json.loads((OUT/'front-fixed-port-clearance-native.json').read_text())
    model=P.ROOT/native['native'];assert P.SHA(model)==native['native_sha256']
    reader=B.H.P.SavedShapes()
    targets,wires,archive,sf,hw=B.current_scene(reader)
    af=P.ROOT/'hardware/simulation/p0/e6-leg-compatibility.json'
    axes=json.loads(af.read_text())['axes']
    zf=P.ROOT/'hardware/simulation/v35/inputs.zip'
    with zipfile.ZipFile(zf) as z:members=json.loads(z.read('geometry.json'))['components']
    ownership={'P0_'+r['name']:tuple(r['stage'].split('_')[1:]) for r in members if r['stage'].startswith('Motion_')}
    familyfile=OUT/'leg-source-near-member-plan.json';family=json.loads(familyfile.read_text())
    for n in reader.doc(model):
        if not(n.endswith('SourceCarrier') or n.startswith('Ref_')):continue
        key=n.removeprefix('Ref_');targets[key]=reader.shape(model,n)
        if key.endswith(('SourceCarrier','SourceCaseBond')):
            leg=key.removesuffix('SourceCarrier').removesuffix('SourceCaseBond')
            code=next(r['cad_code'] for r in family['hips'] if r['physical_leg']==leg)
        else:code=next(r['cad_code'] for r in family['hips'] if r['loom']==key.removesuffix('IndependentBand'))
        ownership[key]=(code,'Hip')
    paths=json.loads((OUT/'remaining-support-shared-paths.json').read_text())
    retention=json.loads((OUT/'remaining-retention-entry.json').read_text())
    roots=json.loads((OUT/'remaining-loom-roots-plan.json').read_text())
    parents={r['preserved_owner']:targets[r['preserved_owner']] for r in gate['recipes'].values() if r['preserved_owner']}
    supports,recipes,bands,bonds,errors=cached_allocation(paths,retention,roots,parents)
    assert not errors
    for name,recipe in recipes.items():
        old=recipe['preserved_owner']
        if old:targets.pop(old,None);ownership.pop(old,None)
        targets[name]=supports[name]
        ownership[name]=tuple(recipe['owner_stage'].split('_')[1:]) if recipe['owner_stage']!='Body' else (None,'Body')
    for collection in (bands,bonds):
        for name,s in collection.items():
            owner=name.removesuffix('Bond') if name.endswith('Bond') else next(g['id'] for g in retention['groups'] if any('Band_'+p['land_id']==name for p in g['ports']))
            targets[name]=s;ownership[name]=ownership[owner]
    transforms={}
    def pose(code,stage,h,k):
        key=(code,stage,h,k)
        if key not in transforms:transforms[key]=transform(axes,code,h,k,stage)
        return transforms[key]
    tris=[];triangle_ids=[];names=[];mesh_count=0
    def mesh(name,s):
        nonlocal mesh_count
        bb=s.BoundBox
        if any(v<b for v,b in zip((bb.XMax,bb.YMax,bb.ZMax),LOW)) or any(v>b for v,b in zip((bb.XMin,bb.YMin,bb.ZMin),HIGH)):return
        vv,tt=s.tessellate(.25)
        q=np.asarray([list(v) for v in vv])[np.asarray(tt,dtype=int)]
        mask=np.all(q.max(axis=1)>=LOW-2,axis=1)&np.all(q.min(axis=1)<=HIGH+2,axis=1)
        q=q[mask]
        if not len(q):return
        index=len(names);names.append(name);tris.append(q);triangle_ids.extend([index]*len(q));mesh_count+=1
    for name,s in targets.items():
        code,stage=ownership.get(name,(None,'Body'))
        poses=itertools.product(ANGLES,repeat=2) if code and stage in ('Knee','Ankle') else ((h,0) for h in ANGLES) if code else [(0,0)]
        # Fixed fanouts may meet any independently moving leg. Ankle materials
        # retain all three ankle rotations in each Hip/Knee sample.
        for h,k in poses:
            if stage=='Ankle':
                for a in ANGLES:
                    ax=next(r for r in axes if r['code']==code and r['stage']=='Ankle')
                    p=A.Vector(*ax['pivot_mm']);rot=A.Rotation(A.Vector(*ax['axis']),a)
                    mesh(f'{name}/{h}/{k}/{a}',moved(s,pose(code,'Knee',h,k)*A.Placement(p-rot.multVec(p),rot)))
            else:mesh(f'{name}/{h}/{k}',moved(s,pose(code,stage,h,k)) if code else s)
    points=[];radii=[];wire_ids=[];wire_names=[]
    def wire(name,shape,radius):
        index=len(wire_names);wire_names.append(name)
        for e in shape.Edges:
            count=max(2,int(np.ceil(e.Length/.75))+1)
            for p in e.discretize(Number=count):
                v=list(p)
                if np.all(np.asarray(v)>=LOW-5) and np.all(np.asarray(v)<=HIGH+5):
                    points.append(v);radii.append(radius);wire_ids.append(index)
    for name,(s,r) in wires.items():wire(name,s,r)
    for row in family['routes']:
        for h,k in itertools.product(ANGLES,repeat=2):
            parts=B.parts_for_loom(family,row['loom'],h,k,axes)+B.moved_parts(row['source_parts'],row['source'],h,k,axes)
            wire('leg/'+row['loom']+f'/{h}/{k}',P.wire(parts),3)
    dest=OUT/'body-fanout-scene.npz'
    np.savez_compressed(dest,triangles=np.concatenate(tris),triangle_ids=np.asarray(triangle_ids),
        material_names=np.asarray(names),wire_points=np.asarray(points),wire_radii=np.asarray(radii),
        wire_ids=np.asarray(wire_ids),wire_names=np.asarray(wire_names),low=LOW,high=HIGH)
    files=[gatefile,af,zf,archive,sf,hw,B.H.HEAD,model,familyfile,Path(__file__),Path(B.__file__),
           OUT/'remaining-support-shared-paths.json',OUT/'remaining-retention-entry.json',OUT/'remaining-loom-roots-plan.json']
    result=dict(status='CURRENT_SHARED_FANOUT_PLANNING_SCENE_NOT_MATERIAL_ACCEPTANCE',
        scene=dest.relative_to(P.ROOT).as_posix(),sha256=P.SHA(dest),material_instances=mesh_count,
        triangles=len(triangle_ids),wire_samples=len(points),all_new_supports=12,
        sampled_degrees=list(ANGLES),wire_sample_max_step_mm=.75,tessellation_mm=.25,
        material_interiors_require_actual_BRep=True,selected=False,W5_complete=False,physical_pass=False,
        source_sha256={f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in files},worker_seconds=round(time.monotonic()-tick,3))
    (OUT/'body-fanout-scene.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','material_instances','triangles','wire_samples','worker_seconds')}),flush=True)


if __name__=='__main__':run()
