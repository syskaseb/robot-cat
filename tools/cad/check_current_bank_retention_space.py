"""Shared bank-panel/foot/hardware/access gate before four structural roots.

Purchased housing bounds are reservations. A panel's prescribed flange/aperture
interface stays a delivered-fit gate, never reclassified as proven clearance.
"""
import json
import time
from pathlib import Path
import FreeCAD as A
from remaining25_shared_context import load,P
from current_source_retention_context import C,same_parent
from current_bank_retention_material import geometry
from current_work_guard import check
from plan_remaining25_restraint_space import profile


def run(material_map_only=False):
    check();tick=time.monotonic();targets,wires,pins,parents,grips=load();q=geometry()
    restraint_file=P.OUT/'remaining25-restraint-space.json';restraints=json.loads(restraint_file.read_text())
    assert restraints['status']=='REMAINING25_SADDLE_DOMAINS_AND_SHARED_MATERIAL_CLEAR_ROOTS_OPEN'
    assert len(restraints['selected_options'])==restraints['expected_groups']==54
    for n,h in restraints['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    groups={g['id']:g for g in restraints['spatial_groups']}
    for gid,index in restraints['selected_options'].items():
        r=restraints['domains'][gid][index]['recipe'];s=profile(groups[gid],r['normal'],r['knot_sign'])
        assert s['recipe']==r
        for kind in ('body','band'):targets['Remaining25/'+gid+'/'+kind]=s[kind]
    pins[restraint_file.relative_to(P.ROOT).as_posix()]=P.SHA(restraint_file)
    pieces={**q['prints'],**{'Foot/'+n:v['shape'] for n,v in q['feet'].items()},**q['hardware']}
    bounds=C.ImmutableBounds();cache=C.AtomicMaterial(P.OUT/'current-bank-retention-pairs.json',bounds.near)
    rows=[];contacts=[];errors=[];interface_overlaps=[];access_conflicts=[];coarse_overlaps=[];pairs=0
    sources=[Path(__file__),Path(__file__).with_name('current_bank_retention_material.py'),
        P.ROOT/'hardware/reference/servo-holder-p0-2026-09-24/ENVELOPE.md',
        P.ROOT/'tools/electronics/servo_fuse_side_bank_r4.py']
    pins.update({f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in sources})
    def save_partial(status):
        result=dict(status=status,completed_material=rows,contacts=contacts,errors=errors,
            access_reservation_conflicts=access_conflicts,assigned_flange_reservation_overlaps=interface_overlaps,
            recipe=q['recipe'],pairs=pairs,source_sha256=pins,worker_seconds=round(time.monotonic()-tick,3),
            scope='Incremental current bank material diagnosis, not root/native/whole assembly acceptance.',
            material_map_only=material_map_only,selected=False,W5_complete=False,M4_complete=False,physical_pass=False)
        f=P.OUT/'current-bank-retention-space.json';tmp=f.with_suffix('.tmp')
        tmp.write_text(json.dumps(result,indent=2)+'\n');tmp.replace(f);cache.save()
    def test(n,s,m,t,r=0,budget=False,interface=False):
        nonlocal pairs
        if not bounds.near(s,t,r+.0001):return
        if r and not t.Solids and len(t.Edges)>1:
            for i,e in enumerate(t.Edges):test(n,s,m+'/'+str(i),e,r,budget,interface)
            return
        try:check()
        except TimeoutError as e:
            errors.append(dict(reason='guarded_partial',error=str(e)))
            save_partial('BANK_SHARED_GATE_GUARDED_PARTIAL');raise
        pairs+=1
        try:gap,volume=cache.check(s,t,0,r)
        except (AssertionError,RuntimeError,ValueError) as e:
            errors.append(dict(a=n,b=m,error=str(e)));return
        if volume>1e-5 or (r and gap<r-1e-6):
            row=dict(a=n,b=m,volume_mm3=volume,gap_mm=gap,required_mm=r)
            (interface_overlaps if interface else access_conflicts if budget else contacts).append(row)
    for n,s in pieces.items():
        for m,t in targets.items():
            if not t.Solids:continue
            # Only the assigned housing/flange reservation of the same bank
            # row may overlap its aperture-bearing panel or retention bar.
            # TE/ATO/wires/other cases never receive this exception.
            side=n[4:5] if n.startswith('Bank') else None
            identity=m.split('/')[0]
            own_housing=bool(side and identity in {f'F_{side}{i}_CP2_Housing' for i in range(1,7)})
            test(n,s,m,t,interface=own_housing)
        for m,(w,r) in wires.items():test(n,s,m,w,r+.25)
        rows.append(n)
        save_partial('BANK_SHARED_MATERIAL_IN_PROGRESS')
        print('bank shared material',n,'pairs',pairs,'contacts',len(contacts),flush=True)
        if material_map_only and contacts:
            save_partial('BANK_SHARED_FIRST_CONFLICT_MAP_SAVED')
            print(json.dumps(dict(first_material=n,contacts=contacts,interface_reservations=interface_overlaps,
                worker_seconds=round(time.monotonic()-tick,3))),flush=True)
            return
    names=list(pieces)
    for i,n in enumerate(names):
        for m in names[i+1:]:test(n,pieces[n],m,pieces[m])
    for category,items in [('ATO_sweep',q['ATO_sweeps']),('ATO_jaws',q['ATO_jaws']),('Lkey',q['tools'])]:
        for n,s in items.items():
            for m,t in {**targets,**pieces}.items():
                if category.startswith('ATO') and m.startswith(n.split('/')[0]):continue
                if t.Solids:test(category+'/'+n,s,m,t,budget=True)
            for m,(w,r) in wires.items():test(category+'/'+n,s,m,w,r+.25,budget=True)
    for n,s in q['ATO_access'].items():
        for m,t in {**targets,**pieces}.items():
            if not t.Solids or not bounds.near(s,t,0):continue
            coarse_overlaps.append(dict(a=n,b=m,bbox_candidate_only=True,physical_collision_established=False))
    sources=[Path(__file__),Path(__file__).with_name('current_bank_retention_material.py'),
        P.ROOT/'hardware/reference/servo-holder-p0-2026-09-24/ENVELOPE.md',
        P.ROOT/'tools/electronics/servo_fuse_side_bank_r4.py']
    pins.update({f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in sources})
    result=dict(status='BANK_SHARED_MATERIAL_OR_ACCESS_REQUIRES_CHANGE' if contacts or errors or access_conflicts else
                'BANK_SHARED_NOMINAL_MATERIAL_ACCESS_CLEAR_ROOTS_NATIVE_OPEN',
        completed_material=rows,contacts=contacts,errors=errors,access_reservation_conflicts=access_conflicts,
        coarse_service_budget_candidates=coarse_overlaps,
        assigned_flange_reservation_overlaps=interface_overlaps,
        assigned_interface_remains_delivered_fit_gate=True,
        recipe=q['recipe'],pairs=pairs,source_sha256=pins,worker_seconds=round(time.monotonic()-tick,3),
        root_goals={n:{k:v for k,v in r.items() if k!='shape'} for n,r in q['feet'].items()},
        open=['Four actual structural roots, changed current parent unions',
              'Shared gate with all55 chosen new saddle profiles and their roots',
              'Native/parameter/reopen/STL/stock/whole assembled selection',
              'Delivered holder/body/aperture/ATO/tool fit; nominal reservation is not measured action'],
        selected=False,W5_complete=False,M4_complete=False,physical_pass=False)
    f=P.OUT/'current-bank-retention-space.json';f.write_text(json.dumps(result,indent=2)+'\n');cache.save()
    print(json.dumps({k:result[k] for k in ('status','pairs','worker_seconds')}),flush=True)


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--material-map-only',action='store_true')
    run(parser.parse_args().material_map_only)
