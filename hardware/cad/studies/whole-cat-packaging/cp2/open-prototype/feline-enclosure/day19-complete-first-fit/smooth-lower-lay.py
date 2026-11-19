from common import *
from scipy.interpolate import BSpline
from scipy.optimize import least_squares
from scipy.ndimage import map_coordinates
m=np.load(P/'clearance-cache.npz');field=m['dist'];origin=m['origin'];step=m['step']
term=rd(H19/'whole-termination-plan.json');rows={q['wire']:q for q in term['wires']};ep=term['endpoints']
for i in range(1,6):ep['G1.'+str(i)].update(point=[6-6.5*(i-1),70,151],outward_axis=[0,-1,0])
ep['BAT.minus'].update(outward_axis=[0,0,-1])
# Each B-spline has the two actual port faces and their axial exit tangents.
N=9;bt=np.r_[np.zeros(4),np.linspace(0,1,N-2)[1:-1],np.ones(4)];sp=BSpline(bt,np.eye(N),3)
t0=np.linspace(0,1,83);te=np.linspace(0,1,601)
def mats(t):return [sp(t),sp.derivative()(t),sp.derivative(2)(t)]
B,V,A=mats(t0);BE,VE,AE=mats(te)
def unit(p):return p/np.maximum(np.linalg.norm(p,axis=-1,keepdims=True),1e-9)
def cur(v,a):return np.linalg.norm(np.cross(v,a),axis=1)/np.maximum(np.linalg.norm(v,axis=1),.001)**3
def distance(p):return map_coordinates(field,((p-origin)/step).T,order=1,mode='constant',cval=0,prefilter=False)
def length(p):return float(np.linalg.norm(np.diff(p,axis=0),axis=1).sum())
def fit(start,sa,end,ea,r,od,seed):
 start,sa,end,ea=map(lambda q:np.array(q,float),(start,sa,end,ea))
 def ctrl(u):return np.vstack([start,start+sa*u[0],u[2:].reshape(-1,3),end+ea*u[1],end])
 seed=np.asarray(seed,float);u0=np.r_[18,18,seed.flatten()]
 lo=np.r_[3,3,np.tile([-108,-98,43],N-4)];hi=np.r_[65,65,np.tile([190,99,170],N-4)]
 def res(u):
    c=ctrl(u);p=B@c;v=V@c;ac=A@c;ds=np.linalg.norm(v,axis=1)
    near=np.minimum(np.linalg.norm(p-start,axis=1),np.linalg.norm(p-end,axis=1))
    target=np.minimum(od/2+2.4,np.maximum(0,near-3)*.68)
    # XT60 separation and finger space extend to the deck opening. Signed distance
    # retains an escape gradient even when a starting interpolation crosses the box.
    delta=np.abs(p-[20,-30,138])-np.array([12,9,36])
    signed=np.linalg.norm(np.maximum(delta,0),axis=1)+np.minimum(np.max(delta,axis=1),0)
    keep=np.maximum(0,od/2+1.25-signed) if w!='W001' else np.zeros(len(p))
    if w=='pack':
        delta=np.abs(p-[61.05,-16.45,145.25])-[1.35,1.3,27.75]
        post=np.linalg.norm(np.maximum(delta,0),axis=1)+np.minimum(np.max(delta,axis=1),0)
        keep=keep+np.maximum(0,od/2+1.2-post)
    return np.r_[6*np.maximum(0,target-distance(p)),8*keep,150*np.maximum(0,cur(v,ac)*r-1),.0045*ds,.006*(c[2:-2]-seed).flatten(),.012*np.diff(c,2,axis=0).flatten()]
 sol=least_squares(res,u0,bounds=(lo,hi),max_nfev=240,ftol=.00001,xtol=.00001,gtol=.0001)
 c=ctrl(sol.x);pp=BE@c;vv=VE@c;rr=1/max(cur(vv,AE@c));return pp,vv,dict(controls=c.tolist(),developed=length(pp),minimum_centre_radius=rr)
def point(k):return np.array(ep[k]['point'])
tr={};led={}
for w in ['W025','W036','W061','W001','W060','pack']:
 if w=='pack':
    start=[86.5,30,73.5];end=[61,-30,145];sa=[0,0,1];ea=[0,0,-1]
    seed=[[86,30,95],[86,12,111],[85,-14,122],[73,-31,122],[61,-30,132]];od=10.1;r=19
 else:
    a,b=rows[w]['ends'];g,k=(a,b) if a.startswith('G1.') else (b,a)
    start=point(g);sa=[0,-1,0];end=point(k);ea=ep[k].get('outward_axis',[0,0,1]);od=3 if w=='W060' else 4.8;r=(21+od/2+.75 if w in ['W025','W036','W061'] else 13+od/2)
    p=np.array(start);q=np.array(end);k1=p+[0,-24,0];k2=q+np.array(ea)*26
    seed=np.linspace(k1,k2,7)[1:-1];seed[:,1]+=np.sin(np.linspace(.4,2.74,5))*12
    if w in ['W025','W036','W061']:
        seed[:,1]=np.linspace(46,-36,5)
        seed[:,2]=np.linspace(148,120,5)
    if w=='W001':seed=np.array([[0,52,149],[2,29,136],[0,8,107],[5,-12,85],[24,-25,81]])
    if w=='W061':seed=np.array([[-9,48,150],[4,25,145],[39,6,141],[47,-27,133],[32,-42,118.5]])
 pp,vv,q=fit(start,sa,end,ea,r,od,seed);led[w]=q
 if w=='pack':
    T=unit(vv);Y=np.array([0,1,0]);normal=unit(Y-(T@Y)[:,None]*T)
    for sg in [-1,1]:
        p=pp+sg*2.65*normal;tr['pack'+str(sg)]=dict(points=p.round(4).tolist(),diameter=4.8);q[str(sg)+'_mm']=length(p)
 else:
    if not rows[w]['ends'][0].startswith('G1.'):pp=pp[::-1]
    tr[w]=dict(points=pp.round(4).tolist(),diameter=od);mat=rows[w]['material'][0]
    q.update(material=mat['sku'],own_unit=mat['physical_unit'],end_mm=mat['termination_project_allowance_mm'],dress=15,project_blank_mm=5*math.ceil((length(pp)+mat['termination_project_allowance_mm']+15)/5),stock_limit=mat['retained_limit_mm'])
 print(w,round(q['developed'],2),round(q['minimum_centre_radius'],2),flush=True)
 wr('lower-approaches.json',tr);wr('lower-unit-lengths.json',dict(rows=led,endpoints={k:v for k,v in ep.items() if k.startswith('G1.')}))
