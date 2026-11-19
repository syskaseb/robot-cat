"""Choose a reachable bay for the actual full project XT60 pair and its withdrawal, within the fixed F0 lead."""
from common import *
from scipy.ndimage import minimum_filter
q=np.load(P/'clearance-cache.npz');dist=q['dist'];o=q['origin'];step=q['step'];coords=np.indices(dist.shape).reshape(3,-1).T*step+o
# Evaluate connected volumes only within the source-side bay and common top opening.
candidates=[]
for ax in [0,1,2]:
 for sign in [-1,1]:
    dims=np.array([24,18,18]);dims[ax]=64;dims[(ax+1)%3]=24
    win=tuple((2*np.ceil(dims/4).astype(int)+1).tolist());room=minimum_filter(dist,size=win,mode='constant')
    valid=np.argwhere(room>=1.5);c=o+valid*step;u=np.eye(3)[ax]*sign;boot=c-32*u;far=c+18*u
    ds=np.linalg.norm(boot-[12,0,86.25],axis=1)
    ok=(ds<44)&(c[:,2]<135)&(c[:,0]<52)&(c[:,0]>-51)
    for cc,b,f,g in zip(c[ok],boot[ok],far[ok],ds[ok]):
        # Cost uses access to battery service door or open top split, not only distance from F0.
        door=max(0,93-f[1])+max(0,75-f[2])+max(0,f[2]-79)*3+max(0,-13-f[0])*3
        top=max(0,170-f[2])+max(0,abs(f[1]+42)-12)*2+max(0,abs(f[0]-16)-18)*2
        candidates.append((min(door,top)+.12*g,ax,sign,cc.tolist(),b.tolist(),f.tolist(),float(g),'door' if door<top else 'top'))
candidates.sort();wr('battery-bays.json',dict(best=candidates[:8],basis='50 x24 x18 connected pair plus 14 axial withdrawal and gross clearance; F0 single lead 50 including 5 at termination'));print(candidates[:2])
