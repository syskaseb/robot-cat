"""One coupled four-feeder skeleton, lower/upper tiers instead of one fat bundle.

No final cuts, stock choice, new purchased part, native mount or N04 release.
Both full ends use actual received prefix caps; all four links tested together.
"""
import math,os,time
from pathlib import Path
import numpy as np
import FreeCAD as A
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_output_composed_context import compose
from compose_feline_output_boundaries import current,cap_at
from feline_selected_material_contract import load as profiles
from feline_common_space_context import is_jacket
from receive_feline_underplate_return_gallery import bend,forward
from receive_feline_planning_links import receive
from feline_atomic_save import save_json


def shifted(rows,q,d,dy,R):
    if abs(dy)<1e-8:return q,d
    assert abs(dy)<2*R
    normal=np.array([0,1 if dy>0 else -1,0.]);angle=math.acos(1-abs(dy)/(2*R))
    q,t=bend(rows,q,d,normal,R,angle)
    # Its second arc restores the original tangent, not a kinked polyline.
    n=(d-t*float(d@t));n/=np.linalg.norm(n)
    q,t=bend(rows,q,t,n,R,angle);assert np.linalg.norm(t-d)<1e-6
    return q,t


def construct(start,axis,end,upper,R=25.2,landing=4.5):
    q=np.array(start,float);d=np.array(axis,float);target=np.array(end,float);rows=[]
    if upper:
        vertical=target[2]-q[2]-2*R;assert vertical>=0
        fore=abs(d[1])>.9;out=np.array([1.,0,0]) if fore else d.copy()
        q,d=bend(rows,q,d,[0,0,1],R);q=forward(rows,q,d,vertical);q,d=bend(rows,q,d,out,R)
    assert abs(d[0])>.999 and abs(q[2]-target[2])<1e-6
    elbow=target-np.array([0.,landing,0])
    q,d=shifted(rows,q,d,elbow[1]-R-q[1],R)
    corner=elbow-R*d-np.array([0.,R,0]);advance=float((corner-q)@d)
    assert advance>=0 and np.linalg.norm((corner-q)-advance*d)<1e-5,(q,corner,advance)
    q=forward(rows,q,d,advance);q,d=bend(rows,q,d,[0,1,0],R);q=forward(rows,q,d,landing)
    assert np.linalg.norm(q-target)<1e-5 and np.linalg.norm(d-[0,1,0])<1e-6
    return rows


def main():
    tick=time.monotonic();base,ends,files=current();contract,pf,bf=profiles();lookup={r['id']:r for r in ends}
    planned=[]
    for w in ('W026','W037','W045','W053'):
        a=lookup[w+'/custom/start'];b=lookup[w+'/custom/end'];radius=contract['portions'][w+'/custom']['project_radius_mm'];assert abs(radius-2.1)<1e-6
        station=b['endpoint'].split('.')[0]
        neighbors=[r for r in ends if (r.get('endpoint') or '').split('.')[0]==station and r.get('routing_exit_mm') is not None]
        max_radius=max(contract['portions'][r['portion_id']].get('project_radius_mm') or radius for r in neighbors)
        landing=b['routing_exit_mm'][1]-min(r['routing_exit_mm'][1] for r in neighbors)+radius+max_radius+.3
        rows=construct(a['routing_exit_mm'],a['routing_exit_axis'],b['routing_exit_mm'],w in ('W037','W053'),landing=landing)
        planned.append((w,a,b,radius,rows,landing,[r['id'] for r in neighbors]))
    print('Whole four-feeder math preflight',[(w,round(landing,3),round(sum(r['length_mm'] for r in rows),3)) for w,a,b,radius,rows,landing,neighbors in planned],flush=True)
    context=compose();world,parts,meta,pins,docs=context;links=[]
    for w,a,b,radius,rows,landing,neighbors in planned:
        source='EndCustom:'+w;cap_at(parts[source],a['routing_exit_mm'],a['routing_exit_axis'],radius)
        preferred=b.get('prefix_geometry_owner');matches=[];point=A.Vector(*b['routing_exit_mm'])
        for n in ([preferred] if preferred in parts else list(parts)):
            s=parts[n]
            if not s.Solids or (n!=preferred and not is_jacket(n,meta[n])):continue
            bb=s.BoundBox
            if not (bb.XMin-1e-4<=point.x<=bb.XMax+1e-4 and bb.YMin-1e-4<=point.y<=bb.YMax+1e-4 and bb.ZMin-1e-4<=point.z<=bb.ZMax+1e-4):continue
            try:cap_at(s,b['routing_exit_mm'],b['routing_exit_axis'],radius)
            except AssertionError:continue
            matches.append(n)
        assert len(matches)==1,('Ambiguous current target cap',w,preferred,matches)
        links.append(dict(name='PlanningFeeder:'+w,wire=w,portion=w+'/custom',parts=rows,radius_mm=radius,
            required_project_R_mm=25.2,joins=[source,matches[0]],target_endpoint=b,
            planned_link_length_mm=sum(e['length_mm'] for e in rows),terminal_fan_straight_mm=landing,
            neighboring_fan_ends=neighbors,final_cut_and_stock_not_selected=True))
    sources=(*files,pf,bf,Path(__file__),ROOT/'tools/cad/receive_feline_planning_links.py',ROOT/'tools/cad/receive_feline_underplate_return_gallery.py',ROOT/'tools/cad/feline_selected_material_contract.py')
    result=receive('n01-four-power-feeders',links,context,{p.relative_to(ROOT).as_posix():sha(p) for p in sources})
    result['worker_seconds']=round(time.monotonic()-tick,3);save_json(OUT/'n01-four-power-feeders.json',result)
    print('Whole worker seconds',result['worker_seconds'],flush=True)


if __name__=='__main__':print('WORKER_PID',os.getpid(),flush=True);main()
