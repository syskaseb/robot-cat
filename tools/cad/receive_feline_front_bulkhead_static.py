"""Receive saved239-part architecture, with unchanged rigid ownership reuse.

Distance-first exact CAD clearance; no expensive Boolean for already clear
pairs. Reservation conflict is explicitly not evidence of real-part collision.
Progress receipts retain each completed query. No rebuild or native write.
"""
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
    tick=time.monotonic();src=OUT/'n01-front-bulkhead-architecture.json'
    dest=OUT/'n01-front-bulkhead-static-received.json';assert not dest.exists()
    plan=json.loads(src.read_text());assert len(plan['parts'])==239
    for n,h in plan['source_sha256'].items():assert sha(ROOT/n)==h,n
    bundle=ROOT/plan['bundle'];assert sha(bundle)==plan['bundle_sha256']
    scene,meta,_,_,pins,_=load()
    for n in plan['retired_planning_parts']:
        assert n in scene,n
        scene.pop(n);meta.pop(n)
    localfile=OUT/'n01-selected-local-head-tail-sources.json';local=json.loads(localfile.read_text())
    lb=ROOT/local['bundle'];assert sha(lb)==local['bundle_sha256']
    with zipfile.ZipFile(lb) as z:
        for r in local['parts']:
            raw=z.read(r['entry']);assert hashlib.sha256(raw).hexdigest()==r['sha256']
            s=Part.Shape();s.importBrepFromString(raw.decode('utf-8'))
            if not s.Solids:continue
            if r['role']=='HeadElectricalYaw':s.translate(A.Vector(0,0,35))
            scene[r['name']]=s;meta[r['name']]=r
    assert len(scene)==911,len(scene)
    candidates={};rows={}
    with zipfile.ZipFile(bundle) as z:
        for r in plan['parts']:
            raw=z.read(r['entry']);assert hashlib.sha256(raw).hexdigest()==r['sha256']
            s=Part.Shape();s.importBrepFromString(raw.decode('utf-8'));assert s.isValid() and s.Solids
            candidates[r['name']]=s;rows[r['name']]=r
    fixed={n:s for n,s in scene.items() if not meta[n].get('role','').startswith('leg:')}
    world={**fixed,**candidates};bounds={n:s.BoundBox for n,s in world.items()}
    owner={n:('HeadRaised' if meta[n].get('role')=='HeadElectricalYaw' else 'retained') for n in fixed}
    owner.update({n:r['group'] for n,r in rows.items()})
    def kind(n):
        if n in rows:return rows[n]['kind']
        r=meta[n];k=r.get('kind','')
        return 'reservation' if 'reservation' in k or r.get('role')=='ScaffoldPlanning' else 'material'
    r=dict(status='RUNNING_SAVED_WHOLE_TOPOLOGY_STATIC',selected=False,N01_complete=False,physical_pass=False,
        actual_geometry_clearance_failures=[],reservation_conflicts=[],errors=[],completed_queries=[],
        tested_groups=[],pairs=0,unchanged_rigid_head_local_pairs_reused_by_owner=True,
        full89plus34middles_motion_native_roots_tools_not_qualified=True,
        source_sha256={**pins,src.relative_to(ROOT).as_posix():sha(src),bundle.relative_to(ROOT).as_posix():sha(bundle),
            localfile.relative_to(ROOT).as_posix():sha(localfile),lb.relative_to(ROOT).as_posix():sha(lb),
            Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))})
    def save():
        r['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8',newline='\n')
    def gate():
        if time.monotonic()-tick>180:raise TimeoutError('180s saved geometry receive; completed queries retained')
    seen=set();valid={}
    save();print('Received239frozen proposal shapes; rigid head/local owner reuse, no reconstruction',flush=True)
    try:
        for group in plan['proposed_group_parts']:
            group_queries=0
            for n in plan['proposed_group_parts'][group]:
                if kind(n)=='proposal_wire':continue # bodies/ports before full wire gate
                s=candidates[n];gate()
                for m,t in world.items():
                    if owner[m]==group or not near(bounds[n],bounds[m],1.25):continue
                    if n.endswith(':bed_root') and m=='StructureReserve:BankBed'+str(1 if group=='F_HP' else -1):continue
                    key=tuple(sorted((n,m)))
                    if key in seen:continue
                    gate();seen.add(key)
                    if m not in valid:valid[m]=t.isValid() and bool(t.Solids)
                    if not valid[m]:
                        r['errors'].append(dict(a=n,b=m,error='Invalid source; not clearance'))
                        r['completed_queries'].append(dict(pair=key,status='invalid_source'));continue
                    distance=s.distToShape(t)[0];r['pairs']+=1;group_queries+=1
                    received=dict(pair=key,gap_mm=distance,required_air_gap_mm=1.25)
                    if distance<1.25-1e-5:
                        # Root top55 intentionally extends the same bank-bed
                        # bearing plane. Only exact zero-volume mating at the
                        # existing housing bottom55 is a permitted interface.
                        if n.endswith(':bed_root') and 'Housing' in m and abs(bounds[m].ZMin-55)<1e-6 and abs(bounds[n].ZMax-55)<1e-6:
                            intersection=s.common(t);assert intersection.isNull() or intersection.isValid()
                            if intersection.Volume<1e-6:
                                received['status']='existing_bank_bearing_plane_mate';r['completed_queries'].append(received);continue
                        reserved=kind(n)=='reservation' or kind(m)=='reservation'
                        item=dict(a=n,b=m,gap_mm=distance,group=group,other_group=owner[m],
                            exact_CAD_distance_not_bbox=True,positive_intersection_volume_not_claimed=True,
                            reservation_overlap_is_not_real_part_contact=reserved)
                        (r['reservation_conflicts'] if reserved else r['actual_geometry_clearance_failures']).append(item)
                        received['status']='reservation_hold' if reserved else 'actual_clearance_failure'
                    else:received['status']='clear'
                    r['completed_queries'].append(received)
                    if r['pairs']%10==0:save()
            r['tested_groups'].append(group);save()
            print('Received',group,'queries',group_queries,'failures',len(r['actual_geometry_clearance_failures']),
                'reservation holds',len(r['reservation_conflicts']),flush=True)
        r['status']='SAVED_WHOLE_TOPOLOGY_STATIC_REJECTED' if r['actual_geometry_clearance_failures'] or r['reservation_conflicts'] or r['errors'] else 'SAVED_WHOLE_TOPOLOGY_BODIES_NOMINATED_FULL_WIRING_MOTION_OPEN'
    except Exception as e:r['status']='PARTIAL_SAVED_WHOLE_TOPOLOGY_STATIC';r['errors'].append(repr(e))
    save();print(json.dumps(dict(status=r['status'],pairs=r['pairs'],material_failures=len(r['actual_geometry_clearance_failures']),
        reservation_holds=len(r['reservation_conflicts']),errors=r['errors'],seconds=r['worker_seconds'])),flush=True)


if __name__=='__main__':main()
