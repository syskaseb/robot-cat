"""Whole changed operating rail/W041 interface, bounded parking contribution.

Keep actual four native Frames, all current wires/parts and new12 bank roots.
Retire ONLY four named Upper source-grip children and two moved W041 groups.
Parking remains incomplete until three full fixed-length heavy curves exist.
"""
import json,time
from pathlib import Path
import FreeCAD as A
import Part
from remaining25_shared_context import load,P
from current_source_retention_context import C,same_parent
from check_main_p0_placement import SavedShapes
from plan_remaining25_restraint_space import profile,own_wire_name
from plan_axial_source_supports import arm_box
from plan_individual_bank_seats import seats
from current_bank_datums import datums
from bank_prototype_service_material import material
from bank_service_source_routes import routes
from current_work_guard import check


def run():
    check();tick=time.monotonic();targets,wires,pins,parents,grips=load();reader=SavedShapes()
    names=['bank-prototype-service-plan','current-body-native-composition','local-source-retention-native/manifest',
        'remaining25-restraint-space','remaining25-saddle-roots','individual-bank-roots','mta-interface-plan','main-source-plan']
    files=[P.OUT/(n+'.json') for n in names]
    plan,composition,source,saddles,roots,bank,mta,main=[json.loads(f.read_text()) for f in files]
    for p in (plan,composition,source,saddles,roots,bank):
        for n,h in p['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    # Current Frame unions contain exactly the previously qualified pieces;
    # replace historical Frame bodies, not whole purchased-component owners.
    for r in (r for r in composition['prints'] if r['part'].endswith('FixedCarrier')):
        for n in list(targets):
            if same_parent(r['part'],n,grips):targets.pop(n)
        targets['CurrentNative/'+r['part']]=reader.shape(P.ROOT/r['native'],r['native_object'])
    upper=next(r for r in source['parts'] if r['part']=='UpperCarrier001');retired=set(upper['source_groups'])
    assert retired=={'W066_0_15','W067_P_SYS','W068_P_SYS','W043_P_SYS'}
    native=P.ROOT/upper['native'];xml=reader.doc(native)[upper['object']]
    linked=[n.get('value') for n in xml.findall("./Properties/Property[@name='Shapes']/LinkList/Link")]
    removed=[n for n in linked if any(n.startswith('SourceSeat'+g) or n.startswith('SourcePilot'+g+'N') for g in retired)]
    kept=[n for n in linked if n not in removed]
    assert kept==['UpperCarrierFixedFeedsCurrent'] and len(removed)==21
    retained=reader.shape(native,kept[0]);old=reader.shape(native,upper['object'])
    assert retained.copy().cut(old.copy()).Volume<1e-5
    for n in list(targets):
        if same_parent('UpperCarrier001',n,grips) or any(n=='RetainedSourceLacing/'+ref for ref in upper['lacing_reference_objects']):targets.pop(n)
    targets['CurrentNative/UpperCarrier001']=retained
    # Full current fixed saddles. Only the two moved W041 joint ends retire.
    moved_groups={'W041/factory/end','W041/custom/start'};groups={g['id']:g for g in saddles['spatial_groups']}
    for r in roots['groups']:
        if r['id'] in moved_groups:continue
        rec=r['recipe'];q=profile(groups[r['id']],rec['normal'],rec['knot_sign']);assert q['recipe']==rec
        targets['CurrentSaddleBand/'+r['id']]=q['band']
        if r['owner']=='UpperCarrier001':
            targets['CurrentSaddleBody/'+r['id']]=q['body']
            for i,(a,b) in enumerate(zip(r['path'],r['path'][1:])):
                targets['CurrentSaddleRoot/UpperCarrier001/'+r['id']+'/'+str(i)]=arm_box(a,b,roots['arm_half_widths_mm'])
    panels=seats(datums(targets),True)
    assert bank['accepted']==12 and not bank['errors']
    for r in bank['groups']:
        targets['CurrentBankOwned/'+r['id']+'/Seat']=panels[r['id']]['body']
        targets['CurrentBankOwned/'+r['id']+'/Leaf']=arm_box(*r['leaf_points'],bank['leaf_half_mm'])
        for i,(a,b) in enumerate(zip(r['path'],r['path'][1:])):
            targets['CurrentBankOwned/'+r['id']+'/'+str(i)]=arm_box(a,b,bank['trunk_half_mm'])
    changed=routes(mta,main);old_joint=next(r for r in mta['joints'] if r['id']=='W041_Joint')
    origin=old_joint['factory_entry_mm'];end=changed['W041_FACTORY']['parts'][-1]['end']
    rot=A.Rotation(A.Vector(1,0,0),-90);pose=A.Placement(A.Vector(*end)-rot.multVec(A.Vector(*origin)),rot)
    joints=[n for n in targets if n.split('/')[0]=='W041_Joint'];assert joints
    moved_joint_shapes={}
    for n in joints:
        s=targets.pop(n).copy();s.Placement=pose*s.Placement;moved_joint_shapes['Changed/'+n]=s
    retired_wires=[n for n in wires if n.rsplit('/',1)[-1] in changed];assert len(retired_wires)==2
    for n in retired_wires:wires.pop(n)
    q=material(plan);operating=dict(q['parts'],**{'RailBand/'+g:s for g,s in q['bands'].items()},**moved_joint_shapes)
    files.extend(Path(__file__).with_name(n) for n in ('check_bank_prototype_service_space.py','bank_prototype_service_material.py','bank_service_source_routes.py','plan_individual_bank_seats.py'))
    pins.update(reader.hashes);pins.update({f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in files})
    bounds=C.ImmutableBounds();cache=C.AtomicMaterial(P.OUT/'bank-prototype-service-pairs.json',bounds.near)
    checks=0;errors=[];records=[];wire_records=[];park_records=[]
    stationary=set(q['stationary'])
    def save(status):
        result=dict(status=status,operating_parts=records,changed_whole_wire_checks=wire_records,parking_contribution=park_records,
            changed_routes=changed,source_sha256=pins,checks=checks,errors=errors,worker_seconds=round(time.monotonic()-tick,3),
            exact_retained_Upper_children=kept,retired_Upper_children=removed,superseded_two_W041_grip_groups=sorted(moved_groups),
            superseded_wire_instances=retired_wires,moved_joint_instances=joints,
            no_whole_parent_collision_masks=True,existing_other_Upper_wire_roots_retained=True,
            new_part_counts=dict(removable_rail=1,stationary_bosses=2,parking_cups=2,prefuse_parking_seat=1,metal_fasteners=6),
            scope='Full changed operating rail/hardware/W041factory+custom vs retained scene including4nativeFrames and12bankroots. Parking is NECESSARY contribution ONLY: three heavy whole parked curves/continuous handling not yet provided.',
            missing_parked_whole_curves=['W066','W067','W068'],
            open=['Affected Upper wire/support roots and new boss/cup/parking-seat roots','Whole parked heavy curves/slack and actual ATO extraction/restore sequence',
                  'G1/five grounds,W042/W011/XA03 and all remaining41service witnesses','Native editable rail/Upper,whole stock/release'],
            selected=False,W5_complete=False,M4_complete=False,A2_complete=False,physical_pass=False)
        f=P.OUT/'bank-prototype-service-space.json';tmp=f.with_suffix('.tmp');tmp.write_text(json.dumps(result,indent=2)+'\n');tmp.replace(f);cache.save()
    def hit(a,b,ra=0,rb=0):
        nonlocal checks
        if not bounds.near(a,b,ra+rb+.0001):return None
        try:
            check();checks+=1;gap,volume=cache.check(a,b,ra,rb)
        except (TimeoutError,AssertionError,RuntimeError,ValueError) as e:errors.append(str(e));save('SERVICE_SPACE_GUARDED_OR_ERROR');raise
        if volume>1e-5 or ((ra+rb)>0 and gap<ra+rb-1e-6):return dict(volume_mm3=volume,gap_mm=gap,required_mm=ra+rb)
        return None
    save('SERVICE_OPERATING_LAYOUT_STARTED')
    for name,s in operating.items():
        row=dict(part=name,contacts=[],assigned_parent_unions=[]);records.append(row)
        for n,t in targets.items():
            if not t.Solids:continue
            v=hit(s,t)
            if v is None:continue
            if name in stationary and (n=='CurrentNative/UpperCarrier001' or n.startswith(('CurrentBankOwned/','CurrentSaddleRoot/UpperCarrier001/'))):
                row['assigned_parent_unions'].append(dict(part=n,**v));continue
            row['contacts'].append(dict(obstacle=n,**v))
        for n,(w,r) in wires.items():
            own=name.startswith('RailBand/') and own_wire_name(n,{name.removeprefix('RailBand/').split('_')[0]})
            if (v:=hit(s,w,0,r if own else r+.25)) is not None:row['contacts'].append(dict(obstacle=n,**v))
        for n,t in operating.items():
            if n==name:continue
            if (v:=hit(s,t)) is not None:row['contacts'].append(dict(obstacle='New/'+n,**v))
        save('SERVICE_OPERATING_PARTS_IN_PROGRESS');print('service operating',name,'contacts',len(row['contacts']),'pairs',checks,flush=True)
    all_targets=dict(targets,**operating)
    def trimmed(parts,side,amount):
        p=[dict(r) for r in parts];i=0 if side=='start' else -1;r=p[i];assert r['kind']=='line' and r['length_mm']>amount
        axis=[(b-a)/r['length_mm'] for a,b in zip(r['start'],r['end'])]
        r[side]=[x+(amount if side=='start' else -amount)*u for x,u in zip(r[side],axis)]
        r['length_mm']-=amount;return P.wire(p)
    for name,r in changed.items():
        s=P.wire(r['parts']);rad=r['radius_mm'];row=dict(wire=name,contacts=[],assigned_endpoint_reliefs=[]);wire_records.append(row)
        for n,t in all_targets.items():
            if not t.Solids:continue
            side=None
            if name=='W041_FACTORY' and n=='MTA/FL':side='start'
            if n.startswith('Changed/W041_Joint'):side='end' if name=='W041_FACTORY' else 'start'
            if name=='W041_CUSTOM' and n.startswith('P_FRONT'):side='end'
            curve=trimmed(r['parts'],side,rad+.2501) if side else s
            if side:row['assigned_endpoint_reliefs'].append(dict(component=n,side=side,trimmed_endpoint_mm=rad+.2501,whole_remaining_curve_checked=True))
            own_band=n.startswith('CurrentSaddleBand/W041/'+('factory' if name=='W041_FACTORY' else 'custom')+'/')
            if (v:=hit(curve,t,rad if own_band else rad+.25,0)) is not None:row['contacts'].append(dict(obstacle=n,**v))
        for n,(w,rr) in wires.items():
            if (v:=hit(s,w,rad,rr+.25)) is not None:row['contacts'].append(dict(obstacle=n,**v))
        other='W041_CUSTOM' if name=='W041_FACTORY' else 'W041_FACTORY'
        if (v:=hit(s,P.wire(changed[other]['parts']),rad,changed[other]['radius_mm']+.25)) is not None:row['contacts'].append(dict(obstacle=other,**v))
        save('SERVICE_FULL_W041_CURVES_IN_PROGRESS');print('service full wire',name,'contacts',len(row['contacts']),flush=True)
    # Required parking-material contribution, explicitly NOT full service.
    parked=dict(q['stationary'],Rail=q['parked_rail'],**{'RailBand/'+g:s for g,s in q['parked_bands'].items()})
    for name,s in parked.items():
        row=dict(part=name,contacts=[]);park_records.append(row)
        for n,t in targets.items():
            if t.Solids and (v:=hit(s,t)) is not None:
                if name in stationary and (n=='CurrentNative/UpperCarrier001' or n.startswith(('CurrentBankOwned/','CurrentSaddleRoot/UpperCarrier001/'))):continue
                row['contacts'].append(dict(obstacle=n,**v))
        for n,(w,r) in wires.items():
            if n.rsplit('/',1)[-1] in ('W043','W066','W067','W068'):continue
            if (v:=hit(s,w,0,r+.25)) is not None:row['contacts'].append(dict(obstacle=n,**v))
        save('SERVICE_PARK_MATERIAL_CONTRIBUTION_IN_PROGRESS');print('service park contribution',name,'contacts',len(row['contacts']),flush=True)
    save('SERVICE_OPERATING_AND_PARK_MATERIAL_CONTRIBUTION_COMPLETE_NOT_FULL_SERVICE')
    print(json.dumps(dict(parts=len(records),whole_changed_wires=len(wire_records),park_parts=len(park_records),
        contacts=sum(len(r['contacts']) for r in records+wire_records+park_records),checks=checks,seconds=round(time.monotonic()-tick,3))),flush=True)


if __name__=='__main__':run()
