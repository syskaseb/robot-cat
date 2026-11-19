from common import *
from scipy.spatial import cKDTree
Q=rd(H19/'whole-termination-plan.json');routes=rd(H19/'named-approaches.json');l=rd(F/'service-lay.json')
def dense(ps,inc=.85):
 return np.vstack([np.linspace(a,b,max(2,1+math.ceil(np.linalg.norm(np.array(b)-a)/inc))) for a,b in zip(ps,ps[1:])])
def layout(x,y,u,rr=17):
 u=np.array([*u,0.]);u=u/np.linalg.norm(u);ac=np.cross(u,[0,0,1.]);rows=[]
 for lift in np.linspace(0,14,15):
    h=163+lift/2;a=np.array([x,y,h]);p=[a+[0,0,152+lift-h],a]
    p.extend(a+rr*((1-math.cos(t))*u+np.array([0,0,math.sin(t)])) for t in np.linspace(0,math.pi,64));p.append(a+2*rr*u+[0,0,145-h])
    for sg in [-1,1]:
        pp=dense(np.array(p)+sg*2.65*ac);rows.append(dict(lift=lift,side=sg,points=np.round(pp,4).tolist(),length=82.407075111,min_bend=rr-2.4))
 return rows
def neighbours(b):
 other={k:(v['points'],v['diameter']/2) for k,v in routes.items()};out={}
 for i,q in enumerate([*l['fixed'].values(),*rd(P/'remote-pulldown-lay.json')['pitch']]):
    other[q['unit']+' pose '+str(i)]=(q['points'],3.4 if q['unit']=='DATA500' else 1.98)
 for k,(pts,r) in other.items():
    t=cKDTree(dense(pts));mn=min(float(min(t.query(q['points'])[0])) for q in b);out[k]=round(mn-r-2.4,3)
 return out
if __name__=='__main__':
 b=layout(20,-30,[0,1]);wr('battery-first-layout.json',dict(bights=b,neighbours=neighbours(b)));print([(k,v) for k,v in neighbours(b).items() if v<3])
