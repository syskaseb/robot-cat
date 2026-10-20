"""All four custom departures and four frame-bearing feet in one shared plan.

Keep purchased parts, ground pads and M2 bearing material. Replace only
middle printed stems and their floor edge channels. No native manufacturing,
physical load rating, final wire cuts or whole-N01 acceptance is claimed.
"""
import copy,gzip,hashlib,json,time,zipfile
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_main_hung_context import compose
from receive_feline_rrp_shared_height import load
from receive_feline_factory_saddle_revision import owner
from receive_feline_factory_saddle_plan import box
from receive_feline_underplate_return_gallery import bend,forward,minimum_for
from plan_feline_n01_shared import pipe
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from plan_feline_pi_root_access import profile_gap
from plan_feline_usb_service_bight import outer_margin
from receive_feline_global_case_candidates import placement
from feline_atomic_save import save_json
import numpy as np


def foot(old,x,side):
    upper=old.common(box([x-10,19 if side>0 else -29.85,-5],[x+10,29.85 if side>0 else -19,2]))
    lower=old.common(box([x-10,-55,-80],[x+10,55,-47]))
    y0,y1=sorted((side*27.75,side*29.75))
    web=box([x-9,y0,-50],[x+9,y1,-3])
    y0,y1=sorted((side*27.75,side*36))
    tongue=box([x-5,y0,-51],[x+5,y1,-47])
    new=lower.multiFuse([upper,web,tongue]);assert new.isValid() and len(new.Solids)==1
    ground=old.common(box([x-10,-55,-80],[x+10,55,-51]));assert ground.cut(new).Volume<1e-5
    holes=(-80,-70) if x<0 else (112,122)
    for hx in holes:
        bearing=Part.makeCylinder(4,10,A.Vector(hx,side*22.5,-10))
        assert old.common(bearing).cut(new).Volume<1e-5
    b0,b=old.BoundBox,new.BoundBox
    assert max(abs(getattr(b0,k)-getattr(b,k)) for k in ('XMin','XMax','YMin','YMax','ZMin','ZMax'))<1e-5
    return new,dict(original_ground_region_below_minus51_preserved=True,original_M2_R4_bearing_material_preserved=True,
        pad_tip_Z_mm=b.ZMin,post_absY_mm=[27.75,29.75],post_thickness_mm=2.,bottom_bridge_Z_mm=[-51,-47],
        upper_bridge_outer_absY_mm=29.85,physical_strength_creep_print_and_load_test_OPEN=True,
        original_spatial_extents_preserved_NOT_contact_proof=True)


def main():
    tick=time.monotonic();world,parts,meta,pins,docs=compose()
    sf=OUT/'n01-factory-bay-layout-received.json';prior=json.loads(sf.read_text());old=load(prior)
    for p,h in prior['source_sha256'].items():assert sha(ROOT/p)==h,p
    actors={n:s.copy() for n,s in old.items()};ameta=copy.deepcopy(prior['actor_meta']);recipes=copy.deepcopy(prior['recipes']);retired=set(prior['retired']);changed=set();proofs={};extras={}
    effective={n:s for n,s in parts.items() if n not in retired};effective.update(actors)
    for i,(x,side) in enumerate(((-75.5,-1),(-75.5,1),(117.5,-1),(117.5,1)),1):
        n='BellyFoot'+str(i);actors[n],proofs[n]=foot(parts[n],x,side);ameta[n]=dict(kind='frame_reservation');retired.add(n);changed.add(n)
        extras[n]=actors[n].cut(parts[n]);assert extras[n].isValid() and extras[n].Solids
    for w in recipes:
        n='CustomPrefix:'+w;oldshape=actors[n];d=np.array([1.,0,0]) if w in ('W041','W042') else np.array([-1.,0,0])
        # Saved producer owns the existing9.25mm land; do not add another9.
        source=oldshape.BoundBox.XMin if d[0]>0 else oldshape.BoundBox.XMax
        y=recipes[w]['parts'][-1]['end'][1];z=recipes[w]['parts'][-1]['end'][2]
        p=np.array([source,y,z]);route=[];q=forward(route,p,d,9.25);extra=[]
        q,t=bend(extra,q,d,[0,0,1],25.2);forward(extra,q,t,45.26-q[2]);route+=extra
        actors[n]=pipe(route,2.1);assert oldshape.cut(actors[n]).Volume<1e-5
        extras[n]=pipe(extra,2.1);changed.add(n)
        recipes[w]['custom_plan']=dict(parts=route,radius_mm=2.1,R_mm=25.2,existing_grip9_preserved=True,
            routing_exit_mm=route[-1]['end'],routing_exit_axis=[0,0,1],full_middle_route_and_stock_NOT_qualified=True)
    for parent in ('LowerBay:ForePanel','LowerBay:RearPanel'):
        floor=actors[parent];oldfloor=floor.copy();cx=-75.5 if 'Fore' in parent else 117.5
        for side in (-1,1):
            yy=sorted((side*26.5,side*31))
            floor=floor.cut(box([cx-10.25,yy[0],-52],[cx+10.25,yy[1],-3]))
        if 'Fore' in parent:
            for w,side in (('W044',1),('W052',-1)):
                case=actors['Ref_Material_'+w+'_Joint_0_0'].BoundBox;seat=actors['Seat:'+w+':custom'].BoundBox;yy=sorted((side*26,side*28))
                floor=floor.cut(box([seat.XMin-1.25,yy[0],-42],[case.XMax+1.25,yy[1],-37]))
        assert floor.isValid() and len(floor.Solids)==1 and floor.cut(oldfloor).Volume<1e-5
        actors[parent]=floor;changed.add(parent)
    roots={}
    for n,root in prior['positive_roots'].items():
        c=actors[n].common(actors[root['parent']]);assert c.isValid() and c.Volume>1e-5,(n,'Changed floor lost root')
        roots[n]=dict(parent=root['parent'],actual_common_mm3=c.Volume)
    fixed={n:s for n,s in parts.items() if n not in retired};query=SolidQueries()
    dest=OUT/'n01-MTA-feet-common-plan.json';pf=dest.with_suffix('.pairs.json.gz');archive=dest.with_suffix('.breps.zip')
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (sf,ROOT/prior['bundle'],Path(__file__))})
    checks={};result=dict(status='RUNNING_MTA_FOUR_FEET_SHARED_PLAN',source_sha256=pins,recipes=recipes,retired=sorted(retired),actor_meta=ameta,
        changed=sorted(changed),foot_interface_proofs=proofs,positive_roots=roots,completed_static=[],completed_motion=[],
        N01_complete=False,native_changed=False,physical_pass=False,all_physical_load_print_insulation_and_stock_gates_OPEN=True)
    if dest.exists():
        result=json.loads(dest.read_text());assert result['source_sha256']==pins
        assert sha(pf)==result['pair_rows_sha256'];checks=json.loads(gzip.decompress(pf.read_bytes()));actors=load(result)
    else:
        geometry=[]
        with zipfile.ZipFile(ROOT/prior['bundle']) as src,zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
            for i,(n,s) in enumerate(actors.items()):
                row=next((r for r in prior['geometry'] if r['name']==n),None);raw=src.read(row['entry']) if n not in changed else s.exportBrepToString().encode()
                entry=str(i)+'.brep';z.writestr(entry,raw);geometry.append(dict(ameta[n],name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
        result.update(geometry=geometry,bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive))
    def save():
        pf.write_bytes(gzip.compress(json.dumps(checks,separators=(',',':')).encode(),mtime=0))
        result.update(checks=len(checks),failures=[k for k,v in checks.items() if not v['ok']],pair_rows=pf.relative_to(ROOT).as_posix(),pair_rows_sha256=sha(pf),worker_seconds=round(time.monotonic()-tick,3));save_json(dest,result)
    save()
    # The shared gate includes ALL current parts. Test only newly changed
    # interfaces; retained floor pairs are monotone material deletions.
    for n in sorted(changed):
        if n in result['completed_static']:continue
        s=actors[n]
        checks[n+'|outer']=dict(ok=True,unchanged_ground_support_spatial_extents=True) if n.startswith('BellyFoot') else outer_margin(s,docs['outer'])
        for m,t in {**fixed,**actors}.items():
            if n==m:continue
            key='|'.join(sorted((n,m))) if m in actors else n+'|'+m
            if key in checks:continue
            mr=ameta[m] if m in actors else meta[m];minimum=minimum_for(n,ameta[n],m,mr);tested=s
            # Existing root/body bearing surfaces were not moved or grown.
            # Any new foot material still keeps full foreign1.25mm.
            if n.startswith('BellyFoot') and m in fixed:tested=extras[n]
            if n.startswith('LowerBay:') and m in fixed:
                checks[key]=dict(ok=True,no_new_material_in_floor_and_fixed_mate_unchanged=True);continue
            same=owner(n) is not None and owner(n)==owner(m)
            if n.startswith('CustomPrefix:') and same:
                tested=extras[n]
                if m.startswith('Seat:'+owner(n)+':custom'):minimum=.15
            # Named features of the same existing printed floor unit. Its
            # individual root volumes are checked above, not waved through.
            if n.startswith('LowerBay:') and m in roots and roots[m]['parent']==n:
                checks[key]=dict(ok=True,actual_root_common_mm3=roots[m]['actual_common_mm3']);continue
            if bbox_lower_bound(tested.BoundBox,t.BoundBox)>=minimum:continue
            a=tested;bb=t
            if m==world.bus['name']:a=a.copy();a.Placement=docs['inverse']*a.Placement;bb=world.bus['original']
            row=dict(ok=(gap:=query.distance(a,bb))>=minimum-1e-6,gap_mm=gap,minimum_mm=minimum) if bb.Solids else profile_gap(a,bb,mr.get('nominal_profile_radius_mm') or mr.get('radius_mm'),minimum)
            if not row['ok'] and bb.Solids:
                _,pts,_=a.distToShape(bb);row['witness_mm']=[[list(x),list(y)] for x,y in pts[:1]]
            checks[key]=row
        result['completed_static'].append(n);save();print(n,'holds',len(result['failures']),flush=True)
        if time.monotonic()-tick>220:result['status']='PARTIAL_MTA_FOUR_FEET_SAVED';save();return
    if not result['failures']:
        for n in sorted(changed):
            if n in result['completed_motion']:continue
            s=actors[n] if n.startswith('BellyFoot') else extras.get(n,actors[n])
            for pose in world.motion:
                if bbox_lower_bound(s.BoundBox,A.BoundBox(*pose['bounds'][0],*pose['bounds'][1]))>=1.25:continue
                key=n+'|motion:'+pose['name']+':'+str(pose['pose'])
                if key in checks:continue
                a=s.copy();a.Placement=placement(pose['r'],pose['t']).inverse()*a.Placement
                gap=query.distance(a,world.rest[pose['name']]);checks[key]=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25)
            result['completed_motion'].append(n);save()
            if time.monotonic()-tick>220:result['status']='PARTIAL_MTA_FOUR_FEET_SAVED';save();return
    result['status']='MTA_FOUR_FEET_SHARED_HOLDS' if result['failures'] else 'MTA_FULL_CUSTOM_FOUR_FEET_STATIC36_RECEIVED_ACCESS_OPEN'
    result['motion_is_sampled_not_continuous']=True;save();print(result['status'],result['checks'],len(result['failures']),result['worker_seconds'],flush=True)


if __name__=='__main__':main()
