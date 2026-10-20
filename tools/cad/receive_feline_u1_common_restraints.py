"""Receive the complete U1 source-side kit, not one saddle at a time."""
import gzip,hashlib,json,time
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT,BASE
from receive_feline_rrp_shared_height import load
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from plan_feline_pi_root_access import profile_gap
from plan_feline_usb_service_bight import outer_margin
from receive_feline_global_case_candidates import placement
from feline_atomic_save import save_json


def minimum(a,b,meta,plan,groups,own_module):
    ar=meta.get(a,{});br=meta.get(b,{})
    if any(a in g and b in g for g in groups.values()):return None,'same proved whole print'
    if b in plan['intended_insulation_mates'].get(a,[]) or a in plan['intended_insulation_mates'].get(b,[]):return 0.,'named9mm jacket seat or snug band'
    for grip,source in ((a,b),(b,a)):
        if source.endswith(':bare') and source.removesuffix(':bare')+':jacket' in plan['intended_insulation_mates'].get(grip,[]):
            return .2,'same grip adjacent to its OWN formed bare/jacket transition, not a foreign conductor'
    if a.rsplit(':',1)[0]==b.rsplit(':',1)[0]:
        pair={a.rsplit(':',1)[-1],b.rsplit(':',1)[-1]}
        if pair in ({'band','head'},{'band','pad'}):return 0.,'same T18I or flat seat boundary'
        if pair=={'head','pad'}:return .2,'same grip, head separate from pad'
    if ar.get('kind')==br.get('kind')=='T18I':return .2,'separate soft nylon stock envelopes, full heads retained'
    if ar.get('wire') and ar.get('wire')==br.get('wire'):return 0.,'same selected jacket/bare seam'
    if b=='Ref_Material_PWM1608NominalPCB_0_0':
        if a.startswith('U1Relief:Stand'):return 0.,'actual PCB underside bearing'
        if ar.get('kind')=='bare':return 0.,'named through-hole in nominal PCB, delivered fit open'
    if b in own_module:return .2,'intrinsic U1 module fit only, not electrical qualification'
    if ar.get('kind')=='wire' and br.get('kind') in ('wire','proposal_wire','actual_wire','curve_profile_reservation'):return .2,'insulated jackets'
    return 1.25,None


def run(world,fixed,meta,pins,docs,mta,source_doc,upper_sources,root_clearance=False,resume_policy=False):
    tick=time.monotonic();sf=OUT/('n01-U1-common-restraints-rooted-plan.json' if root_clearance else 'n01-U1-common-restraints-plan.json');plan=json.loads(sf.read_text());new=load(plan)
    for p,h in plan['source_sha256'].items():assert sha(ROOT/p)==h,p
    carrierfile=BASE/'body-harness-checkpoint/u1-socket-carrier-plan.json';carrier=json.loads(carrierfile.read_text())
    drills=[v for g in carrier['board']['groups'] for v in g['pads']]
    assert len(plan['lands'])==5 and len(new)==26
    dest=OUT/('n01-U1-common-restraints-rooted-received.json' if root_clearance else 'n01-U1-common-restraints-received.json')
    previous_policy=None
    if dest.exists():
        assert resume_policy,'Receive the existing worker before restarting'
        old_policy=json.loads(dest.read_text());assert old_policy['status']=='U1_WHOLE_KIT_LOCAL_HOLD' and not old_policy['whole_prints']
        old_rows=json.loads(gzip.decompress((ROOT/old_policy['pair_rows']).read_bytes()))
        expected={f'U1Relief:{g}:head|U1Relief:{g}:band' for g in ('XS13','XS23','XS33','E2pair')}
        assert set(old_policy['failures'])==expected and old_policy['source_sha256'][sf.relative_to(ROOT).as_posix()]==sha(sf)
        previous_policy=dict(status=old_policy['status'],worker_seconds=old_policy['worker_seconds'],wrong_policy_rows={k:old_rows[k] for k in expected},
                             all_geometry_unchanged=True,positive_local_pairs_reused=True)
    source_parts=load(source_doc);scene={**fixed,**source_parts,**upper_sources,**new}
    nm={g['name']:g for g in plan['geometry']};fm={**meta,**nm}
    fm.update({n:dict(kind='bare' if n.endswith(':bare') else 'wire',wire=n.split(':')[1]) for n in upper_sources})
    own_module={n for n in fixed if n.startswith(('Ref_Material_U1_','Ref_Material_PWM1608'))}
    groups=dict(fore=set(mta['print_groups']['LowerBay:ForePanel'])|set(plan['print_groups']['fore'])|{'StructureReserve:U1CarrierArm0','StructureReserve:U1CarrierRoot0'},
                rear=set(json.loads((OUT/'n01-source-restraints-whole-r5.json').read_text())['print_groups']['lower'])|set(plan['print_groups']['rear'])|{'StructureReserve:U1CarrierArm1','StructureReserve:U1CarrierRoot1'})
    assert not groups['fore']&groups['rear']
    result=dict(status='RUNNING_WHOLE_U1_RESTRAINT_GATE',source_sha256={**pins,**{p.relative_to(ROOT).as_posix():sha(p) for p in
        (sf,ROOT/plan['bundle'],OUT/'n01-source-restraints-head-case-bypass.json',ROOT/source_doc['bundle'],carrierfile,Path(__file__))}},
        completed_static=[],completed_motion=[],whole_prints={},failures=[],sampled_motion_not_sweep=True,
        all_five_lands=True,remaining_common123_and_assembly_OPEN=True,N01_complete=False,native_changed=False,physical_pass=False)
    checks={};query=SolidQueries();pf=dest.with_suffix('.pairs.json.gz')
    if previous_policy:
        checks.update({k:v for k,v in old_rows.items() if v['ok']})
        result['prior_pure_policy_failure']=previous_policy
    oldfile=OUT/'n01-U1-remaining-five-coupled-plan-neighbors.json';old=json.loads(oldfile.read_text())
    for p,h in pins.items():assert old['source_sha256'][p]==h,p
    unchanged={n for n in new if n.startswith('U1Five:') and (n.endswith(':bare') or n.split(':')[1] in ('XS13','XS33'))}
    result['reused_unchanged_source_queries']=[];result['nominal_named_pad_holes']={}
    def save():
        pf.write_bytes(gzip.compress(json.dumps(checks,separators=(',',':')).encode(),mtime=0))
        result.update(checks=len(checks),failures=[k for k,v in checks.items() if not v['ok']],worker_seconds=round(time.monotonic()-tick,3),pair_rows=pf.relative_to(ROOT).as_posix(),pair_rows_sha256=sha(pf))
        save_json(dest,result)
    # Cheap entire own-kit preflight, BEFORE heavy whole-print or world work.
    for n,s in new.items():
        for b,t in new.items():
            if b>=n:continue
            if n+'|'+b in checks:continue
            limit,mate=minimum(n,b,fm,plan,groups,own_module)
            if limit is None or bbox_lower_bound(s.BoundBox,t.BoundBox)>limit+1e-6:continue
            gap=query.distance(s,t);row=dict(ok=gap>=limit-1e-6,gap_mm=gap,minimum_mm=limit,intended_mate=mate)
            if limit==0:row['common_mm3']=s.copy().common(t.copy()).Volume;row['ok'] &= row['common_mm3']<1e-5
            checks[n+'|'+b]=row
    save()
    if result['failures']:result['status']='U1_WHOLE_KIT_LOCAL_HOLD';save();return result
    for group,members in groups.items():
        assert all(n in scene for n in members),sorted(members-set(scene))
        names=sorted(members);whole=scene[names[0]].copy().multiFuse([scene[n].copy() for n in names[1:]])
        b=whole.BoundBox;size=[b.XLength,b.YLength,b.ZLength]
        result['whole_prints'][group]=dict(valid=whole.isValid(),solids=len(whole.Solids),envelope_mm=size,members=names)
        checks['wholeprint:'+group]=dict(ok=whole.isValid() and len(whole.Solids)==1 and max(size)<250)
        save()
        if not checks['wholeprint:'+group]['ok']:result['status']='U1_SHARED_PRINT_JOINT_HOLD';save();return result
    bounds={n:s.BoundBox for n,s in scene.items()}
    for n,s in new.items():
        checks[n+'|outer']=outer_margin(s,docs['outer'])
        for b,t in scene.items():
            if b==n or b in new and b>=n:continue
            key=n+'|'+b
            if key in checks:continue
            limit,mate=minimum(n,b,fm,plan,groups,own_module)
            if limit is None or bbox_lower_bound(s.BoundBox,bounds[b])>limit+1e-6:continue
            if n in unchanged and b not in new and b!='Ref_Material_PWM1608NominalPCB_0_0' and key in old['checks']:
                row=old['checks'][key]
                if row['ok'] and row.get('minimum_mm',-1)>=limit:
                    checks[key]=row;result['reused_unchanged_source_queries'].append(key);continue
            a=s;other=t
            if b==world.bus['name']:a=s.copy();a.Placement=docs['inverse']*a.Placement;other=world.bus['original']
            if b=='Ref_Material_PWM1608NominalPCB_0_0' and nm[n].get('kind')=='bare':
                # Use the documented1.2mm PermaProto pad drill locally, not
                # a waiver for a conductor crossing an unperforated PCB box.
                wire=nm[n]['wire'];spec=next(v for v in plan['specs'].values() if v['wire']==wire)
                x,y,_=spec['pad_world_mm'];bb=other.BoundBox;c=bb.Center
                matches=[v for v in drills if abs(c.x+float(v['x'])-x)<1e-5 and abs(c.y+float(v['y'])-y)<1e-5]
                assert len(matches)==1 and abs(float(matches[0]['drill'])-1.2)<1e-6,(wire,'No documented carrier drill at named pad')
                hole=Part.makeCylinder(float(matches[0]['drill'])/2,bb.ZLength+.2,A.Vector(x,y,bb.ZMin-.1))
                other=other.copy().cut(hole);assert other.isValid()
                result['nominal_named_pad_holes'][wire]=dict(centre_xy_mm=[x,y],drill_mm=1.2,terminal=spec['selected_carrier_pad_identity'],delivered_fit_open=True)
            if not other.Solids:
                md=fm.get(b,{});radius=md.get('nominal_profile_radius_mm') or md.get('radius_mm')
                row=profile_gap(a,other,radius,limit) if radius else dict(ok=False,unreceived_curve_profile=True)
            else:
                gap=query.distance(a,other);row=dict(ok=gap>=limit-1e-6,gap_mm=gap,minimum_mm=limit,intended_mate=mate)
                if limit==0:row['common_mm3']=a.copy().common(other.copy()).Volume;row['ok'] &= row['common_mm3']<1e-5
            checks[key]=row
            if not row['ok']:print('U1_SHARED_WITNESS',key,row,flush=True)
        result['completed_static'].append(n);save()
    if result['failures']:result['status']='U1_SHARED_STATIC_HOLD';save();return result
    moving=[(p,A.BoundBox(*p['bounds'][0],*p['bounds'][1])) for p in world.motion]
    for n,s in new.items():
        for p,b in moving:
            if bbox_lower_bound(s.BoundBox,b)>=1.25:continue
            tf=placement(p['r'],p['t']);q=s.copy();q.Placement=tf.inverse()*q.Placement
            gap=query.distance(q,world.rest[p['name']]);key=n+'|motion:'+p['name']+':'+str(p['pose'])
            checks[key]=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25)
            if gap<1.25-1e-6:result['status']='U1_SHARED_MOTION_HOLD';save();return result
        result['completed_motion'].append(n);save()
    result['status']='U1_FIVE_COMMON_RESTRAINTS_STATIC36_RECEIVED_FULL123_ASSEMBLY_OPEN';save()
    print(result['status'],len(checks),result['worker_seconds'],flush=True);return result
