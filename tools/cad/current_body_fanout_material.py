"""Load the SAME shared fanout scene as valid BReps, without tessellating again.

Planning meshes never qualify continuous wire/material distances. This loader
retains the twelve accepted supports, their bands/bonds, all current head poses
and the same independently sampled leg stages for the eventual exact gate.
"""
import itertools
import json
import zipfile
from pathlib import Path
import FreeCAD as A
import prepare_body_fanout_scene as S

B=S.B
P=B.P


def load():
    receipt_file=P.OUT/'body-fanout-scene.json'
    receipt=json.loads(receipt_file.read_text())
    for n,h in receipt['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    reader=B.H.P.SavedShapes()
    targets,wires,archive,sf,hw=B.current_scene(reader)
    af=P.ROOT/'hardware/simulation/p0/e6-leg-compatibility.json'
    axes=json.loads(af.read_text())['axes']
    zf=P.ROOT/'hardware/simulation/v35/inputs.zip'
    with zipfile.ZipFile(zf) as z:members=json.loads(z.read('geometry.json'))['components']
    ownership={'P0_'+r['name']:tuple(r['stage'].split('_')[1:])
        for r in members if r['stage'].startswith('Motion_')}
    familyfile=P.OUT/'leg-source-near-member-plan.json';family=json.loads(familyfile.read_text())
    native=json.loads((P.OUT/'front-fixed-port-clearance-native.json').read_text())
    model=P.ROOT/native['native'];assert P.SHA(model)==native['native_sha256']
    for n in reader.doc(model):
        if not(n.endswith('SourceCarrier') or n.startswith('Ref_')):continue
        key=n.removeprefix('Ref_');targets[key]=reader.shape(model,n)
        if key.endswith(('SourceCarrier','SourceCaseBond')):
            leg=key.removesuffix('SourceCarrier').removesuffix('SourceCaseBond')
            code=next(r['cad_code'] for r in family['hips'] if r['physical_leg']==leg)
        else:code=next(r['cad_code'] for r in family['hips'] if r['loom']==key.removesuffix('IndependentBand'))
        ownership[key]=(code,'Hip')
    paths=json.loads((P.OUT/'remaining-support-shared-paths.json').read_text())
    retention=json.loads((P.OUT/'remaining-retention-entry.json').read_text())
    roots=json.loads((P.OUT/'remaining-loom-roots-plan.json').read_text())
    gate=json.loads((P.OUT/'remaining-support-shared-material.json').read_text())
    parents={r['preserved_owner']:targets[r['preserved_owner']]
        for r in gate['recipes'].values() if r['preserved_owner']}
    supports,recipes,bands,bonds,errors=S.cached_allocation(paths,retention,roots,parents)
    assert not errors,errors
    for name,recipe in recipes.items():
        old=recipe['preserved_owner']
        if old:targets.pop(old,None);ownership.pop(old,None)
        targets[name]=supports[name]
        ownership[name]=tuple(recipe['owner_stage'].split('_')[1:]) if recipe['owner_stage']!='Body' else (None,'Body')
    for collection in (bands,bonds):
        for name,shape in collection.items():
            owner=name.removesuffix('Bond') if name.endswith('Bond') else next(
                g['id'] for g in retention['groups'] if any('Band_'+p['land_id']==name for p in g['ports']))
            targets[name]=shape;ownership[name]=ownership[owner]
    transforms={}
    def pose(code,stage,h,k):
        key=(code,stage,h,k)
        if key not in transforms:transforms[key]=S.transform(axes,code,h,k,stage)
        return transforms[key]
    actual={}
    def put(name,shape):
        bb=shape.BoundBox
        if any(v<b for v,b in zip((bb.XMax,bb.YMax,bb.ZMax),S.LOW)):return
        if any(v>b for v,b in zip((bb.XMin,bb.YMin,bb.ZMin),S.HIGH)):return
        actual[name]=shape
    for name,shape in targets.items():
        code,stage=ownership.get(name,(None,'Body'))
        poses=itertools.product(S.ANGLES,repeat=2) if code and stage in ('Knee','Ankle') else (
            (h,0) for h in S.ANGLES) if code else [(0,0)]
        for h,k in poses:
            if stage=='Ankle':
                ax=next(r for r in axes if r['code']==code and r['stage']=='Ankle')
                pivot=A.Vector(*ax['pivot_mm'])
                for a in S.ANGLES:
                    rot=A.Rotation(A.Vector(*ax['axis']),a)
                    put(f'{name}/{h}/{k}/{a}',S.moved(shape,pose(code,'Knee',h,k)*A.Placement(pivot-rot.multVec(pivot),rot)))
            else:put(f'{name}/{h}/{k}',S.moved(shape,pose(code,stage,h,k)) if code else shape)
    for row in family['routes']:
        for h,k in itertools.product(S.ANGLES,repeat=2):
            parts=B.parts_for_loom(family,row['loom'],h,k,axes)+B.moved_parts(row['source_parts'],row['source'],h,k,axes)
            wires['leg/'+row['loom']+f'/{h}/{k}']=(P.wire(parts),3)
    pins={**receipt['source_sha256'],receipt_file.relative_to(P.ROOT).as_posix():P.SHA(receipt_file),
        Path(__file__).relative_to(P.ROOT).as_posix():P.SHA(Path(__file__))}
    return actual,wires,pins


if __name__=='__main__':
    import time
    tick=time.monotonic();targets,wires,pins=load()
    print(json.dumps(dict(material_instances=len(targets),wires=len(wires),
        worker_seconds=round(time.monotonic()-tick,3),physical_pass=False)),flush=True)
