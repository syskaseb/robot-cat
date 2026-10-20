"""Whole four inboard S fans BEFORE any new support/foot detail.

Keep all original feet/P0. Full grip can use the first10mm arc, not another
invented straight9. Both real factory sides and complete moved joint kits
remain in the shared obstacle scene. A wire-only preflight never awards N01.
"""
import copy,gzip,hashlib,json,time,zipfile
from pathlib import Path
import FreeCAD as A
import Part
import numpy as np
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_main_hung_context import compose
from receive_feline_rrp_shared_height import load
from receive_feline_factory_saddle_revision import owner
from receive_feline_factory_saddle_plan import CASES
from plan_feline_remaining_factory_inputs import offset,forward
from receive_feline_underplate_return_gallery import bend,minimum_for
from plan_feline_n01_shared import pipe
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from plan_feline_pi_root_access import profile_gap
from plan_feline_usb_service_bight import outer_margin
from receive_feline_global_case_candidates import placement
from feline_atomic_save import save_json


def main():
    tick=time.monotonic();world,parts,meta,pins,docs=compose()
    sf=OUT/'n01-factory-saddles-received.json';r=json.loads(sf.read_text());base=load(r);original={**parts,**base}
    fixed={n:s for n,s in parts.items() if n not in r['retired']};fixed.update(base);fm={**meta,**r['actor_meta']};moved=[]
    profiles=copy.deepcopy(r['recipes']);delta=-10.
    for n in list(fixed):
        w=owner(n)
        if w in ('W044','W052') and not n.startswith('Factory:'):
            fixed[n]=fixed[n].copy();fixed[n].translate(A.Vector(delta,0,0));moved.append(n)
    for w in ('W044','W052'):
        p=profiles[w]['parts'];p[-1]['end'][0]+=delta;p[-1]['length_mm']-=delta
        fixed['Factory:'+w]=pipe(p,2.1)
        assert profiles[w]['guide_mm']-delta+21<100
    for w in profiles:
        for n in list(fixed):
            if n.startswith(('Seat:'+w+':custom','TieLoop:Seat:'+w+':custom','TieHead:Seat:'+w+':custom')):fixed.pop(n);fm.pop(n,None)
    # Actual shared lower corridor: old foot stem inner absY31; output
    # frame webs formerly extended to24.5. Keep their INBOARD load face,
    # trim only the outboard face to23.5, retaining a3x3mm web, not2mm.
    web_proofs={}
    for i in range(1,5):
        n='RootWebReserve'+str(i);before=fixed[n];b=before.BoundBox
        if b.Center.y>0:cut=Part.makeBox(400,80,200,A.Vector(-200,23.5,-100))
        else:cut=Part.makeBox(400,80,200,A.Vector(-200,-103.5,-100))
        fixed[n]=before.cut(cut);assert fixed[n].isValid() and len(fixed[n].Solids)==1
        assert fixed[n].cut(before).Volume<1e-5 and abs(fixed[n].BoundBox.YLength-3)<1e-5
        for parent in ('RootPlateReserve'+str(i),'LowerBay:'+('ForePanel' if i<3 else 'RearPanel')):
            c=fixed[n].common(fixed[parent]);assert c.isValid() and c.Volume>1e-5,(n,parent)
        web_proofs[n]=dict(printed_web_min_section_mm=[3,3],inboard_face_preserved=True,
            removed_only_outboard_material_mm3=before.cut(fixed[n]).Volume,physical_load_and_native_gate_OPEN=True)
    actors={};recipes={};retired=[]
    for w in profiles:
        n='CustomPrefix:'+w;s=fixed.pop(n);fm.pop(n,None);retired.append(n)
        d=np.array([1.,0,0]) if w in ('W041','W042') else np.array([-1.,0,0]);side=1 if w in ('W041','W044') else -1
        point=np.array([s.BoundBox.XMin if d[0]>0 else s.BoundBox.XMax,side*33.25,profiles[w]['parts'][-1]['end'][2]])
        path=[];q=forward(path,point,d,.25)
        q=offset(path,q,d,[0,side*27-point[1],0]);q,t=bend(path,q,d,[0,0,1],25.2);forward(path,q,t,45.26-q[2])
        assert path[1]['length_mm']>=10
        actors[n]=pipe(path,2.1);recipes[n]=dict(parts=path,point_mm=point.tolist(),axis=d.tolist(),radius_mm=2.1,R_mm=25.2,
            routing_exit_mm=path[-1]['end'],routing_exit_axis=[0,0,1],first_full_grip_arclength_mm=[.25,10.25],
            early_grip_root_band_head_and_native_not_received=True,final_cut_and_stock_NOT_qualified=True)
    checks={};query=SolidQueries();dest=OUT/'n01-MTA-inboard-fans-preflight.json';pf=dest.with_suffix('.pairs.json.gz')
    archive=dest.with_suffix('.breps.zip');geometry=[]
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for i,(n,s) in enumerate(actors.items()):
            raw=s.exportBrepToString().encode();entry=str(i)+'.brep';z.writestr(entry,raw);geometry.append(dict(name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest(),kind='actual_wire'))
    result=dict(status='RUNNING_MTA_INBOARD_FOUR_FAN_STATIC',recipes=recipes,geometry=geometry,
        bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),printed_web_proofs=web_proofs,
        completed_static=[],proposed_rear_whole_kit_shift_X_mm=delta,original_feet_and_P0_unchanged=True,
        source_factory_and_bought_parts_unchanged=True,N01_complete=False,native_changed=False,physical_pass=False,
        whole_grips_roots_factory_nominal_tools_stock_and_motion_OPEN=True,
        source_sha256={**pins,**{p.relative_to(ROOT).as_posix():sha(p) for p in (sf,ROOT/r['bundle'],Path(__file__))}})
    def save():
        pf.write_bytes(gzip.compress(json.dumps(checks,separators=(',',':')).encode(),mtime=0))
        result.update(checks=len(checks),failures=[k for k,v in checks.items() if not v['ok']],pair_rows=pf.relative_to(ROOT).as_posix(),pair_rows_sha256=sha(pf),worker_seconds=round(time.monotonic()-tick,3));save_json(dest,result)
    save()
    for n,s in actors.items():
        checks[n+'|outer']=outer_margin(s,docs['outer']);w=owner(n)
        for m,t in {**fixed,**actors}.items():
            if n==m:continue
            key='|'.join(sorted((n,m))) if m in actors else n+'|'+m
            if key in checks:continue
            minimum=minimum_for(n,dict(kind='actual_wire'),m,dict(kind='actual_wire') if m in actors else fm[m])
            if bbox_lower_bound(s.BoundBox,t.BoundBox)>=minimum:continue
            a=s
            if m=='Ref_Material_'+w+'_Joint_0_0':
                c=s.common(t);assert c.isNull() or c.isValid();p=recipes[n]['point_mm'];d=A.Vector(*recipes[n]['axis'])
                a=s.cut(Part.makeCylinder(3,2.5,A.Vector(*p),d));assert c.Volume<1e-5
            if m==world.bus['name']:a=a.copy();a.Placement=docs['inverse']*a.Placement;t=world.bus['original']
            row=dict(ok=(gap:=query.distance(a,t))>=minimum-1e-6,gap_mm=gap,minimum_mm=minimum) if t.Solids else profile_gap(a,t,fm[m].get('nominal_profile_radius_mm') or fm[m].get('radius_mm'),minimum)
            # Only the already received local mouth shoe may retain its
            # nominal clearance; compare the full old/new conductor material.
            if m=='CaseBase:'+w+'_Joint':
                oldwire=original[n].copy()
                if w in ('W044','W052'):oldwire.translate(A.Vector(delta,0,0))
                before=oldwire.common(t);now=s.common(t);assert (now.isNull() or now.isValid()) and (before.isNull() or before.isValid())
                baseline=query.distance(oldwire,t);row.update(ok=now.cut(before).Volume<1e-5 and gap>=min(baseline,minimum)-1e-6,old_own_shoe_gap_mm=baseline)
            if not row['ok'] and t.Solids:
                _,pts,_=a.distToShape(t);row['witness_mm']=[[list(x),list(y)] for x,y in pts[:1]]
            checks[key]=row
        result['completed_static'].append(n);save();print(n,'holds',len(result['failures']),flush=True)
    result['status']='MTA_INBOARD_FOUR_FAN_STATIC_HOLDS' if result['failures'] else 'MTA_INBOARD_FOUR_FAN_STATIC_RECEIVED_FULL_GRIPS_ROOTS_MOTION_OPEN'
    save();print(result['status'],len(checks),len(result['failures']),result['worker_seconds'],flush=True)


if __name__=='__main__':main()
