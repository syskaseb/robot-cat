"""One complete RR_P source topology: four early S curves and shared grip.

No case pose/SKU changes, final cuts, native production or N01 claim. The
first full nine-mm jacket grip lies along an arc, not a mandatory straight.
Existing source point/axis and all other current actors are retained.
"""
import gzip, hashlib, json, math, os, time, zipfile
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT, sha
from plan_feline_layout import OUT
from feline_adjudicated_boundaries import current
from feline_selected_material_contract import load as profiles
from feline_output_composed_context import compose
from feline_received_own_channels import own_channel
from feline_atomic_save import save_json
from receive_feline_underplate_return_gallery import bend, forward, minimum_for
from plan_feline_n01_shared import pipe
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from plan_feline_pi_root_access import profile_gap
from plan_feline_usb_service_bight import outer_margin
from receive_feline_global_case_candidates import placement


def source_path(q, trim=0):
    q=np.array(q,float); d=np.array([0.,-1,0]); R=25.2; angle=math.radians(35)
    rows=[]; q=forward(rows,q,d,.25)
    if trim:
        assert trim > .25 and trim < R*angle+.25
        rows=[]; t=(trim-.25)/R
        q=q+R*math.sin(t)*d+R*(1-math.cos(t))*np.array([0.,0,-1])
        heading=math.cos(t)*d+math.sin(t)*np.array([0.,0,-1])
        normal=-math.sin(t)*d+math.cos(t)*np.array([0.,0,-1])
        q,heading=bend(rows,q,heading,normal,R,angle-t)
    else:q,heading=bend(rows,q,d,[0,0,-1],R,angle)
    normal=d-heading*float(d@heading); normal/=np.linalg.norm(normal)
    q,heading=bend(rows,q,heading,normal,R,angle)
    assert np.linalg.norm(heading-d)<1e-6
    return rows,q,heading


def sector(origin, r0, r1, angle, width):
    c=A.Vector(*origin)
    def at(r,t): return c+A.Vector(0,-r*math.sin(t),r*math.cos(t))
    es=[Part.Arc(at(r1,0),at(r1,angle/2),at(r1,angle)).toShape(),
        Part.makeLine(at(r1,angle),at(r0,angle)),
        Part.Arc(at(r0,angle),at(r0,angle/2),at(r0,0)).toShape(),
        Part.makeLine(at(r0,0),at(r1,0))]
    s=Part.Face(Part.Wire(es)).extrude(A.Vector(width,0,0))
    assert s.isValid() and len(s.Solids)==1
    return s


def construct(ends, contract):
    rows=[e for e in ends if e['group']=='WAGO:RR_P']; assert len(rows)==4
    rows.sort(key=lambda e:e['point_mm'][0])
    shapes={}; kinds={}; recipes={}; trimmed={}; channels=[]
    R=25.2; first=.25; grip_length=9.; theta=grip_length/R
    for e in rows:
        assert np.linalg.norm(np.array(e['departure_axis'])-[0,-1,0])<1e-6
        profile=contract['portions'][e['portion_id']]; radius=profile['project_radius_mm']
        assert profile['minimum_project_R_mm']<=R+1e-6
        path,q,d=source_path(e['point_mm']); name='EarlyRR:'+e['id']
        shapes[name]=pipe(path,radius); kinds[name]={'kind':'wire'}
        trimmed[name]=pipe(source_path(e['point_mm'],2.5)[0],radius)
        channels.append(pipe(path,radius+.15))
        recipes[name]=dict(end_id=e['id'],point_mm=e['point_mm'],departure_axis=e['departure_axis'],
            parts=path,project_radius_mm=radius,R_mm=R,full_grip_arc_length_mm=9,
            first_mm=first,grip_angle_radians=theta,routing_exit_mm=q.tolist(),routing_exit_axis=d.tolist(),
            project_prefix_length_mm=sum(p['length_mm'] for p in path),
            total_wire_or_final_cut_NOT_selected=True)
    a=np.array(rows[0]['point_mm']); assert all(abs(e['point_mm'][1]-a[1])<1e-6 and abs(e['point_mm'][2]-a[2])<1e-6 for e in rows)
    xmin=min(e['point_mm'][0]-contract['portions'][e['portion_id']]['project_radius_mm']-2.15 for e in rows)
    xmax=max(e['point_mm'][0]+contract['portions'][e['portion_id']]['project_radius_mm']+2.15 for e in rows)
    nn=max(r['project_radius_mm'] for r in recipes.values())+2.15
    centre=[xmin,a[1]-first,a[2]-R]; width=xmax-xmin
    for suffix,r0,r1 in [('outer',R+.125,R+nn),('inner',R-nn,R-.125)]:
        s=sector(centre,r0,r1,theta,width)
        for hole in channels:s=s.cut(hole)
        s=s.removeSplitter(); assert s.isValid() and len(s.Solids)==1,suffix
        shapes['EarlyRR:comb:'+suffix]=s; kinds['EarlyRR:comb:'+suffix]={'kind':'proposal_material'}
    mid=theta/2; radial=np.array([0.,-math.sin(mid),math.cos(mid)])
    tangent=np.array([0.,-math.cos(mid),-math.sin(mid)])
    origin=np.array([0.,a[1]-first-R*math.sin(mid),a[2]-R+R*math.cos(mid)])
    tf=placement(np.column_stack((tangent,[1,0,0],radial)),origin)
    def box(lo,hi):
        s=Part.makeBox(*(np.array(hi)-lo),A.Vector(*lo)); s.Placement=tf*s.Placement; return s
    band=box([-1.25,xmin-1.4,-nn-1.4],[1.25,xmax+1.4,nn+1.4]).cut(
        box([-1.35,xmin-.2,-nn-.2],[1.35,xmax+.2,nn+.2]))
    shapes['EarlyRR:band_budget']=band
    shapes['EarlyRR:head_budget']=box([-2.5,xmax+1.4,-2.65],[2.5,xmax+5.7,2.65])
    kinds['EarlyRR:band_budget']={'kind':'project_stock_reservation','material_role':'selected_T18I_nylon_budget'}
    kinds['EarlyRR:head_budget']=dict(kinds['EarlyRR:band_budget'])
    assert abs(shapes['EarlyRR:head_budget'].Volume-5*4.3*5.3)<1e-5
    return shapes,kinds,recipes,trimmed


def main():
    tick=time.monotonic(); _,ends,files=current(); contract,pf,bf=profiles()
    actors,kinds,recipes,trimmed=construct(ends,contract)
    world,fixed,meta,pins,docs=compose()
    retired=[n for n in fixed if n.startswith('Station:RR_P:') and n!='Station:RR_P:case']
    assert len(retired)==7,retired
    for n in retired:fixed.pop(n);meta.pop(n)
    sources=(*files,pf,bf,Path(__file__),ROOT/'tools/cad/feline_received_own_channels.py')
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in sources})
    dest=OUT/'n01-early-curved-RRP.json'; archive=dest.with_suffix('.breps.zip'); pairfile=dest.with_suffix('.pairs.json.gz')
    assert not dest.exists(),'Receive the existing result; do not repeat this topology'
    records=[]
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for i,(n,s) in enumerate(actors.items()):
            raw=s.exportBrepToString().encode(); entry=str(i)+'.brep';z.writestr(entry,raw)
            records.append(dict(name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest(),**kinds[n]))
    checks={}; result=dict(status='RUNNING_WHOLE_EARLY_RRP_RECEIPT',source_sha256=pins,geometry=records,
        bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),recipes=recipes,retired=retired,
        completed_static=[],completed_motion=[],N01_complete=False,physical_pass=False,native_changed=False,
        case_pose_and_bought_parts_unchanged=True,independent_four_jacket_channels=True,
        nominal_grip_fit_and_individual_pull_phase2=True,root_assembly_AND_full_middle_still_OPEN=True)
    def save():
        pairfile.write_bytes(gzip.compress(json.dumps(checks,separators=(',',':')).encode(),mtime=0))
        result.update(pair_rows=pairfile.relative_to(ROOT).as_posix(),pair_rows_sha256=sha(pairfile),checks=len(checks),
            failures=[k for k,v in checks.items() if not v['ok']],worker_seconds=round(time.monotonic()-tick,3))
        save_json(dest,result)
    save(); query=SolidQueries(); boxes={n:s.BoundBox for n,s in {**fixed,**actors}.items()}
    oldends={e['id']:e for e in ends}
    for n,s in actors.items():
        checks[n+'|outer']=outer_margin(s,docs['outer'])
        for m,t in {**fixed,**actors}.items():
            if n==m:continue
            key='|'.join(sorted((n,m))) if m in actors else n+'|'+m
            if key in checks:continue
            mr=kinds[m] if m in actors else meta[m]
            minimum=minimum_for(n,kinds[n],m,mr)
            if n in recipes and m not in actors:minimum=min(minimum,own_channel(oldends[recipes[n]['end_id']],m))
            if m=='Station:RR_P:case' and n.startswith('EarlyRR:comb:'): minimum=.25
            if m in actors:
                if n in recipes and m.startswith('EarlyRR:comb:') or m in recipes and n.startswith('EarlyRR:comb:'):minimum=.15
                if n.startswith('EarlyRR:comb:') and m.startswith('EarlyRR:comb:'):minimum=.25
                if n.startswith('EarlyRR:comb:') and 'budget' in m or m.startswith('EarlyRR:comb:') and 'budget' in n:minimum=.15
                if {'EarlyRR:band_budget','EarlyRR:head_budget'}=={n,m}:minimum=0
            if bbox_lower_bound(boxes[n],boxes[m])>=minimum and minimum>0:continue
            tested=trimmed[n] if m=='Station:RR_P:case' and n in trimmed else s
            if m==world.bus['name']:
                tested=tested.copy();tested.Placement=docs['inverse']*tested.Placement;t=world.bus['original']
            if t.Solids:
                gap=query.distance(tested,t); check=dict(ok=gap>=minimum-1e-6,gap_mm=gap,minimum_mm=minimum)
                if m=='Station:RR_P:case' and n in recipes:
                    common=s.common(t);assert common.isNull() or common.isValid()
                    check.update(ok=check['ok'] and common.Volume<1e-5,source_port_only_first2p5_trim=True,whole_wire_case_overlap_mm3=common.Volume)
            else:
                radius=mr.get('nominal_profile_radius_mm') or mr.get('radius_mm')
                check=profile_gap(tested,t,radius,minimum) if radius else dict(ok=False,unresolved_curve_budget=m)
            checks[key]=check
        result['completed_static'].append(n);save();print('EarlyRR',n,'holds',len(result['failures']),flush=True)
    if not result['failures']:
        for n,s in actors.items():
            for pose in world.motion:
                if bbox_lower_bound(boxes[n],A.BoundBox(*pose['bounds'][0],*pose['bounds'][1]))>=1.25:continue
                a=s.copy();a.Placement=placement(pose['r'],pose['t']).inverse()*a.Placement
                gap=query.distance(a,world.rest[pose['name']])
                checks[n+'|motion:'+pose['name']+':'+str(pose['pose'])]=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25)
            result['completed_motion'].append(n);save()
    result['status']='WHOLE_EARLY_RRP_HOLD_WITNESSES' if result['failures'] else 'WHOLE_EARLY_RRP_STATIC36_RECEIVED_ROOT_AND_ASSEMBLY_OPEN'
    save(); print(result['status'],result['checks'],len(result['failures']),result['worker_seconds'],flush=True)


if __name__=='__main__':print('WORKER_PID',os.getpid(),flush=True);main()
