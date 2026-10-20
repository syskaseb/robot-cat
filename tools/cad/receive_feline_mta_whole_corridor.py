"""One complete MTA corridor kit, with ALL rest legs before static checks.

No separate wire-only promotion. Four first S/grips, roots, floor tie slots,
whole rear joints and two output heads share one scene. Stop on first cause.
Source-identity and named mate policies are explicit, not bbox contact waivers.
"""
import copy,gzip,hashlib,json,time,zipfile
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_main_hung_context import compose
from receive_feline_rrp_shared_height import load
from receive_feline_factory_saddle_revision import owner
from receive_feline_factory_saddle_plan import WIRES,CASES,box
from receive_feline_underplate_return_gallery import forward,minimum_for
from plan_feline_n01_shared import pipe
from feline_mta_curved_grips import construct
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from receive_feline_global_case_candidates import placement
from plan_feline_usb_service_bight import outer_margin
from plan_feline_pi_root_access import profile_gap
from feline_atomic_save import save_json


def own(n):
    return n.split(':')[1] if n.startswith('ArcGrip:') else owner(n)


def build():
    world,parts,meta,pins,docs=compose()
    sf=OUT/'n01-factory-saddles-received.json';base=json.loads(sf.read_text());kit=load(base)
    rf=OUT/'n01-MTA-four-fans-received.json';prior=json.loads(rf.read_text());fans=load(prior)
    for record in (base,prior):
        for p,h in record['source_sha256'].items():assert sha(ROOT/p)==h,p
    allparts={n:s for n,s in parts.items() if n not in base['retired']};allparts.update(kit)
    fm={**meta,**base['actor_meta']};retired=set(base['retired']);changed=set(kit)
    recipes=copy.deepcopy(prior['recipes']);roots={};groups={};datums={};factory=copy.deepcopy(base['recipes'])
    for n in list(allparts):
        w=owner(n)
        if w in WIRES[2:] and not n.startswith('Factory:'):
            allparts[n]=allparts[n].copy();allparts[n].translate(A.Vector(-10,0,0));changed.add(n)
        if w and n.startswith(('Seat:'+w+':custom','TieLoop:Seat:'+w+':custom','TieHead:Seat:'+w+':custom')):
            allparts.pop(n);fm.pop(n,None);changed.discard(n);retired.add(n)
    for w in WIRES[2:]:
        row=factory[w];row['parts'][-1]['end'][0]-=10;row['parts'][-1]['length_mm']+=10
        row['guide_mm']+=10;row['project_factory100_margin_mm']-=10
        assert row['project_factory100_margin_mm']>0
        allparts['Factory:'+w]=pipe(row['parts'],2.1)
    # Choose outside-Hip+outside-AUX portal from actual source shapes. Bounds
    # are a conservative FREE-SPACE choice, never an overlap/contact result.
    aux=parts['Ref_Material_F_AUX_candidate_case_0_0'].BoundBox
    for n,r in recipes.items():
        w=owner(n);d=np.asarray(r['axis']);positive=d[0]>0
        code=('FL' if w=='W041' else 'FR') if positive else ('RL' if w=='W044' else 'RR')
        hip_names={p['name'] for p in world.motion if p['code']==code and p['stage']=='Hip'}
        assert hip_names
        posed_bounds=[p['bounds'] for p in world.motion if p['name'] in hip_names]
        target=(max(aux.XMax,max(b[1][0] for b in posed_bounds))+3.35+.4) if positive else min(b[0][0] for b in posed_bounds)-3.35-.4
        oldx=r['routing_exit_mm'][0];delta=(target-oldx)/d[0];assert delta>0
        rows=copy.deepcopy(r['parts'][:3]);forward(rows,np.asarray(rows[-1]['end']),d,delta)
        shift=delta*d
        for raw in r['parts'][3:]:
            piece=copy.deepcopy(raw)
            for k in ('start','mid','end'):
                if k in piece:piece[k]=(np.asarray(piece[k])+shift).tolist()
            rows.append(piece)
        r.update(parts=rows,routing_exit_mm=rows[-1]['end'],portal_X_mm=target,first_S_and_grip_recipe_unchanged=True)
        datums[w]=dict(portal_X_mm=target,lower_extension_mm=delta,actual_hip_members=sorted(hip_names),
            reserve_wire_radius_mm=2.1,foreign_margin_mm=1.25,additional_design_reserve_mm=.4)
        allparts[n]=pipe(rows,2.1);fm[n]=dict(kind='actual_wire');changed.add(n)
        grip,proof=construct(r);parent=base['recipes'][w]['root']['parent']
        roots[w]=dict(proof,parent=parent)
        for k,s in grip.items():
            name='ArcGrip:'+w+':'+k;allparts[name]=s;changed.add(name)
            fm[name]=dict(kind='proposal_material') if k=='pad' else dict(kind='project_stock_reservation',material_role='selected_T18I_nylon_budget')
    for n,s in fans.items():
        if n.startswith('EndGrip:'):allparts[n]=s;changed.add(n);fm[n]=dict(kind='project_stock_reservation',material_role='selected_T18I_nylon_budget')
    outputs=json.loads((OUT/'n01-rooted-end-bays-caps.json').read_text())
    for parent in ('LowerBay:ForePanel','LowerBay:RearPanel'):
        floor=allparts[parent].copy()
        for w,p in roots.items():
            if p['parent']!=parent:continue
            pad=allparts['ArcGrip:'+w+':pad'];b=pad.BoundBox
            if parent.endswith('ForePanel'):
                lo,hi=p['actual_root_bounds_mm']
                floor=floor.fuse(box([lo[0]-.3,lo[1]-.3,-44.3],[-49.25,hi[1]+.3,-42]))
            for k in ('band','head'):
                b=allparts['ArcGrip:'+w+':'+k].BoundBox
                floor=floor.cut(box([b.XMin-.2,b.YMin-.2,-44.5],[b.XMax+.2,b.YMax+.2,-41.8]))
        assert floor.isValid() and len(floor.Solids)==1,(parent,floor.isValid(),len(floor.Solids))
        allparts[parent]=floor;changed.add(parent);fm[parent]=meta[parent]
        original=next(g['members'] for g in outputs['revision']['planned_print_unions'] if g['panel']==parent)
        members=list(original)
        if parent.endswith('RearPanel'):members+=['StructureReserve:U1CarrierRoot1']
        for w,p in roots.items():
            if p['parent']!=parent:continue
            members+=['CaseBase:'+w+'_Joint','InputGrip:'+w+':pad','ArcGrip:'+w+':pad']
        unit=floor.multiFuse([allparts[n] for n in members if n!=parent])
        assert unit.isValid() and len(unit.Solids)==1,(parent,'Disconnected complete print')
        b=unit.BoundBox;assert max(b.XLength,b.YLength,b.ZLength)<250
        groups[parent]=members
        for w,p in roots.items():
            if p['parent']==parent:
                c=allparts['ArcGrip:'+w+':pad'].common(floor);assert c.isValid() and c.Volume>1e-5
                p.update(parent_actual_overlap_mm3=c.Volume,root_parent_and_full_scene_and_pull_test_OPEN=True)
    actors={n:allparts[n] for n in changed};fixed={n:s for n,s in allparts.items() if n not in changed}
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (sf,rf,ROOT/base['bundle'],ROOT/prior['bundle'],
        OUT/'n01-rooted-end-bays-caps.json',Path(__file__),ROOT/'tools/cad/feline_mta_curved_grips.py')})
    return world,parts,actors,fixed,fm,pins,docs,recipes,factory,roots,groups,retired,datums


def main():
    tick=time.monotonic();dest=OUT/'n01-MTA-whole-corridor.json';pf=dest.with_suffix('.pairs.json.gz')
    world,old,actors,fixed,meta,pins,docs,recipes,factory,roots,groups,retired,datums=build()
    result=dict(status='RUNNING_COMPLETE_MTA_KIT_REST_LEGS_FIRST',source_sha256=pins,recipes=recipes,factory_recipes=factory,
        positive_roots=roots,print_groups=groups,portal_datums=datums,retired=sorted(retired),
        completed_rest=[],completed_static=[],completed_motion=[],N01_complete=False,native_changed=False,physical_pass=False)
    assert not dest.exists(),'Receive saved complete kit; never duplicate'
    archive=dest.with_suffix('.breps.zip');geometry=[]
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for i,(n,s) in enumerate(actors.items()):
            raw=s.exportBrepToString().encode();entry=str(i)+'.brep';z.writestr(entry,raw)
            geometry.append(dict(meta[n],name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    result.update(geometry=geometry,bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive))
    checks={};query=SolidQueries()
    def save(status=None):
        if status:result['status']=status
        pf.write_bytes(gzip.compress(json.dumps(checks,separators=(',',':')).encode(),mtime=0))
        result.update(checks=len(checks),failures=[k for k,v in checks.items() if not v['ok']],worker_seconds=round(time.monotonic()-tick,3),
            pair_rows=pf.relative_to(ROOT).as_posix(),pair_rows_sha256=sha(pf));save_json(dest,result)
    def check(n,s,m,t,minimum=1.25):
        if bbox_lower_bound(s.BoundBox,t.BoundBox)>=minimum:return True
        gap=query.distance(s,t);key=n+'|'+m;row=dict(ok=gap>=minimum-1e-6,gap_mm=gap,minimum_mm=minimum)
        if not row['ok']:
            _,pts,_=s.distToShape(t);row['witness_mm']=[[list(a),list(b)] for a,b in pts[:1]]
        checks[key]=row;return row['ok']
    save()
    # All current rest parts, including moving hips, precede static-only scene.
    for n,s in actors.items():
        for m,t in world.rest.items():
            if not check(n,s,'rest:'+m,t):save('COMPLETE_MTA_KIT_REST_LEG_HOLD');return
        result['completed_rest'].append(n);save()
    print('All complete MTA actors clear all rest legs',flush=True)
    # Rest success is not the entire36-pose result; never promote on this gate.
    save('COMPLETE_MTA_KIT_REST_RECEIVED_STATIC_MOTION_ACCESS_OPEN')
    print(result['status'],len(actors),result['worker_seconds'],flush=True)


if __name__=='__main__':main()
