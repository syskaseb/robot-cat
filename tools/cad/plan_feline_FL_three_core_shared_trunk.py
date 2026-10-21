"""Three real FL power cores in one received trunk, not coincident graph paths.

Reuse W022 unchanged. Parallel transport gives actual offset circles through
its trunk; branch once before the bank. No guessed SKU/OD, lost9 or new seam.
"""
import math
import numpy as np
import feline_tangent_routes as ft


def transport(parts,offset):
    v=np.asarray(offset,float);out=[]
    for s in parts:
        p=np.asarray(s['start']);q=np.asarray(s['end'])
        if s['kind']=='line':out.append(ft.line(p+v,q+v));continue
        t=np.asarray(s['tangent']);b=np.asarray(s['bend']);n=np.cross(t,b)
        assert abs(float(v@t))<1e-6
        angle=s['angle'];nextv=v*math.cos(angle)+np.cross(n,v)*math.sin(angle)+n*float(n@v)*(1-math.cos(angle))
        shifted=ft.arc(p+v,t,q+nextv)
        assert abs(shifted['radius']-(s['radius']-float(v@b)))<1e-5
        out.append(shifted);v=nextv
    return out,v


def construct(received_middle,rows,profiles):
    byid={r['id']:r for r in rows};base=received_middle['parts']
    # The last two arcs are W022's own bank branch, not shared capacity.
    assert len(base)==15 and base[12]['kind']=='arc'
    assert np.allclose(base[12]['end'],[-8,-22,38])
    assert np.allclose(base[12]['end_tangent'],[0,0,1])
    result={};minimum_trunk_R=ft.min_radius(base[:13])
    assert minimum_trunk_R-2.2>=12.4-1e-6
    for wire,zoffset in (('W020',-2.2),('W022',0.),('W024',2.2)):
        pid=wire+'/body';source=byid[pid+'/start'];target=byid[pid+'/end']
        if wire=='W022':parts=base
        else:
            trunk,v=transport(base[:13],[0,0,zoffset]);p=trunk[-1]['end']
            branch=ft.biarc(p,[0,0,1],target['routing_exit_mm'],-np.asarray(target['routing_exit_axis']))
            parts=trunk+branch
        assert np.allclose(parts[0]['start'],source['routing_exit_mm'],atol=1e-6)
        assert np.allclose(parts[-1]['end'],target['routing_exit_mm'],atol=1e-6)
        R=ft.min_radius(parts);required=profiles[pid]['minimum_project_R_mm']
        result[pid]=dict(parts=parts,minimum_R_mm=R,required_R_mm=required,
            radius_qualified=bool(R>=required-1e-6),length_mm=ft.length(parts),
            radius_mm=profiles[pid]['project_radius_mm'],parallel_transport_offset_mm=[0,0,zoffset],
            common_trunk_segments=13,shared_centreline_recipe='CurrentMiddle:W022',
            branch_after_common_trunk=True,source_and_receiver_not_moved=True,
            full_factory900_NOT_received=True,N01_complete=False)
    return result
