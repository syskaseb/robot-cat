"""One CP2 service-zone plan, using saved native geometry rather than cached BUS.

Reservations are labelled as such. Inventory never saves its source document.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import sys
import time
import math

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'hardware/cad/studies/whole-cat-packaging/cp2'
SOURCE = BASE / 'BoardDatumCandidate.FCStd'


def allocation():
    """One derived zoning proposal, not a scalar-position search.

    Keep the existing40mm/2mm F_PI access allowance. Allocate complete banks
    and side distribution together, including necessary insulated runouts.
    Purchased terminal seating remains the inherited explicit prototype datum.
    """
    return dict(left_bank_shift_y_mm=2.5, right_bank_raise_z_mm=12,
        left_wago_lower_z_mm=21, right_wago_lower_z_mm=10,
        F_PI_access_unchanged=True, wire_OD_budget_mm=3.1,
        wire_radius_budget_mm=12.4, straight_grip_mm=9,
        left_output_straight_mm=19, right_output_straight_mm=9,
        derivation=dict(left_service_gap_mm=52.2695+2.5-53.375,
            left_input_elbow_floor_mm=73.37-9-12.4-3.1/2,
            left_wago_top_mm=70-21,
            right_input_elbow_floor_mm=73.37+12-9-12.4-3.1/2,
            F0_top_mm=61),
        preserved=['F_PI and both exits','W043 short input','Pi solder topology',
            'source/S0/S1','Pi and all controller boards','4 MTA branch holders',
            'P0/E6 and torso325x200x160'],
        invalidated=['12 left ATO terminal endpoints and their routes/supports',
            '12 right ATO terminal endpoints and their routes/supports',
            'all10 side WAGO ports/routes/supports',
            'ATO supports/shell clearance and bank mounting'],
        no_whole_harness_claim=True, exact_supplier_lid_motion_OPEN=True)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory():
    import FreeCAD as A
    start = datetime.now(timezone.utc); tick = time.monotonic()
    output = BASE / 'service-zone-inventory.json'
    assert not output.exists(), 'Do not repeat unchanged inventory'
    before = sha(SOURCE)
    doc = A.openDocument(str(SOURCE))
    try:
        rows = []
        for ob in doc.Objects:
            if 'Shape' not in ob.PropertiesList or ob.Shape.isNull():
                continue
            b = ob.Shape.BoundBox
            if b.XMax < -115 or b.XMin > 145 or b.ZMax < 30 or b.ZMin > 165:
                continue
            if ob.Name in ['TorsoEnvelope', 'BatteryNominal']:
                continue
            parents = [p.Name for p in ob.InList]
            relevant = any(p in ['InteriorReservations', 'ServiceReservations',
                'HarnessCandidate', 'S0TerminalCandidates', 'S1TerminalCandidates',
                'ATOStackCandidates'] for p in parents) or 'Category' in ob.PropertiesList
            if not relevant:
                continue
            basis = ob.DimensionBasis if 'DimensionBasis' in ob.PropertiesList else (
                'Nominal service reservation' if ob.Name.startswith('Access_') else
                'Saved native geometry; purchased/retained status follows source')
            rows.append(dict(name=ob.Name, bounds_mm=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax],
                placement_base_mm=list(ob.Placement.Base), rotation=list(ob.Placement.Rotation.Q),
                parents=parents, basis=basis, category=ob.Category if 'Category' in ob.PropertiesList else None))
        report = dict(status='READ_ONLY_SERVICE_ZONE_INVENTORY', source_native_sha256=before,
            physical_pass=False, bbox_is_collision_proof=False, selected=False, components=rows,
            started_utc=start.isoformat(), worker_wall_seconds=round(time.monotonic()-tick,3))
        output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        assert sha(SOURCE)==before
        for r in rows:
            if r['name'].endswith('_CP2') and not any(s in r['name'] for s in ['STRIP','Factory','_Source_']):
                print(r['name'], [round(v,2) for v in r['bounds_mm']],flush=True)
        print('elapsed',report['worker_wall_seconds'],'rows',len(rows),flush=True)
    finally:
        A.closeDocument(doc.Name)


def gate():
    import FreeCAD as A
    import Part
    from whole_cat_source_bay_plan import Route
    started = datetime.now(timezone.utc); tick = time.monotonic()
    canted='--canted' in sys.argv
    output=BASE/('service-zone-canted-gate.json' if canted else 'service-zone-gate.json')
    native=BASE/('ServiceZoneCantedCandidate.FCStd' if canted else 'ServiceZoneCandidate.FCStd')
    assert not output.exists() and not native.exists(), 'No unchanged retry'
    assert started < datetime.fromisoformat('2026-10-06T18:50:00+00:00')
    plan=allocation()
    if canted:
        plan=dict(recipe_family='CANTED_BANKS_NOT_VERTICAL_SHIFT_RETRY',
            bank_axis_tilt_deg=30,bank_lane_y_mm=48,flange_z_mm=138,
            side_wago_lower_z_mm=10,front_MTA_FL_centre_mm=[-15,36.6,122],
            front_MTA_FR_centre_mm=[37.5,-7,122],
            wire_OD_budget_mm=3.1,wire_radius_budget_mm=12.4,straight_grip_mm=9,
            F_PI_access_unchanged=True,no_whole_harness_claim=True,
            exact_supplier_lid_motion_OPEN=True,
            cause_change='Inclined terminal departure creates side escape instead of vertically raising ends',
            invalidated=['All24 ATO endpoints/routes/supports','All10 side WAGO ports/routes/supports',
                'Front MTA holders and BOTH factory leads each; far endpoints/joins must be rebuilt',
                'Bank mounts and assembled fuse-removal sequence'])
    paths=[SOURCE, Path(__file__), BASE/'ato-stack-checks.json',
        BASE/'service-zone-inventory.json', BASE/'whole-harness-board-plan.json']
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in paths}
    terminals=json.loads(paths[2].read_text(encoding='utf-8'))['terminal_datums']
    inventory_proof=json.loads(paths[3].read_text(encoding='utf-8'))
    assert inventory_proof['source_native_sha256']==sha(SOURCE)
    d=A.openDocument(str(SOURCE)); changed={}; service=set(); contacts=[]; errors=[]
    tested=0; outside=[]; ends=[]; action_overlaps=[];mouths={};departures={}
    try:
        datum=d.addObject('App::FeaturePython','ServiceZonePlan')
        for name,value in [('LeftLaneShift',2.5),('RightBankRaise',12),
                ('LeftWAGOLower',21),('RightWAGOLower',10)]:
            datum.addProperty('App::PropertyLength',name);setattr(datum,name,value)
        if canted:
            for name,value in [('BankLane',48),('BankFlangeZ',138),('SideWAGOLower',10)]:
                datum.addProperty('App::PropertyLength',name);setattr(datum,name,value)
            datum.addProperty('App::PropertyString','TiltBasis')
            datum.TiltBasis='Fixed nominal30deg aboutX; supplier seating/clip action remains provisional'
        def translate(ob,axis,parameter,sign=1):
            # Y/Z may already be expression-driven. Preserve the Z stack when
            # allocating Y; replace only the expression of the changed axis.
            initial=getattr(ob.Placement.Base,axis)
            old=dict(ob.ExpressionEngine).get('Placement.Base.'+axis)
            expression=f'({old})' if old else f'{initial} mm'
            ob.setExpression('Placement.Base.'+axis,
                expression+f'+{sign}*ServiceZonePlan.{parameter}')
            changed[ob.Name]=None
            if ob.Name.startswith('Access_'):service.add(ob.Name)
        def cant(ob,side):
            sign=1 if side=='L' else -1
            rotation=A.Rotation(A.Vector(1,0,0),sign*30)
            old_axis=A.Vector(0,sign*62,126);new_axis=A.Vector(0,sign*48,138)
            transform=A.Placement(new_axis-rotation.multVec(old_axis),rotation)
            if ob.Name.endswith(('_IN','_OUT')):
                b=ob.Shape.BoundBox
                mouths[ob.Name]=list(transform.multVec(A.Vector((b.XMin+b.XMax)/2,(b.YMin+b.YMax)/2,b.ZMin)))
                departures[ob.Name]=list(rotation.multVec(A.Vector(0,0,-1)))
            for axis in ['y','z']:ob.setExpression('Placement.Base.'+axis,None)
            ob.Placement=transform.multiply(ob.Placement)
            y,z=ob.Placement.Base.y,ob.Placement.Base.z
            ob.setExpression('Placement.Base.y',f'{y} mm+{sign}*(ServiceZonePlan.BankLane-48 mm)')
            ob.setExpression('Placement.Base.z',f'{z} mm+ServiceZonePlan.BankFlangeZ-138 mm')
            changed[ob.Name]=None
            if ob.Name.startswith('Access_'):service.add(ob.Name)
        for ob in list(d.Objects):
            if ob.Name.startswith(('F_L1_CP2_','F_L2_CP2_','F_L3_CP2_',
                    'F_L4_CP2_','F_L5_CP2_','F_L6_CP2_','Access_F_L')):
                cant(ob,'L') if canted else translate(ob,'y','LeftLaneShift')
            elif ob.Name.startswith(('F_R1_CP2_','F_R2_CP2_','F_R3_CP2_',
                    'F_R4_CP2_','F_R5_CP2_','F_R6_CP2_','Access_F_R')):
                cant(ob,'R') if canted else translate(ob,'z','RightBankRaise')
        for side,parameter in [('L','LeftWAGOLower'),('R','RightWAGOLower')]:
            for leg in ['F'+side,'R'+side]:
                for suffix in ['P','G']+(['D'] if leg.startswith('F') else []):
                    name=('D_'+leg if suffix=='D' else leg+'_'+suffix)+'_CP2'
                    translate(d.getObject(name),'z','SideWAGOLower' if canted else parameter,-1)
        if canted:
            for leg,delta in [('FL',A.Vector(0,0,-18.6)),('FR',A.Vector(52.5,29.6,-18.6))]:
                for name in ['MTA_'+leg+'_CP2','Factory_'+leg+'_SOURCE','Factory_'+leg+'_OUTPUT']:
                    ob=d.getObject(name)
                    for axis in ['x','y','z']:ob.setExpression('Placement.Base.'+axis,None)
                    ob.Placement.Base=ob.Placement.Base+delta
                    changed[name]=None
        d.recompute()
        for name in changed:changed[name]=d.getObject(name).Shape.copy()
        group=d.addObject('App::DocumentObjectGroup','NecessaryWireEscapeBudgets')
        for terminal in terminals:
            ob=d.getObject(terminal['native']);b=ob.Shape.BoundBox
            mouth=mouths[ob.Name] if canted else [(b.XMin+b.XMax)/2,(b.YMin+b.YMax)/2,b.ZMin]
            left=terminal['native'].startswith('F_L')
            role=terminal['role']
            length=9 if canted else 19 if left and role=='OUT' else 9
            departure=departures[ob.Name] if canted else [0,0,-1]
            route=Route(terminal['wire_id']+'_NECESSARY_ESCAPE',mouth,departure,
                3.1,12.4,0,[terminal['a'],terminal['b']])
            route.line(length);route.turn([0,-1 if left else 1,0],12.4)
            edges=[Part.makeLine(A.Vector(*s['start_mm']),A.Vector(*s['end_mm']))
                if s['kind']=='line' else Part.Arc(A.Vector(*s['start_mm']),
                    A.Vector(*s['mid_mm']),A.Vector(*s['end_mm'])).toShape()
                for s in route.row['segments']]
            pipe=Part.Wire(edges).makePipeShell([Part.Wire(Part.makeCircle(1.55,
                A.Vector(*mouth),A.Vector(*departure)))],True,False)
            name=terminal['wire_id']+'_EscapeBudget'
            witness=d.addObject('Part::Feature',name);witness.Shape=pipe
            witness.addProperty('App::PropertyString','DimensionBasis')
            witness.DimensionBasis='Necessary insulation/elbow budget; NOT complete route/stock or restraint'
            group.addObject(witness);changed[name]=pipe
            if canted:
                witness.setExpression('Placement.Base.y',f'{1 if left else -1}*(ServiceZonePlan.BankLane-48 mm)')
                witness.setExpression('Placement.Base.z','ServiceZonePlan.BankFlangeZ-138 mm')
            ends.append(dict(wire_id=terminal['wire_id'],terminal=terminal['native'],
                a=terminal['a'],b=terminal['b'],mouth_mm=mouth,
                straight_mm=length,departure=departure,segments=route.row['segments'],
                full_route_qualified=False))
        d.recompute()
        # Use all relevant shape-bearing objects, not only the old inventory
        # parent allow-list: newer source/MTA groups are also critical neighbors.
        original_names={r['name'] for r in inventory_proof['components']}
        shapes={ob.Name:ob.Shape.copy() for ob in d.Objects
            if 'Shape' in ob.PropertiesList and not ob.Shape.isNull()
            and ob.Name not in ['TorsoEnvelope','BatteryNominal']
            and (ob.Name in original_names or ob.Name.endswith('_CP2')
                or any(p.Name.endswith('Candidate') for p in ob.InList))}
        shapes.update(changed)
        torso=d.getObject('TorsoEnvelope').Shape
        assert torso.isValid()
        done=set()
        own={r['wire_id']+'_EscapeBudget':r['terminal'] for r in ends}
        def check(name,s,owner,q):
            nonlocal tested
            if name==owner or own.get(name)==owner:return
            pair=tuple(sorted([name,owner]))
            if pair in done or not s.BoundBox.intersect(q.BoundBox):return
            done.add(pair);tested+=1
            try:
                assert s.isValid() and q.isValid(), 'Invalid input BRep'
                common=s.common(q);assert common.isValid(),'Invalid common BRep'
                if common.Volume>1e-5:
                    row=dict(pair=list(pair),volume_mm3=common.Volume)
                    if name.startswith('Access_') and owner.startswith('Access_'):
                        action_overlaps.append(row)
                    else:
                        row['basis']='Reservation conflict, NOT measured supplier material collision'
                        contacts.append(row)
            except Exception as error:errors.append(dict(pair=list(pair),error=str(error)))
        for name,s in changed.items():
            for owner,q in shapes.items():check(name,s,owner,q)
            if name not in service:
                assert s.isValid()
                cut=s.cut(torso);assert cut.isValid()
                if cut.Volume>1e-4:outside.append(dict(name=name,volume_mm3=cut.Volume))
        # This unchanged access used to fail against a moved left endpoint.
        # Do not rerun its other unchanged neighbor pairs.
        for name,q in changed.items():
            if name not in service:check('Access_F_PI',d.getObject('Access_F_PI').Shape,name,q)
        result=dict(status='NECESSARY_SHARED_ZONING_CLEAR' if not(contacts or errors or outside)
                else 'SHARED_ZONING_GATE_REJECTED',
            selected=False,physical_pass=False,W1_complete=False,W5_complete=False,
            plan=plan,source_sha256=pins,changed_names=sorted(changed),
            terminal_escapes=ends,exact_pairs_tested=tested,contacts=contacts,
            errors=errors,outside=outside,mutually_exclusive_access_overlaps=action_overlaps,
            remaining=['Complete all24 wires to actual receivers, not just necessary elbows',
                'All other branch/source/logic leads and connector access',
                'FHAC tethered cover motion and tool access remain prototype assumptions',
                'Native supports/strain relief and assembled service sequence',
                'One selected stock/export; each printed part fits256cube with margins'],
            started_utc=started.isoformat(),finished_utc=datetime.now(timezone.utc).isoformat(),
            worker_wall_seconds=round(time.monotonic()-tick,3))
        if not(contacts or errors or outside):
            if canted:
                original=d.getObject('F_L2_CP2_OUT').Placement.Base.z
                datum.BankFlangeZ=139;d.recompute()
                assert abs(d.getObject('F_L2_CP2_OUT').Placement.Base.z-original-1)<1e-6
                datum.BankFlangeZ=138;d.recompute()
            else:
                datum.LeftLaneShift=3;d.recompute()
                assert abs(d.getObject('F_L2_CP2_OUT').Shape.BoundBox.YMin-(52.2695+3))<1e-6
                datum.LeftLaneShift=2.5;d.recompute()
            d.saveAs(str(native));result['candidate_native_sha256']=sha(native)
            A.closeDocument(d.Name);d=A.openDocument(str(native))
            assert d.getObject('ServiceZonePlan').BankFlangeZ.Value==138 if canted else d.getObject('ServiceZonePlan').LeftLaneShift.Value==2.5
            assert all(d.getObject(name).Shape.isValid() for name in changed)
            result['parameter_restore_and_reopen']=True
        assert all(sha(ROOT/path)==digest for path,digest in pins.items())
        output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(result['status'],'pairs',tested,'contacts',len(contacts),'outside',len(outside),
            'errors',errors,'seconds',result['worker_wall_seconds'],flush=True)
        print('contacts',contacts,'outside',outside,flush=True)
    finally:A.closeDocument(d.Name)


if __name__ == '__main__':
    gate() if '--gate' in sys.argv or '--canted' in sys.argv else inventory()
