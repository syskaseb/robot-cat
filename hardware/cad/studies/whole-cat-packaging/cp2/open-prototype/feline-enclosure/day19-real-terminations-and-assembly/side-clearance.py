"""Refine the broad leg height bound only where a moving member reaches the footprint of the added skirt."""
from pathlib import Path
import json,itertools,math,runpy,numpy as np
from scipy.spatial.transform import Rotation
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.gp import gp_Pnt,gp_Trsf
from OCP.TopLoc import TopLoc_Location
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
P=Path(__file__).parent;R=next(x for x in P.parents if (x/'.git').exists())
def rd(p):return json.loads(p.read_bytes())
q=rd(P.parent/'motion-layout.json');j={(a['code'],a['stage']):a for a in rd(R/'hardware/simulation/p0/e6-leg-compatibility.json')['axes']}
inv={r['object']:np.array(list(itertools.product(*zip(*r['bounds_mm'])))) for r in q['inventory'] if r['object'].startswith('Ref_Material_P0')}
skirts=[[-161.5,-113.95,82,-62.7,-112.30,110.6],[-161.6,-113.95,82,-159.95,-101.95,111],[-161.3,-113.75,82,-62.8,-106.15,83.65]];pairs=[];gz=1e9
for i,p in enumerate(q['poses']):
 for code,x in p['legs'].items():
    t=np.eye(4)
    for stage,deg in zip(['Hip','Knee','Ankle'],x['angles_delta_degrees']):
        a=j[code,stage];v=np.array(a['pivot_mm']);r=Rotation.from_rotvec(np.array(a['axis'])*math.radians(deg)).as_matrix();m=np.eye(4);m[:3,:3]=r;m[:3,3]=v-r@v;t=t@m
        for n in q['membership'][code][stage]:
            pts=inv[n]@t[:3,:3].T+t[:3,3];lo=pts.min(0);hi=pts.max(0)
            for h,b in enumerate(skirts):
                if all(lo[:2]<=b[3:5]) and all(hi[:2]>=b[:2]):
                    gz=min(gz,b[2]-hi[2])
                    if hi[2]>=b[2] and lo[2]<=b[5]:pairs.append((i,n,h,t.copy()))
out=dict(candidates=len(pairs),lowest_Z_separation_with_overlapping_XY=gz if gz<1e8 else None,scope='three added lower walls only, 49 retained poses; mesh-box upper limits, before wire dressing',material_intersections=[])
if pairs:
 src=(P.parent/'day18-front-insert-correction/saved-front.py').read_text();src=src.replace('assert np.allclose(self.bounds("VL53L5CX"),[-208.566,-6.35,94,-206,6.35,111.78],atol=1e-4)','pass');exec(src);old=Saved(P.parent/'FelineInteriorMotion.FCStd')
 solid=[BRepPrimAPI_MakeBox(gp_Pnt(*b[:3]),gp_Pnt(*b[3:])).Shape() for b in skirts]
 for i,n,h,t in pairs:
    assert np.allclose(old.bounds(n),[*inv[n].min(0),*inv[n].max(0)],atol=.7),n
    tr=gp_Trsf();tr.SetValues(*t[:3,:].flatten());sh=old.shape(n).Moved(TopLoc_Location(tr));common=BRepAlgoAPI_Common(sh,solid[h]);pr=GProp_GProps();BRepGProp.VolumeProperties_s(common.Shape(),pr)
    if pr.Mass()>.00001:out['material_intersections'].append([i,n,h,pr.Mass()])
(P/'side-clearance.json').write_bytes((json.dumps(out,indent=1)+'\n').encode());print(out)
