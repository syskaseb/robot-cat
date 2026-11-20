"""Read the eight original nominal fixing parts and map the proper S0 datum."""
from pathlib import Path
from zipfile import ZipFile
from runpy import run_path
import hashlib, json, math
import numpy as np
import FreeCAD as App
import Part

p=Path(__file__).resolve().parent
g=run_path(str(p/'candidate.py')); V=App.Vector
study=p.parent.parent
source=study/'day07-S0-bounded-mount-disposition.json'
archive=study/'day07-S0-current-case-whole-mount.breps.zip'
sha=lambda q:hashlib.sha256(q.read_bytes()).hexdigest()
assert sha(source)=='661979b912db8f149c7dc2cfefde90ebd1a2a1be670ffef314b885bf98106348'
datum=json.loads(source.read_bytes())['source_mapping']
p0=np.array(datum['current_neck_seating_plane_centre_mm'])
old_to_axes=np.array([datum['labelled_IN_OUT_direction'],[-x for x in datum['current_axis_into_body']],
                      [-x for x in datum['current_casefix_pair_direction']]])
assert np.linalg.det(old_to_axes)>.999999
target=np.array([178.5,99,104.5])
shift=target-old_to_axes@p0
M=App.Matrix(*[v for i in range(3) for v in [*old_to_axes[i,:],shift[i]]],0,0,0,1)
move=App.Placement(M)
def load():
    results={}
    with ZipFile(archive) as z:
        manifest=json.loads(z.read('manifest.json'))['geometry']
        for j in manifest:
            if not j['name'].startswith('caseM6') or 'approach' in j['name']:
                continue
            raw=z.read(j['entry'])
            assert hashlib.sha256(raw).hexdigest()==j['sha256']
            s=Part.Shape()
            s.importBrepFromString(raw.decode('ascii'))
            s.Placement=move.multiply(s.Placement)
            results[j['name']]=s
    assert len(results)==8
    return results
if __name__=='__main__':
    gsrc=g['source_shapes']()
    fast=load()
    for n,s in fast.items():
        K=gsrc['S0_key']; B=gsrc['S0_body']
        print(n,g['bounds'](s),'key reserve',g['solid_hit'](s,K),'body proxy',round(s.common(B).Volume,6),flush=True)
    print('source archive',sha(archive),flush=True)
