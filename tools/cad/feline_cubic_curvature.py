"""Continuous cubic B-spline curvature extrema, not a sample-only verdict.

Per-span stationary roots of N'/D^3-3ND'/D^4, with N=|v cross a|² and
D=|v|². Numerical polynomial roots are reported as such, not formal interval
certification or a manufacturer bend guarantee. Zero-speed spans are failures.
"""
import math
import numpy as np
from numpy.polynomial import Polynomial as P
from scipy.interpolate import BSpline,PPoly
from scipy.integrate import quad


def clamped_knots(count,degree=3):
    return np.r_[np.zeros(degree+1),np.linspace(0,1,count-degree+1)[1:-1],np.ones(degree+1)]


def real_unit_roots(poly):
    return [float(np.clip(z.real,0,1)) for z in poly.trim(1e-10).roots()
            if abs(z.imag)<1e-7 and -1e-8<=z.real<=1+1e-8]


def extrema(knots,controls,degree=3):
    assert degree==3
    pp=[PPoly.from_spline(BSpline(knots,np.asarray(controls)[:,i],degree)) for i in range(3)]
    maximum=0.;minimum_speed=math.inf;rows=[]
    for j,(lo,hi) in enumerate(zip(pp[0].x[:-1],pp[0].x[1:])):
        span=hi-lo
        if span<1e-12:continue
        rr=[P(q.c[:,j][::-1]*span**np.arange(4)) for q in pp]
        v=[q.deriv() for q in rr];a=[q.deriv(2) for q in rr]
        cross=[v[1]*a[2]-v[2]*a[1],v[2]*a[0]-v[0]*a[2],v[0]*a[1]-v[1]*a[0]]
        N=sum((q*q for q in cross),P([0]));D=sum((q*q for q in v),P([0]))
        speed_values=[max(0,float(D(t))) for t in [0.,1.]+real_unit_roots(D.deriv())]
        min_speed=math.sqrt(min(speed_values));minimum_speed=min(minimum_speed,min_speed/span)
        if min_speed<1e-9:return dict(regular=False,minimum_radius_mm=0,zero_speed_span=[float(lo),float(hi)],method='Cubic stationary polynomial roots')
        candidates=[0.,1.]+real_unit_roots(N.deriv()*D-3*N*D.deriv())
        values=[math.sqrt(max(0,float(N(t))))/max(float(D(t)),1e-25)**1.5 for t in candidates]
        k=max(values);maximum=max(maximum,k);index=int(np.argmax(values))
        rows.append(dict(u_span=[float(lo),float(hi)],maximum_curvature_per_mm=k,
            maximum_u=float(lo+span*candidates[index]),stationary_candidates=len(candidates)))
    return dict(regular=True,minimum_radius_mm=1/maximum if maximum>1e-12 else None,
        maximum_curvature_per_mm=maximum,minimum_speed_mm_per_u=minimum_speed,spans=rows,
        method='Numerical real stationary polynomial roots on EVERY cubic span plus span endpoints; not formal interval arithmetic')


def exact_length(knots,controls):
    b=BSpline(knots,controls,3);d=b.derivative();total=0.;error=0.
    for lo,hi in zip(np.unique(knots)[:-1],np.unique(knots)[1:]):
        v,e=quad(lambda u:float(np.linalg.norm(d(u))),lo,hi,epsabs=1e-8,epsrel=1e-10,limit=100)
        total+=v;error+=e
    return total,error
