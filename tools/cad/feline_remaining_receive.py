"""Receive selected remaining kits in the same pinned world, not all variants.

Actual mates use no-positive-common checks only for their named parents;
all unrelated owners, true contour and current36motion positions remain.
"""
import hashlib
import json
import time
import ast
import subprocess
import sys
from functools import lru_cache
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_remaining_kits import materialise,candidates
from feline_two_lane_receive import world_context
from feline_fore_power_pair import SolidQueries,pair_spacing
from feline_solid_distance import bbox_lower_bound
from receive_feline_global_case_candidates import placement


def key(group,recipe):
    return group+':'+hashlib.sha256(json.dumps(recipe,sort_keys=True).encode()).hexdigest()


@lru_cache(maxsize=1)
def open_bank_terminal():
    source=json.loads((OUT/'n01-bank-W027-open-saddle.json').read_text())
    return source['source_endpoint']['terminal_name']


def terminal_owner(group,recipe):
    return recipe.get('terminal_name') or (open_bank_terminal() if group=='Bank:W027/single/end' else None)


def repair_open_bank_owner():
    """Reopen only false air-gap negatives; never promote them to clear."""
    path=OUT/'n01-remaining27-static.json';result=json.loads(path.read_text())
    _,pins=candidates();own='tools/cad/feline_remaining_receive.py';pins[own]=sha(Path(__file__))
    if result['source_sha256']==pins:return
    assert all(pins[n]==v for n,v in result['source_sha256'].items() if n!=own)
    old=subprocess.run(['git','show','f172a295:'+own],cwd=ROOT,check=True,capture_output=True).stdout
    assert hashlib.sha256(old).hexdigest()==result['source_sha256'][own]
    get=lambda t:next(n for n in ast.walk(ast.parse(t)) if isinstance(n,ast.FunctionDef) and n.name=='receive')
    before=get(old);after=get(Path(__file__).read_text())
    for node in ast.walk(after):
        if isinstance(node,ast.Assign) and ast.unparse(node.value)=="terminal_owner(group, recipe) == other":
            node.value=ast.parse("recipe.get('terminal_name') == other",mode='eval').body
    assert ast.dump(before)==ast.dump(after),'Only named mate owner lookup may change'
    reopened=[];owner=open_bank_terminal()
    for code,r in result['units'].items():
        if r['group']!='Bank:W027/single/end':continue
        failure=r.get('failure')
        if isinstance(failure,str) and failure.endswith('|fixed:'+owner):
            oldpair=r['pairs'].pop(failure)
            r.setdefault('retired_wrong_airgap_receipts',[]).append(dict(pair_key=failure,receipt=oldpair,
                reason='Owned TE entry requires exact positive-common check, not foreign1.25air. Still OPEN.'))
            r.pop('failure');reopened.append(code)
    result.setdefault('named_owner_repairs',[]).append(dict(owner=owner,reopened_only=reopened,
        constructor_geometry_unchanged=True,other_negative_receipts_preserved=True,no_clearance_awarded=True))
    result['source_sha256']=pins
    temp=path.with_suffix('.writing.json');temp.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n');temp.replace(path)
    print('Reopened W027 owned-entry checks',len(reopened),'not accepted',flush=True)


def receive_requests(requests):
    tick=time.monotonic();dest=OUT/'n01-remaining27-static.json'
    _,pins=candidates();pins['tools/cad/feline_remaining_receive.py']=sha(Path(__file__))
    result=dict(status='RUNNING_CHOSEN_REMAINING_KITS',source_sha256=pins,units={},errors=[],N01_complete=False,physical_pass=False)
    if dest.exists():
        result=json.loads(dest.read_text())
        if result['source_sha256']!=pins and '--extend-open-bank' in sys.argv:
            from feline_remaining_kits import prove_additive_extension
            helper='tools/cad/feline_remaining_kits.py';own='tools/cad/feline_remaining_receive.py'
            assert all(pins[n]==v for n,v in result['source_sha256'].items() if n not in (helper,own))
            proof=prove_additive_extension(result['source_sha256'][helper])
            old=subprocess.run(['git','show','65e2b033:'+own],cwd=ROOT,check=True,capture_output=True).stdout
            assert hashlib.sha256(old).hexdigest()==result['source_sha256'][own]
            get=lambda t:next(n for n in ast.walk(ast.parse(t)) if isinstance(n,ast.FunctionDef) and n.name=='receive')
            assert ast.dump(get(old))==ast.dump(get(Path(__file__).read_text()))
            assert all('wire_bend_clock_degrees' not in r['recipe'] for r in result['units'].values())
            result.setdefault('additive_geometry_extensions',[]).append(proof);result['source_sha256']=pins
        else:assert result['source_sha256']==pins
        result.setdefault('prior_worker_seconds',[]).append(result['worker_seconds'])
    def save():
        result['worker_seconds']=round(time.monotonic()-tick,3)
        temp=dest.with_suffix('.writing.json');temp.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n');temp.replace(dest)
    save();world,fixed=world_context();query=SolidQueries()
    if result.get('world_source_sha256'):assert result['world_source_sha256']==world.pins
    result['world_source_sha256']=world.pins
    outer=Part.Shape();outer.read(str(OUT/'n01-six-source-shared-lanes.outer.brep'))
    def receive(group,recipe,rec):
        parts,kinds=materialise(group,recipe);done=rec.setdefault('pairs',{})
        for n,s in parts.items():
            if time.monotonic()-tick>240:raise TimeoutError('4minute requested-kit slice; all actual pairs retained')
            k=n+'|outer'
            if k not in done:
                outside=s.copy().cut(outer);assert outside.isNull() or outside.isValid()
                gap=s.distToShape(outer.Shells[0])[0]
                done[k]=dict(ok=outside.Volume<1e-5 and gap>=3.25-1e-6,outside_mm3=outside.Volume,gap_mm=gap);save()
            if not done[k]['ok']:return k
            for other,t in fixed.items():
                minimum=pair_spacing(group+':'+n,dict(kind=kinds[n]),other,world.meta.get(other,{}))
                own=terminal_owner(group,recipe)==other
                if group.startswith('Anchor:'):
                    clamp=next(p['clamp'] for p in recipe['actual_parts'] if p['name']==n)
                    own=other=='Ref_Material_P0_Side'+('Right' if clamp in (1,3) else 'Left')+'22_0_0'
                if bbox_lower_bound(s.BoundBox,t.BoundBox)>=(0 if own else minimum):
                    if not own:continue
                k=n+'|fixed:'+other
                if k not in done:
                    q=s
                    if other==world.bus['name']:
                        q=s.copy();q.Placement=world.bus['inverse']*q.Placement;t=world.bus['original']
                    if own:
                        overlap=q.copy().common(t.copy());assert overlap.isNull() or overlap.isValid()
                        done[k]=dict(ok=overlap.Volume<1e-7,own_named_mate=True,positive_common_mm3=overlap.Volume,
                                     other_owners_NOT_exempt=True)
                    else:
                        gap=query.distance(q,t);done[k]=dict(ok=gap>=minimum-1e-6,gap_mm=gap,minimum_mm=minimum)
                    save()
                if not done[k]['ok']:return k
            for p in world.motion:
                if bbox_lower_bound(s.BoundBox,A.BoundBox(*p['bounds'][0],*p['bounds'][1]))>=1.25:continue
                k=n+'|motion:'+p['name']+':'+str(p['pose'])
                if k not in done:
                    q=s.copy();q.Placement=placement(p['r'],p['t']).inverse()*q.Placement
                    gap=query.distance(q,world.rest[p['name']]);done[k]=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25);save()
                if not done[k]['ok']:return k
        return None
    try:
        for group,recipe in requests:
            code=key(group,recipe);rec=result['units'].setdefault(code,dict(group=group,recipe=recipe))
            if 'failure' not in rec:
                rec['failure']=receive(group,recipe,rec);save()
                print('Remaining kit',group,'clear' if rec['failure'] is None else rec['failure'],flush=True)
        result['status']='REQUESTED_REMAINING_KITS_RECEIVED_NOT_N01'
    except TimeoutError as exc:result['status']='PARTIAL_REMAINING_KITS';result['slice_note']=str(exc)
    except Exception as exc:result['status']='REMAINING_KIT_ERROR';result['errors'].append(repr(exc))
    save();assert not result['errors'],result['errors'];return result
