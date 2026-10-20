"""Fixed-radius spatial circle/straight/circle witnesses, not clearance.

The straight tangent has two free angles. Endpoint displacements of each
circular turn are R*tan(angle/2)*(incoming+outgoing). Solve those three
equations before constructing any CAD. Failure is this family, not global
infeasibility. No component positions or material margins are optimized.
"""
import math
import numpy as np
from scipy.optimize import least_squares
from receive_feline_underplate_return_gallery import bend,forward


def spatial_csc(start,t0,end,t1,R=12.4):
    p,q,a,b=map(lambda x:np.asarray(x,float),(start,end,t0,t1))
    a/=np.linalg.norm(a);b/=np.linalg.norm(b);delta=q-p
    assert R>0 and np.linalg.norm(delta)>1e-7
    def tangent(x):
        th,ph=x[:2]
        return np.array([math.cos(ph)*math.cos(th),math.cos(ph)*math.sin(th),math.sin(ph)])
    def geometry(x):
        d=tangent(x);ca=float(np.clip(a@d,-1+1e-12,1));cb=float(np.clip(b@d,-1+1e-12,1))
        aa=R*math.sqrt((1-ca)/(1+ca));bb=R*math.sqrt((1-cb)/(1+cb))
        return d,aa,bb,math.acos(ca),math.acos(cb)
    def residual(x):
        d,aa,bb,_,_=geometry(x)
        return aa*(a+d)+x[2]*d+bb*(d+b)-delta
    direction=delta/np.linalg.norm(delta)
    normal=np.cross(a,b)
    if np.linalg.norm(normal)<1e-8:normal=np.cross(direction,[0,0,1])
    if np.linalg.norm(normal)<1e-8:normal=np.array([1.,0,0])
    normal/=np.linalg.norm(normal)
    solutions=[]
    for seed in (direction,direction+.6*normal,direction-.6*normal,direction+.6*(a+b)):
        if np.linalg.norm(seed)<1e-8:continue
        seed=seed/np.linalg.norm(seed)
        initial=[math.atan2(seed[1],seed[0]),math.asin(float(seed[2])),max(0.,np.linalg.norm(delta)-2*R)]
        fit=least_squares(residual,initial,bounds=([-4*math.pi,-math.pi/2,0],[4*math.pi,math.pi/2,1000]),
                          max_nfev=120,ftol=1e-12,xtol=1e-12,gtol=1e-12)
        if np.linalg.norm(residual(fit.x))>1e-6:continue
        d,aa,bb,alpha,beta=geometry(fit.x)
        solutions.append((R*(alpha+beta)+fit.x[2],d,alpha,beta,float(fit.x[2])))
    if not solutions:raise ValueError('No fixed-radius spatial CSC witness in this tangent family')
    length,d,alpha,beta,straight=min(solutions,key=lambda x:x[0]);rows=[];point=p.copy();heading=a.copy()
    for turn in (0,1):
        target=d if turn==0 else b;angle=alpha if turn==0 else beta
        if angle>1e-7:
            normal=target-heading*float(heading@target);normal/=np.linalg.norm(normal)
            point,heading=bend(rows,point,heading,normal,R,angle)
        if turn==0:point=forward(rows,point,d,straight);heading=d.copy()
    assert np.linalg.norm(point-q)<2e-6 and np.linalg.norm(heading-b)<2e-6
    return rows
