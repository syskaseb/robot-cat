"""Scale final tangent handles to the real gap, including short approaches.

A12mm minimum handle can exclude a valid R10 connection across a13mm gap.
These are mathematical proposals; all existing curvature/material gates stay.
"""
import math


def pairs(distance):
    assert math.isfinite(distance) and distance>0
    fractions=(distance/3,distance*.4,distance/2)
    values=[max(1,min(65,h)) for h in fractions]
    old=max(12,min(65,distance/3))
    return list(dict.fromkeys([(h,h) for h in values]+[(old,old),(18,38),(38,18),(38,38)]))
