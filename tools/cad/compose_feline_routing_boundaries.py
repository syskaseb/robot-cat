"""One current123-portion routing input, not full middles or N01 approval.

Keep electrical pads/accounting ends distinct from physical jacket exits.
Use the END of received prefixes, not a second invented mandatory9mm land.
Explicitly retain unresolved interfaces instead of inheriting old poses.
"""
import copy,json,math,time
from pathlib import Path
import numpy as np
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from compose_feline_shared_layout import station_model


def main():
    tick=time.monotonic();files={k:OUT/n for k,n in dict(ends='n01-shared-end-plan.json',shared='n01-shared54-current.json',
        inline='n01-remaining-inline-body-closure.json',stations='n01-flat-station-architecture.json',
        lower='n01-full-lower-bay-plan-r3.json',source='n01-central-spine-power-plan-r4.json',spec='prefix-allocation.json').items()}
    files['bus']=OUT/'n01-bus-both-plugs-plan-r3.json'
    files['main']=OUT/'n01-supported-fore-layout.json'
    docs={k:json.loads(p.read_text()) for k,p in files.items()};inline=docs['inline'];shared=docs['shared']
    assert inline['status']=='TWO_WHOLE_INLINE_KITS_RECEIVED_ROOTS_CORRIDORS_OPEN' and not inline['errors']
    for doc in (shared,inline):
        for n,h in doc['source_sha256'].items():assert sha(ROOT/n)==h,n
    result=copy.deepcopy(docs['ends']);rows=result['endpoints'];byid={r['id']:r for r in rows}
    def set_exit(row,point,axis,status,basis):
        assert len(point)==len(axis)==3 and abs(np.linalg.norm(axis)-1)<1e-5
        row.update(routing_exit_mm=list(point),routing_exit_axis=list(axis),routing_boundary_status=status,routing_boundary_basis=basis)
    for r in rows:
        q=r.get('jacket_routing_point_mm',r.get('point_mm'));d=r.get('jacket_departure_axis',r.get('departure_axis'))
        if q is not None and d is not None:
            if r.get('jacket_grip9_mm'):
                a,b=r['jacket_grip9_mm'];v=np.asarray(b)-a;v/=np.linalg.norm(v)
                set_exit(r,b,v,'NOMINAL_OR_RECEIVED_GRIP_END_ONLY','No inferred full-middle or other moved source approval')
            else:set_exit(r,q,d,'CURRENT_MOUTH_PREFIX_ALLOCATION_OPEN','Current identity point, not automatically qualified9mm land')
    stations={s['ref']:s for s in docs['stations']['stations']};changed=[]
    for group,choice in shared['chosen'].items():
        if group not in stations:continue
        model=station_model(stations[group],choice)
        for w in model['wires']+model.get('reused_jacket_lands',[]):
            endpoint=w.get('endpoint') or next(p['endpoint'] for p in stations[group]['ports'] if p['wire']==w['wire'])
            match=[r for r in rows if r['endpoint']==endpoint and (r['portion_id']==w['wire'] or r['wire']==w['wire'])]
            assert len(match)==1,(group,endpoint,w['wire']);r=match[0]
            if w.get('not_new_wire_geometry'):
                r['routing_boundary_status']='PROTECTED_COMPLETE_W043_SOURCE_CURVE_REUSED';continue
            if w.get('straight_tip_mm') is not None:q=w['straight_tip_mm'];axis=w['departure_axis']
            elif w.get('after_arc_end_mm') is not None:
                q=w['after_arc_end_mm'];axis=w.get('after_arc_exit_axis',w.get('bend_unit'))
            elif w.get('grip_end_mm') is not None:q=w['grip_end_mm'];axis=w['grip_axis']
            else:
                points=w['points'];q=points[-1];axis=w['bend_unit']
            set_exit(r,q,axis,'RECEIVED_COMPLETE_CURRENT_PREFIX_EXIT','Whole shared54 current constructor, not the historical station fan or grip midpoint');changed.append(r['id'])
    for r in rows:
        if r['pose_status']=='CURRENT_SHARED_BANK_FULL_BEFORE9_TYPED60':
            set_exit(r,r['routing_prefix_exit_mm'],r['routing_prefix_exit_axis'],'RECEIVED_COMPLETE_CURRENT_PREFIX_EXIT','Full9 BEFORE received typed60; no mandatory duplicate9 AFTER')
        elif r['pose_status']=='CURRENT_SHARED_SOURCE_MOUTH_FULL9_AFTER_ARC':
            set_exit(r,r['jacket_grip9_mm'][-1],r['grip_axis'],'RECEIVED_COMPLETE_CURRENT_PREFIX_EXIT','All six whole source fans, full9 after arc')
        elif r['pose_status']=='CURRENT_SHARED_INLINE_JACKET_INTERNAL_ACCOUNTING_SEPARATE':
            a,b=r['jacket_grip9_mm'];axis=np.asarray(b)-a;axis/=np.linalg.norm(axis)
            set_exit(r,b,axis,'RECEIVED_COMPLETE_CURRENT_PREFIX_EXIT','F_PWM whole jacket exits; internal accounting point staysNone')
        elif r['endpoint'].startswith('F_HY.'):
            a,b=r['custom_grip9_mm'];axis=np.asarray(b)-a;axis/=np.linalg.norm(axis)
            set_exit(r,b,axis,'RECEIVED_COMPLETE_CURRENT_PREFIX_EXIT','Current complete F_HY factory/sleeve/custom path; not bare splice as jacket mouth')
        elif r['group']=='BUS':
            p=next(p for p in docs['bus']['routes'] if p['wire']==r['endpoint'])
            assert math.dist(r['point_mm'],p['parts'][0]['start'])<1e-5
            set_exit(r,p['end_mm'],p['end_direction'],'CURRENT_FULL_BUS_DG_R10_AFTER9_PREFIX','Whole current D/G source guide: original jacket mouth is before its arc, not the shared relief centre')
        elif r['group']=='MAIN':
            assert docs['main']['MAIN_whole_changed_unit']['full_first12_jacket_lands_preserved']
            set_exit(r,(np.asarray(r['point_mm'])+12*np.asarray(r['departure_axis'])).tolist(),r['departure_axis'],
                'CURRENT_MAIN_FULL12_AND_COMMON_COMB','Whole MAIN18parts source/current datum and complete12mm jacket lands preserved; no inferred old middle')
    for rec in inline['recipes']:
        match=[r for r in rows if r['endpoint']==rec['endpoint']];assert len(match)==1;r=match[0]
        assert r['point_mm'] is None and r['local_point_mm'] is not None
        r.update(point_mm=rec['point_mm'],departure_axis=rec['departure_axis'],jacket_grip9_mm=rec['factory_grip9_mm'],
            pose_status='CURRENT_RETAINED_FHAC_BOTH_EXITS_FULL_KIT',minimum_R_mm=rec['minimum_R_project_mm'],
            factory_prefix_and_solder_recipe=rec,factory_pose_is_project_not_supplier_guarantee=True)
        set_exit(r,rec['routing_exit_mm'],rec['routing_exit_axis'],'RECEIVED_COMPLETE_CURRENT_PREFIX_EXIT','Both case exits + full factory/sleeve/custom/grips received; custom routing exit is not a new connector')
    # Protected W043 is FHAC source wiring, not the new HELU S1 wire type.
    protected=next(r for r in docs['source']['routes'] if r['wire']=='W043')
    assert protected['radius_mm']==1.7
    for r in rows:
        if r['wire']=='W043':r.update(protected_complete_curve=True,protected_source_radius_mm=1.7,
            protected_source_project_R_mm=min(p['radius_mm'] for p in protected['parts'] if p['kind']=='arc'),
            no_new_HELU_type_or_R_inferred_from_station_port=True)
    factory=[]
    for rec in docs['lower']['factory_routes']:
        ids=result['portions'][rec['wire']+'/factory'];a,b=[byid[n] for n in ids]
        assert math.dist(a['point_mm'],rec['parts'][0]['start'])<1e-4
        assert math.dist(b['point_mm'],rec['parts'][-1]['end'])<1e-4
        factory.append(dict(portion_id=rec['wire']+'/factory',complete_current_curve_reused=True,
            guide_mm=rec['guide_mm'],nominal_usable100_is_project_assumption=True,
            nominal_remaining_before_trim_mm=100-rec['guide_mm'],both_full9grips_preserved=True))
        for r in (a,b):r.update(routing_boundary_status='RECEIVED_WHOLE_FACTORY_CURVE_NO_NEW_MIDDLE',complete_factory_curve_reused=True)
    assert len(factory)==8 and len(rows)==246 and len(result['portions'])==123
    result.update(status='CURRENT_SHARED_ROUTING_BOUNDARIES_COMPLETE_IDENTITIES_CORRIDORS_OPEN',N01_complete=False,
        native_changed=False,physical_pass=False,all_123_portions=list(result['portions']),all246_ids_preserved=True,
        complete_station_prefix_exits_updated=changed,remaining_two_FHAC_full_kit_ends=4,
        received_factory4MTA_curves=factory,
        unresolved_routing_boundaries=[r['id'] for r in rows if r.get('routing_exit_mm') is None],
        prefixes_still_requiring_shared_space=[r['id'] for r in rows if r.get('routing_boundary_status') in ('CURRENT_MOUTH_PREFIX_ALLOCATION_OPEN','NOMINAL_OR_RECEIVED_GRIP_END_ONLY')],
        fixed_total_unchanged=10,current_completed=0,selected=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (*files.values(),Path(__file__))},
        worker_seconds=round(time.monotonic()-tick,3))
    save_json(OUT/'n01-shared-routing-boundaries.json',result)
    print(json.dumps(dict(status=result['status'],seconds=result['worker_seconds'],portions=123,ends=246,
        unresolved=result['unresolved_routing_boundaries'],prefixes_open=len(result['prefixes_still_requiring_shared_space']))),flush=True)


if __name__=='__main__':main()
