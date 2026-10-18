"""Batch the SAME224 complete source profiles, no changed numerical geometry."""
import math
import numpy as np


def evaluate(q,d,u,v,interpolators,profile_points,gate=lambda:None,debug=None):
    records=[];chunks=[];radii=[];starts=[];total=0
    for first in (9,18,27,36,45,54,63):
        gate()
        for angle in np.linspace(0,2*math.pi,32,endpoint=False):
            b=u*math.cos(angle)+v*math.sin(angle)
            parts,end,tip=profile_points(q,d,b,first)
            points=np.vstack([parts[name] for name in ('factory','sleeve','custom')])
            radius=np.concatenate([np.full(len(parts[name]),r) for name,r in (('factory',2),('sleeve',2.4),('custom',1.55))])
            starts.append(total);total+=len(points);chunks.append(points);radii.append(radius)
            records.append((first,b,end,tip))
    points=np.concatenate(chunks);radius=np.concatenate(radii);minimum=np.full(total,np.inf)
    layers={}
    for category,interpolator in interpolators.items():
        gate();values=interpolator(points)
        assert np.all(np.isfinite(values)),'Unknown/nonfinite source field is not a pass'
        allowance=3.25 if category=='outer' else .2 if category=='material' else 3.35 if category=='curve_hold' else 1.25
        layer=values-radius-allowance;layers[category]=layer
        minimum=np.minimum(minimum,layer)
    margins=np.minimum.reduceat(minimum,np.array(starts))
    if debug is not None:
        rejected=np.flatnonzero(margins < -1e-5)
        if len(rejected):
            index=int(rejected[np.argmax(margins[rejected])]);start=starts[index];stop=starts[index+1] if index+1<len(starts) else total
            category=min(layers,key=lambda k:float(layers[k][start:stop].min()))
            point=start+int(np.argmin(layers[category][start:stop]));first,b,end,tip=records[index]
            debug.update(best_rejected=dict(first_mm=first,bend_unit=b.tolist(),minimum_margin_mm=float(margins[index]),
                limiting_layer=category,point_mm=points[point].tolist(),profile_radius_mm=float(radius[point]),
                note='Source-field witness ONLY, not physical contact or infeasibility'))
    return [(float(margin),*record) for margin,record in zip(margins,records) if margin>=-1e-5],len(records)
