from common import *
import zipfile,shutil
from xml.etree import ElementTree as ET
exec((P/'final-evidence.py').read_text().split('with zipfile.ZipFile(native)')[0])
with zipfile.ZipFile(native) as z,zipfile.ZipFile(P/'geometry-tested.FCBak') as t:
 assert z.testzip() is None;now=streams(z);previous=streams(t);assert set(now)==set(previous)
 delta=[n for n in now if now[n]!=previous[n]]
 assert 'H19_FrontFrame' in delta and set(delta)<={'YAW_SOURCE_EAR_19_full_screw','YAW_SOURCE_EAR_19_headwasher','H19_FrontFrame'},delta
before=Saved(P/'geometry-tested.FCBak');after=Saved(native)
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
steel={}
for name in set(delta)-{'H19_FrontFrame'}:
 a,b=before.shape(name),after.shape(name);assert np.allclose(before.bounds(name),after.bounds(name),atol=1e-6,rtol=0)
 residual=[]
 for x,y in [(a,b),(b,a)]:
    op=BRepAlgoAPI_Cut(x,y);assert op.IsDone();props=GProp_GProps();BRepGProp.VolumeProperties_s(op.Shape(),props);residual.append(abs(props.Mass()))
 assert max(residual)<.000001,(name,residual);steel[name]=residual
receipt=rd(P/'export-identity.json')
exec(compile((H19/'frame-export.py').read_text(),str(H19/'frame-export.py'),'exec'))
idx=rd(P/'material-index.json');frame=next(v for v in idx['parts'] if v['part']=='H19_FrontFrame');frame['volume_total_mm3']=rd(P/'frame-mesh-proof.json')['native_volume']*frame['qty']
mass=sum(r['volume_total_mm3'] for r in idx['parts'])*.00127;idx.update(native_sha256=sha(native),geometric_P_g=mass,known_robot_scenario_g=[1853.4+mass,2593.4+mass]);wr('material-index.json',idx)
receipt.update(final_native=sha(native),changed_serialized_streams_since_display=delta,steel_world_symmetric_difference_mm3=steel,solid_parts_reexported_after_display=['H19_FrontFrame'],remaining_geometry_unchanged=len(now)-1);wr('export-identity.json',receipt)
shutil.copyfile(native,P/'geometry-tested.FCBak');print(sha(native),mass)
