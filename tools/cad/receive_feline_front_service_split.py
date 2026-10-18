"""Exact shared first-space gate; reused byte-identical pairs stay closed."""
import hashlib
import json
import time
import zipfile
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from check_feline_all_current_lands import near
from feline_current_scene import load
from plan_feline_layout import OUT


def main():
    tick=time.monotonic();src=OUT/'n01-front-service-split-plan.json';dest=OUT/'n01-front-service-split-static.json'
    assert not dest.exists();plan=json.loads(src.read_text())
    parent=json.loads((ROOT/plan['parent_static_receipt']).read_text())
    oldplan=json.loads((ROOT/plan['source_parent']).read_text())
    for n,h in plan['source_sha256'].items():assert sha(ROOT/n)==h,n
    bundle=ROOT/plan['bundle'];assert sha(bundle)==plan['bundle_sha256']
    scene,meta,_,_,pins,_=load()
    for n in plan['retired_planning_parts']:scene.pop(n);meta.pop(n)
    localfile=OUT/'n01-selected-local-head-tail-sources.json';local=json.loads(localfile.read_text());lb=ROOT/local['bundle']
    assert sha(lb)==local['bundle_sha256']
    with zipfile.ZipFile(lb) as z:
        for r in local['parts']:
            raw=z.read(r['entry']);assert hashlib.sha256(raw).hexdigest()==r['sha256']
            s=Part.Shape();s.importBrepFromString(raw.decode('utf-8'))
            if not s.Solids:continue
            if r['role']=='HeadElectricalYaw':s.translate(A.Vector(0,0,35))
            scene[r['name']]=s;meta[r['name']]=r
    assert len(scene)==911
    candidate={};rows={}
    with zipfile.ZipFile(bundle) as z:
        for r in plan['parts']:
            raw=z.read(r['entry']);assert hashlib.sha256(raw).hexdigest()==r['sha256']
            s=Part.Shape();s.importBrepFromString(raw.decode('utf-8'));assert s.isValid() and s.Solids
            candidate[r['name']]=s;rows[r['name']]=r
    fixed={n:s for n,s in scene.items() if not meta[n].get('role','').startswith('leg:')}
    world={**fixed,**candidate};bounds={n:s.BoundBox for n,s in world.items()}
    owner={n:('HeadRaised' if meta[n].get('role')=='HeadElectricalYaw' else 'retained') for n in fixed}
    owner.update({n:r['group'] for n,r in rows.items()})
    def kind(n):
        if n in rows:return rows[n]['kind']
        r=meta[n];return 'reservation' if 'reservation' in r.get('kind','') or r.get('role')=='ScaffoldPlanning' else 'material'
    def iswire(n):return n in ('W043','W077','W078') or n.startswith(('BankFullPrefix:','End:','Factory:','PiGPIO:','PiGPIOAfterGrip:')) or kind(n)=='proposal_wire'
    changed=set(plan['changed_part_names']);unchanged=set(plan['unchanged_part_names'])
    oldrows={r['name']:r for r in oldplan['parts']}
    assert all(rows[n]['sha256']==oldrows[n]['sha256'] for n in unchanged)
    reusable={tuple(r['pair']):r for r in parent['completed_queries'] if r['status'] in ('clear','existing_bank_bearing_plane_mate') and not changed.intersection(r['pair']) and all(n in world for n in r['pair'])}
    result=dict(status='RUNNING_CHANGED_SERVICE_SPLIT_AND_FIRST_WIRE_GATE',selected=False,N01_complete=False,physical_pass=False,
        exact_geometry_failures=[],reservation_holds=[],errors=[],completed_queries=[],reused_pairs=list(reusable),pairs=0,
        own_down_factory_floor_passages=[],full_middles_motion_roots_tools_skin_not_qualified=True,
        source_sha256={**pins,src.relative_to(ROOT).as_posix():sha(src),bundle.relative_to(ROOT).as_posix():sha(bundle),
            localfile.relative_to(ROOT).as_posix():sha(localfile),lb.relative_to(ROOT).as_posix():sha(lb),Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))})
    def save():
        result['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    def gate():
        if time.monotonic()-tick>180:raise TimeoutError('180s scoped receive; retain every completed query')
    def query(n,m):
        gate();s,t=world[n],world[m]
        if not t.isValid() or not t.Solids:
            result['errors'].append(dict(a=n,b=m,error='Invalid source, not clearance'));return
        required=.2 if iswire(n) and iswire(m) else 1.25
        gap=s.distToShape(t)[0];result['pairs']+=1
        received=dict(pair=sorted((n,m)),gap_mm=gap,required_mm=required)
        if gap<required-1e-5:
            if n.endswith(':bed_root') and 'Housing' in m and abs(bounds[m].ZMin-55)<1e-6 and abs(bounds[n].ZMax-55)<1e-6 and s.common(t).Volume<1e-6:
                received['status']='existing_bank_bearing_plane_mate';result['completed_queries'].append(received);return
            reserved=kind(n)=='reservation' or kind(m)=='reservation'
            item=dict(a=n,b=m,gap_mm=gap,required_mm=required,group=owner[n],other_group=owner[m],
                actual_geometry_distance_not_bbox=True,positive_overlap_volume_not_claimed=True,
                reservation_is_not_real_part_contact=reserved)
            (result['reservation_holds'] if reserved else result['exact_geometry_failures']).append(item)
            received['status']='reservation_hold' if reserved else 'actual_clearance_failure'
        else:received['status']='clear'
        result['completed_queries'].append(received)
        if result['pairs']%10==0:save()
    save();seen=set()
    try:
        for n in candidate:
            if n not in changed and not iswire(n):continue
            for m,t in world.items():
                if owner[n]==owner[m] or not near(bounds[n],bounds[m],1.25):continue
                if n.endswith(':bed_root') and m=='StructureReserve:BankBed'+str(1 if owner[n]=='F_HP' else -1):continue
                key=tuple(sorted((n,m)))
                if key in seen or key in reusable:continue
                seen.add(key);query(n,m)
            save();print('Received',n,'pairs',result['pairs'],'failures',len(result['exact_geometry_failures']),
                'reserved',len(result['reservation_holds']),flush=True)
        for role in ('F_HY','F_HP','F_TY'):
            downward=next(k for k,v in plan['changed_endpoints'].items() if k.startswith(role+'.') and v['departure_axis'][2]<-.99)
            wire=role+':factory_'+downward.rsplit('.',1)[1];gap=world[role+':floor'].distToShape(world[wire])[0]
            result['own_down_factory_floor_passages'].append(dict(role=role,gap_mm=gap,minimum_mm=1.25))
            assert gap>=1.25-1e-5,(role,gap)
        result['status']='SERVICE_SPLIT_STATIC_FIRST_SPACE_REJECTED' if result['exact_geometry_failures'] or result['reservation_holds'] or result['errors'] else 'SERVICE_SPLIT_STATIC_FIRST_SPACE_NOMINATED_FULL_N01_OPEN'
    except Exception as e:result['status']='PARTIAL_SERVICE_SPLIT_FIRST_SPACE_GATE';result['errors'].append(repr(e))
    save();print(json.dumps(dict(status=result['status'],pairs=result['pairs'],failures=len(result['exact_geometry_failures']),
        reservation_holds=len(result['reservation_holds']),errors=result['errors'],seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':main()
