"""Receive whole-bank opposed-Z exits, only the chosen complete units.

Unchanged before-grips may reuse a COMPLETE source-pinned old-unit receipt.
Other units receive all parts. No old failed wire is inherited as a new pass.
"""
import json
import ast
import hashlib
import subprocess
import time
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_bank_exit_lanes import materialise
from feline_two_lane_receive import world_context
from feline_fore_power_pair import SolidQueries,pair_spacing
from feline_solid_distance import bbox_lower_bound
from receive_feline_global_case_candidates import placement
from feline_remaining_receive import terminal_owner,key
from feline_atomic_save import save_json


def receive_requests(requests,factory=None,destination='n01-bank-lanes-static.json',factory_sources=(),stock_geometry_unchanged=True):
    tick=time.monotonic();dest=OUT/destination;factory=factory or materialise;world,fixed=world_context();query=SolidQueries()
    files=[Path(__file__),Path(__file__).with_name('feline_bank_exit_lanes.py'),Path(__file__).with_name('feline_remaining_kits.py')]
    files.extend(Path(p) for p in factory_sources)
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in files}
    result=dict(status='RUNNING_BANK_OPPOSED_LANES',source_sha256=pins,world_source_sha256=world.pins,units={},errors=[],N01_complete=False,physical_pass=False,
        stock_geometry_unchanged=stock_geometry_unchanged,geometry_factory=factory.__module__+'.'+factory.__name__)
    if dest.exists():
        result=json.loads(dest.read_text());assert result['world_source_sha256']==world.pins
        assert result.get('stock_geometry_unchanged',True)==stock_geometry_unchanged
        if result['source_sha256']!=pins:
            own=Path(__file__).relative_to(ROOT).as_posix();helper='tools/cad/feline_bank_exit_lanes.py'
            assert set(pins)==set(result['source_sha256'])
            assert all(pins[n]==v for n,v in result['source_sha256'].items() if n not in (own,helper))
            get=lambda t,name:next(n for n in ast.walk(ast.parse(t)) if isinstance(n,ast.FunctionDef) and n.name==name)
            previous={}
            for name in (own,helper):
                versions=[subprocess.run(['git','show',c+':'+name],cwd=ROOT,check=True,capture_output=True).stdout for c in ('48659c05','928307e5','541dda10')]
                previous[name]=next(t for t in versions if hashlib.sha256(t).hexdigest()==result['source_sha256'][name])
            for name in ('candidates','materialise','under_key_candidates','under_key_materialise'):
                if any(isinstance(n,ast.FunctionDef) and n.name==name for n in ast.walk(ast.parse(previous[helper]))):
                    assert ast.dump(get(previous[helper],name))==ast.dump(get((ROOT/helper).read_text(),name)),name
            class DefaultFactory(ast.NodeTransformer):
                def visit_Name(self,n):return ast.copy_location(ast.Name(id='factory',ctx=n.ctx),n) if n.id=='materialise' else n
            class DefaultStock(ast.NodeTransformer):
                def visit_IfExp(self,n):return self.visit(n.body) if isinstance(n.test,ast.Name) and n.test.id=='stock_geometry_unchanged' else self.generic_visit(n)
            assert ast.dump(DefaultFactory().visit(get(previous[own],'receive')))==ast.dump(DefaultStock().visit(get(Path(__file__).read_text(),'receive')))
            result.setdefault('additive_receipt_repairs',[]).append(dict(old_source_sha256=result['source_sha256'],reason='All existing constructors and receive kernel AST unchanged; optional factory API only'))
            result['source_sha256']=pins
    def save():result['worker_seconds']=round(time.monotonic()-tick,3);save_json(dest,result)
    old=json.loads((OUT/'n01-remaining27-static.json').read_text());assert old['world_source_sha256']==world.pins
    assert old['source_sha256']['tools/cad/feline_remaining_kits.py']==pins['tools/cad/feline_remaining_kits.py']
    outer=Part.Shape();outer.read(str(OUT/'n01-six-source-shared-lanes.outer.brep'))
    def receive(group,recipe,record):
        parts,kinds=factory(group,recipe);done=record.setdefault('pairs',{});base=recipe['base_recipe']
        prior=old['units'].get(key(group,base),{}) if stock_geometry_unchanged else {};complete_old='failure' in prior and prior['failure'] is None
        if complete_old:record['unchanged_before_stock_reused_from']=key(group,base)
        for n,s in parts.items():
            if kinds[n]!='proposal_wire' and complete_old:continue
            if time.monotonic()-tick>240:raise TimeoutError('4minute bank-lane receipt slice, all completed pairs retained')
            if kinds[n]=='proposal_wire':
                for other,t in parts.items():
                    if kinds[other]=='proposal_wire':continue
                    k=n+'|own:'+other
                    if k not in done:
                        common=s.copy().common(t.copy());assert common.isNull() or common.isValid()
                        done[k]=dict(ok=common.Volume<1e-7,positive_common_mm3=common.Volume);save()
                    if not done[k]['ok']:return k
            k=n+'|outer'
            if k not in done:
                outside=s.copy().cut(outer);assert outside.isNull() or outside.isValid()
                gap=s.distToShape(outer.Shells[0])[0];done[k]=dict(ok=outside.Volume<1e-5 and gap>=3.25-1e-6,outside_mm3=outside.Volume,gap_mm=gap);save()
            if not done[k]['ok']:return k
            for other,t in fixed.items():
                minimum=pair_spacing(group+':'+n,dict(kind=kinds[n]),other,world.meta.get(other,{}));own=terminal_owner(group,base)==other
                if not own and bbox_lower_bound(s.BoundBox,t.BoundBox)>=minimum:continue
                k=n+'|fixed:'+other
                if k not in done:
                    q=s
                    if other==world.bus['name']:q=s.copy();q.Placement=world.bus['inverse']*q.Placement;t=world.bus['original']
                    if own:
                        common=q.copy().common(t.copy());assert common.isNull() or common.isValid()
                        done[k]=dict(ok=common.Volume<1e-7,own_named_mate=True,positive_common_mm3=common.Volume)
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
    save()
    try:
        for group,recipe in requests:
            code=key(group,recipe);record=result['units'].setdefault(code,dict(group=group,recipe=recipe))
            if 'failure' not in record:
                record['failure']=receive(group,recipe,record);save()
                print('Bank lane',group,'clear' if record['failure'] is None else record['failure'],flush=True)
        result['status']='REQUESTED_BANK_LANES_RECEIVED_NOT_N01'
    except TimeoutError as exc:result['status']='PARTIAL_BANK_LANES';result['slice_note']=str(exc)
    except Exception as exc:result['status']='BANK_LANE_ERROR';result['errors'].append(repr(exc))
    save();assert not result['errors'],result['errors'];return result
