from common import *
from scipy.spatial import cKDTree
from importlib.machinery import SourceFileLoader
j=SourceFileLoader('bight',str(P/'joint-layout.py')).load_module()
from scipy.ndimage import map_coordinates
m=np.load(H19/'clearance-cache.npz');o=m['origin'];step=m['step']
r=rd(H19/'named-approaches.json');l=rd(F/'service-lay.json')
trees={k:(cKDTree(j.dense(v['points'])),v['diameter']/2) for k,v in r.items()}
for i,q in enumerate([*l['fixed'].values(),*l['pitch_transfer']]):
 trees[q['unit']+str(i)]=(cKDTree(j.dense(q['points'])),3.4 if q['unit']=='DATA500' else 1.98)
def points(x,y,u):
 u=np.r_[u,0];ac=np.cross(u,[0,0,1]);r=17;a=np.array([x,y,163]);rows=[]
 for lift in (0,7,14):
    c=a+[0,0,lift/2];p=np.array([a+[0,0,lift-11],*[(c+r*((1-math.cos(t))*u+np.array([0,0,math.sin(t)]))) for t in np.linspace(0,math.pi,25)],a+34*u+[0,0,-18]])
    for sg in [-1,1]:rows.extend(j.dense(p+sg*2.65*ac,2.5))
 return np.array(rows)
opt=[]
for x in [13,20,27]:
 for y in [-34,-30,-26]:
    for deg in range(0,360,15):
        u=np.array([math.cos(math.radians(deg)),math.sin(math.radians(deg))]);p=points(x,y,u)
        vals={k:round(float(min(t.query(p)[0]))-2.4-rad,2) for k,(t,rad) in trees.items()}
        # Minimise changes to actual fixed purchased units and prioritise clear release.
        bad=[k for k in vals if vals[k]<1];opt.append((len(bad),-min(vals.values()),x,y,deg,bad))
opt.sort();wr('release-plane-survey.json',dict(survey=opt[:20],scope='alternative ports on the same original boot face, full constant-length loop with three withdrawals, source flexible jacket neighbours only'));print(opt[:8])
