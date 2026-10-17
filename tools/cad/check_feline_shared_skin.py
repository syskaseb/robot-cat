"""Exact changed shared skin gate with certified subset and tool containment reuse.

Old clear material/69wire pairs cannot worsen after removal only. Recheck all
old positives, full36leg poses and9head poses. Bboxes prune only if the
possible common is contained in an actual native rectangular cutting solid.
"""
import json,time
from pathlib import Path
import FreeCAD as A
from check_main_p0_placement import ROOT,SavedShapes,sha
from plan_feline_layout import OUT,STAGES
from check_feline_leg_body import placement
from datetime import datetime as task_datetime,timezone as task_timezone


def main():
    tick=time.monotonic();reader=SavedShapes();af=OUT/'skin-access-native.json'
    access=json.loads(af.read_text());assert access['status']=='FOUR_NATIVE_PANELS_WITH_SEVEN_SHARED_PORTALS_EXACT_MOTION_OPEN'
    native=ROOT/access['native'];assert sha(native)==access['native_sha256']
    oldfile=OUT/'torso-panel-interfaces.json';old=json.loads(oldfile.read_text())
    assert old['status']=='UNNOTCHED_WALL_REJECTED_PARTIAL_MATRIX_STOPPED'
    ancestor=access
    while ancestor['source_native_sha256']!=old['native_sha256']:
        previous=ancestor['previous_access_receipt']
        assert previous['native_sha256']==ancestor['source_native_sha256']
        assert all(v<1e-5 for v in previous['new_material_mm3'].values())
        ancestor=previous
    assert not old['errors'] and not old['clearance_failures']
    assert all(v<1e-5 for v in access['new_material_mm3'].values())
    interior=json.loads((OUT/'interior-native-checks.json').read_text());current=ROOT/interior['native']
    assert sha(current)==interior['native_sha256']
    plan=json.loads((OUT/'module-layout.json').read_text());motion=json.loads((OUT/'motion-layout.json').read_text())
    for p in (current,OUT/'module-layout.json',OUT/'motion-layout.json'):
        assert old['source_sha256'][p.relative_to(ROOT).as_posix()]==sha(p),p
    for filename in ('prefix-allocation.json','factory-routes.json'):
        p=OUT/filename;assert interior['reused_qualified_interface_receipts'][p.relative_to(ROOT).as_posix()]==sha(p)
    head=set(next(g['objects'] for g in plan['groups'] if g['role']=='HeadMechanism'))
    leg={n for g in motion['membership'].values() for ns in g.values() for n in ns}
    prior_positive={(r['panel'],r['object']) for r in old['contacts'] if r['scope']=='fixed_material'}
    names=head|leg|{n for pn,n in prior_positive};scene={n:reader.shape(current,n) for n in names}
    panels={r['object']:reader.shape(native,r['object']) for r in access['parts']}
    panel_boxes={n:reader.shape(native,n+'SplitTool').BoundBox for n in panels}
    material_boxes={n:s.BoundBox for n,s in panels.items()}
    interior_boxes=[]
    for portal in access['portals']:
        for b in portal['straight_interior_boxes']:interior_boxes.append(reader.shape(native,b['object']).BoundBox)
    report=dict(status='SHARED_NATIVE_SKIN_EXACT_RUNNING',selected=False,physical_pass=False,
        native=native.relative_to(ROOT).as_posix(),native_sha256=sha(native),
        contacts=[],errors=[],pairs=0,tool_containment_prunes=0,leg_poses=[],head_poses=[],
        unchanged_fixed_clear_pairs_reused_by_material_subset=True,
        unchanged_known_wire_scope_reused_by_material_subset={'factory_pieces':8,'end_approaches':61,'full_wiring':False},
        continuous_motion=False,full_wiring_complete=False,cowls_complete=False,mounts_service_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (af,oldfile,current,native,OUT/'module-layout.json',OUT/'motion-layout.json',OUT/'prefix-allocation.json',OUT/'factory-routes.json',Path(__file__))})
    destination=OUT/'shared-skin-exact.json'
    deadline=task_datetime.fromisoformat('2026-10-17T07:30:00+00:00')
    def save():
        report['worker_seconds']=round(time.monotonic()-tick,3);destination.write_text(json.dumps(report,indent=2)+'\n')
    def stop_gate():
        if task_datetime.now(task_timezone.utc)>=deadline:
            report.update(status='SHARED_SKIN_EXACT_DEADLINE_PARTIAL',deadline_reached=True);save();raise TimeoutError('Authorized window deadline reached')
    def intersection_bounds(a,b,c):
        lo=[max(a.XMin,b.XMin,c.XMin),max(a.YMin,b.YMin,c.YMin),max(a.ZMin,b.ZMin,c.ZMin)]
        hi=[min(a.XMax,b.XMax,c.XMax),min(a.YMax,b.YMax,c.YMax),min(a.ZMax,b.ZMax,c.ZMax)]
        return lo,hi
    def check(pn,p,n,s,scope,pose=None):
        stop_gate();b=s.BoundBox;lo,hi=intersection_bounds(material_boxes[pn],panel_boxes[pn],b)
        if any(x>y+.001 for x,y in zip(lo,hi)):return
        for box in interior_boxes:
            # Strict containment with0.01mm safety budget in a genuine
            # rectangular native cut solid, not an approximate rounded bbox.
            if all(x>=a+.01 and y<=b-.01 for x,y,a,b in zip(lo,hi,
                [box.XMin,box.YMin,box.ZMin],[box.XMax,box.YMax,box.ZMax])):
                report['tool_containment_prunes']+=1;return
        report['pairs']+=1
        try:
            c=p.common(s)
            if not c.isNull() and not c.isValid():raise ValueError('Invalid exact intersection')
            if c.Volume>1e-5:
                # Preserve actual witness points, never oversized trimmed
                # surface bboxes, for any further topology decision.
                points,faces=c.tessellate(.2)
                if points:
                    coords=[list(v) for v in points];lower=[min(v[i] for v in coords) for i in range(3)];upper=[max(v[i] for v in coords) for i in range(3)]
                else:lower=upper=None
                report['contacts'].append(dict(panel=pn,object=n,scope=scope,pose=pose,volume_mm3=c.Volume,
                    witness_mesh_bounds_mm=[lower,upper],witness_deflection_mm=.2))
        except Exception as exc:report['errors'].append(dict(panel=pn,object=n,scope=scope,error=str(exc)))
    save()
    try:
        for pn,n in sorted(prior_positive):check(pn,panels[pn],n,scene[n],'previous_fixed_positive')
        save();print('Shared skin fixed positives',len(report['contacts']),'errors',len(report['errors']),flush=True)
        if report['contacts'] or report['errors']:
            report.update(status='SHARED_SKIN_NOMINAL_REJECTED_BEFORE_MOTION');save();return
        axes=json.loads((ROOT/'hardware/simulation/p0/e6-leg-compatibility.json').read_text())['axes']
        for i,pose in enumerate(motion['poses'][:36]):
            first=report['pairs']
            for code,g in motion['membership'].items():
                aa=[next(a for a in axes if a['code']==code and a['stage']==stage) for stage in STAGES];tf=placement(aa,pose['legs'][code]['angles_delta_degrees'])
                for stage,ns in g.items():
                    for n in ns:
                        s=scene[n].copy();s.Placement=tf[stage]*s.Placement
                        for pn,p in panels.items():check(pn,p,n,s,'leg_motion',i)
            report['leg_poses'].append(dict(index=i,pairs=report['pairs']-first));save()
            print('Shared skin leg',i,'hits',len(report['contacts']),'pairs',report['pairs'],flush=True)
            if report['contacts'] or report['errors']:
                report.update(status='SHARED_SKIN_LEG_REJECTED_NO_MORE_UNCHANGED_POSES');save();return
        for pitch in (-10,0,5):
            for yaw in (-15,0,15):
                for n in head:
                    s=scene[n].copy()
                    if pitch:s.rotate(A.Vector(*plan['head_pitch_axis_mm']),A.Vector(0,1,0),pitch)
                    if yaw:s.rotate(A.Vector(*plan['head_yaw_axis_mm']),A.Vector(0,0,1),yaw)
                    for pn,p in panels.items():check(pn,p,n,s,'head_conservative_union',[pitch,yaw])
                report['head_poses'].append([pitch,yaw]);save()
        report.update(status='SAMPLED_SHARED_SKIN_CLEAR_COWLS_MOUNTS_WIRING_OPEN' if not report['contacts'] and not report['errors'] else 'SHARED_SKIN_HEAD_WITNESSES_REQUIRE_REVIEW')
        report['source_sha256'].update(reader.hashes);save()
        print(json.dumps({k:report[k] for k in ('status','pairs','tool_containment_prunes','worker_seconds')}),flush=True)
    except TimeoutError:
        print('Deadline: partial saved, no further exact operations',flush=True)


if __name__=='__main__':main()
