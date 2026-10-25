"""Saved cubic normal-disc halfspace bound; no replacement curve or pipe repair."""
import math
import numpy as np
from numpy.polynomial import Polynomial
from scipy.interpolate import PPoly


def bernstein_minimum(poly):
    c=poly.coef;n=len(c)-1
    return min(sum(c[i]*math.comb(k,i)/math.comb(n,i) for i in range(k+1)) for k in range(n+1))


def positive_x_halfspace(curve,plane_x,radius):
    """Every normal disc must lie on X>=plane_x. Negative bound is HOLD.

    For positive speed, (x-plane)^2*|v|^2-r^2*(vy^2+vz^2)>=0,
    together with x-plane>=0, bounds the complete circular normal section.
    Bernstein coefficients enclose whole polynomial spans, not samples.
    """
    assert curve.Degree==3 and not curve.isRational()
    knots=np.repeat(curve.getKnots(),curve.getMultiplicities())
    poles=np.array([list(p) for p in curve.getPoles()])
    pp=[PPoly.from_spline((knots,poles[:,j],curve.Degree)) for j in range(3)]
    rows=[]
    for i,(a,b) in enumerate(zip(pp[0].x[:-1],pp[0].x[1:])):
        if b-a<1e-12:continue
        xyz=[Polynomial(p.c[:,i][::-1]*(b-a)**np.arange(4)) for p in pp]
        x=xyz[0]-plane_x;dx,dy,dz=[p.deriv() for p in xyz]
        speed=dx*dx+dy*dy+dz*dz
        speed_lower=bernstein_minimum(speed)
        if speed_lower<=0:
            raise ValueError('Normal plane not certified: speed lower bound is nonpositive')
        witness=x*x*speed-radius**2*(dy*dy+dz*dz)
        rows.append(dict(parameter=[float(a),float(b)],
                         x_bernstein_min=bernstein_minimum(x),
                         speed_squared_bernstein_min=speed_lower,
                         disc_polynomial_bernstein_min=bernstein_minimum(witness)))
    return rows
