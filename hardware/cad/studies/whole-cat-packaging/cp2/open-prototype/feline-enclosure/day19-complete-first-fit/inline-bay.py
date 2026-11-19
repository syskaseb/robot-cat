from common import *
from scipy.ndimage import map_coordinates
m=np.load(P/'clearance-cache.npz');o=m['origin'];d=m['dist'];step=m['step'];options=[]
def block(lo,hi,inc=3):
 return np.array(np.meshgrid(*[np.linspace(v,w,max(2,math.ceil((w-v)/inc)+1)) for v,w in zip(lo,hi)],indexing='ij')).reshape(3,-1).T
for rot in [0,90]:
 for tier in [False,True]:
    q=block([-18,-4.05,0],[18,4.05,8.9]);r=block([-27,-2,2.2],[27,2,6.7]);base=np.vstack([q,r]);vec=[0,0,13] if tier else [0,11,0];pts=np.vstack([base,base+vec])
    if rot:pts[:,:2]=pts[:,:2]@np.array([[0,1],[-1,0]])
    for x in range(-69,2,5):
     for y in range(-79,-24,5):
      for z in [50,55,61,67,73]:
        a=pts+[x,y,z];g=min(map_coordinates(d,((a-o)/step).T,order=1,mode='constant',cval=0));score=min(g,7)-.018*abs(x+55)-.012*abs(y+65)-.1*tier
        if g>1.:options.append((round(float(score),3),round(float(g),3),rot,tier,x,y,z))
options.sort(reverse=True);wr('inline-bay-options.json',dict(best=options[:20]));print(options[:5])
