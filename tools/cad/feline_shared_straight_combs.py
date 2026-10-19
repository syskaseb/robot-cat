"""Simple shared first-land combs, not imposed immediate90deg fan-outs.

Purchased mouths stay together. A complete9mm saddle precedes downstream
routing; every wire keeps its documented R, which remains a corridor gate.
Full strap sits in the13.48mm clear interdeck channel; head is at side X,
not stacked vertically into the bankbed. No downstream-route/N01 claim.
"""
import json
import numpy as np
import FreeCAD as A
import Part
from feline_flat_station_templates import build
from receive_feline_global_case_candidates import placement
from feline_underplate_station_templates import box
from plan_feline_layout import OUT


def slots():
    result=[]
    # Bottom channel datum is the midpoint between actual P0 sidebeam38.52
    # and bankbed52, not battery height. Top galleries are a distinct cavity.
    for profile,dims in (('standard',[30.,19.,9.]),('large',[37.,22.,11.])):
        xs=[(i-3.5)*31.25 for i in range(8)] if profile=='standard' else [-85.,-45.,-5.,35.,75.,115.]
        for side in (-1,1):
            for tier,y,z in (('interdeck',66. if profile=='standard' else 75.,45.26),
                             ('overbank',79.,98.)):
                for x in xs:
                    result.append(dict(id=len(result),profile=profile,tier=tier,centre_mm=[x,side*y,z],dimensions_mm=dims,side=side))
    return result


def unit(st,slot):
    centre=np.asarray(slot['centre_mm']);side=slot['side'];rot=np.array([[0.,-1.,0.],[1.,0.,0.],[0.,0.,1.]])
    base=build(dict(st,row_families=['inner','outer']),'outer',1,-side)
    old=np.asarray(base['centre_mm']);d=np.array([0.,-side,0.]);u=np.array([side,0.,0.]);n=np.array([0.,0.,1.])
    dims=np.asarray(slot['dimensions_mm']);parts={'case':box(centre-dims/2,centre+dims/2)};wires=[];starts=[]
    assert abs(parts['case'].Volume-st['source_part_record']['volume_mm3'])<1e-5
    for w in base['wires']:
        q=rot@(np.asarray(w['point_mm'])-old)+centre;r=w['radius'];start=q+d*.25;tip=q+d*12.25
        parts['wire:'+w['endpoint']]=Part.makeCylinder(r,12.25,A.Vector(*q),A.Vector(*d));starts.append(start)
        wires.append(dict(endpoint=w['endpoint'],wire=w['wire'],point_mm=q.tolist(),departure_axis=d.tolist(),
            radius_mm=r,minimum_R_mm=w['R_mm'],grip_start_mm=start.tolist(),grip_length_mm=9,
            straight_tip_mm=tip.tolist(),downstream_R_corridor_NOT_qualified=True))
    origin=np.mean(starts,axis=0);pose=placement(np.column_stack((u,n,d)),origin)
    xx=(np.asarray(starts)-origin)@u;rmax=max(w['radius_mm'] for w in wires)
    xmin=min(x-w['radius_mm']-2 for x,w in zip(xx,wires));xmax=max(x+w['radius_mm']+2 for x,w in zip(xx,wires));nn=rmax+2
    cap=box(np.array([xmin,-nn,0.]),np.array([xmax,nn,9.]),pose)
    for w in wires:cap=cap.cut(Part.makeCylinder(w['radius_mm']+.15,11,A.Vector(*(np.asarray(w['grip_start_mm'])-d)),A.Vector(*d)))
    assert cap.isValid() and len(cap.Solids)==1;parts['split_common_comb']=cap
    strips=[([xmin-1.2,-nn-1.2,3.25],[xmin,nn+1.2,5.75]),([xmax,-nn-1.2,3.25],[xmax+1.2,nn+1.2,5.75]),
            ([xmin,-nn-1.2,3.25],[xmax,-nn,5.75]),([xmin,nn,3.25],[xmax,nn+1.2,5.75])]
    parts['band_budget']=Part.makeCompound([box(np.asarray(a),np.asarray(b),pose) for a,b in strips])
    hc=np.array([xmax+1.2+3,0.,4.5]);parts['head_budget']=box(hc-3,hc+3,pose)
    assert all(s.isValid() and s.Solids for s in parts.values())
    return dict(parts=parts,wires=wires,nylon_loop_upper_bound_mm=2*(xmax-xmin+2*nn)+10,
        interdeck_actual_required_height_mm=2*(rmax+2+1.2),full9_first_land=True,
        full_loadroot_service_and_R_corridors_open=True)


if __name__=='__main__':
    stations=json.loads((OUT/'n01-flat-station-architecture.json').read_text())['stations']
    for ref in ('D_FL','FL_P','P_FRONT','G1'):
        st=next(s for s in stations if s['ref']==ref);profile='large' if st['flat_dimensions_pitch_departure_thickness_mm'][2]>10 else 'standard'
        m=unit(st,next(s for s in slots() if s['profile']==profile))
        for w in m['wires']:
            for n in ('case','split_common_comb','band_budget','head_budget'):
                assert m['parts']['wire:'+w['endpoint']].common(m['parts'][n]).Volume<1e-5,(ref,n)
        assert abs(m['parts']['head_budget'].Volume-216)<1e-6
        print(ref,'full9straight saddle/strap/head own-fit',m['interdeck_actual_required_height_mm'],flush=True)
