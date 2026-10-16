"""Actual current Frame unions and declared Upper child retirement for roots."""
import json
from pathlib import Path
import FreeCAD as A
from remaining25_shared_context import load,P
from current_source_retention_context import same_parent
from check_main_p0_placement import SavedShapes
from plan_remaining25_restraint_space import profile
from plan_individual_bank_seats import seats
from current_bank_datums import datums,nominal_sweep
from plan_axial_source_supports import arm_box
from bank_prototype_service_material import material,hexagon
from loom_land_port import box
from current_source_case_retention import material as source_cases
import Part


def prepare():
    targets,wires,pins,parents,grips=load();reader=SavedShapes()
    files=[P.OUT/(n+'.json') for n in ('bank-prototype-service-plan','current-body-native-composition',
        'local-source-retention-native/manifest','remaining25-restraint-space','remaining25-saddle-roots','individual-bank-roots')]
    plan,current,source,saddles,roots,bank=[json.loads(f.read_text()) for f in files]
    for p in (plan,current,source,saddles,roots,bank):
        for n,h in p['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    for r in (r for r in current['prints'] if r['part'].endswith('FixedCarrier')):
        for n in list(targets):
            if same_parent(r['part'],n,grips):targets.pop(n)
        targets['CurrentNative/'+r['part']]=reader.shape(P.ROOT/r['native'],r['native_object'])
        parents[r['part']]=targets['CurrentNative/'+r['part']]
    upper=next(r for r in source['parts'] if r['part']=='UpperCarrier001')
    assert set(upper['source_groups'])=={'W066_0_15','W043_P_SYS','W067_P_SYS','W068_P_SYS'}
    file=P.ROOT/upper['native'];xml=reader.doc(file)[upper['object']]
    children=[n.get('value') for n in xml.findall("./Properties/Property[@name='Shapes']/LinkList/Link")]
    keep=[n for n in children if not n.startswith(('SourceSeat','SourcePilot'))]
    assert keep==['UpperCarrierFixedFeedsCurrent'] and len(children)==22
    retained=reader.shape(file,keep[0]);old=reader.shape(file,upper['object'])
    assert retained.copy().cut(old.copy()).Volume<1e-5
    for n in list(targets):
        if same_parent('UpperCarrier001',n,grips) or any(n=='RetainedSourceLacing/'+ref for ref in upper['lacing_reference_objects']):targets.pop(n)
    targets['CurrentNative/UpperCarrier001']=retained
    parents['UpperCarrier001']=retained
    groups={g['id']:g for g in saddles['spatial_groups']};upper_profiles={}
    for r in roots['groups']:
        rec=r['recipe'];q=profile(groups[r['id']],rec['normal'],rec['knot_sign']);assert q['recipe']==rec
        targets['CurrentSaddleBand/'+r['id']]=q['band']
        if r['owner']=='UpperCarrier001':
            upper_profiles[r['id']]=q;targets['CurrentSaddleBody/'+r['id']]=q['body']
    assert len(upper_profiles)==24
    # All old24 Upper paths retire: their parent lost21 declared children and
    # the service/rail interface changed. Do not inherit an unrooted old path.
    placed=datums(targets);panels=seats(placed,True);anchors=[];root_points=set()
    for r in bank['groups']:
        targets['CurrentBankOwned/'+r['id']+'/Seat']=panels[r['id']]['body']
        targets['CurrentBankOwned/'+r['id']+'/Leaf']=arm_box(*r['leaf_points'],bank['leaf_half_mm'])
        root_points.add(tuple(r['path'][0]))
        for i,(a,b) in enumerate(zip(r['path'],r['path'][1:])):
            s=arm_box(a,b,bank['trunk_half_mm']);name='CurrentBankOwned/'+r['id']+'/'+str(i);targets[name]=s
            for p in (a,[(x+y)/2 for x,y in zip(a,b)],b):anchors.append(dict(point=list(p),component=s,provenance=name))
    assert bank['accepted']==12 and not bank['errors']
    for p in root_points:assert arm_box(p,p,bank['trunk_half_mm']).cut(retained.copy()).Volume<1e-5,('Retired bank load root',p)
    q=material(plan)
    targets.update({'NewRail/'+n:s for n,s in q['parts'].items()})
    targets.update({'NewRailBand/'+n:s for n,s in q['bands'].items()})
    assert plan['removable_rail']['in_robot_park_enabled'] is False
    for r in placed:
        targets['ServiceATO/'+r['id']]=nominal_sweep(r)
        x,y=r['centre_xy_mm'];z=r['flange_top_z_mm']
        for sign in (-1,1):
            lo,hi=(-5.55,-2.55) if sign==-1 else (2.55,5.55)
            targets['ServiceJaw/'+r['id']+'/'+str(sign)]=box([x-10.55,y+lo,z+11,x+10.55,y+hi,z+58])
    dz=plan['removable_rail']['plate_stack_raise_mm']
    for i,(x,y,z) in enumerate(plan['removable_rail']['bolt_centres_mm']):
        targets['RailHoleKeepout'+str(i)]=Part.makeCylinder(1.7,12,A.Vector(x,y,147.9+dz))
        targets['RailNutTrapKeepout'+str(i)]=hexagon(x,y,149.4+dz,5.7,2.6)
        targets['RailDriverKeepout'+str(i)]=Part.makeCylinder(3,35,A.Vector(x,y,158.9+dz))
    fixed_owned={'CurrentNative/UpperCarrier001'}|{n for n in targets if n.startswith(('CurrentBankOwned/','CurrentSaddleBody/'))}|{'NewRail/'+n for n in q['stationary']}
    rows=[]
    for gid,p in upper_profiles.items():rows.append(dict(id=gid,owner='UpperCarrier001',body=p['body'],goal=p['root_tip_mm'],half=[1.4]*3,recipe=p['recipe'],kind='wire_saddle'))
    for n,goal in zip(('RailBoss0','RailBoss1'),q['root_goals']):
        rows.append(dict(id=n,owner='UpperCarrier001',body=q['stationary'][n],goal=goal,half=[2]*3,recipe=None,kind='structural_station'))
    allocation_file=P.OUT/'remaining25-interface-allocation.json';legs_file=P.OUT/'leg-stations-plan.json'
    cases=source_cases(targets,json.loads(allocation_file.read_text()),json.loads(legs_file.read_text()))
    targets.update({'SourceCase/'+n:s for n,s in cases['parts'].items()})
    targets.update({'SourceCaseBand/'+n:s for n,s in cases['bands'].items()})
    targets.update({'SourceCaseAdhesive/'+n:s for n,s in cases['adhesive'].items()})
    rows.extend(cases['rows']);assert len(rows)==38
    owned={o:set() for o in parents}
    owned['UpperCarrier001']=fixed_owned
    for o in parents:owned[o].add('CurrentNative/'+o)
    for r in cases['rows']:owned[r['owner']].add('SourceCase/'+r['id'])
    anchor_file=P.OUT/'body36-receiver-support-reservations.json'
    files.extend([allocation_file,legs_file,anchor_file])
    files.extend(Path(__file__).with_name(n) for n in ('bank_upper_retained_context.py','current_source_case_retention.py','bank_prototype_service_material.py','plan_axial_source_supports.py','plan_remaining25_restraint_space.py','plan_individual_bank_seats.py'))
    pins.update(reader.hashes);pins.update({f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in files})
    return dict(targets=targets,wires=wires,pins=pins,parent=retained,parents=parents,anchors=anchors,rows=rows,allowed=fixed_owned,owned=owned,cases=cases,
        frame_anchor_metadata=json.loads(anchor_file.read_text()),
        bank=bank,retired_old_Upper_roots=24,retired_Upper_native_children=[n for n in children if n not in keep])
