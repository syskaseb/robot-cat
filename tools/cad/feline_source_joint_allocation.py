"""One actual six-source fan assignment; remaining47 are NOT yet qualified."""
import hashlib
import json
import time
import zipfile
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_fore_power_pair import SolidQueries,pair_spacing
from feline_solid_distance import bbox_lower_bound
from plan_feline_central_pi_wedge import packed


def main():
    tick=time.monotonic();src=OUT/'n01-six-source-shared-lanes.json'
    doc=json.loads(src.read_text());assert len(doc['complete_ports'])==6 and all(doc['domains'].values()) and not doc['errors']
    archive=ROOT/doc['bundle'];assert sha(archive)==doc['bundle_sha256']
    dest=OUT/'n01-source-joint-allocation.json';assert not dest.exists()
    corepath=OUT/'n01-six-source-current-core.json';core,current,currentrows=packed(corepath)
    assert core['all_current_blockers']['status']=='ALL_CURRENT_POWER_BLOCKERS_RECEIVED_NOT_N01'
    assert not core['all_current_blockers']['failures'] and not core['all_current_blockers']['errors']
    assert core['source_fan_domains_sha256']==sha(src)
    q=SolidQueries();shapes={};meta={};domains=doc['domains'];cache={};queries=[];visited=0
    with zipfile.ZipFile(archive) as z:
        for record in doc['parts']:
            raw=z.read(record['entry']);assert hashlib.sha256(raw).hexdigest()==record['sha256']
            s=Part.Shape();s.importBrepFromString(raw.decode());assert s.isValid() and s.Solids
            shapes[record['name']]=s
            meta[record['name']]={'kind':'proposal_wire' if record['kind']=='wire' else 'project_stock_reservation' if record['kind'] in ('band_budget','head_budget') else 'proposal_material'}
    result=dict(status='RUNNING_SIX_SOURCE_MUTUAL',N01_complete=False,physical_pass=False,selected=False,
        source_sha256={src.relative_to(ROOT).as_posix():sha(src),doc['bundle']:doc['bundle_sha256'],
            corepath.relative_to(ROOT).as_posix():sha(corepath),core['bundle']:core['bundle_sha256'],
            Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},pairs=queries,errors=[],joint_assignment=None,
        current121_core_actual_receipt=dict(pairs=len(core['all_current_blockers']['pairs']),failures=0,errors=0),
        affected_core_true_outer=[],fan_against_added_frame=[],
        open=['Other47joint','All246ends/4MTA/factorycorridors','Roots/tools/assembly/remainingouter'])
    def save():
        result['worker_seconds']=round(time.monotonic()-tick,3)
        result['visited_nodes']=visited
        dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    def pair(a,i,b,j):
        key=(a,i,b,j) if a<b else (b,j,a,i)
        if key in cache:return cache[key]
        for ar in domains[a][i]['parts']:
            for br in domains[b][j]['parts']:
                n,o=ar['name'],br['name'];s,t=shapes[n],shapes[o]
                minimum=pair_spacing(n,meta[n],o,meta[o]);lower=bbox_lower_bound(s.BoundBox,t.BoundBox)
                if lower>=minimum:continue
                gap=q.distance(s,t);positive=None
                if gap<1e-8:
                    common=s.common(t);assert common.isNull() or common.isValid();positive=common.Volume
                queries.append(dict(part=n,other=o,gap_mm=gap,minimum_mm=minimum,positive_common_mm3=positive))
                save()
                if gap<minimum-1e-6:cache[key]=False;return False
        cache[key]=True;return True
    def solve(chosen,remaining):
        nonlocal visited
        visited+=1
        if time.monotonic()-tick>120:raise TimeoutError('Retain exact mutual receipts, no acceptance from timeout')
        if not remaining:return chosen
        viable={n:[i for i in opts if all(pair(n,i,o,j) for o,j in chosen.items())] for n,opts in remaining.items()}
        if any(not opts for opts in viable.values()):return None
        name=min(viable,key=lambda n:len(viable[n]));other={n:opts for n,opts in viable.items() if n!=name}
        for i in viable[name]:
            result=solve({**chosen,name:i},other)
            if result is not None:return result
        return None
    save()
    try:
        outer=Part.Shape();outer.read(str(ROOT/doc['outer']['brep']))
        assert sha(ROOT/doc['outer']['brep'])==doc['outer']['sha256']
        surface=Part.makeCompound(outer.Shells)
        affected=set(core['changed_parts'])|{'StructureReserve:BankBed-1','BundleTie:FLHead'}
        affected.update(n for n,r in currentrows.items() if r['group']=='FRBodyReceiver' or n.startswith('ForeFHAC:out:custom:'))
        for n in sorted(affected):
            s=current[n];outside=s.cut(outer);assert outside.isNull() or outside.isValid()
            gap=s.distToShape(surface)[0]
            result['affected_core_true_outer'].append(dict(part=n,outside_mm3=outside.Volume,gap_mm=gap,required_mm=3.25))
            assert outside.Volume<1e-5 and gap>=3.25-1e-5,(n,'Actual current outer budget')
        # Fan-domain world proof used the old full cuff. Only the newly
        # added frame material must be queried; the strap cut only removes.
        _,old,_=packed(ROOT/core['equivalent_prior_packet'])
        added=current['BundleCuff:FR'].cut(old['BundleCuff:FR']);assert added.isValid() and added.Solids
        for n,s in shapes.items():
            lower=bbox_lower_bound(s.BoundBox,added.BoundBox)
            gap=lower if lower>=1.25 else q.distance(s,added)
            result['fan_against_added_frame'].append(dict(part=n,gap_lower_bound_or_exact_mm=gap,
                broad_separation_proof=lower>=1.25,required_mm=1.25))
            assert gap>=1.25-1e-5,(n,'New shared frame material')
        save()
        chosen=solve({}, {n:list(range(len(opts))) for n,opts in domains.items()})
        result['joint_assignment']=chosen
        result['status']='SIX_SOURCE_MUTUAL_ASSIGNMENT_RECEIVED_NOT_N01' if chosen else 'SIX_SOURCE_BOUNDED_DOMAINS_NEED_COMMON_LAYOUT_REVIEW'
        if chosen:result['chosen_templates']={n:domains[n][i] for n,i in chosen.items()}
    except Exception as e:result['errors'].append(repr(e));result['status']='SIX_SOURCE_MUTUAL_ERROR_OR_PARTIAL_NOT_CLEARANCE'
    save();print(json.dumps(dict(status=result['status'],seconds=result['worker_seconds'],nodes=visited,actual_pairs=len(queries),assignment=result['joint_assignment'],errors=result['errors'])),flush=True)


if __name__=='__main__':main()
