"""Whole measured MAIN bay, hung from the retained rooted printed carrier.

No original Pi/PWM material removed. No ground post through the complete tie.
Bay centre is derived from outer reservation and actual PCB/parent witnesses.
"""
import gzip,hashlib,json,os,time,zipfile
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from receive_feline_rrp_shared_height import load
from receive_feline_main_supported_unit import intrinsic,local_inputs,cylinder,BOARD
from receive_feline_main_ato_gallery import selected
from feline_channelled_foundation import bearing_area
from feline_solid_distance import bbox_lower_bound
from feline_fore_power_pair import SolidQueries
from receive_feline_underplate_return_gallery import minimum_for
from feline_atomic_save import save_json


def main():
    tick=time.monotonic();gf=OUT/'n01-MAIN-ATO-gallery-local.json';g=json.loads(gf.read_text())
    pf=OUT/'n01-MAIN-supported-unit.json';p=json.loads(pf.read_text());actors=load(g);original,_=local_inputs()
    assert len(g['failures'])==2 and all(k.endswith('|SharedPi:Carrier') for k in g['failures'])
    for doc in (p,g):
        for f,h in doc['source_sha256'].items():assert sha(ROOT/f)==h,f
    pi,_,pins=selected(OUT/'n01-shared-Pi-carrier-r3-core-received.json','geometry',lambda n:n=='SharedPi:Carrier')
    pcb=actors[BOARD];parent=pi['SharedPi:Carrier']
    gap,pairs,_=pcb.distToShape(parent);assert abs(gap-.445)<1e-5
    assert all(abs(a.x-b.x)<1e-4 and abs(a.z-b.z)<1e-4 for a,b in pairs)
    rear_plane=min(b.y for a,b in pairs);half=pcb.BoundBox.YLength/2
    interval=[-96+half,rear_plane-1.25-half];assert interval[1]>interval[0]
    centre=sum(interval)/2;dy=centre-pcb.BoundBox.Center.y
    actors.pop('MainSupported:root')
    for s in actors.values():s.translate(A.Vector(0,dy,0))
    upper=load(p)['MainSupported:root'].common(Part.makeBox(100,100,30,A.Vector(-70,-120,91.15)))
    rot=A.Rotation(A.Vector(0,0,1),90);origin=A.Vector(-20,-76,0);target=A.Vector(-28.549,centre,0)
    tf=A.Placement(target-rot.multVec(origin),rot);upper.Placement=tf*upper.Placement
    pi_doc=json.loads((OUT/'n01-shared-Pi-carrier-r3-core-received.json').read_text())
    anchor=A.Vector(*pi_doc['recipe']['Pi_actual_root']['point_mm']);assert parent.isInside(anchor,1e-7,False)
    fork=tf.multVec(A.Vector(-29.271,-72.25,95.25));elbow=A.Vector(-24.5,fork.y,95.25)
    z=min(s.BoundBox.ZMin for n,s in actors.items() if n.endswith(':jacket'))
    lower=A.Vector(-24.5,fork.y,z+8);comb=A.Vector(-24.5,centre-7.5,z+8)
    root=upper
    for a,b,r in ((anchor,fork,1.5),(fork,elbow,1.5),(elbow,lower,1.25),(lower,comb,1.25)):
        root=root.fuse(cylinder(a,b,r)).fuse(Part.makeSphere(r,a)).fuse(Part.makeSphere(r,b))
    root=root.removeSplitter();assert root.isValid() and len(root.Solids)==1
    actors['MainSupported:root']=root;kinds={r['name']:r for r in g['geometry']}
    checks=intrinsic(actors,original,kinds)
    for i in (0,1):
        area=bearing_area(root,actors[f'Ref_Material_MAIN_{i}_lower_washer_0_0'],91.25)
        checks['fork_washer_bearing:'+str(i)]=dict(ok=area>10,area_mm2=area)
    area=bearing_area(root,actors[BOARD],99.25);checks['fork_PCB_bearing']=dict(ok=area>20,area_mm2=area)
    joint=root.common(parent);union=root.fuse(parent).removeSplitter()
    checks['actual_rooted_Pi_print_union']=dict(ok=joint.Volume>1 and union.isValid() and len(union.Solids)==1 and max(union.BoundBox.XLength,union.BoundBox.YLength,union.BoundBox.ZLength)<250,
        positive_common_mm3=joint.Volume,combined_solids=len(union.Solids),combined_bounds_mm=[union.BoundBox.XLength,union.BoundBox.YLength,union.BoundBox.ZLength])
    neighbours=dict(pi);meta={n:dict(kind='proposal_material') for n in pi}
    for file,field,want in [('n01-full-material-scene.json','parts',lambda n:n.startswith('Ref_Material_F_R') and ('_ATO_' in n or '_Housing_' in n)),('n01-shared54-current.json','parts',lambda n:n.startswith('Service:Ref_Material_F_R'))]:
        pp,rr,pins_=selected(OUT/file,field,want);neighbours.update(pp);meta.update(rr);pins.update(pins_)
    query=SolidQueries()
    for n,s in actors.items():
        for m,t in neighbours.items():
            if n=='MainSupported:root' and m=='SharedPi:Carrier':continue
            minimum=minimum_for(n,kinds[n],m,meta[m])
            if bbox_lower_bound(s.BoundBox,t.BoundBox)>=minimum:continue
            d=query.distance(s,t);checks[n+'|'+m]=dict(ok=d>=minimum-1e-6,gap_mm=d,minimum_mm=minimum)
    recipes={}
    for e,r in g['recipes'].items():
        q=dict(r)
        for k in ('source_pad_mm','jacket_start_mm','routing_exit_mm'):q[k]=list(A.Vector(*r[k])+A.Vector(0,dy,0))
        q['source_neck_parts']=[dict(part,**{k:list(A.Vector(*part[k])+A.Vector(0,dy,0)) for k in ('start','mid','end') if k in part}) for part in r['source_neck_parts']]
        recipes[e]=q
    stem=OUT/'n01-MAIN-hung-bay-local';arc=stem.with_suffix('.breps.zip');rows=stem.with_suffix('.pairs.json.gz');geometry=[]
    with zipfile.ZipFile(arc,'w',zipfile.ZIP_DEFLATED) as zz:
        for i,(n,s) in enumerate(actors.items()):
            raw=s.exportBrepToString().encode();entry=str(i)+'.brep';zz.writestr(entry,raw);geometry.append(dict(kinds[n],entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    rows.write_bytes(gzip.compress(json.dumps(checks,separators=(',',':')).encode(),mtime=0))
    pins.update({f.relative_to(ROOT).as_posix():sha(f) for f in (gf,pf,ROOT/g['bundle'],ROOT/p['bundle'],Path(__file__),OUT/'n01-psys-flp-frame-load-paths.json')})
    result=dict(status='MAIN_HUNG_BAY_LOCAL_HOLDS' if any(not v['ok'] for v in checks.values()) else 'MAIN_HUNG_BAY_LOCAL_RECEIVED_WORLD_TOOLS_OPEN',source_sha256=pins,
        geometry=geometry,bundle=arc.relative_to(ROOT).as_posix(),bundle_sha256=sha(arc),pair_rows=rows.relative_to(ROOT).as_posix(),pair_rows_sha256=sha(rows),
        checks=len(checks),failures=[k for k,v in checks.items() if not v['ok']],recipes=recipes,retired=g['retired'],
        bay_centre_Y_interval_mm=interval,bay_chosen_mid_Y_mm=centre,actual_parent_rear_plane_Y_mm=rear_plane,
        current_outer_fit_still_required=True,root_owner='SharedPi:Carrier',original_Pi_PWM_carrier_unchanged=True,
        root_load_path_basis='Exact positive union to retained one-solid Pi carrier; original four-clamp foundation receipt unchanged',
        no_post_through_tie_or_ATO=True,no_purchased_parts_changed=True,N01_complete=False,physical_pass=False,native_changed=False,worker_seconds=round(time.monotonic()-tick,3))
    save_json(stem.with_suffix('.json'),result);print(result['status'],result['worker_seconds'],len(result['failures']),flush=True)
    print(json.dumps({k:v for k,v in checks.items() if not v['ok']},indent=2),flush=True)


if __name__=='__main__':print('WORKER_PID',os.getpid(),flush=True);main()
