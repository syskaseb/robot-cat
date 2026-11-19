from common import *
from scipy.ndimage import minimum_filter, map_coordinates
from scipy.spatial import cKDTree
m=np.load(H19/'clearance-cache.npz');o=m['origin'];d=m['dist'];step=m['step']
w=rd(H19/'named-approaches.json');l=rd(F/'service-lay.json')
cloud=np.vstack([q['points'] for q in list(w.values())+list(l['fixed'].values())+l['pitch_transfer']]);tr=cKDTree(cloud)
def sample(lo,hi):
 return np.array(np.meshgrid(*[np.linspace(a,b,math.ceil((b-a)/3)+1) for a,b in zip(lo,hi)],indexing='ij')).reshape(3,-1).T
def vals(p):return map_coordinates(d,((p-o)/step).T,order=1,mode='constant',cval=0)
# Search two side-gallery strips immediately above the lower banks. Reserve a
# full wire-entry lane ahead of all five terminals and two short roots to the wall.
opts=[]
for side in [-1,1]:
 sy=-side
 for z in [135,143,151,159,166]:
    for x in range(-49,141,6):
        for back in [97,92,87]:
            c=np.array([x,side*(back-11),z]);u=np.array([0,sy,0])
            body=sample([-18.5,-11,-5.5],[18.5,11,5.5])+c
            entry=sample([-15.3,-.1,-2.4],[15.3,19.6,2.4]);entry[:,1]*=sy;entry+=c+11*u
            a=np.vstack([body,entry]);h=float(min(vals(a)));f=float(min(tr.query(a)[0]))-2.5
            score=min(h,f,6)-.006*abs(x-40)-.015*(97-back)
            opts.append((score,h,f,c.tolist(),side,back))
opts.sort(reverse=True);wr('gallery-station-options.json',dict(best=opts[:14],basis='two upper side galleries with actual 37x22x11 gross body + full 5-port straight entry layer + retained wire sets'));print(opts[:6])
