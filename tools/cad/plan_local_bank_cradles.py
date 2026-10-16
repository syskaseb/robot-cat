"""Shared four-comb allocation with current54 restraints; no old wide panel.

Frame roots/native case retention stay OPEN. Save every received family and
on a guard interruption. Nominal vertical ATO service is checked separately.
"""
import json
import time
from pathlib import Path
import FreeCAD as A
from remaining25_shared_context import load,P
from current_source_retention_context import C,same_parent
from local_bank_cradle_material import families,GROUPS
from plan_remaining25_restraint_space import profile
from current_bank_retention_material import geometry as service_geometry
from current_work_guard import check


def run():
    check();tick=time.monotonic();targets,wires,pins,parents,grips=load()
    rf=P.OUT/'remaining25-restraint-space.json';r=json.loads(rf.read_text())
    assert r['status']=='REMAINING25_SADDLE_DOMAINS_AND_SHARED_MATERIAL_CLEAR_ROOTS_OPEN'
    assert len(r['selected_options'])==54 and not r['errors']
    for n,h in r['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    groups={g['id']:g for g in r['spatial_groups']}
    for gid,i in r['selected_options'].items():
        rec=r['domains'][gid][i]['recipe'];q=profile(groups[gid],rec['normal'],rec['knot_sign'])
        assert q['recipe']==rec
        targets.update({'Remaining25/'+gid+'/'+k:q[k] for k in ('body','band')})
    files=[rf,Path(__file__),Path(__file__).with_name('local_bank_cradle_material.py'),
           P.ROOT/'tools/electronics/servo_fuse_bank_restraints_r3.py',
           Path(__file__).with_name('current_bank_retention_material.py')]
    pins.update({f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in files})
    bounds=C.ImmutableBounds();cache=C.AtomicMaterial(P.OUT/'local-bank-cradle-pairs.json',bounds.near)
    rows=[];choices={};options={};errors=[];checks=0;service=[]
    def save(status):
        result=dict(status=status,groups=rows,chosen_families=choices,errors=errors,checks=checks,
            nominal_vertical_ATO_service_conflicts=service,source_sha256=pins,
            worker_seconds=round(time.monotonic()-tick,3),scope='Four local combs/T18Icase straps against current full material, full wires and54 chosen insulation saddles. Current routes unchanged. Own housing-flange bounds are assigned provisional fit interfaces, not proved vendor interference or clearance.',
            open=['Four actual Frame roots and native unions/parameter/reopen/exports',
                  'Installed service motion and real tool/engagement fit','Source cases/whole stock/current assembly'],
            selected=False,W5_complete=False,M4_complete=False,physical_pass=False)
        f=P.OUT/'local-bank-cradle-space.json';tmp=f.with_suffix('.tmp')
        tmp.write_text(json.dumps(result,indent=2)+'\n');tmp.replace(f);cache.save()
    def hit(a,b,radius=0):
        nonlocal checks
        if not bounds.near(a,b,radius+.0001):return None
        if radius and not b.Solids and len(b.Edges)>1:
            return next((v for e in b.Edges if (v:=hit(a,e,radius)) is not None),None)
        try:check()
        except TimeoutError as e:
            errors.append(str(e));save('LOCAL_BANK_GUARDED_PARTIAL');raise
        checks+=1
        try:gap,volume=cache.check(a,b,0,radius)
        except (AssertionError,RuntimeError,ValueError) as e:
            errors.append(str(e));return dict(error=str(e))
        if volume>1e-5 or (radius and gap<radius-1e-6):return dict(volume_mm3=volume,gap_mm=gap,required_mm=radius)
        return None
    family=families()
    for leg,y,centres,owner in GROUPS:
        row=dict(id=leg,qualified_options=[],rejected=[]);rows.append(row);options[leg]={}
        side='L' if y>0 else 'R';indices=range(1,4) if leg.startswith('F') else range(4,7)
        own_cases={f'F_{side}{i}_CP2_Housing' for i in indices}
        for key,q in family[leg].items():
            material={'body':q['body'],**q['ties']};contacts=[];interfaces=[];unions=[]
            for name,s in material.items():
                for n,t in targets.items():
                    if not t.Solids:continue
                    v=hit(s,t)
                    if v is None:continue
                    if n.split('/')[0] in own_cases:
                        interfaces.append(dict(part=name,nominal_case=n,**v));continue
                    if name=='body' and same_parent(owner,n,grips):
                        unions.append(dict(parent=n,**v));continue
                    contacts.append(dict(part=name,obstacle=n,**v))
                    if len(contacts)>=4:break
                if len(contacts)>=4:break
                for n,(w,rad) in wires.items():
                    if (v:=hit(s,w,rad+.25)) is not None:
                        contacts.append(dict(part=name,obstacle=n,**v))
                        if len(contacts)>=4:break
                if len(contacts)>=4:break
            if contacts:row['rejected'].append(dict(family=key,contacts=contacts))
            else:
                options[leg][key]=q
                row['qualified_options'].append(dict(family=key,recipe=q['recipe'],
                    assigned_provisional_case_interfaces=interfaces,parent_union_candidates=unions))
            save('LOCAL_BANK_FAMILY_DOMAINS_IN_PROGRESS')
            print('local bank',leg,key,'clear',not contacts,'checks',checks,flush=True)
    if all(options.values()) and not errors:
        selected={};ordered=sorted(options,key=lambda n:len(options[n]))
        def choose(i):
            if i==len(ordered):return True
            leg=ordered[i]
            for key,q in options[leg].items():
                parts=[q['body'],*q['ties'].values()]
                if any(hit(a,b) is not None for other in selected.values() for a in parts
                       for b in [other['body'],*other['ties'].values()]):continue
                selected[leg]=q;choices[leg]=key
                if choose(i+1):return True
                selected.pop(leg);choices.pop(leg)
            return False
        choose(0)
    save('FOUR_LOCAL_BANK_COMBS_MATERIAL_CLEAR_ROOTS_SERVICE_OPEN' if len(choices)==4 else 'LOCAL_BANK_COMB_LAYOUT_REQUIRES_CHANGE')
    # Diagnose the actual nominal component sweep, not a wide26mm tool bbox.
    # This is a separately OPEN service map, never a routine-access approval.
    sweeps=service_geometry()['ATO_sweeps']
    for name,s in sweeps.items():
        for n,t in targets.items():
            if n.startswith(name) or not t.Solids:continue
            if (v:=hit(s,t)) is not None:service.append(dict(fuse=name,obstacle=n,**v))
        for n,(w,rad) in wires.items():
            if (v:=hit(s,w,rad+.25)) is not None:service.append(dict(fuse=name,obstacle=n,**v))
        save('FOUR_LOCAL_BANK_COMBS_MATERIAL_CLEAR_ROOTS_SERVICE_OPEN' if len(choices)==4 else 'LOCAL_BANK_COMB_LAYOUT_REQUIRES_CHANGE')
        print('local bank service map',name,'conflicts',len(service),flush=True)
    print(json.dumps(dict(chosen=choices,checks=checks,service_conflicts=len(service),seconds=round(time.monotonic()-tick,3))),flush=True)


if __name__=='__main__':run()
