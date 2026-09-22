"""Export checked world BReps without touching the GUI model.

Run with FreeCAD's Python. All CAD units are mm; report units are explicit.
This is geometry, NOT a claim of measured physical mass or completed mounts.
"""
from pathlib import Path
import hashlib
import json
import sys
import FreeCAD as A
import Part
import MeshPart
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools/simulation'))
from cad_model import OUT, REVISION
CACHE = ROOT / ('hardware/skorupa/'+REVISION+'/shape-cache' if REVISION in ('v28','v29') else 'hardware/skorupa/v26/shape-cache')
SOURCE = ROOT / {'v25':'hardware/skorupa/v25/Kot_v25_DOMOWA_OSLONA.FCStd',
                 'v27':'hardware/skorupa/v27/Kot_v27_BIODRA_ASSEMBLY.FCStd',
                 'v28':'hardware/skorupa/v28/Kot_v28_BIODRA_PETG.FCStd',
                 'v29':'hardware/skorupa/v29/Kot_v29_OGON_PROTOTYP.FCStd'}[REVISION]


def main():
    index = json.loads((CACHE / 'index.json').read_text())
    source_sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if REVISION=='v27':
        validation=json.loads((ROOT/'hardware/skorupa/v27/assembly-validation.json').read_text())
        assert validation['geometry_unchanged'] and validation['source_sha256']==source_sha
        assert validation['geometry_cache_source_sha256']==index['source_sha256']
    else:assert source_sha == index['source_sha256']
    plan_revision='v29' if REVISION=='v29' else ('v27' if REVISION in ('v27','v28') else 'v24')
    plan = json.loads((ROOT / ('hardware/skorupa/'+plan_revision+'/assembly-plan.json')).read_text(encoding='utf8'))
    assert set(index['objects']) == {p['name'] for p in plan['components']}
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for p0 in plan['components']:
        p=dict(p0)
        # The leg experiment remains 13 dynamic links. Carry the new tail's
        # complete mass/inertia/mesh at rest, but make its frozen axis explicit.
        # Do not silently leave this stage out of the base-link inertia.
        if REVISION=='v29' and p['stage']=='Motion_Tail_Yaw':
            p['native_stage']=p['stage'];p['stage']='Chassis'
        s = Part.Shape()
        s.read(str(CACHE / (p['name'] + '.brep')))
        b = s.BoundBox
        assert s.Solids and all(t.Volume > 0 for t in s.Solids), p['name']
        volume = sum(t.Volume for t in s.Solids)
        com = sum(t.Volume*np.array(list(t.CenterOfMass)) for t in s.Solids)/volume
        inertia = np.zeros((3,3))
        for solid in s.Solids:
            m = solid.MatrixOfInertia
            r = np.array(list(solid.CenterOfMass))-com
            inertia += np.array([[getattr(m,'A%d%d' % (i,j)) for j in range(1,4)] for i in range(1,4)])
            inertia += solid.Volume*(np.dot(r,r)*np.eye(3)-np.outer(r,r))
        rows.append(dict(p, volume_mm3=volume, com_mm=com.tolist(),
                         inertia_volume_mm5=inertia.tolist(),
                         bbox_mm=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax],
                         valid=s.isValid(), solids=len(s.Solids)))
    report = dict(source_sha256=source_sha, geometry_cache_source_sha256=index['source_sha256'], components=rows,
                  axes=plan['axes'], temporary_locks=plan['temporary_locks'],
                  frozen_native_joints=['Rev_TailYaw29'] if REVISION=='v29' else [],
                  physics_scope='Leg load screening; head and tail are fixed at CAD rest. Native tail animation is a separate kinematic test.')
    (OUT / 'geometry.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf8')
    print('Exported',len(rows),'components; source document untouched')
    for p in rows:
        if p['name'] in ['Part__Feature104','Part__Feature105','Part__Feature106','Part__Feature123','Part__Feature124','Part__Feature125']:
            print(p['name'],p['label'],p['bbox_mm'],p['volume_mm3'])
    print('Largest solid volumes (mm3):',[(p['name'],round(p['volume_mm3'])) for p in sorted(rows,key=lambda p:p['volume_mm3'],reverse=True)[:12]])


def meshes():
    sys.path.insert(0, str(ROOT/'tools/simulation'))
    from cad_model import xyz, R, make_model
    geometry=json.loads((OUT/'geometry.json').read_text(encoding='utf8'))
    assert geometry['source_sha256']==hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    model=make_model(geometry)
    meshdir=OUT/'meshes';meshdir.mkdir(exist_ok=True)
    feet={}
    for link in model['links']:
        shapes=[]
        for p in geometry['components']:
            if p['stage']!=link['stage']:continue
            s=Part.Shape();s.read(str(CACHE/(p['name']+'.brep')));shapes.append(s)
            if p['label'].startswith('Bracket_'):
                points,_=s.tessellate(.1)
                zmin=min(v.z for v in points)
                low=np.array([list(v) for v in points if v.z<zmin+.1])
                # Centre of near-lowest tread points; conservative contact proxy,
                # not an invented extra 12 mm rubber ball.
                contact=(low.min(axis=0)+low.max(axis=0))/2;contact[2]=zmin
                feet[link['stage'].split('_')[1]]=xyz(contact).tolist()
        shape=Part.makeCompound(shapes)
        mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.35,AngularDeflection=.4,Relative=False)
        transform=A.Matrix()
        for i in range(3):
            for j in range(3):setattr(transform,'A%d%d'%(i+1,j+1),R[i,j]*.001)
        from cad_model import ORIGIN_MM
        translation=-R@ORIGIN_MM*.001-np.array(link['origin_m'])
        transform.A14,transform.A24,transform.A34=translation.tolist()
        mesh.transform(transform);mesh.write(str(meshdir/(link['name']+'.stl')))
        print(link['name'],mesh.CountFacets,'facets',flush=True)
    assert len(feet)==4
    (OUT/'feet.json').write_text(json.dumps(feet,indent=2),encoding='utf8')
    print('Foot contacts:',feet,flush=True)


if __name__ == '__main__':
    meshes() if '--meshes' in sys.argv else main()
