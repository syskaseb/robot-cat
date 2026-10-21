"""Reject conflicting saved portal routes before expensive CAD work."""
import json
import numpy as np
from scipy.spatial.distance import cdist
from plan_feline_layout import OUT
from feline_atomic_save import save_json
import feline_tangent_routes as ft


def sample(recipe):
    points=[];along=[];travel=0.
    for part in recipe['parts']:
        pp=list(ft.samples(part,.5));points.extend(pp)
        along.extend(np.linspace(travel,travel+part['length'],len(pp)));travel+=part['length']
    return np.array(points),np.array(along)


def run():
    folder=OUT/'W009-W069-harness-corridor';dest=folder/'portal-pair-preflight.json'
    assert not dest.exists()
    proposals=json.loads((folder/'W009-saved-portals.json').read_text())['proposals']
    other=json.loads((folder/'pair-preflight.json').read_text())['paths']['W069/body']
    q,_=sample(other);rows=[]
    for recipe in proposals:
        p,s=sample(recipe);r=recipe['radius_mm'];d=cdist(p,p)
        d[np.abs(s[:,None]-s[None,:])<=8*max(r,1)]=np.inf
        own=float(d.min()-.5-2*r);mutual=cdist(p,q)
        ij=np.unravel_index(mutual.argmin(),mutual.shape)
        pair=float(mutual[ij]-.5-r-other['radius_mm'])
        rows.append(dict(end_heading=recipe['end_heading'],self_lower_bound_mm=own,
                         pair_lower_bound_mm=pair,self_positive=own>=.2,pair_positive=pair>=.2,
                         closest_sample_points=[p[ij[0]].tolist(),q[ij[1]].tolist()]))
    result=dict(status='SAVED_PORTAL_PAIR_PLANNING_GATE',candidates=rows,
                actual_geometry_and_whole_scene_OPEN=True,N01_complete=False,physical_pass=False)
    save_json(dest,result);print(rows,flush=True);return result

if __name__=='__main__':run()
