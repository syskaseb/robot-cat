"""Develop the factory pitch reserve in the negative cheek and receive it on the body."""
from pathlib import Path
import numpy as np,json,math
from scipy.interpolate import BSpline,make_interp_spline
from scipy.optimize import minimize
P=Path(__file__).parent;Y=np.array([0.,1.,0]);X=np.array([1.,0.,0]);Z=np.array([0.,0.,1]);C=np.array([-130.,0,127])
def arc(s,t,n,r,a):
    return np.array([s+r*(math.sin(q)*t+(1-math.cos(q))*n) for q in np.linspace(0,a,49)])
# A stationary mating pair is approached from the anterior cheek. The return
# bends in XZ on the outboard side of the fork rather than above the terminals.
E=np.array([-113.,-55.,142.]);K=17
knots=np.r_[np.zeros(4),np.linspace(0,1,K-2)[1:-1],np.ones(4)]
basis=BSpline(knots,np.eye(K),3)
u=np.linspace(0,1,101);B,B1,B2=(basis(u,n) for n in (0,1,2))
gx,gw=np.polynomial.legendre.leggauss(8);br=np.unique(knots);t=np.concatenate([a+(b-a)*(gx+1)/2 for a,b in zip(br,br[1:])]);weight=np.concatenate([(b-a)*gw/2 for a,b in zip(br,br[1:])]);L=basis(t,1)
ans=[];raw=223.55;debit=math.pi*12.5
for y in [-20,-10,0,10,20]:
    a=math.radians(y);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1.]])
    lead=(arc(np.array([-159,-43.8,131.5]),-Y,X,25,math.pi/2)-C)@R.T+C
    S=lead[0];T=R@(-Y);out=R@X
    def seed(u):
        v0=np.clip((u-debit/raw)/(1-debit/raw),0,1);h=v0*v0*(3-2*v0);b=2*np.pi*v0
        v=(1-h[:,None])*out+h[:,None]*X
        circle=lead[-1]+(E-lead[-1])*h[:,None]+27*(np.sin(b)[:,None]*v+(1-np.cos(b))[:,None]*Z)
        a=np.minimum(1,u*raw/debit)*np.pi/2
        first=S+25*(np.sin(a)[:,None]*T+(1-np.cos(a))[:,None]*out)
        return np.where((u<debit/raw)[:,None],first,circle)
    s0=seed(u);mid=np.linalg.lstsq(B,s0,rcond=None)[0][2:-2]
    def cp(q):return np.vstack([S,S+q[0]*T,q[2:].reshape(-1,3),E-q[1]*X,E])
    def length(c):return weight@np.linalg.norm(L@c,axis=1)
    def radius(c):
        d=B1@c;dd=B2@c;return np.linalg.norm(d,axis=1)**3/np.maximum(.000001,np.linalg.norm(np.cross(d,dd),axis=1))
    def score(q):
        c=cp(q);return np.mean((B@c-s0)**2)+.003*np.mean((np.diff(c,n=2,axis=0))**2)
    def cons(q):
        c=cp(q);pts=B@c
        return np.r_[1-24.6/np.maximum(radius(c),.01),(-42-pts[22:,1])/22,(pts[:,1]+81)/22,(196-pts[:,2])/22]
    res=minimize(score,np.r_[6.,6.,mid.flat],method="SLSQP",bounds=[(2,14)]*2+[(None,None)]*mid.size,
                 constraints=[dict(type="eq",fun=lambda q:(length(cp(q))-raw)/10),dict(type="ineq",fun=cons)],options=dict(maxiter=240,ftol=2e-7))
    c=cp(res.x);fine=np.linspace(0,1,801);d=basis(fine,1)@c;dd=basis(fine,2)@c
    realR=np.min(np.linalg.norm(d,axis=1)**3/np.maximum(.000001,np.linalg.norm(np.cross(d,dd),axis=1)))
    pts=basis(np.linspace(0,1,241))@c
    ans.append(dict(yaw=y,centreline=pts.round(6).tolist(),key_tip=(E+15*X).tolist(),key_axis=X.tolist(),raw=250,case_stub=11.45,free=length(c),key=15,inner_R=realR-math.hypot(1.75,.9),sampled_curve_radius=realR,solver=res.message))
(P/"side-flex.json").write_bytes((json.dumps(ans,separators=(",",":"))+"\n").encode())
print([(q["yaw"],round(q["free"],4),round(q["inner_R"],3),q["solver"]) for q in ans])
