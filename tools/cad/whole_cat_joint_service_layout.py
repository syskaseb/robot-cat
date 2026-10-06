"""One coupled CP2 allocation, before supports or complete harness claims.

Retain the proven short F_PI input and move F_AUX/P_REAR/XA01 as a cell.
Read existing native geometry; do not edit selected R53 or retry this recipe.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import math
import time

from whole_cat_source_bay_plan import Route

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'hardware/cad/studies/whole-cat-packaging/cp2'
SOURCE = BASE / 'BoardDatumCandidate.FCStd'
OUTPUT = BASE / 'joint-service-layout.json'
NATIVE = BASE / 'JointServiceLayoutCandidate.FCStd'


def recipe():
    return dict(
        family='ALL_FUSE_CELLS_AND_MTA_SHARED_ALLOCATION',
        bank_tilt_deg=30, bank_lane_y_mm=48, bank_flange_z_mm=138,
        bank_shift_x_mm=7, side_WAGO_lower_z_mm=10,
        MTA_centres_mm={'FL': [18, 23, 119], 'FR': [18, -23, 119],
                        'RL': [82, 23, 119], 'RR': [82, -23, 119]},
        AUX_cell_translation_mm=[-90, 20, 3],
        AUX_cell_members=['F_AUX_CP2', 'Access_F_AUX', 'P_REAR_CP2',
                          'XA01_SHORT_CP2', 'XA01_SHORT_STRIP_CP2'],
        head_tail_centres_mm={'F_HP_CP2': [-27, -28, 116],
                              'F_TY_CP2': [-100, 44, 122]},
        F_TY_rotate_z_deg=180,
        P_FRONT_translation_mm=[98, 0, 0], F_PWM_centre_mm=[-7.75, 0, 115],
        preserved=['P0/E6/15 actuators/replaceable MG92B', 'Torso325x200x160',
                   'Source/S0/S1/Pi/controller boards',
                   'F_PI/P_SYS/W043 and Pi solder topology',
                   'F_HY and its service direction', 'Both sides of all4MTA'],
        cause_change='Allocate all fuse bodies and service budgets together; '
                     'retain short-input mates as one cell, not independent offsets',
        derivation=dict(S0_key_to_left_bank_service_X_gap_mm=2,
            MTA_bottom_to_controller_top_mm=3,
            MTA_top_to_relocated_AUX_bottom_mm=3.5,
            XA01_rigid_translation_preserves_29mm_blank=True),
        invalidated=['24ATO ends/routes/supports', '10 side WAGO ports/routes/supports',
                     '4MTA positions/all8 complete leads/mates/supports',
                     'P_FRONT/P_REAR ports and all affected connected routes',
                     'F_HP/F_TY/F_PWM ends/routes/supports',
                     'AUX output and full assembly/shell mounting'],
        assumptions='FHAC thickness22/OD3.4/R6 and40mm access remain provisional; '
                    'MTA factory length/lead class and terminal seating need supplied parts',
        complete_harness=False, physical_pass=False, selected=False)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    import FreeCAD as A
    import Part
    started = datetime.now(timezone.utc); tick = time.monotonic()
    assert not OUTPUT.exists() and not NATIVE.exists(), 'Receive result; no unchanged retry'
    plan = recipe()
    paths = [SOURCE, Path(__file__), BASE / 'ato-stack-checks.json',
             BASE / 'service-zone-inventory.json', BASE / 'whole-harness-board-plan.json']
    pins = {p.relative_to(ROOT).as_posix(): digest(p) for p in paths}
    inventory = json.loads(paths[3].read_text(encoding='utf-8'))
    assert inventory['source_native_sha256'] == digest(SOURCE)
    terminals = json.loads(paths[2].read_text(encoding='utf-8'))['terminal_datums']
    d = A.openDocument(str(SOURCE))
    changed = set(); services = set(); mouths = {}; departures = {}; escapes = []
    try:
        datum = d.addObject('App::FeaturePython', 'JointServiceAllocation')
        datum.addProperty('App::PropertyLength', 'BankShiftX'); datum.BankShiftX = 7
        def clear_position(ob):
            for axis in 'xyz': ob.setExpression('Placement.Base.' + axis, None)
        def transform(ob, placement):
            clear_position(ob); ob.Placement = placement.multiply(ob.Placement)
            changed.add(ob.Name)
            if ob.Name.startswith('Access_'): services.add(ob.Name)
        def shift(name, delta):
            transform(d.getObject(name), A.Placement(A.Vector(*delta), A.Rotation()))
        def move_centre(name, centre, angle=0):
            ob = d.getObject(name); b = ob.Shape.BoundBox
            old = A.Vector((b.XMin+b.XMax)/2, (b.YMin+b.YMax)/2, (b.ZMin+b.ZMax)/2)
            rot = A.Rotation(A.Vector(0,0,1), angle)
            placement = A.Placement(A.Vector(*centre) - rot.multVec(old), rot)
            transform(ob, placement)
            return placement
        for ob in list(d.Objects):
            if ob.Name.startswith(('F_L', 'F_R', 'Access_F_L', 'Access_F_R')):
                side = 1 if '_L' in ob.Name else -1
                rotation = A.Rotation(A.Vector(1,0,0), side*30)
                old_axis = A.Vector(0, side*62, 126)
                new_axis = A.Vector(7, side*48, 138)
                placement = A.Placement(new_axis-rotation.multVec(old_axis), rotation)
                if ob.Name.endswith(('_IN','_OUT')):
                    b = ob.Shape.BoundBox
                    mouths[ob.Name] = list(placement.multVec(A.Vector(
                        (b.XMin+b.XMax)/2, (b.YMin+b.YMax)/2, b.ZMin)))
                    departures[ob.Name] = list(rotation.multVec(A.Vector(0,0,-1)))
                transform(ob, placement)
                ob.setExpression('Placement.Base.x', f'{ob.Placement.Base.x} mm+'
                                 'JointServiceAllocation.BankShiftX-7 mm')
        for side in 'LR':
            for leg in ['F'+side, 'R'+side]:
                for suffix in ['P','G'] + (['D'] if leg.startswith('F') else []):
                    shift(('D_'+leg if suffix=='D' else leg+'_'+suffix)+'_CP2', [0,0,-10])
        for leg, centre in plan['MTA_centres_mm'].items():
            ob=d.getObject('MTA_'+leg+'_CP2'); b=ob.Shape.BoundBox
            old=[(b.XMin+b.XMax)/2,(b.YMin+b.YMax)/2,(b.ZMin+b.ZMax)/2]
            delta=[v-a for v,a in zip(centre,old)]
            for name in ['MTA_'+leg+'_CP2', 'Factory_'+leg+'_SOURCE', 'Factory_'+leg+'_OUTPUT']:
                shift(name,delta)
        for name in plan['AUX_cell_members']: shift(name,plan['AUX_cell_translation_mm'])
        for name, centre in plan['head_tail_centres_mm'].items():
            placement=move_centre(name,centre,180 if name=='F_TY_CP2' else 0)
            transform(d.getObject('Access_'+name.removesuffix('_CP2')),placement)
        shift('P_FRONT_CP2',plan['P_FRONT_translation_mm'])
        move_centre('F_PWM_CP2',plan['F_PWM_centre_mm'])
        d.recompute()
        original_names={r['name'] for r in inventory['components']}
        shapes={ob.Name:ob.Shape.copy() for ob in d.Objects
            if 'Shape' in ob.PropertiesList and not ob.Shape.isNull()
            and ob.Name not in ['TorsoEnvelope','BatteryNominal']
            and (ob.Name in original_names or ob.Name.endswith('_CP2')
                 or any(p.Name.endswith('Candidate') for p in ob.InList))}
        own={}; routes={}
        def pipe(row, owner):
            edges=[Part.makeLine(A.Vector(*s['start_mm']),A.Vector(*s['end_mm']))
                if s['kind']=='line' else Part.Arc(A.Vector(*s['start_mm']),
                    A.Vector(*s['mid_mm']),A.Vector(*s['end_mm'])).toShape()
                for s in row['segments']]
            profile=Part.Wire(Part.makeCircle(row['OD_mm']/2,
                A.Vector(*row['start_mm']),A.Vector(*row['segments'][0]['tangent'])))
            shape=Part.Wire(edges).makePipeShell([profile],True,False)
            assert shape.isValid() and len(shape.Solids)==1
            name=row['id']; shapes[name]=shape; changed.add(name); own[name]=owner
            escapes.append(row); routes[name]=shape
        for terminal in terminals:
            left=terminal['native'].startswith('F_L')
            row=Route(terminal['wire_id']+'_ESCAPE',mouths[terminal['native']],
                departures[terminal['native']],3.1,12.4,0,[terminal['a'],terminal['b']])
            row.line(9); row.turn([0,-1 if left else 1,0],12.4)
            pipe(row.row,terminal['native'])
        # Only necessary factory runouts; they do not invent remaining mates or lengths.
        for leg in 'FL FR RL RR'.split():
            for role in ['SOURCE','OUTPUT']:
                name='Factory_'+leg+'_'+role
                b=shapes[name].BoundBox
                direction=[-1 if role=='SOURCE' else 1,0,0]
                start=[b.XMin if role=='SOURCE' else b.XMax,
                       (b.YMin+b.YMax)/2,(b.ZMin+b.ZMax)/2]
                row=Route(name+'_ESCAPE',start,direction,4.2,25.2,0,[])
                row.line(9); row.turn([0,0,-1],25.2)
                pipe(row.row,'MTA_'+leg+'_CP2'); own[name+'_ESCAPE']=name
        # Reuse W043 and rigidly translated XA01. Both remain full short-input geometries.
        for role in ['F_PI','F_AUX','F_HY','F_HP','F_TY']:
            ob=d.getObject(role+'_CP2')
            for port in ['IN','OUT']:
                if port=='IN' and role in ['F_PI','F_AUX']: continue
                positive=(port=='IN') if role=='F_PI' else (port=='OUT')
                point=ob.Placement.multVec(A.Vector(51 if positive else 0,10.125,10))
                direction=ob.Placement.Rotation.multVec(A.Vector(1 if positive else -1,0,0))
                # Vertical holders turn toward the centre; horizontal ones escape down.
                turn=[1,0,0] if abs(direction.z)>.5 else [0,0,-1]
                row=Route(role+'_'+port+'_ESCAPE',list(point),list(direction),3.4,6,0,[])
                row.line(9);row.turn(turn,6);pipe(row.row,ob.Name)
        torso=d.getObject('TorsoEnvelope').Shape
        contacts=[];errors=[];outside=[];exclusive=[];done=set(); tested=0
        for name in sorted(changed):
            shape=shapes[name]
            if name not in services:
                try:
                    assert shape.isValid() and torso.isValid()
                    cut=shape.cut(torso);assert cut.isValid()
                    if cut.Volume>1e-4:outside.append(dict(name=name,volume_mm3=cut.Volume))
                except Exception as err:errors.append(dict(name=name,error=str(err)))
            for other,q in shapes.items():
                pair=tuple(sorted([name,other]))
                if name==other or pair in done or own.get(name)==other or own.get(other)==name:
                    continue
                # The exit budgets share a designed mouth with their own housing.
                if name.endswith('_ESCAPE') and name.startswith('Factory_') and other=='MTA_'+name.split('_')[1]+'_CP2':continue
                if other.endswith('_ESCAPE') and other.startswith('Factory_') and name=='MTA_'+other.split('_')[1]+'_CP2':continue
                if not shape.BoundBox.intersect(q.BoundBox):continue
                done.add(pair);tested+=1
                try:
                    assert shape.isValid() and q.isValid(),'Invalid source BRep'
                    common=shape.common(q);assert common.isValid(),'Invalid Boolean'
                    if common.Volume>1e-5:
                        row=dict(pair=pair,volume_mm3=common.Volume,
                            basis='Reservation conflict, not measured supplier plastic collision')
                        (exclusive if all(p.startswith('Access_') for p in pair) else contacts).append(row)
                except Exception as err:errors.append(dict(pair=pair,error=str(err)))
        result=dict(status='NECESSARY_SHARED_ALLOCATION_CLEAR' if not(contacts or errors or outside)
                          else 'NECESSARY_SHARED_ALLOCATION_REJECTED',
            selected=False,physical_pass=False,W1_complete=False,W5_complete=False,
            recipe=plan,source_sha256=pins,changed_names=sorted(changed),
            necessary_escapes=escapes,exact_pairs_tested=tested,contacts=contacts,
            errors=errors,outside=outside,exclusive_service_overlaps=exclusive,
            remaining=['Full routes with exact a/b mapping, all8MTA mates/lengths',
                'Remaining FHAC inputs/outputs and <=50mm constraints where applicable',
                'Native supports/restraints and assembly/removal including tools',
                'Supplier-qualified lid/levers and supplied lead/terminal geometry',
                'One stock/export and segmented printed parts within256cube with margin'],
            started_utc=started.isoformat(),finished_utc=datetime.now(timezone.utc).isoformat(),
            worker_wall_seconds=round(time.monotonic()-tick,3))
        if not(contacts or errors or outside):
            initial=d.getObject('F_L2_CP2_OUT').Placement.Base.x
            datum.BankShiftX=8;d.recompute()
            assert abs(d.getObject('F_L2_CP2_OUT').Placement.Base.x-initial-1)<1e-7
            datum.BankShiftX=7;d.recompute()
            # Save native bodies, not separate per-shape caches.
            group=d.addObject('App::DocumentObjectGroup','NecessaryRunoutReservations')
            for name,shape in routes.items():
                ob=d.addObject('Part::Feature',name);ob.Shape=shape;group.addObject(ob)
                ob.addProperty('App::PropertyString','DimensionBasis')
                ob.DimensionBasis='Necessary lead reservation only; complete route/mount/stock OPEN'
            d.saveAs(str(NATIVE));result['candidate_native_sha256']=digest(NATIVE)
            A.closeDocument(d.Name);d=A.openDocument(str(NATIVE))
            assert all(d.getObject(n).Shape.isValid() for n in changed)
            result['parameter_restore_and_reopen']=True
        assert all(digest(ROOT/path)==value for path,value in pins.items())
        OUTPUT.write_text(json.dumps(result,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
        print(result['status'],tested,'pairs',len(contacts),'contacts',len(outside),
              'outside',len(errors),'errors',result['worker_wall_seconds'],'seconds',flush=True)
        for row in contacts+outside+errors:print(row,flush=True)
    finally:A.closeDocument(d.Name)


if __name__=='__main__':main()
