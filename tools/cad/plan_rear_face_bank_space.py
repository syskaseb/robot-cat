"""Preflight ONE rear facade before changing any source route or native CAD.

All retained material/motion/source factory feeds remain.24 explicitly changed
wire curves and12 terminal-side saddle groups cannot inherit qualification.
"""
import json
import time
from pathlib import Path
import FreeCAD as A
from remaining25_shared_context import load,P
from current_source_retention_context import C
from plan_remaining25_restraint_space import profile
from plan_axial_source_supports import arm_box
from rear_face_bank_layout import layout
from current_work_guard import check


def run():
    check();tick=time.monotonic();targets,wires,pins,parents,grips=load()
    names=['body36-current-contract','remaining25-interface-allocation',
           'remaining25-restraint-space','remaining25-saddle-roots']
    files=[P.OUT/(n+'.json') for n in names]
    contract,allocation,saddles,roots=[json.loads(f.read_text()) for f in files]
    assert roots['accepted_groups']==54 and not roots['errors']
    for receipt in (saddles,roots):
        for n,h in receipt['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    q=layout(targets,contract,allocation)
    changed_ends={e['id'] for e in allocation['ends'] if e['wire'] in q['changed_wire_ids'] and e['role'].startswith('F_') and e['role'].endswith('.in')}
    old_groups={g['id']:g for g in saddles['spatial_groups']}
    superseded_groups={gid for gid,g in old_groups.items() if any(e in changed_ends for e in g['ends'])}
    assert len(superseded_groups)==12
    for gid,i in saddles['selected_options'].items():
        if gid in superseded_groups:continue
        rec=saddles['domains'][gid][i]['recipe'];s=profile(old_groups[gid],rec['normal'],rec['knot_sign'])
        assert s['recipe']==rec
        targets.update({'Remaining25/'+gid+'/'+kind:s[kind] for kind in ('body','band')})
    for row in roots['groups']:
        if row['id'] in superseded_groups:continue
        for i,(a,b) in enumerate(zip(row['path'],row['path'][1:])):
            targets['CurrentSaddleRoot/'+row['owner']+'/'+row['id']+'/'+str(i)]=arm_box(a,b,roots['arm_half_widths_mm'])
    for n in q['retired_targets']:targets.pop(n)
    retired_wires=[n for n in wires if n.rsplit('/',1)[-1] in q['changed_wire_ids']]
    assert len({n.rsplit('/',1)[-1] for n in retired_wires})==24
    for n in retired_wires:wires.pop(n)
    files.extend(Path(__file__).with_name(n) for n in ('rear_face_bank_layout.py','current_bank_datums.py',
        'plan_axial_source_supports.py','plan_rear_face_bank_space.py'))
    pins.update({f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in files})
    bounds=C.ImmutableBounds();cache=C.AtomicMaterial(P.OUT/'rear-face-bank-pairs.json',bounds.near)
    checks=0;errors=[];records=[];service=[];installed=dict(q['parts'],RearBankPanel=q['panel'])
    def save(status):
        result=dict(status=status,layout=q['records'],panel_recipe=q['panel_recipe'],basis=q['basis'],
            material=records,service=service,checks=checks,errors=errors,source_sha256=pins,
            retained_saddle_groups=42,superseded_saddle_group_ids=sorted(superseded_groups),
            superseded_old_bank_targets=sorted(q['retired_targets']),
            changed_wire_ids=sorted(q['changed_wire_ids']),superseded_wire_instances=retired_wires,
            kept='All4MTA/eight factory feeds,24D/G/19retained nets and unchanged42 saddle/root groups. Existing native printed material remains conservatively present.',
            scope='Necessary installed nominal48part/panel/ATO/projectjaw/remainingwire space only. No omitted24 curve is claimed rerouted or supported.',
            open=['Full12 bank-input routes and12 whole V source/body curves with exact bends/length/coupled material',
                  'Changed12 terminal-side saddles,12 output receivers and independent wire roots',
                  'Actual panel support/fasteners/snap/tool fit/native CAD/whole stock/assembly'],
            worker_seconds=round(time.monotonic()-tick,3),selected=False,W5_complete=False,M4_complete=False,physical_pass=False)
        f=P.OUT/'rear-face-bank-space.json';tmp=f.with_suffix('.tmp');tmp.write_text(json.dumps(result,indent=2)+'\n');tmp.replace(f);cache.save()
    def hit(a,b,r=0):
        nonlocal checks
        if not bounds.near(a,b,r+.0001):return None
        if r and not b.Solids and len(b.Edges)>1:
            return next((v for e in b.Edges if (v:=hit(a,e,r)) is not None),None)
        try:check()
        except TimeoutError as e:errors.append(str(e));save('REAR_BANK_GUARDED_PARTIAL');raise
        checks+=1
        try:gap,volume=cache.check(a,b,0,r)
        except (AssertionError,RuntimeError,ValueError) as e:errors.append(str(e));return dict(error=str(e))
        if volume>1e-5 or (r and gap<r-1e-6):return dict(volume_mm3=volume,gap_mm=gap,required_mm=r)
        return None
    save('REAR_BANK_PREFLIGHT_STARTED')
    for n,s in installed.items():
        row=dict(part=n,contacts=[],assigned_catalog_fit_interfaces=[]);records.append(row)
        for m,t in targets.items():
            if t.Solids and (v:=hit(s,t)) is not None:row['contacts'].append(dict(obstacle=m,**v))
        for m,(w,r) in wires.items():
            if (v:=hit(s,w,r+.25)) is not None:row['contacts'].append(dict(obstacle=m,**v))
        for m,t in installed.items():
            if m==n:continue
            v=hit(s,t)
            if v is None:continue
            if (n=='RearBankPanel' and m.endswith('/Housing')) or (m=='RearBankPanel' and n.endswith('/Housing')):
                row['assigned_catalog_fit_interfaces'].append(dict(part=m,**v));continue
            row['contacts'].append(dict(obstacle=m,**v))
        save('REAR_BANK_INSTALLED_MATERIAL_IN_PROGRESS')
        print('rear bank',n,'contacts',len(row['contacts']),'pairs',checks,flush=True)
    all_targets=dict(targets,**installed)
    for name,s in {**q['sweeps'],**q['jaws']}.items():
        row=dict(id=name,contacts=[]);service.append(row)
        own=name.split('/')[0]
        for m,t in all_targets.items():
            if m=='RearBank/'+own+'/ATO' or not t.Solids:continue
            if (v:=hit(s,t)) is not None:row['contacts'].append(dict(obstacle=m,**v))
        for m,(w,r) in wires.items():
            if (v:=hit(s,w,r+.25)) is not None:row['contacts'].append(dict(obstacle=m,**v))
        save('REAR_BANK_PROJECT_SERVICE_IN_PROGRESS')
        print('rear service',name,'contacts',len(row['contacts']),flush=True)
    clear=not errors and not any(r['contacts'] for r in records+service)
    save('REAR_BANK_NECESSARY_SPACE_CLEAR_CHANGED_ROUTES_ROOTS_NATIVE_OPEN' if clear else 'REAR_BANK_PREFLIGHT_REQUIRES_CHANGED_LAYOUT')
    print(json.dumps(dict(parts=len(records),services=len(service),contacts=sum(len(r['contacts']) for r in records+service),checks=checks,seconds=round(time.monotonic()-tick,3))),flush=True)


if __name__=='__main__':run()
