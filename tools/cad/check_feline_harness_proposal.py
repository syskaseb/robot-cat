"""Actual-solid rejection check for the new harness-aware W069 proposal.

Partial scene coverage can reject, never receive, a complete route.
"""
import json,time,zipfile,hashlib
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from receive_feline_W024_shared_body import solid
from receive_feline_jpwm_whole_pose import solid_profile_target
from feline_solid_distance import bbox_lower_bound
from feline_fore_power_pair import SolidQueries
from feline_atomic_save import save_json


def classify_W069_spacing(result,metadata,source_records):
    """Classify already computed distances; never repeat unchanged CAD pairs."""
    from feline_fore_power_pair import pair_spacing
    source=OUT/'n01-RL9-common-arc-rooted-space.json';rl=json.loads(source.read_text())
    records={r['name']:r for r in rl['geometry']}
    own={'RLArc:W069/body/start','Station:RL_G:wire:RL_G.1'};checks={}
    for n,row in result['checks'].items():
        typed=dict(metadata.get(n,{}))
        if n in rl['plan']['recipes']:
            assert source_records[n][2]==records[n]['sha256']
            typed.update(kind='wire',wire=rl['plan']['recipes'][n]['wire'])
        required=0. if n in own else pair_spacing('CurrentMiddle:W069',dict(kind='wire',wire='W069'),n,typed)
        ok=row['gap_mm']>=required-1e-6
        if n in own:ok=ok and row['gap_mm']<1e-6 and row.get('common_mm3',1)<1e-5
        checks[n]=dict(row,minimum_mm=required,ok=ok)
    packet=dict(status='W069_RECOVERED_SUBSET_MARGINS_POSITIVE' if all(r['ok'] for r in checks.values()) and not result['errors'] else 'W069_RECOVERED_SUBSET_MARGINS_HOLD',
        checks=checks,unrecovered=result['unrecovered'],
        source_sha256={source.relative_to(ROOT).as_posix():sha(source)},
        whole_scene_received=False,N01_complete=False,physical_pass=False)
    save_json(OUT/'W009-W069-harness-corridor/W069-subset-spacing.json',packet)
    print(packet['status'],[n for n,r in checks.items() if not r['ok']],flush=True)
    return packet


def save_recovered_context(scene,metadata,expected,source_records):
    """Persist existing evidence once; this is deliberately an incomplete scene."""
    folder=OUT/'W009-W069-harness-corridor';dest=folder/'recovered-context.json'
    archive=folder/'recovered-context.breps.zip'
    assert not dest.exists() and not archive.exists()
    rows=[]
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for n,s in scene.items():
            raw=s.exportBrepToString().encode();entry=str(len(rows))+'.brep';z.writestr(entry,raw)
            rows.append(dict(name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest(),
                             expected_scene_hash=expected.get(n),metadata=metadata.get(n,{}),
                             recovered_source=source_records.get(n)))
    result=dict(status='PARTIAL_HASH_RECOVERED_SCENE_NOT_WHOLE_RECEIPT',geometry=rows,
        bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),
        unrecovered=sorted(set(expected)-set(scene)),N01_complete=False,physical_pass=False)
    save_json(dest,result);print('SAVED_PARTIAL_CONTEXT',len(rows),len(result['unrecovered']),flush=True)
    return result


def check(scene,metadata,expected,boundaries,wire='W069',recipe=None,destination=None):
    tick=time.monotonic()
    folder=OUT/'W009-W069-harness-corridor'
    source=folder/('pair-preflight.json' if wire=='W069' else 'W009-saved-portals.json')
    dest=folder/(destination or wire+'-actual-subset.json')
    assert not dest.exists(),'Receive existing check instead of repeating'
    if recipe is None:
        plan=json.loads(source.read_text());recipe=plan['paths'][wire+'/body']
        assert recipe['status']=='SELF_SEPARATION_PROPOSAL_POSITIVE'
    for side,part,key in [('start',recipe['parts'][0],'start'),('end',recipe['parts'][-1],'end')]:
        row=next(e for e in boundaries if e['id']==wire+'/body/'+side)
        assert (A.Vector(*part[key])-A.Vector(*row['routing_exit_mm'])).Length<1e-6
    actor=solid(recipe['parts'],recipe['radius_mm']);query=SolidQueries()
    checks={};errors={}
    for name,shape in scene.items():
        reserve=metadata.get(name,{}).get('nominal_profile_radius_mm',0) if not shape.Solids else 0
        if bbox_lower_bound(actor.BoundBox,shape.BoundBox)>=1.25+reserve+1e-6:continue
        try:
            other=solid_profile_target(shape,metadata.get(name,{}))
            gap=query.distance(actor,other);row=dict(gap_mm=gap)
            if gap<1e-6:
                a=Part.Shape();a.importBrepFromString(actor.exportBrepToString())
                b=Part.Shape();b.importBrepFromString(other.exportBrepToString())
                row['common_mm3']=a.common(b).Volume
                row['hard_intersection']=row['common_mm3']>1e-5
            checks[name]=row
        except Exception as error:errors[name]=str(error)
    failures=[n for n,r in checks.items() if r.get('hard_intersection')]
    result=dict(status='ACTUAL_INTERSECTION_REJECTED' if failures else 'SUBSET_CLEAR_NOT_RECEIVED',
        checks=checks,failures=failures,errors=errors,
        current_actors_checked=len(scene),unrecovered=sorted(set(expected)-set(scene)),
        source_sha256={source.relative_to(ROOT).as_posix():sha(source)},
        whole_scene_received=False,N01_complete=False,physical_pass=False,
        worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,result)
    print(result['status'],failures,'queries',len(checks),'errors',errors,result['worker_seconds'],flush=True)
    return result,actor
