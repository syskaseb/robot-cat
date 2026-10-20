"""Fail-fast whole-unit motion BEFORE costly world checks; atomic progress."""
import gzip,json,time
import FreeCAD as A
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from receive_feline_rrp_shared_height import load
from feline_fore_power_pair import SolidQueries,pair_spacing
from feline_solid_distance import bbox_lower_bound
from receive_feline_global_case_candidates import placement
from plan_feline_pi_root_access import profile_gap
from plan_feline_usb_service_bight import outer_margin
from feline_atomic_save import save_json


def material_spacing(a,ar,b,br):
    def typed(n,r):
        if r.get('kind')=='T18I':return n+':tie_budget',dict(r,kind='project_stock_reservation')
        if r.get('kind') in ('PETG','PETG_lid','retained_AUX_component'):
            r={k:v for k,v in r.items() if k not in ('wire','wire_owner')}
        return n,r
    aa,ar=typed(a,ar);bb,br=typed(b,br)
    return pair_spacing(aa,ar,bb,br)


def run(world,fixed,fixed_meta,pins,outer,shared_cell=False,compact=False,resume_policy=False,fore_group=None,plan_stem=None,static_only=False,resume_static=False,local_receipt=None,resume_received_local=False):
    stem=plan_stem or ('n01-AUX-battery-slot-unit' if compact else 'n01-AUX-shared-cell-unit' if shared_cell else 'n01-AUX-whole-vertical-unit')
    tick=time.monotonic();src=OUT/(stem+'-plan.json');p=json.loads(src.read_text());new=load(p)
    dest=OUT/(stem+'-received.json');assert not dest.exists() or resume_policy or resume_static or resume_received_local
    assert all(n in fixed for n in p['retired']) and len(new)==len(p['geometry'])
    for path,h in p['source_sha256'].items():assert sha(ROOT/path)==h,path
    targets={n:s for n,s in fixed.items() if n not in p['retired']};checks={};q=SolidQueries();rows={g['name']:g for g in p['geometry']}
    result=dict(status='RUNNING_WHOLE_AUX_UNIT_MOTION_FIRST',source_sha256={**pins,
        src.relative_to(ROOT).as_posix():sha(src),(ROOT/p['bundle']).relative_to(ROOT).as_posix():sha(ROOT/p['bundle'])},
        completed_motion=[],completed_static=[],failures=[],checks=0,
        unchanged_rigid_local_source_and_board_interfaces_reused=True,whole_fore_print1Solid=p['whole_fore_support_solids']==1,
        whole_fore_print_envelope_mm=p['whole_fore_support_envelope_mm'],sampled_motion36_not_continuous_sweep=True,
        full_N01_assembly_corridors_OPEN=True,N01_complete=False,physical_pass=False,native_changed=False)
    pf=dest.with_suffix('.pairs.json.gz')
    if local_receipt:
        lr=json.loads((ROOT/local_receipt).read_text())
        assert lr['status'] in ('AUX_INBOARD_ALL34_LOCAL_RECEIVED','AUX_UPPER_RIGID33_AND_NEW_ROOT_LOCAL_RECEIVED','AUX_UPPER33_SUBSETS_WITH_FULL_R15_ESCAPES_AND_ROOT_LOCAL_RECEIVED') and not lr['failures']
        assert lr['source_plan_sha256']==sha(src) and lr['source_bundle_sha256']==p['bundle_sha256']
        result['changed_local_gate_reused']=dict(path=local_receipt,sha256=sha(ROOT/local_receipt))
    if resume_received_local:
        previous=json.loads(dest.read_text());priorrows=json.loads(gzip.decompress((ROOT/previous['pair_rows']).read_bytes()))
        assert local_receipt and previous['status']=='WHOLE_AUX_UNIT_NEW_FLOOR_LOCAL_HOLD'
        assert previous['source_sha256']==result['source_sha256']
        assert previous['failures']==['AuxGrip:FloorRoot|local:Ref_Material_AUX409223Screw_0_0']
        result['prior_duplicate_local_policy_check']=dict(rows={k:priorrows[k] for k in previous['failures']},
            superseded_by_complete_current_local34_receipt=True,geometry_unchanged=True)
    if fore_group:
        from feline_source_restraint_plan import joined
        group=set(p['print_group'])|set(fore_group)
        whole=joined([new[n] if n in new else fixed[n] for n in group])
        assert whole.isValid() and len(whole.Solids)==1
        bb=whole.BoundBox;assert max(bb.XLength,bb.YLength,bb.ZLength)<250
        p['print_group']=sorted(group)
        result.update(current_fore_print_members=sorted(group),whole_fore_print1Solid=True,
            whole_fore_print_envelope_mm=[bb.XLength,bb.YLength,bb.ZLength])
    if resume_static:
        previous=json.loads(dest.read_text())
        assert previous['status']=='WHOLE_AUX_STATIC_ONLY_RECEIVED_MOTION36_NOT_EXECUTED' and not previous['failures']
        assert previous['source_sha256']==result['source_sha256']
        checks.update(json.loads(gzip.decompress((ROOT/previous['pair_rows']).read_bytes())))
        result['completed_static']=list(previous['completed_static']);assert len(result['completed_static'])==len(new)
        result['reused_identical_static_checks']=len(checks)
    if resume_policy:
        previous=json.loads(dest.read_text());oldrows=json.loads(gzip.decompress((ROOT/previous['pair_rows']).read_bytes()))
        group_repair=bool(fore_group)
        expected=['AuxGrip:FloorRoot|EndBay:CaseBase:W026_Joint'] if group_repair else ['AuxGrip:XA02:head|local_changed:AuxSource:XA03:jacket']
        assert previous['status']==('WHOLE_AUX_UNIT_CURRENT_STATIC_HOLD' if group_repair else 'WHOLE_AUX_UNIT_LOCAL_CHANGED_HOLD') and previous['failures']==expected
        assert previous['source_sha256'][src.relative_to(ROOT).as_posix()]==sha(src)
        assert oldrows[previous['failures'][0]]['gap_mm']>=.2
        checks.update({k:v for k,v in oldrows.items() if v['ok'] and ('|motion:' in k or '|local_changed:' in k or '|outer' in k or v.get('minimum_mm',-1)>=1.25)})
        if group_repair:
            assert 'AuxGrip:FloorRoot' in p['print_group'] and 'EndBay:CaseBase:W026_Joint' in p['print_group']
            result['completed_motion']=list(previous['completed_motion'])
            assert len(result['completed_motion'])==40
        result['prior_pure_policy_failure']=dict(rows={k:oldrows[k] for k in previous['failures']},worker_seconds=previous['worker_seconds'],geometry_unchanged=True)
    def save():
        pf.write_bytes(gzip.compress(json.dumps(checks,separators=(',',':')).encode(),mtime=0))
        result.update(checks=len(checks),failures=[k for k,v in checks.items() if not v['ok']],
            pair_rows=pf.relative_to(ROOT).as_posix(),pair_rows_sha256=sha(pf),worker_seconds=round(time.monotonic()-tick,3))
        save_json(dest,result)
    def reject(status):result['status']=status;save();print(status,result['failures'],flush=True);return result
    try:
        for n in ([] if local_receipt else p.get('changed_local_actor_names',[])):
            s=new[n]
            for b,t in new.items():
                if b==n or n in p['print_group'] and b in p['print_group']:continue
                same=n.rsplit(':',1)[0]==b.rsplit(':',1)[0]
                own=rows[n].get('wire') and rows[n].get('wire')==rows[b].get('wire')
                limit=0. if same and {n.rsplit(':',1)[-1],b.rsplit(':',1)[-1]} in ({'head','band'},{'pad','band'}) or own and b.endswith(':jacket') else .2 if same or own else material_spacing(n,rows[n],b,rows[b])
                if bbox_lower_bound(s.BoundBox,t.BoundBox)>limit+1e-6:continue
                gap=q.distance(s,t);row=dict(ok=gap>=limit-1e-6,gap_mm=gap,minimum_mm=limit)
                if limit==0:row.update(common_mm3=s.copy().common(t.copy()).Volume,ok=s.copy().common(t.copy()).Volume<1e-5)
                checks[n+'|local_changed:'+b]=row
                if not row['ok']:return reject('WHOLE_AUX_UNIT_LOCAL_CHANGED_HOLD')
        order=sorted(new,key=lambda n:(n not in ('Ref_Material_AUX4092NominalPCB_0_0','AuxGrip:FloorRoot','StructureReserve:AUXBacker'),n))
        for n in ([] if static_only else order):
            s=new[n]
            if n in result['completed_motion']:continue
            for actor in world.motion:
                if bbox_lower_bound(s.BoundBox,A.BoundBox(*actor['bounds'][0],*actor['bounds'][1]))>=1.25:continue
                tf=placement(actor['r'],actor['t']);first=s.copy();first.Placement=tf.inverse()*first.Placement
                gap=q.distance(first,world.rest[actor['name']]);key=n+'|motion:'+actor['name']+':'+str(actor['pose'])
                checks[key]=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25)
                if not checks[key]['ok']:return reject('WHOLE_AUX_UNIT_MOTION_HOLD')
            result['completed_motion'].append(n);save()
        if not static_only:print('WHOLE_AUX_UNIT_MOTION_RECEIVED',len(new),round(time.monotonic()-tick,3),flush=True)
        # New floor joint alone changes the already received local relative
        # geometry. Its positive printed union is proved by the constructor.
        rootname=p.get('root_actor','AuxGrip:FloorRoot');root=new[rootname];group=set(p['print_group'])
        for n,t in ({} if local_receipt else new).items():
            if n in group or bbox_lower_bound(root.BoundBox,t.BoundBox)>=1.25:continue
            gap=q.distance(root,t);checks['AuxGrip:FloorRoot|local:'+n]=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25)
            if gap<1.25-1e-6:return reject('WHOLE_AUX_UNIT_NEW_FLOOR_LOCAL_HOLD')
        for n in order:
            if n in result['completed_static']:continue
            s=new[n];checks[n+'|outer']=outer_margin(s,outer)
            if not checks[n+'|outer']['ok']:return reject('WHOLE_AUX_UNIT_OUTLINE_HOLD')
            for b,t in targets.items():
                if n in group and b in group:continue
                limit=material_spacing(n,rows[n],b,fixed_meta.get(b,{}))
                if bbox_lower_bound(s.BoundBox,t.BoundBox)>=limit:continue
                first=s;other=t
                if b==world.bus['name']:first=s.copy();first.Placement=world.bus['inverse']*first.Placement;other=world.bus['original']
                if not other.Solids:
                    radius=fixed_meta.get(b,{}).get('nominal_profile_radius_mm') or fixed_meta.get(b,{}).get('radius_mm')
                    row=profile_gap(first,other,radius,limit) if radius else dict(ok=False,unreceived_profile=True)
                else:
                    gap=q.distance(first,other);numeric=min(1e-5,max(1e-6,first.getTolerance(1)+other.getTolerance(1)))
                    row=dict(ok=gap>=limit-numeric,gap_mm=gap,minimum_mm=limit,numeric_budget_mm=numeric)
                checks[n+'|'+b]=row
                if not row['ok']:return reject('WHOLE_AUX_UNIT_CURRENT_STATIC_HOLD')
            result['completed_static'].append(n);save()
        result['status']='WHOLE_AUX_STATIC_ONLY_RECEIVED_MOTION36_NOT_EXECUTED' if static_only else 'WHOLE_AUX_BOARD_THREE_SOURCE_GRIPS_ROOT_STATIC36_RECEIVED_N01_OPEN'
        result['motion_gate_executed']=not static_only
        result['sampled_motion36_not_continuous_sweep']=not static_only
        save()
        print(result['status'],result['worker_seconds'],len(checks),flush=True);return result
    except BaseException:
        result['status']='OWN_WHOLE_AUX_UNIT_PROGRESS_SAVED_NOT_ACCEPTED';save();raise
