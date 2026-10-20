"""One shared rear retention topology, preserving all four received wires.

Planning solids only. Native production/split tolerances remain N03. Stop at
the first actual outline/rest witness; whole static/motion/tools stay separate.
"""
import copy,hashlib,json,time,zipfile
from pathlib import Path
import FreeCAD as A
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_main_hung_context import compose
from receive_feline_rrp_shared_height import load
from feline_mta_rear_keeper import build
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from plan_feline_usb_service_bight import outer_margin
from feline_atomic_save import save_json


def main():
    tick=time.monotonic();world,parts,meta,pins,docs=compose()
    sf=OUT/'n01-MTA-body-head-clock.json';r=json.loads(sf.read_text());actors=load(r)
    observed=sf.with_name(sf.stem+'-scene.json');prior=json.loads(observed.read_text())
    assert prior['failures']==['CaseTie:RL|Ref_Material_F0_CP2_0_0']
    for record in (r,prior):
        for p,h in record['source_sha256'].items():assert sha(ROOT/p)==h,p
    fm={**meta,**{p['name']:p for p in r['geometry']}};changed=set();plans={};roots={};newfeatures={}
    contracts=copy.deepcopy(r['named_interface_pairs']);groups=copy.deepcopy(r['print_groups']);query=SolidQueries()
    for code,wire in (('RL','W041'),('RR','W042')):
        t=r['body_ties'][code];case=parts[t['case']]
        cap=actors['CaseCap:'+wire+'_Joint'];bolts=[actors['CapScrew:'+wire+'_Joint:'+str(i)].BoundBox.Center.x for i in (0,1)]
        side=1 if code=='RL' else -1;new,plan=build(case.optimalBoundingBox(False,False),cap.BoundBox,bolts,side)
        features=plan.pop('full_fork_features');newfeatures[code]=features
        names=dict(base='MTARetain:'+code+':base',fork='MTARetain:'+code+':fork',band=t['band'],head=t['head'])
        plans[code]=dict(plan,names=names,case=t['case'],parent=t['parent'],old_transverse_body_tie_replaced=True,
            selected_bought_quantity_NOT_changed=True,unpowered_cut_own_band_then_lift_fork_mm=5)
        for kind,s in new.items():
            n=names[kind];actors[n]=s;changed.add(n)
            fm[n]=dict(name=n,kind='proposal_material' if kind in ('base','fork') else 'tie_reservation',
                material_role='PETG_planning_retention' if kind in ('base','fork') else 'selected_T18I_nylon_budget')
        groups[t['parent']].append(names['base'])
        c=new['base'].common(actors[t['parent']]);assert c.isValid() and c.Volume>1e-5
        roots[code]=dict(parent=t['parent'],actual_positive_overlap_mm3=c.Volume)
        own=[('base','fork',0),('base','band',.2),('fork','band',.2),('band','head',0)]
        for a,b,minimum in own:
            c=new[a].common(new[b]);assert c.isNull() or c.isValid();gap=query.distance(new[a],new[b])
            assert c.Volume<1e-5 and gap>=minimum-1e-6,(code,a,b,gap,c.Volume)
            contracts['|'.join(sorted((names[a],names[b])))]=dict(ok=True,gap_mm=gap,minimum_mm=minimum,
                whole_common_mm3=c.Volume,exact_own_keeper_interface=[names[a],names[b]],foreign_margin_NOT_changed_mm=1.25)
        for a in ('base','fork'):
            c=new[a].common(case);assert c.isNull() or c.isValid();gap=query.distance(new[a],case)
            assert c.Volume<1e-5 and gap>=.2-1e-6,(code,a,'case',gap,c.Volume)
            contracts['|'.join(sorted((names[a],t['case'])))]=dict(ok=True,gap_mm=gap,minimum_mm=.2,
                whole_common_mm3=c.Volume,exact_own_insulating_case_keeper=[names[a],t['case']],foreign_margin_NOT_changed_mm=1.25)
    # Old nylon-to-case/floor contracts are not valid for the new neck ties.
    for key in list(contracts):
        if any(n in key.split('|') for n in changed if n.startswith('CaseTie:')) and not contracts[key].get('exact_own_keeper_interface'):
            contracts.pop(key)
    floor='LowerBay:RearPanel';unit=actors[floor].multiFuse([actors[n] if n in actors else parts[n] for n in groups[floor] if n!=floor])
    assert unit.isValid() and len(unit.Solids)==1
    b=unit.BoundBox;assert max(b.XLength,b.YLength,b.ZLength)<250
    dest=OUT/'n01-MTA-rear-keepers.json';assert not dest.exists();archive=dest.with_suffix('.breps.zip')
    before={p['name']:p for p in r['geometry']};geometry=[]
    with zipfile.ZipFile(ROOT/r['bundle']) as src,zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as target:
        for i,(n,s) in enumerate(actors.items()):
            raw=s.exportBrepToString().encode() if n in changed else src.read(before[n]['entry'])
            if n not in changed:assert hashlib.sha256(raw).hexdigest()==before[n]['sha256']
            entry=str(i)+'.brep';target.writestr(entry,raw);geometry.append(dict(fm[n],name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (sf,ROOT/r['bundle'],observed,ROOT/prior['pair_rows'],
        OUT/'n01-MTA-rear-wrap-domain.json',ROOT/'tools/cad/feline_mta_rear_keeper.py',Path(__file__))})
    inherited=[n for n in r['completed_rest'] if n not in changed]
    result=dict(r,status='RUNNING_REAR_KEEPER_REST',source_sha256={**r['source_sha256'],**pins},geometry=geometry,
        bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),changed_actors=sorted(changed),
        print_groups=groups,body_ties={c:t for c,t in r['body_ties'].items() if c not in plans},rear_keepers=plans,
        new_root_proofs=roots,rear_print_union_solids=1,rear_print_envelope_mm=[b.XLength,b.YLength,b.ZLength],
        named_interface_pairs=contracts,byte_identical_actors_from_prior=len(before)-4,
        reuse_scene=dict(path=observed.relative_to(ROOT).as_posix(),sha256=sha(observed)),
        completed_rest=inherited,completed_static=[],completed_motion=[],rest_checks={},outline_checks={},failures=[],
        N01_complete=False,native_changed=False,physical_pass=False)
    for n in sorted(changed):
        s=actors[n];result['outline_checks'][n]=outer_margin(s,docs['outer'])
        if not result['outline_checks'][n]['ok']:result['failures'].append(n+'|outer');break
        for name,material in world.rest.items():
            if bbox_lower_bound(s.BoundBox,material.BoundBox)>=1.25:continue
            gap=query.distance(s,material);key=n+'|rest:'+name
            result['rest_checks'][key]=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25)
            if gap<1.25-1e-6:result['failures'].append(key);break
        if result['failures']:break
        result['completed_rest'].append(n)
    result.update(status='REAR_KEEPER_OUTLINE_OR_REST_HOLD' if result['failures'] else 'COMPLETE_MTA_KIT_REST_RECEIVED_STATIC_MOTION_ACCESS_OPEN',
        worker_seconds=round(time.monotonic()-tick,3),checks=len(result['rest_checks']))
    save_json(dest,result);print(result['status'],len(actors),'rest',len(result['completed_rest']),result['failures'],result['worker_seconds'],flush=True)


if __name__=='__main__':main()
