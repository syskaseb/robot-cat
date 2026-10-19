"""Whole fore power pair BEFORE another detailed fan or mount family.

S0 lower fore compartment, S1 retained fore-outboard, PWM above. Purchased
parts remain rigid and unchanged. Case-only gate cannot award N01: two S0
mouths, six source fan roots, tools, other47 and true contour remain explicit.
"""
import hashlib
import json
import math
import sys
import time
import zipfile
from pathlib import Path
import FreeCAD as A
import Part
import numpy as np

from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from plan_feline_central_pi_wedge import packed
from feline_candidate_collision_scene import Scene
from feline_pwm_board_shelf import build,source_inputs
from feline_solid_distance import bbox_lower_bound
from receive_feline_global_case_candidates import placement
from receive_feline_s1_source_datums import mouth_receipts
from plan_feline_front_bulkhead_architecture import tube
from plan_feline_front_service_split import line_tube


class SolidQueries:
    """Validate each unchanged actual solid once, never once per pair.

    Same containment-aware child-solid semantics as feline_solid_distance.
    Boolean diagnostics use copies, so cached actual sources stay unchanged.
    """
    def __init__(self):self.valid={}
    def children(self,s):
        key=(id(s),tuple(s.Placement.toMatrix().A))
        if key not in self.valid:
            assert s.isValid() and s.Solids,'Invalid source is not clearance'
            children=s.Solids
            assert all(x.isValid() for x in children)
            self.valid[key]=(s,children)
        return self.valid[key][1]
    def distance(self,a,b):
        aa=self.children(a);bb=self.children(b);best=math.inf
        for x in aa:
            for y in bb:
                if bbox_lower_bound(x.BoundBox,y.BoundBox)>=best:continue
                best=min(best,float(x.distToShape(y)[0]))
                if best<1e-9:return 0.
        return best


def pair_spacing(a,ar,b,br):
    """Mechanical margin by material/interface, not an electrical rating.

    Fully insulated flexible jackets and soft nylon tie stock use the same
    .2mm no-penetration reserve as jacket/jacket. Rigid supports, purchased
    modules and exposed bare conductors keep1.25mm. Insulation geometry is
    not thinned and power/thermal/dielectric qualification is not claimed.
    """
    def jacket(n,r):
        if r.get('kind')=='bare' or ':bare' in n:return False
        return r.get('kind') in ('wire','proposal_wire','actual_wire','insulation_reservation') or bool(r.get('wire_owner')) or bool(r.get('wire')) or n.startswith(('End:','ShelfPWM:jacket:','PiGPIO:','PiPower:','PiUSBData')) or n in ('W043','W077','W078')
    def tie(n,r):
        return r.get('kind') in ('tie_reservation','project_stock_reservation') and ('Tie' in n or ':band_budget' in n or ':head_budget' in n or 'tie_budget' in n)
    wa,wb=jacket(a,ar),jacket(b,br)
    return .2 if (wa and wb) or (wa and tie(b,br)) or (wb and tie(a,ar)) else 1.25


def actual_s0_mouths(parts,ends,transform):
    """Find real saved bore/end planes, not a transferred guide direction."""
    result=[]
    for e in ends:
        side='IN' if e['role']=='S0.in' else 'OUT'
        name='Ref_Material_S0_ring_'+side+'_0_0';s=parts[name]
        hint=A.Vector(*e['point_mm']);stud=parts['Ref_Material_S0_stud_'+side+'_0_0'].BoundBox.Center
        axes=[]
        for f in s.Faces:
            surface=f.Surface
            if type(surface).__name__!='Cylinder':continue
            d=surface.Axis;d.normalize();c=surface.Center
            if abs(d.y)>.1:continue
            # A re-clocked barrel does not inherit the old guide's axis.
            # Actual non-stud cylindrical faces and their outward axial
            # centre determine the source bore; no inferred manufacturer pad.
            if d.dot(f.CenterOfMass-stud)<0:d=-d
            axes.append((d,c))
        assert axes,('No actual S0 barrel axis',name)
        d,c=axes[0];planes=[]
        for f in s.Faces:
            if type(f.Surface).__name__!='Plane':continue
            if abs(f.normalAt(0,0).dot(d))<1-1e-6:continue
            t=d.dot(f.CenterOfMass-c);planes.append((t,c+d*t))
        assert planes
        q=max(planes,key=lambda x:x[0])[1]
        matches,_=mouth_receipts({name:s},q,d);assert matches
        result.append(dict(endpoint=e['id'],source_role=e['role'],source_ring=name,
            old_guide_point_mm=e['point_mm'],old_guide_departure=e['departure_axis'],actual_source_point_mm=list(q),
            actual_departure=list(d),new_point_mm=list(transform.multVec(q)),new_departure=list(transform.Rotation.multVec(d)),
            saved_nominal_coaxial_end_plane_receipts=matches,
            method='Farthest actual annular plane on saved coaxial barrel; direction away from selected stud',
            supplier_or_delivered_crimp_fit_verified=False))
    return result


def aux_front_packet(world,s1):
    """Complete selected AUX case plus BOTH full nominal100mm factory tails.

    One whole swap into the vacated S0 upper bay. Factory length is the
    inherited provisional project value, never promoted to delivered data.
    """
    name='Ref_Material_F_AUX_candidate_case_0_0';original=world.parts[name]
    rot=A.Rotation(A.Vector(0,0,1),90);local=original.copy();local.Placement=A.Placement(A.Vector(),rot)*local.Placement
    frame=world.parts['Ref_Material_P0_FrameFront20_0_0'].optimalBoundingBox()
    z=s1['Ref_Material_current_S1_control_CP2_0_0'].optimalBoundingBox().ZMax+1.25+local.optimalBoundingBox().ZLength/2
    centre=A.Vector(frame.XMin-1.25-local.optimalBoundingBox().XLength/2,0,z)
    tf=A.Placement(centre-rot.multVec(original.BoundBox.Center),rot)
    case=original.copy();case.Placement=tf*case.Placement
    parts={name:case};facts=[]
    contractpath=OUT/'n01-all-extra-interface-contract.json';contract=json.loads(contractpath.read_text())
    _,fore,rows=packed(OUT/'n01-fore-topology.json')
    foretop=max(s.optimalBoundingBox().ZMax for n,s in fore.items() if rows[n]['group']=='ForeFHAC')
    R=12.4;first=9.;length=100.
    rise=math.ceil(max(0,(foretop+1.25+2.4-z)/(2*R))*10)/10
    assert rise<1
    for sec in contract['sections']:
        for e in sec['ends']:
            if e['group']!='F_AUX':continue
            q=tf.multVec(A.Vector(*e['point_mm']));d=rot.multVec(A.Vector(*e['departure_axis']))
            assert abs(abs(d.x)-1)<1e-6
            bend=A.Vector(0,math.sqrt(1-rise**2),rise) if d.x>0 else A.Vector(0,0,-1)
            a=q+d*first;mid=a+d*R+bend*R;end=a+bend*(2*R)
            remaining=length-first-math.pi*R;tip=end-d*remaining
            spine=Part.Wire([Part.makeLine(q,a),Part.Arc(a,mid,end).toShape(),Part.makeLine(end,tip)])
            assert abs(spine.Length-length)<1e-5
            prefix='AUXFront:'+e['endpoint']
            parts[prefix+':factory100']=tube(spine,2)
            parts[prefix+':joint_budget']=line_tube(list(tip+d*8),list(tip-d*12),2.4)
            parts[prefix+':custom21']=line_tube(list(tip-d*12),list(tip-d*21),2.1)
            facts.append(dict(wire=sec['wire'],endpoint=e['endpoint'],point_mm=list(q),departure_axis=list(d),
                factory_length_project_mm=spine.Length,factory100_is_provisional=True,
                first_straight_mm=first,R_mm=R,bend_unit=list(bend),sweep_degrees=180,
                factory_end_mm=list(tip),custom_full9_grip_land_mm=[list(tip-d*12),list(tip-d*21)],
                case_and_full_factory_wires_both_sides_included=True,custom_radius2_1_is_space_budget_not_new_SKU=True,
                retention_roots_tools_STILL_OPEN=True))
    assert len(facts)==2 and len(parts)==7
    return parts,dict(case_centre_mm=list(centre),case_rotation_quaternion=list(rot.Q),source_ends=facts,
                     right_tail_rise_from_actual_F_HY_top_mm=foretop,supplier_factory_length_guaranteed=False,
                     source_sha256={contractpath.relative_to(ROOT).as_posix():sha(contractpath)})


def main():
    tick=time.monotonic();dest=OUT/'n01-fore-power-pair.json';prior=None
    swap='--swap-aux-front' in sys.argv
    rear='--rear-source-panel' in sys.argv or swap
    axial='--axial-source-panel' in sys.argv or rear
    if dest.exists():
        assert axial,'Receive existing whole power pair, do not duplicate'
        prior=json.loads(dest.read_text());assert prior['status']=='SOURCE_PAIR_RIGID_LAYOUT_REJECTED'
        if prior.get('prior_rejected_layouts'):
            assert (rear and len(prior['prior_rejected_layouts'])==1) or (swap and len(prior['prior_rejected_layouts'])==2),'Next must change functional bay/whole obstructing owner, not scalar retry'
    world=Scene();query=SolidQueries()
    pwmfile=OUT/'n01-pwm-board-shelf.json';pwm,pwmparts,_=packed(pwmfile)
    assert pwm['status']=='OWNER_OWN_AND_FIXED_CLEAR_SHARED47_OUTER_PENDING'
    sourcefile=OUT/'n01-source-saddles-whole-joint.json';source=json.loads(sourcefile.read_text())
    _,_,s1,_=build(*source_inputs())
    s0={n:s.copy() for n,s in world.parts.items() if world.meta[n].get('role')=='S0'}
    assert len(s0)==11,list(s0)
    body=s0['Ref_Material_S0_body_CP2_0_0'];plate=world.parts['Print_P0_BATTERY_PLATE_R4']
    origin=body.BoundBox.Center
    target=A.Vector(plate.BoundBox.XMin-1.25-body.BoundBox.XLength/2,0,-48+3.25+body.BoundBox.ZLength/2)
    rotation=A.Rotation();floor_angle=0
    if axial:
        # Rear-facing key under deck, both source ring barrels point upward.
        # Angle balances full case/key floor limits, not a scalar case offset.
        key=s0['Ref_Material_S0_key_CP2_0_0'].BoundBox
        bodyradius=body.BoundBox.ZLength/2;keyradius=key.ZLength/2
        keyreach=origin.y-key.YMin;halfaxis=body.BoundBox.YLength/2
        floor_angle=math.degrees(math.atan((bodyradius-keyradius)/(keyreach-halfaxis)))
        rotation=A.Rotation(A.Vector(0,1,0),-floor_angle if rear else floor_angle)*A.Rotation(A.Vector(1,0,0),180)*A.Rotation(A.Vector(0,0,1),-90 if rear else 90)
        relative=A.Placement(-rotation.multVec(origin),rotation)
        local={}
        for n,s in s0.items():
            t=s.copy();t.Placement=relative*t.Placement;local[n]=t
        if rear:
            # Bind actual aft/floor limits of the COMPLETE owner. A rotated
            # case's frontmost bbox corner is not its plate-plane clearance.
            # Exact plate/key/body gaps below decide, not overlapping boxes.
            target=A.Vector(183.5-3.25-max(s.optimalBoundingBox().XMax for s in local.values()),0,
                            -48+3.25-min(s.optimalBoundingBox().ZMin for s in local.values()))
        else:
            obstacle=world.rest['Ref_Material_P0_Part__Feature014_0_0'].BoundBox
            target=A.Vector(obstacle.XMin-1.25-local['Ref_Material_S0_body_CP2_0_0'].BoundBox.XMax,0,
                            -48+3.25-min(s.BoundBox.ZMin for s in local.values()))
    transform=A.Placement(target-rotation.multVec(origin),rotation)
    shift=target-origin
    packetfile=OUT/'n01-current-endpoint-packet-r3.json';packet=json.loads(packetfile.read_text())
    ends=[r for r in packet['endpoints'] if r['group']=='S0'];assert len(ends)==2
    mouths=actual_s0_mouths(s0,ends,transform)
    rec=dict(status='RUNNING_SOURCE_PAIR_RIGID_GATE',selected=False,N01_complete=False,physical_pass=False,
             S0_centre_mm=list(target),S0_translation_mm=list(shift),S0_parts=sorted(s0),S1_parts=sorted(s1),
             S0_rotation_quaternion=list(rotation.Q),S0_floor_balance_angle_degrees=floor_angle,
             functional_bay='REAR_SOURCE_KEY_FORWARD_UNDER_PLATE' if rear else 'FORE_SOURCE_KEY_REAR_UNDER_PLATE' if axial else 'FORE_SOURCE_LATERAL_KEY',
             source_S0_mouths=mouths,selected_parts_changed=False,prior_S1_core_global_not_previously_closed=True,
             changed_custom_wire_routes_invalidated=[e['wire'] for e in ends],
             old_S0_owner_witnesses=[],pairs=[],first_failure=None,errors=[],completed_parts=[],
             motion_samples=36,continuous_sweep_verified=False,
             bounding_neck_torso_not_true_shell=True,all6source_fans_roots_tools_other47_STILL_OPEN=True,
             source_sha256={**world.pins,**{p.relative_to(ROOT).as_posix():sha(p) for p in (pwmfile,ROOT/pwm['bundle'],sourcefile,packetfile,Path(__file__))}})
    if prior:
        # Old rejection's inverse-motion witness is valid. Its earlier static
        # rows used a mutable parent cache and are explicitly NOT reused.
        old=list(prior.get('prior_rejected_layouts',[]));prior.pop('prior_rejected_layouts',None)
        rec['prior_rejected_layouts']=old+[prior]
        rec['prior_rejected_layouts'][0]['static_pair_rows_not_reusable']='Source parent translated after its cached child list; inverse-motion first_failure remains a separate fresh-shape witness'
    def save():
        rec['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(rec,indent=2)+'\n',encoding='utf-8',newline='\n')
    save()
    for a,b in (() if prior else (('Ref_Material_current_S1_control_CP2_0_0','Ref_Material_S0_body_CP2_0_0'),
                ('Ref_Material_current_S1_ring_5_0_0','Ref_Material_S0_key_CP2_0_0'))):
        gap=query.distance(s1[a],s0[b]);volume=None
        if gap<1e-6:
            c=s1[a].copy().common(s0[b].copy());assert c.isValid();volume=c.Volume
        rec['old_S0_owner_witnesses'].append(dict(part=a,other=b,gap_mm=gap,positive_common_mm3=volume))
    if prior:rec['old_S0_owner_witnesses']=prior['old_S0_owner_witnesses']
    for s in s0.values():s.Placement=transform*s.Placement
    aux={}
    if swap:
        aux,auxfacts=aux_front_packet(world,s1);rec['whole_AUX_swap']=auxfacts
    for f,groups in (('n01-fore-service-macro.json',{'F_HP','F_TY'}),('n01-fore-topology.json',{'ForeFHAC'})):
        _,parts,rows=packed(OUT/f)
        for n,s in parts.items():
            if rows[n]['group'] in groups:world.parts[n]=s;world.meta[n]=rows[n]
    proof=json.loads((OUT/'n01-flat20-field-modulejoint.json').read_text())
    invalidwires={e['wire'] for e in ends}
    retired=set(pwm['retired_whole_owner'])|set(s0)
    if aux:retired.add('Ref_Material_F_AUX_candidate_case_0_0')
    for n in world.parts:
        if world.wire(n) and (world.meta[n].get('wire_owner') in invalidwires or any(w+'/' in n or n==w for w in invalidwires)):retired.add(n)
        if world.meta[n].get('role')=='ScaffoldPlanning' and 'S0' in n:retired.add(n)
    fixed={r['source']:world.parts[r['source']] for r in proof['material_clouds'] if r['category']!='S1_mating_context' and r['source'] not in retired}
    fixed.update(pwmparts)
    moving={**s0,**s1,**aux};movinggroup={n:'S0' if n in s0 else 'S1' if n in s1 else 'F_AUX' for n in moving}
    rec['retired_whole_owners']=sorted(retired)
    reused={(r['source'],r['obstacle']) for r in source['fore_outboard_budget']['core_pair_receipts']}
    rec['unchanged_S1_P0_bank_F_HY_pairs_reused']=len(reused)
    rec['unchanged_S1_PWM_pairs_reused']=len(s1)*len(pwmparts)
    inner=Part.makeBox(318.5,193.5,153.5,A.Vector(-138.25,-96.75,-44.75))
    neck=Part.makeBox(62,83.5,153.5,A.Vector(-188.75,-41.75,-44.75));inner=inner.fuse(neck)
    def receive(n,s,other,t,scope):
        if bbox_lower_bound(s.BoundBox,t.BoundBox)>=1.25:return True
        q=s
        if other==world.bus['name']:
            q=s.copy();q.Placement=world.bus['inverse']*q.Placement;t=world.bus['original']
        if not t.Solids:
            rec['first_failure']=dict(part=n,other=other,scope=scope,kind='Unknown_curve_jacket_hold');return False
        gap=query.distance(q,t);volume=None
        if gap<1e-6:
            c=q.copy().common(t.copy());assert c.isValid();volume=c.Volume
        row=dict(part=n,other=other,scope=scope,gap_mm=gap,required_mm=1.25,positive_common_mm3=volume)
        rec['pairs'].append(row)
        if gap<1.25-1e-6:rec['first_failure']=row;return False
        return True
    save()
    try:
        for n,s in sorted(moving.items(),key=lambda x:('body' not in x[0],x[0])):
            if time.monotonic()-tick>240:rec['status']='PARTIAL_SOURCE_PAIR_RIGID_GATE';break
            outside=s.copy().cut(inner.copy());assert outside.isNull() or outside.isValid()
            if outside.Volume>1e-5:
                rec['first_failure']=dict(part=n,kind='Outside inner torso/neck bounding budget',volume_mm3=outside.Volume);break
            for other,t in fixed.items():
                if n in s1 and ((n,other) in reused or other in pwmparts):continue
                if not receive(n,s,other,t,'all_remaining_fixed_owners'):break
            if rec['first_failure']:break
            for other,t in moving.items():
                if other<=n or movinggroup[n]==movinggroup[other]:continue
                if not receive(n,s,other,t,'different_whole_power_owners'):break
            if rec['first_failure']:break
            for p in world.motion:
                if bbox_lower_bound(s.BoundBox,A.BoundBox(*p['bounds'][0],*p['bounds'][1]))>=1.25:continue
                q=s.copy();q.Placement=placement(p['r'],p['t']).inverse()*q.Placement
                if not receive(n,q,p['name'],world.rest[p['name']],'actual_motion36_pose'+str(p['pose'])):break
            if rec['first_failure']:break
            rec['completed_parts'].append(n);save();print('Whole power pair',n,'clear',flush=True)
        else:
            rec['status']='SOURCE_PAIR_RIGID_CASES_CLEAR_ENDS_ROOTS_OUTER_OPEN'
            rec['whole_power_core_gate_complete']=True
        if rec['first_failure']:rec['status']='SOURCE_PAIR_RIGID_LAYOUT_REJECTED'
    except Exception as e:rec['errors'].append(repr(e));rec['status']='SOURCE_PAIR_ERROR_NOT_CLEARANCE'
    archive=OUT/'n01-fore-power-pair.breps.zip';records=[]
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for i,(n,s) in enumerate(moving.items()):
            raw=s.exportBrepToString().encode();entry=f'{i:03d}.brep';z.writestr(entry,raw)
            records.append(dict(name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest(),group=movinggroup[n]))
    rec.update(bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),parts=records)
    save();print(json.dumps(dict(status=rec['status'],seconds=rec['worker_seconds'],completed=len(rec['completed_parts']),
                               first_failure=rec['first_failure'],errors=rec['errors'])),flush=True)


def all_current_blockers(packet_path=None,world=None):
    """Inventory ALL changed-space owners, not another first-witness swap.

    No new geometry or selected-native mutation. Reuse complete900/380 S1
    proofs; actual remaining static/moving pairs are saved and resumable.
    """
    tick=time.monotonic();dest=packet_path or OUT/'n01-fore-power-pair.json'
    packet,moving,rows=packed(dest);world=world or Scene();qcache=SolidQueries()
    _,pwm,_=packed(OUT/'n01-pwm-board-shelf.json')
    for file,groups in (('n01-fore-service-macro.json',{'F_HP','F_TY'}),('n01-fore-topology.json',{'ForeFHAC'})):
        _,p,r=packed(OUT/file)
        for n,s in p.items():
            if r[n]['group'] in groups:world.parts[n]=s;world.meta[n]=r[n]
    proof=json.loads((OUT/'n01-flat20-field-modulejoint.json').read_text())
    retired=set(packet['retired_whole_owners'])
    fixed={r['source']:world.parts[r['source']] for r in proof['material_clouds'] if r['category']!='S1_mating_context' and r['source'] not in retired}
    fixed.update({n:s for n,s in pwm.items() if n not in moving})
    source=json.loads((OUT/'n01-source-saddles-whole-joint.json').read_text())
    critical={(r['source'],r['obstacle']) for r in source['fore_outboard_budget']['core_pair_receipts']}
    pins={**world.pins,'power_bundle':packet['bundle_sha256'],'PWM_bundle':sha(ROOT/json.loads((OUT/'n01-pwm-board-shelf.json').read_text())['bundle'])}
    prior=None;unchanged=set()
    if packet.get('equivalent_prior_packet'):
        pf=ROOT/packet['equivalent_prior_packet'];assert sha(pf)==packet['equivalent_prior_packet_sha256']
        prior=json.loads(pf.read_text())
        oldpins=prior['all_current_blockers']['source_sha256']
        assert {n:h for n,h in oldpins.items() if n!='power_bundle'}=={n:h for n,h in pins.items() if n!='power_bundle'}
        oldrows={r['name']:r for r in prior['parts']}
        unchanged={n for n,r in rows.items() if n in oldrows and r['sha256']==oldrows[n]['sha256']}
        changed=set(moving)-unchanged
    rec=packet.get('all_current_blockers')
    if rec:
        assert rec['source_sha256']==pins,'Changed world/owner invalidates pair cache'
        assert rec['status']=='PARTIAL_ALL_CURRENT_POWER_BLOCKERS'
    else:
        rec=dict(status='RUNNING_ALL_CURRENT_POWER_BLOCKERS',source_sha256=pins,pairs={},failures=[],errors=[],
                 completed_static=[],completed_mutual=[],completed_motion=[],source_parts=len(moving),
                 immutable_S1_critical900_and_PWM380_pairs_reused=packet.get('reuse_original_S1_pose',True),N01_complete=False,
                 first_failure_is_NOT_a_complete_owner_inventory=True)
        rec.update(computed_pairs=0,reused_unchanged_pairs=0,unchanged_geometry_actors=sorted(unchanged))
        rec['interface_policy']=dict(rigid_external_mm=1.25,insulated_jacket_to_jacket_or_soft_nylon_tie_mm=.2,
            bare_conductors_not_relaxed=True,insulation_not_thinned=True,not_electrical_thermal_or_physical_qualification=True)
        packet['all_current_blockers']=rec
    def save():
        rec['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(packet,indent=2)+'\n',encoding='utf-8',newline='\n')
    def budget():
        if time.monotonic()-tick>240:raise TimeoutError('240s soft budget; a single OCC pair is atomic, completed pairs retained')
    def query(n,s,other,t,scope,minimum=1.25):
        if bbox_lower_bound(s.BoundBox,t.BoundBox)>=minimum:return
        key=n+'|'+other+'|'+scope
        if key in rec['pairs']:return
        budget()
        if prior and n in unchanged and other not in changed:
            oldrow=prior['all_current_blockers']['pairs'].get(key)
            if oldrow and 'error' not in oldrow and oldrow.get('required_mm')==minimum:
                row=dict(oldrow,inherited_from=packet['equivalent_prior_packet'])
                rec['pairs'][key]=row;rec['reused_unchanged_pairs']+=1
                owned=row.get('kind') in ('OWNED_CARRIER_SUBSET_PLUS_CLEAR_ADDITION','NAMED_SHARED_STRUCTURE_UNION')
                if not owned and ('hold' in row or row.get('gap_mm',minimum)<minimum-1e-6):rec['failures'].append(row)
                save();return
        original_kind=world.meta.get(other,{}).get('kind','actual_current_owner')
        moving_kind=rows.get(n,{}).get('kind','actual_source')
        row=dict(part=n,other=other,scope=scope,required_mm=minimum,owner_meta=world.meta.get(other,{}))
        try:
            rule=next((r for r in packet.get('planned_own_relations',[]) if {r['part'],r['other']}=={n,other}),None)
            if rule:
                c=s.copy().common(t.copy());assert c.isNull() or c.isValid()
                if rule['kind']=='ZERO_PENETRATION_BOTTOM_BEARING':
                    support=s if n==rule['part'] else t;housing=t if n==rule['part'] else s
                    assert abs(support.optimalBoundingBox().ZMax-rule['plane_Z_mm'])<1e-5
                    assert abs(housing.optimalBoundingBox().ZMin-rule['plane_Z_mm'])<1e-5
                    assert c.Volume<1e-5
                elif rule['kind']=='SAME_NAMED_TIE_BUDGET':
                    assert c.Volume>1e-5,'Head and strap budgets must actually connect'
                    assert all('Tie' in x for x in (n,other))
                elif rule['kind']=='RETAINED_ROOT_SUBSET':
                    parent=t if other==rule['other'] else s
                    assert world.meta[rule['other']].get('role')=='ScaffoldPlanning'
                    old=world.parts[rule['part']].copy().common(parent.copy());assert old.isValid() and old.Volume>1e-5
                    extra=c.cut(old);assert extra.isNull() or extra.isValid()
                    assert c.Volume>1e-5 and extra.Volume<1e-5
                elif rule['kind']=='NAMED_POST_SIDE_BOND':
                    assert world.meta[rule['other']].get('role')=='ScaffoldPlanning'
                    lo,hi=rule['intersection_bounds_mm']
                    expected=Part.makeBox(*(b-a for a,b in zip(lo,hi)),A.Vector(*lo))
                    extra=c.cut(expected);assert extra.isNull() or extra.isValid()
                    assert extra.Volume<1e-5 and abs(c.Volume-rule['expected_union_mm3'])<1e-5
                else:raise AssertionError('Unknown ownership rule')
                row.update(kind='NAMED_PLANNED_OWN_RELATION',relation=rule,positive_common_mm3=c.Volume,
                           physical_pass=False,native_connections_pending_N03=True)
                rec['pairs'][key]=row;rec['computed_pairs']+=1;save();return
            root=packet.get('shared_fore_units',{}).get('PWM_changed_root')
            if n=='ShelfPWM:carrier' and root and other==root['root_mate']:
                c=s.copy().common(t.copy());assert c.isValid()
                bounds=root['root_bounds_mm'];lo,hi=bounds
                slab=t.optimalBoundingBox();assert abs(slab.ZLength-3)<1e-5
                foot=Part.makeBox(hi[0]-lo[0],hi[1]-lo[1],3,A.Vector(lo[0],lo[1],slab.ZMin))
                extra=c.cut(foot);assert extra.isNull() or extra.isValid()
                assert extra.Volume<1e-5 and abs(c.Volume-root['expected_shared_slab_union_mm3'])<1e-5
                row.update(kind='NAMED_SHARED_STRUCTURE_UNION',positive_common_mm3=c.Volume,native_union_pending_N03=True)
                rec['pairs'][key]=row;rec['computed_pairs']+=1;save();return
            qq=s
            if other==world.bus['name']:
                qq=s.copy();qq.Placement=world.bus['inverse']*qq.Placement;t=world.bus['original']
            if not t.Solids:
                row['hold']='Curve-only owner, full jacket unknown';rec['failures'].append(row)
            else:
                gap=qcache.distance(qq,t);volume=None
                if gap<1e-6:
                    c=qq.copy().common(t.copy());assert c.isValid();volume=c.Volume
                row.update(gap_mm=gap,positive_common_mm3=volume)
                if gap<minimum-1e-6:
                    row['kind']='RESERVATION_HOLD' if ('reservation' in original_kind or 'reservation' in moving_kind
                        or world.meta.get(other,{}).get('role')=='ScaffoldPlanning') else 'ACTUAL_SOURCE_PAIR_GAP'
                    rec['failures'].append(row)
        except Exception as e:row['error']=repr(e);rec['errors'].append(row)
        rec['pairs'][key]=row;rec['computed_pairs']+=1;save();budget()
    save()
    try:
        for n,s in moving.items():
            if n not in rec['completed_static']:
                for other,t in fixed.items():
                    if packet.get('reuse_original_S1_pose',True) and rows[n]['group']=='S1' and ((n,other) in critical or other in pwm):continue
                    minimum=pair_spacing(n,rows[n],other,world.meta.get(other,{}))
                    query(n,s,other,t,'all_static',minimum)
                rec['completed_static'].append(n);save()
            if n not in rec['completed_mutual']:
                for other,t in moving.items():
                    if other<=n or rows[n]['group']==rows[other]['group']:continue
                    query(n,s,other,t,'all_moving_owners',pair_spacing(n,rows[n],other,rows[other]))
                rec['completed_mutual'].append(n);save()
            if n not in rec['completed_motion']:
                if rows[n]['group']!='S1' or not packet.get('reuse_original_S1_pose',True):
                    for p in world.motion:
                        if bbox_lower_bound(s.BoundBox,A.BoundBox(*p['bounds'][0],*p['bounds'][1]))>=1.25:continue
                        qq=s.copy();qq.Placement=placement(p['r'],p['t']).inverse()*qq.Placement
                        query(n,qq,p['name'],world.rest[p['name']],'motion36_'+str(p['pose']))
                rec['completed_motion'].append(n);save()
            print('All owners',n,'received',flush=True)
        rec['status']='ALL_CURRENT_POWER_BLOCKERS_RECEIVED_NOT_N01'
    except TimeoutError as e:rec['status']='PARTIAL_ALL_CURRENT_POWER_BLOCKERS';rec['stop_note']=str(e)
    except Exception as e:rec['errors'].append(dict(error=repr(e)));rec['status']='ALL_CURRENT_BLOCKERS_ERROR_NOT_CLEARANCE'
    save();print(json.dumps(dict(status=rec['status'],seconds=rec['worker_seconds'],pairs=len(rec['pairs']),failures=len(rec['failures']),
                               owners=sorted({r['other'] for r in rec['failures']}),errors=rec['errors'])),flush=True)


if __name__=='__main__':
    import os
    print('WORKER_PID',os.getpid(),flush=True)
    if '--all-current-blockers' in sys.argv:all_current_blockers()
    else:main()
