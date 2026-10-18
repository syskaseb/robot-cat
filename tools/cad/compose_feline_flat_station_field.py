"""Whole20-flat field with per-source removal, bounded-memory surface union.

Keeps actual P0/modules/bank/4MTA and the adopted36motion field. Only the
named19station kits/old prefix families and unselected common-frame recipes
are variables. P_SYS stays an explicit identity context, not a deleted part.
No native assembly, collision acceptance or N01 score is produced.
"""
import hashlib
import io
import json
import sys
import time
import zipfile
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from scipy.spatial import cKDTree
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_current_candidate_scene import current
from plan_feline_skin_access import surface_samples
from plan_feline_global_case_capacity import points_from_ids
from plan_feline_flat_owner_contract import own_reservation


def points(s):
    assert s.isValid() and s.Solids
    v,f=s.tessellate(.3)
    return surface_samples(np.array([list(p) for p in v])[np.array(f,dtype=int)],2)


def frame_variable(n,m):
    if any(a in sys.argv for a in ('--owner-complete','--joint-space','--bank-joint','--module-joint')) and own_reservation(n,m):return True
    if n=='P_SYS_CommonRelief':
        assert m.get('kind')=='frame_reservation' and m.get('owner')=='UpperFrame',m
        return '--owner-r2' in sys.argv
    if not n.startswith('StructureReserve:'):return False
    variable=n.removeprefix('StructureReserve:').startswith((
        'LowerRail','Crossmember','RootBoss','Post','BankArm','BankForeHanger','BankForeToe','UpperStrip'))
    if variable:assert 'reservation' in m.get('kind','') or m.get('role')=='ScaffoldPlanning',n
    return variable


def main():
    tick=time.monotonic();modulejoint='--module-joint' in sys.argv
    bankjoint='--bank-joint' in sys.argv or modulejoint;joint='--joint-space' in sys.argv or bankjoint
    r2=any(a in sys.argv for a in ('--owner-r2','--owner-complete','--joint-space','--bank-joint','--module-joint'))
    suffix='-modulejoint' if modulejoint else '-bankjoint' if bankjoint else '-joint' if joint else '-owned' if '--owner-complete' in sys.argv else '-r2' if r2 else ''
    dest=OUT/('n01-flat20-field'+suffix+'.json');fieldfile=OUT/('n01-flat20-field'+suffix+'.npz')
    assert not dest.exists() and not fieldfile.exists(),'Receive existing field before rebuilding'
    planfile=OUT/'n01-flat-station-architecture.json';plan=json.loads(planfile.read_text())
    assert plan['station_count']==20 and plan['occupied_ports']==86
    for n,h in plan['source_sha256'].items():assert sha(ROOT/n)==h,n
    scene,meta,templates,pins,bus,changed,removed,variable=current()
    bankrows=[];banktermnames=[];bankcontext={};railnames=[]
    if bankjoint:
        bankfile=OUT/'n01-common-backbone-preflight-r4.json';bankdoc=json.loads(bankfile.read_text())
        gripfile=OUT/'n01-compact-bank-preflight-r2.json';gripdoc=json.loads(gripfile.read_text())
        assert not any(gripdoc[k] for k in ('contacts','grip_conflicts','service_conflicts','errors'))
        grips={r['id']:r for r in gripdoc['grip_allocations']}
        for i,r in enumerate(bankdoc['bend_allocations']):
            a=np.array(r['start_mm']);axis=(np.array(r['end_mm'])-a-r['bend_R_mm']*np.array(r['bend']))/(r['land_mm']+r['bend_R_mm'])
            g=grips[r['id']];assert np.allclose(a,g['start_mm']) and np.allclose(a+9*axis,g['end_mm'])
            assert abs(np.linalg.norm(axis)-1)<1e-6 and abs(g['outer_radius_mm']-2-r['radius_mm'])<1e-6
            terminal=f"Ref_Material_F_{r['holder']}_CP2_{'IN' if g['role'].endswith('.in') else 'OUT'}_0_0"
            assert terminal in scene and scene[terminal].isValid()
            bankrows.append(dict(r,departure_axis=axis.tolist(),terminal_name=terminal,
                terminal_context_key=f'BankTerm{i}_context',fixed_source_grip_mm=9,project_cap_wall_mm=2))
            banktermnames.append(terminal);bankcontext[f'BankTerm{i}_context']=points(scene[terminal])
        assert len(bankrows)==len(set(banktermnames))==24
        railnames=['Ref_Material_P0_SideLeft22_0_0','Ref_Material_P0_SideRight22_0_0']
        bankcontext['BankTerm_context']=np.vstack(list(bankcontext.values()))
        bankcontext['P0Rail_context']=np.vstack([points(scene[n]) for n in railnames])
        for p in (bankfile,gripfile,OUT/'n01-flat20-actual-clamp-kits.json'):
            pins[p.relative_to(ROOT).as_posix()]=sha(p)
    capfile=OUT/'n01-global-case-capacity.json';cap=json.loads(capfile.read_text())
    rawfile=OUT/'n01-shared-space-atlas.json';raw=json.loads(rawfile.read_text());rawbundle=ROOT/raw['bundle']
    originalfield=OUT/'n01-global-current-case-field.npz';assert sha(originalfield)==cap['field_sha256']
    old=np.load(originalfield,allow_pickle=False);axes=[old[k] for k in ('x','y','z')]
    grid=np.stack(np.meshgrid(*axes,indexing='ij'),axis=-1);query=grid.reshape(-1,3)
    macrofile=OUT/'n01-fore-service-macro.json';macro=json.loads(macrofile.read_text())
    forefile=OUT/'n01-fore-topology.json';fore=json.loads(forefile.read_text())
    cases={s['case_name'] for s in plan['stations']};assert cases<=set(scene),(cases-set(scene))
    context=points(scene['Ref_Material_P_SYS_new_0_0'])
    wirecontext=points(scene['W043']) if r2 else None
    protectedfile=OUT/'n01-central-spine-power-plan-r4.json'
    if r2:
        protected=json.loads(protectedfile.read_text());protected=next(r for r in protected['routes'] if r['wire']=='W043')
        assert protected['radius_mm']==1.7 and protected['parts'][-1]['length_mm']>=9
        assert np.allclose(protected['parts'][-1]['end'],[4.55,4,48.5])
        pins[protectedfile.relative_to(ROOT).as_posix()]=sha(protectedfile)
    frame={n for n in scene if frame_variable(n,meta[n])}
    if '--owner-complete' in sys.argv or joint:
        ownerfile=OUT/'n01-flat20-owner-contract.json';contract=json.loads(ownerfile.read_text())
        assert {r['name'] for r in contract['complete_P_SYS_retired_set']}<=frame
        pins[ownerfile.relative_to(ROOT).as_posix()]=sha(ownerfile)
        pins[Path(__file__).with_name('plan_feline_flat_owner_contract.py').relative_to(ROOT).as_posix()]=sha(Path(__file__).with_name('plan_feline_flat_owner_contract.py'))
    retired=cases|frame|{n for n in scene if n.startswith('REV3Station:')}
    retired|={n for n in scene if n.startswith(('End:W067/single/start','End:W068/single/start','End:W066/retained0/end'))}
    retired|={n for n in scene if n.startswith('Ref_Material_current_S1_')}
    if bankjoint:
        bankprefixes={n for n in scene if n.startswith('BankFullPrefix:')}
        assert bankprefixes=={'BankFullPrefix:'+r['id'] for r in bankrows}
        assert all(meta[n].get('kind')=='actual_wire' and meta[n].get('owner')==n for n in bankprefixes)
        retired|=bankprefixes #All24successors preserve q/d/r/first9 and purchased TE ends.
    if modulejoint:
        pigtail={n for n in scene if n.startswith('F_PWM:')}
        assert pigtail=={'F_PWM:'+s for s in ('case','in_first_bend','in_after_turn_grip','out_first_bend','out_after_turn_grip')}
        retired|=pigtail
    originalparts=set(scene)
    for n in retired:scene.pop(n);meta.pop(n)
    overlays=[];s1names=[]
    for doc,groups in ((macro,{'S1Rigid','F_HP','F_TY'}),(fore,{'ForeFHAC'})):
        bundle=ROOT/doc['bundle'];assert sha(bundle)==doc['bundle_sha256'];pins[bundle.relative_to(ROOT).as_posix()]=sha(bundle)
        with zipfile.ZipFile(bundle) as z:
            for r in doc['parts']:
                if r['group'] not in groups or '_S1_ring_' in r['name']:continue
                blob=z.read(r['entry']);assert hashlib.sha256(blob).hexdigest()==r['sha256']
                s=Part.Shape();s.importBrepFromString(blob.decode('utf-8'));assert s.isValid() and s.Solids
                scene[r['name']]=s;meta[r['name']]=dict(kind='wire' if r['wire'] else 'material');overlays.append(r['name'])
                if joint and r['group']=='S1Rigid':s1names.append(r['name'])
    s1context=np.vstack([points(scene[n]) for n in s1names]) if joint else None
    for p in (planfile,capfile,rawfile,rawbundle,originalfield,macrofile,forefile,Path(__file__),
              Path(__file__).with_name('plan_feline_skin_access.py')):pins[p.relative_to(ROOT).as_posix()]=sha(p)
    lo=np.array([-147,-104,-54]);hi=np.array([189,104,118]);dims=hi-lo+1;count=int(np.prod(dims))
    masks={c:np.zeros(count,dtype=bool) for c in ('material','reservation','curve_hold')}
    report=dict(status='RUNNING_FLAT20_SOURCE_FIELD',selected=False,N01_complete=False,physical_pass=False,
        source_sha256=pins,source_parts_fixed=len(scene),old_station_parts_retired=sorted(retired-frame),
        conditional_frame_replacement=sorted(frame|variable),conditional_frame_NOT_approved=True,
        P_SYS_identity_context_preserved=True,S1_ring_clock_and_all8HELU_ENDS_OPEN=True,
        old_operator_outside443_97_ring_wall_root_holds_not_cleared=True,
        full123portions246ends_tools_stock_OPEN=True,voxel_mm=1,surface_sample_budget_mm=2.3,
        voxel_budget_mm=.8662,surface_field_does_not_classify_all_solid_interiors=True,
        material_clouds=[],errors=[],stage='fixed_sources',field=None)
    if r2:report.update(identity_W043_jacket_context_preserved=True,
        replaced_own_reservation='P_SYS_CommonRelief',replacement_must_cover_all4including_W043=True,
        protected_W043_reused_last_straight_mm=protected['parts'][-1]['length_mm'],
        W043_channel_mate_not_foreign_airgap=True)
    if joint:report.update(S1_mating_context_parts=s1names,
        S1_body_control_and_studs_preserved_in_separate_context=True,
        S1_context_must_be_seen_by_all_other_modules_and_wire_jackets=True,
        ring_eye_mate_requires_later_exact_internal_qualification=True)
    if bankjoint:report.update(bank_joint_full_source_ports=bankrows,
        bank_purchased_cases_TE_ends_not_moved_or_deleted=True,
        all24source_first9_must_be_present_in_joint_successors=True,
        bank_new_bends_caps_full_bands_heads_and_roots_NOT_approved=True,
        bank_terminal_context_parts=banktermnames,P0_rail_mating_context_parts=railnames,
        paired_actual_clamp_kit_joint_choices_required=True,
        only_bank_after_first9_directions_reallocated=True)
    if modulejoint:report.update(F_PWM_whole_pigtail_is_joint_variable=True,
        F_PWM_not_FHAC_body_unchanged_0242_100UAT1=True,
        F_PWM_all5_source_shapes_both9_afterturn_grips_required=True,
        F_PWM_source='n01-coupled-clocked-joints.json/F_PWM',
        full_pigtail_conductors_lengths_and_selected_fuse_not_changed=True)
    def save():
        report['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    def gate():
        if time.monotonic()-tick>240:raise TimeoutError('240s bounded whole20 field builder')
    cache={r['source']:r for r in cap['completed_clouds']};save()
    try:
        with zipfile.ZipFile(rawbundle) as z:
            for n,s in scene.items():
                if bankjoint and n in banktermnames+railnames:
                    report['material_clouds'].append(dict(source=n,category='Bank_terminal_mating_context' if n in banktermnames else 'P0_clamp_parent_context',reused=False,samples=len(points(s))))
                    continue
                if joint and n in s1names:
                    report['material_clouds'].append(dict(source=n,category='S1_mating_context',reused=False,samples=len(points(s))))
                    continue
                if r2 and n=='W043':
                    report['material_clouds'].append(dict(source=n,category='identity_wire_context',reused=False,samples=len(wirecontext)))
                    continue
                gate();cached=cache.get(n);reuse=cached and cached['reused_raw_cloud'] and n not in overlays
                if reuse:
                    r=cached['source_record'];blob=z.read(r['entry']);assert hashlib.sha256(blob).hexdigest()==r['sha256']
                    p=np.load(io.BytesIO(blob),allow_pickle=False);category=cached['category']
                else:
                    m=meta[n];category=('curve_hold' if not s.Solids else 'reservation' if
                        'reservation' in m.get('kind','') or m.get('role')=='ScaffoldPlanning' or
                        n.startswith(('StructureReserve:','PiBudget:')) or n=='RetainedMAINCutForeCap' else 'material')
                    if category=='curve_hold':p=np.array([list(v) for e in s.Edges for v in e.discretize(Distance=1)])
                    else:
                        assert n!=bus['name'],'Original valid BUS cloud must be reused, not re-tessellated invalid cache'
                        p=points(s)
                if len(p):
                    p=p[np.all(p>=lo,axis=1)&np.all(p<=hi,axis=1)]
                    q=np.rint(p-lo).astype(np.int32);ids=(q[:,0]*dims[1]+q[:,1])*dims[2]+q[:,2]
                    masks[category][ids]=True
                report['material_clouds'].append(dict(source=n,category=category,reused=bool(reuse),samples=len(p)))
                if len(report['material_clouds'])%100==0:save();print('Flat20 fixed sources',len(report['material_clouds']),flush=True)
        report['stage']='fields';save();fields={}
        for c,o in masks.items():
            gate();ids=np.flatnonzero(o);p=points_from_ids(ids,lo,dims)
            dd=cKDTree(p).query(query,workers=1)[0] if len(ids) else np.full(len(query),1e6)
            fields[c+'_distance']=dd.reshape(grid.shape[:3]).astype(np.float32)
            report.setdefault('unique_voxels',{})[c]=len(ids)
        for c in ('motion36','outer'):fields[c+'_distance']=old[c+'_distance']
        fields.update(service=old['service'],inside=old['inside'],P_SYS_context=context)
        if r2:fields['W043_context']=wirecontext
        if joint:fields['S1_context']=s1context
        if bankjoint:fields.update(bankcontext)
        np.savez_compressed(fieldfile,**dict(zip(('x','y','z'),axes)),**fields)
        report.update(status='FLAT20_SOURCE_FIELD_READY_FOR_JOINT_DOMAINS_NOT_N01',stage='complete',
            field=fieldfile.relative_to(ROOT).as_posix(),field_sha256=sha(fieldfile),
            unchanged36motion_and_ATO_service_reused=True,
            used_single_owner_deletion=False,frame_roots_and_actual_clamps_remain_required=True)
    except Exception as e:report['errors'].append(repr(e));report['status']='PARTIAL_FLAT20_SOURCE_FIELD'
    save();print(json.dumps({k:report[k] for k in ('status','worker_seconds','source_parts_fixed','errors')}),flush=True)


if __name__=='__main__':main()
