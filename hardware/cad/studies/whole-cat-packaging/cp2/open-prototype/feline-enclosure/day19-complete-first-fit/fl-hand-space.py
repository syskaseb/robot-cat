"""Find a continuous bend-limited lane through the open FL bay. Only these two changed ends."""
from common import *
from scipy.spatial import cKDTree
from scipy.ndimage import map_coordinates
m=np.load(P/'clearance-cache.npz');distance=m['dist'];origin=m['origin'];step=m['step']
data=rd(P/'changed-branch-lays.json');regs=rd(P/'fl-region.json');prev=rd(P/'front-service-lay.json');ep=rd(H19/'whole-termination-plan.json')['endpoints'];ep.update(data['endpoints'])
# Restore the actual underside edge missed by the 2 mm travel raster.
# Leave its neighbourhood unallocated when finding a connected lane.
z=np.array([-52.436,-65.955,108.679]);i=np.rint((z-origin)/step).astype(int);grid=np.indices((17,17,17)).transpose(1,2,3,0)+i-8;sl=tuple(slice(v-8,v+9) for v in i)
distance[sl]=np.minimum(distance[sl],np.maximum(0,np.linalg.norm(origin+grid*step-z,axis=-1)-4.5))
# Reserve the complete banks of intact ATO fittings, including their thin end
# blades, as occupied volumes. Do not route the shared lane between blades.
saved=Saved(native)
for n in saved.members:
 if n.startswith('Motor_ATO'):
    b=saved.bounds(n);lo=np.maximum(0,np.floor((b[:3]-origin-9)/step).astype(int));hi=np.minimum(distance.shape,np.ceil((b[3:]-origin+9)/step).astype(int)+1)
    if min(hi-lo)<=0:continue
    c=origin+(np.indices(tuple(hi-lo)).transpose(1,2,3,0)+lo)*step
    delta=np.maximum(b[:3]-c,c-b[3:]);ds=np.linalg.norm(np.maximum(delta,0),axis=-1)
    sl=tuple(slice(a,b) for a,b in zip(lo,hi));distance[sl]=np.minimum(distance[sl],ds)
def free(p):return map_coordinates(distance,((p.reshape(-1,3)-origin)/step).T,order=1,mode='constant',cval=0,prefilter=False).reshape(p.shape[:-1])
def norm(p):return p/np.maximum(np.linalg.norm(p,axis=-1,keepdims=True),1e-9)
def beams(a,u,b,rad,od):
 pos=[np.array(a)];vec=[np.array(u)];paths=[[np.array([a])]];seen=set();levels=[0];low=np.array([-96,-99,43]);high=np.array([97,75,158])
 for lev in range(14):
    ix=np.array(levels);p=np.array(pos)[ix];v=np.array(vec)[ix];side=norm(np.cross(v,np.eye(3)[np.argmin(abs(v),axis=1)]));up=np.cross(v,side);bucket=[]
    for angle in np.arange(10)*math.tau/10:
     w=math.cos(angle)*side+math.sin(angle)*up
     for rr,turn in [(rad,14/rad),(1e5,.00014)] if angle==0 else [(rad,14/rad)]:
        th=np.linspace(0,turn,9);pp=p[:,None]+rr*(np.sin(th)[None,:,None]*v[:,None]+(1-np.cos(th))[None,:,None]*w[:,None]);vv=math.cos(turn)*v+math.sin(turn)*w
        req=np.full((1,9),od/2+1.15)
        if lev==0:req=np.minimum(req,np.maximum(0,rr*th-1)[None,:]*.72);req[0,0]=0
        ok=(free(pp)>=req-.001).all(axis=1)&(pp[:,-1]>=low).all(axis=1)&(pp[:,-1]<=high).all(axis=1)
        for k in np.flatnonzero(ok):bucket.append((float(np.linalg.norm(pp[k,-1]-b)),ix[k],pp[k],vv[k]))
    levels=[]
    for score,k,edge,v1 in sorted(bucket,key=lambda q:q[0]):
        key=tuple(np.r_[np.rint(edge[-1]/7),np.rint(v1*2.4)].astype(int))
        if key in seen:continue
        seen.add(key);levels.append(len(pos));pos.append(edge[-1]);vec.append(v1);paths.append(paths[k]+[edge[1:]])
        if len(levels)>=460:break
    if not levels:break
 return np.array(pos),np.array(vec),paths
def solve(name,rad,od):
 a,e=[ep[k] for k in regs[name]['ends']];p,q=map(lambda v:np.array(v,float),[a['point'],e['point']]);u=np.array(a.get('outward_axis',[1,0,0]));v=np.array(e['outward_axis'])
 x,t,paths=beams(p,u,q,rad,od);y,w,backs=beams(q,v,p,rad,od);tree=cKDTree(y)
 th=np.linspace(0,1,33)[None,:,None];res=[]
 for i in range(0,len(x),35):
    ids=np.arange(i,min(i+35,len(x)));pairs=tree.query_ball_point(x[ids],65)
    aa=[];bb=[]
    for j,ii in enumerate(pairs):
     if ii:aa.extend([ids[j]]*len(ii));bb.extend(ii)
    if not aa:continue
    ar,br=np.array(aa),np.array(bb);d=y[br]-x[ar];L=np.linalg.norm(d,axis=1);u0=norm(d);ok=(L>20)&((t[ar]*u0).sum(axis=1)>.25)&((-w[br]*u0).sum(axis=1)>.25);ar=ar[ok];br=br[ok];L=L[ok]
    if not len(ar):continue
    A=x[ar,None];B=A+t[ar,None]*L[:,None,None]*.38;D=y[br,None];C=D+w[br,None]*L[:,None,None]*.38
    pp=(1-th)**3*A+3*(1-th)**2*th*B+3*(1-th)*th**2*C+th**3*D
    vel=3*((1-th)**2*(B-A)+2*(1-th)*th*(C-B)+th**2*(D-C));acc=6*((1-th)*(C-2*B+A)+th*(D-2*C+B))
    kr=np.linalg.norm(np.cross(vel,acc),axis=2)/np.maximum(.00001,np.linalg.norm(vel,axis=2))**3
    ok=(kr.max(axis=1)<=1/rad)&(free(pp).min(axis=1)>=od/2+1.15)
    for k in np.flatnonzero(ok):
     cost=(len(paths[ar[k]])+len(backs[br[k]])-2)*14+np.linalg.norm(np.diff(pp[k],axis=0),axis=1).sum()
     if not res or cost<res[0]:res=[cost,np.vstack([*paths[ar[k]],pp[k,1:-1],np.vstack(backs[br[k]])[::-1]]),1/max(kr[k].max(),1/rad)]
    if res and res[0]<200:break
 if not res:raise ValueError((name,len(x),len(y),'no radius-qualified lane'))
 cost,pp,r=res;row=dict(prev[name][0]);row.update(developed=cost,points=pp.round(4).tolist(),minimum_centre_radius=rad,method='open bay reachable by tangent circular segments and terminal-matched join, no permanent wire former',controls=None)
 row['planned_blank_mm']=math.ceil((cost+row['ends_outside_lay_mm']+row['project_dress'])/5)*5
 return [row]
out={}
for name,R,od in [('W041/custom',27.6,4.2),('W041/factory',15,4.8)]:
 out[name]=solve(name,R,od);wr('fl-hand-space.json',out);print(name,out[name][0]['developed'],flush=True)
