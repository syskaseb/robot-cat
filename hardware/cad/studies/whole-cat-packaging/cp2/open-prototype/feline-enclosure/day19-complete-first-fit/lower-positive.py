from common import *
from scipy.optimize import minimize
from scipy.special import comb
a=np.array([12,0,86.125]);z=np.array([12,-30,102])
def bern(n,t):return np.stack([comb(n,k)*t**k*(1-t)**(n-k) for k in range(n+1)],axis=1)
def eval_curve(x,t):
 pts=np.array([a,a+[-x[0],0,0],x[2:5],x[5:8],z+[0,0,-x[1]],z]);return bern(5,t)@pts,5*bern(4,t)@np.diff(pts,axis=0),20*bern(3,t)@np.diff(pts,n=2,axis=0)
t=np.linspace(0,1,101)
def metric(x):
 p,v,b=eval_curve(x,t);ss=np.linalg.norm(v,axis=1);return np.trapezoid(ss,t),np.linalg.norm(np.cross(v,b),axis=1)/ss**3
sol=minimize(lambda x:-x[-1],[8,8,-4,-8,86,10,-29,88,6],method='SLSQP',bounds=[(2,19),(2,19),(-10,17),(-27,-1),(80,99),(-5,22),(-38,-10),(80,99),(4,23)],constraints=[dict(type='eq',fun=lambda x:metric(x)[0]-45),dict(type='ineq',fun=lambda x:1-x[-1]*metric(x)[1])],options={'ftol':1e-9,'maxiter':330})
p,v,b=eval_curve(sol.x,np.linspace(0,1,501));ss=np.linalg.norm(v,axis=1);r=min(ss**3/np.maximum(1e-10,np.linalg.norm(np.cross(v,b),axis=1)))
length=np.trapezoid(ss,np.linspace(0,1,501));assert abs(length-45)<.015
wr('W075-seated.json',dict(points=p.round(5).tolist(),diameter=4.8,project_free_mm=length,source_end_debit=5,source_limit=50,achieved_inner_radius=r-2.4,measured_minimum_radius=None,initial_tangent='-X at F0',final_tangent='+Z below XT60 boot',source='F0 supplied 12 AWG',physical=None));print(length,r-2.4)
