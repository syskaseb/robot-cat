"""Current source/MTA overlay over the immutable246-end register.

Read only received BReps, no new routes/supports and no N01 point. In
particular a source wire cap does NOT qualify the still-held shared shelf.
"""
import json,sys,time,zipfile,hashlib
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT,BASE
from receive_feline_existing_lower_caps import current as parent
from compose_feline_integrated_boundaries import apply_updates
from compose_feline_output_boundaries import cap_at
from receive_feline_rrp_shared_height import load
from receive_feline_access_stack_motion import shapes
from feline_source_saddles import segment
from feline_atomic_save import save_json


def current():
    base,rows,files=parent();f=OUT/'n01-current-source-MTA-boundary-overlay.json';r=json.loads(f.read_text())
    for p,h in r['source_sha256'].items():assert sha(ROOT/p)==h,p
    return base,apply_updates(rows,r['updates']),(*files,f)


def receive_existing_pca():
    tick=time.monotonic();dest=OUT/'n01-current-source-MTA-boundary-overlay.json';r=json.loads(dest.read_text())
    assert not r['N01_complete'] and not r['native_changed']
    if len(r['updates'])==25:print('CURRENT25_BOUNDARIES_ALREADY_RECEIVED');return
    assert len(r['updates'])==18
    own=Path(__file__).relative_to(ROOT).as_posix()
    for p,h in r['source_sha256'].items():
        if p!=own:assert sha(ROOT/p)==h,p
    old_sha=sha(dest);old_code=r['source_sha256'][own]
    pf=OUT/'n01-pwm-board-shelf.json';pwm=json.loads(pf.read_text());assert not pwm['failures'] and not pwm['errors']
    assert len(pwm['completed_parts'])==38 and not pwm['internal_assembly']['failures']
    archive=ROOT/pwm['bundle'];assert sha(archive)==pwm['bundle_sha256']
    with zipfile.ZipFile(archive) as z:
        shapes={}
        for row in pwm['parts']:
            if not row['name'].startswith('ShelfPWM:jacket:'):continue
            raw=z.read(row['entry']);assert hashlib.sha256(raw).hexdigest()==row['sha256']
            s=Part.Shape();s.importBrepFromString(raw.decode());shapes[row['name']]=s
    _,rows,_=parent();bywire={e['wire']:e for e in rows if e['endpoint'].startswith('PCA.') and e['routing_boundary_status']=='NOMINAL_OR_RECEIVED_GRIP_END_ONLY'}
    assert len(bywire)==7
    for v in pwm['source_endpoints']:
        e=bywire[v['wire']];owner='ShelfPWM:jacket:'+v['wire'];s=shapes[owner]
        q=A.Vector(*v['grip_end_mm']);p=A.Vector(*v['grip_start_mm']);d=(q-p)/9
        assert abs((q-p).Length-9)<1e-6
        cap=cap_at(s,list(q),list(d),v['jacket_radius_mm'])
        update=dict(jacket_routing_point_mm=v['jacket_mouth_world_mm'],jacket_grip9_mm=[list(p),list(q)],
            grip_axis=list(d),grip_length_mm=9,routing_exit_mm=list(q),routing_exit_axis=list(d),
            routing_boundary_status='CURRENT_EXISTING_PCA_WHOLE_PREFIX_CAP_RECEIVED',prefix_geometry_owner=owner,
            support_owner='ShelfPWM:'+('XScomb' if v['wire'].startswith('XS') else 'XLcomb')+':lower',
            actual_saved_cap_radius_mm=v['jacket_radius_mm'],minimum_R_mm=v['R_mm'],
            source_prefix_length_mm=s.Volume/(3.141592653589793*v['jacket_radius_mm']**2),
            full_middle_route_accepted=False,new_wire_geometry_built=False,nominal_source_solder_fit_still_phase2=True)
        assert e['point_mm'] is None # Logical solder seam is NOT a new connector.
        r['updates'][e['id']]=update;r['actual_cap_proofs'][e['id']]=cap
    r.update(status='CURRENT25_SOURCE_MTA_PCA_CAPS_COMPOSED_NOT_FULL_N01',
        prior18_cap_receipt_sha256=old_sha,prior18_producer_code_sha256=old_code,
        prior18_preserved_in_git_commit='cf4ce7b7',prior18_exact_queries_not_repeated=True,
        PCA_existing_caps_received=7,PCA_new_wire_or_support_geometry_built=False,
        latest_extension_worker_seconds=round(time.monotonic()-tick,3))
    for p in (pf,archive,Path(__file__)):r['source_sha256'][p.relative_to(ROOT).as_posix()]=sha(p)
    save_json(dest,r);print(r['status'],r['latest_extension_worker_seconds'],flush=True)


def allocate_u1_local_sources():
    """Rigidly transfer selected local E1 ends, never the old whole middles.

    These are source geometry allocations, NOT shared-world/root approval.
    Pad identities stay put; the jacket mouth is a SEPARATE datum.
    """
    from plan_feline_n01_shared import pipe
    from receive_feline_global_case_candidates import placement
    import numpy as np
    tick=time.monotonic();dest=OUT/'n01-current-source-MTA-boundary-overlay.json';r=json.loads(dest.read_text())
    assert not r['N01_complete']
    if r.get('U1_local_prefix_source_allocations'):print('U1_LOCAL_ALLOCATIONS_ALREADY_RECORDED');return
    assert len(r['updates'])==25
    own=Path(__file__).relative_to(ROOT).as_posix()
    for p,h in r['source_sha256'].items():
        if p!=own:assert sha(ROOT/p)==h,p
    previous=sha(dest);cf=BASE/'body-harness-checkpoint/u1-common-wiring-plan.json';c=json.loads(cf.read_text())
    mf=OUT/'n01-module-plan-r5.json';module=next(g for g in json.loads(mf.read_text())['groups'] if g['role']=='PWM1608_U1')
    tf=placement(np.array(module['rotation_rows']),module['translation_mm']);_,rows,_=parent();byid={e['id']:e for e in rows}
    transfers=[('XL01','b'),('XL10','b'),('XL07','b'),('XL02','a'),('XL08','b'),('XL09','a'),('XS11','b'),('XS21','b'),('XS31','b')]
    bundle=OUT/'n01-U1-inherited-local-source-budgets.breps.zip';geometry=[];allocations={}
    with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
        for wire,side in transfers:
            src=c['routes'][wire];end=src['ends'][side];eid=wire+'/extra/'+('start' if side=='a' else 'end');e=byid[eid]
            pad=tf.multVec(A.Vector(*src['source'][side]['world_mm']))
            assert (pad-A.Vector(*e['point_mm'])).Length<1e-5,(eid,'Do not invent/move selected carrier pad')
            def transfer(parts):
                return [dict(p,**{k:list(tf.multVec(A.Vector(*p[k]))) for k in ('start','mid','end') if k in p}) for p in parts]
            parts=transfer(end['parts']);s=pipe(parts,end['radius']);d=tf.Rotation.multVec(A.Vector(*end['end_axis']))
            q=tf.multVec(A.Vector(*end['end_mm']));last=segment(parts[-1])
            assert last.Length>=9-1e-6 and (last.valueAt(last.LastParameter)-q).Length<1e-5
            proof=cap_at(s,list(q),list(d),end['radius']);name='U1Local:'+wire+':jacket'
            records=[(name,s)]
            bare=c['bare'][wire+'/'+side];bp=transfer(bare['parts']);bs=pipe(bp,bare['radius']);records.append(('U1Local:'+wire+':bare',bs))
            assert (A.Vector(*bp[-1]['end'])-A.Vector(*parts[0]['start'])).Length<1e-5,'Bare/jacket source seam changed'
            for n,shape in records:
                raw=shape.exportBrepToString().encode();entry=str(len(geometry))+'.brep';z.writestr(entry,raw)
                geometry.append(dict(name=n,wire=wire,kind='bare' if n.endswith(':bare') else 'wire',entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
            allocations[eid]=dict(pad_identity=e['endpoint'],named_physical_source_terminal=end['physical_terminal'],
                pad_world_mm=list(pad),jacket_mouth_world_mm=parts[0]['start'],parts=parts,radius_mm=end['radius'],
                existing_source_solder_instruction=bare['instruction'],bare_parts=bp,bare_radius_mm=bare['radius'],
                source_moved_rigidly_once=True,external_U1_pinout_NOT_inferred=True)
            r['updates'][eid]=dict(jacket_routing_point_mm=parts[0]['start'],
                routing_exit_mm=list(q),routing_exit_axis=list(d),jacket_grip9_mm=[list(q-d*9),list(q)],
                grip_axis=list(d),grip_length_mm=9,prefix_geometry_owner=name,actual_saved_cap_radius_mm=end['radius'],
                source_prefix_length_mm=sum(segment(p).Length for p in parts),
                routing_boundary_status='INHERITED_U1_LOCAL_PREFIX_ALLOCATED_WORLD_AND_GRIP_ROOT_OPEN',
                full_middle_route_accepted=False,independent_relief_root_and_shared_neighbors_NOT_received=True,
                physical_pad_NOT_used_as_jacket_mouth=True,nominal_source_solder_fit_still_phase2=True)
            r['actual_cap_proofs'][eid]=proof
    assert len(allocations)==9 and len(geometry)==18
    r.update(status='CURRENT34_BOUNDARIES_U1_LOCAL_ALLOCATIONS_WORLD_OPEN',prior25_receipt_sha256=previous,
        prior25_current_commit='cf4ce7b7_plus_existing_PCA_receipt',U1_local_prefix_source_allocations=allocations,
        U1_local_geometry=geometry,U1_local_bundle=bundle.relative_to(ROOT).as_posix(),U1_local_bundle_sha256=sha(bundle),
        latest_extension_worker_seconds=round(time.monotonic()-tick,3))
    for p in (cf,mf,bundle,Path(__file__)):r['source_sha256'][p.relative_to(ROOT).as_posix()]=sha(p)
    save_json(dest,r);print(r['status'],len(allocations),r['latest_extension_worker_seconds'],flush=True)


def main():
    tick=time.monotonic();dest=OUT/'n01-current-source-MTA-boundary-overlay.json'
    assert not dest.exists(),'Receive existing overlay, do not regenerate'
    base,rows,files=parent();index={e['id']:e for e in rows}
    sf=OUT/'n01-F0-access-stack.json';src=json.loads(sf.read_text());assert not src['failures']
    wf=OUT/'n01-F0-access-stack-motion.json';motion=json.loads(wf.read_text());assert not motion['failures'] and len(motion['completed_motion'])==7
    mf=OUT/'n01-MTA-low-stop-cradles.json';m=json.loads(mf.read_text());assert not m['failures']
    mwf=OUT/'n01-MTA-low-stop-cradles-scene.json';mw=json.loads(mwf.read_text())
    assert not mw['failures'] and len(mw['completed_static'])==len(mw['completed_motion'])==72
    assert mw['source_sha256'][mf.relative_to(ROOT).as_posix()]==sha(mf)
    actors={**shapes(src),**load(m)};updates={};proofs={}
    def put(eid,owner,parts,radius,whole,grip=None):
        assert eid in index;side=eid.rsplit('/',1)[1];first,last=segment(parts[0]),segment(parts[-1])
        p=first.valueAt(first.FirstParameter);q=last.valueAt(last.LastParameter)
        d=first.tangentAt(first.FirstParameter);t=last.tangentAt(last.LastParameter)
        mouth=p if side=='start' else q;departure=d if side=='start' else -t
        cap=cap_at(actors[owner],list(mouth),list(-d if side=='start' else t),radius)
        if not whole:cap_at(actors[owner],list(q),list(t),radius)
        updates[eid]=dict(point_mm=list(mouth),departure_axis=list(departure),
            routing_exit_mm=list(mouth if whole else q),routing_exit_axis=list(departure if whole else t),
            prefix_geometry_owner=owner,source_prefix_length_mm=actors[owner].Volume/(3.141592653589793*radius**2),
            actual_saved_cap_radius_mm=radius,grip_length_mm=9,
            routing_boundary_status='CURRENT_RECEIVED_COMPLETE_FACTORY_SOURCE' if whole else 'CURRENT_RECEIVED_SOURCE_OR_MTA_PREFIX_EXIT',
            full_middle_route_accepted=whole,nominal_supplier_fit_still_phase2=True,
            source_restraint_shared_shelf_NOT_accepted=True)
        if grip:updates[eid]['support_owner']=grip
        proofs[eid]=cap
    for w,r in m['factory_recipes'].items():
        for side in ('start','end'):put(w+'/factory/'+side,'Factory:'+w,r['parts'],2.1,True)
        c=m['recipes']['CustomPrefix:'+w]
        put(w+'/custom/start','CustomPrefix:'+w,c['parts'],2.1,False,'ArcGrip:'+w+':pad')
    for stem,owner,whole,radius,grip in (
        ('W075/retained0','W075_factory',True,1.55,'SourceGrip:W075:pad'),
        ('W076/retained0','W076_factory',True,1.55,'SourceGrip:F0OUT:pad'),
        ('W001/retained0','W001_ground_prefix',False,1.55,'SourceGrip:GROUND:pad'),
        ('W076/retained1','W076_custom_prefix',False,2.1,'SourceGrip:POSTOUT:pad')):
        for side in (('start','end') if whole else ('start',)):
            put(stem+'/'+side,owner,src['recipes'][owner]['parts'],radius,whole,grip)
    resolved=apply_updates(rows,updates)
    assert len(resolved)==246 and len(base['portions'])==123 and len(updates)==18
    assert [e['id'] for e in resolved]==[e['id'] for e in rows]
    sources=(*files,sf,wf,ROOT/src['bundle'],mf,mwf,ROOT/m['bundle'],Path(__file__))
    r=dict(status='CURRENT_SOURCE_AND_MTA_CAPS_COMPOSED_NOT_FULL_N01',updates=updates,
        actual_cap_proofs=proofs,all123_identities_preserved=True,all246_end_ids_preserved=True,
        logical_None_boundaries_not_invented=True,selected_SKUs_changed=False,native_changed=False,
        support_assembly_corridor_capacity_OPEN=True,N01_complete=False,physical_pass=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in sources},worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,r);print(r['status'],len(updates),r['worker_seconds'],flush=True)


if __name__=='__main__':
    if '--allocate-u1-locals' in sys.argv:allocate_u1_local_sources()
    elif '--receive-existing-pca' in sys.argv:receive_existing_pca()
    else:main()
