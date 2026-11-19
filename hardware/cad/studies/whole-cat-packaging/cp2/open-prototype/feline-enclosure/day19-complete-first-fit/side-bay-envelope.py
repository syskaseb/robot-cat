from common import *
import itertools,trimesh
from scipy.spatial.transform import Rotation
from vtkmodules.util.numpy_support import vtk_to_numpy
s=(G/'named-check.py').read_text().split('tr=json.loads')[0].replace('whole-cat19G.FCStd','whole-cat19I.FCStd');exec(s)
# Only legs whose transformed bounds enter the disputed lower side bay contribute.
# 4 mm cells store upper bounds of all triangle fragments after 3 mm edge subdivision.
q=rd(O/'motion-layout.json');j={(a['code'],a['stage']):a for a in rd(H/'simulation/p0/e6-leg-compatibility.json')['axes']}
inv={v['object']:np.array(list(itertools.product(*zip(*v['bounds_mm'])))) for v in q['inventory'] if v['object'].startswith('Ref_Material_P0')}
code=(O/'day18-front-insert-correction/saved-front.py').read_text().replace('assert np.allclose(self.bounds("VL53L5CX"),[-208.566,-6.35,94,-206,6.35,111.78],atol=1e-4)','pass')
exec(code);D=Saved(O/'FelineInteriorMotion.FCStd');cache={};xx=np.arange(-112,25,4.);yy=np.arange(-108,-47,4.)
Z=np.full((len(xx)-1,len(yy)-1),-999.);obs=set();cnt=0
for i,pose in enumerate(q['poses']):
 for leg,p in pose['legs'].items():
    t=np.eye(4)
    for stage,deg in zip(['Hip','Knee','Ankle'],p['angles_delta_degrees']):
        a=j[leg,stage];v=np.array(a['pivot_mm']);r=Rotation.from_rotvec(np.array(a['axis'])*math.radians(deg)).as_matrix();mat=np.eye(4);mat[:3,:3]=r;mat[:3,3]=v-r@v;t=t@mat
        for n in q['membership'][leg][stage]:
            b=inv[n]@t[:3,:3].T+t[:3,3];lo=b.min(0);hi=b.max(0)
            if hi[0]<xx[0] or lo[0]>xx[-1] or hi[1]<yy[0] or lo[1]>yy[-1] or hi[2]<37:continue
            if n not in cache:
                poly=mesh(n)[1];v=vtk_to_numpy(poly.GetPoints().GetData());f=vtk_to_numpy(poly.GetPolys().GetConnectivityArray()).reshape(-1,3);cache[n]=trimesh.remesh.subdivide_to_size(v,f,3.0,max_iter=8)[:2]
            v,f=cache[n];xyz=(v@t[:3,:3].T+t[:3,3])[f];lo=xyz.min(axis=1);hi=xyz.max(axis=1);use=(hi[:,0]>=xx[0])&(lo[:,0]<=xx[-1])&(hi[:,1]>=yy[0])&(lo[:,1]<=yy[-1])&(hi[:,2]>37)
            if not use.any():continue
            cnt+=1;obs.add(leg);lo=lo[use];hi=hi[use]
            low=np.maximum(0,np.floor((lo[:,:2]-[xx[0],yy[0]])/4).astype(int));high=np.minimum(np.array(Z.shape)-1,np.floor((hi[:,:2]-[xx[0],yy[0]])/4).astype(int))
            for dx in (0,1):
             for dy in (0,1):
                at=low+[dx,dy];use=np.all(at<=high,axis=1);np.maximum.at(Z,(at[use,0],at[use,1]),hi[use,2])
wr('side-bay-envelope.json',dict(x=xx.tolist(),y=yy.tolist(),upper_z=Z.round(3).tolist(),legs=sorted(obs),member_pose_subsets=cnt,fragment_edge_mm=3,cell_mm=4,stock_49_basis='planning only, no measured gait/physical PASS'))
print('legs',obs,'max',Z.max(),'zones',[(x,round(float(Z[i].max()),1)) for i,x in enumerate(xx[:-1]) if i%3==0])
