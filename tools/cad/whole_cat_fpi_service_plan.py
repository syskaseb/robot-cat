"""Two-release F_PI service hypothesis with a real opposite-entry join.

Not a selected redesign. Gate one complete factory output and its mating
connector, then the necessary body removal corridor. Wire withdrawal/parking,
MAIN extension, clip tools and native supports must still be qualified together.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import math
import time
import sys
from whole_cat_source_bay_plan import Route

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT/'hardware/cad/studies/whole-cat-packaging/cp2'
SOURCE = BASE/'BoardDatumCandidate.FCStd'
OUT = BASE/'fpi-two-release-plan.json'
NATIVE = BASE/'FPITwoReleaseCandidate.FCStd'
SIDE_FIRST='--side-first' in sys.argv
if SIDE_FIRST:
    OUT=BASE/'fpi-side-first-plan.json'
    NATIVE=BASE/'FPISideFirstCandidate.FCStd'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def recipe(side_first=False):
    r = Route('W077_FACTORY_TO_QUICK_RELEASE', [-24,41.25,53], [0,0,-1],
              3.4, 6, 11, ['F_PI.out','SPLICE_PI.16'])
    r.line(9)
    if side_first:
        r.turn([0,1,0],6)
        r.line(9)
        r.turn([-1,0,0],6)
        r.line(9)
        end=[-39,62.25,38]
    else:
        r.turn([-1,0,0],6)
        r.line(16)
        end=[-46,41.25,38]
    row = r.finish(end,[-1,0,0],11)
    assert row['nominal_blank_mm'] <= 84.5
    return dict(factory_output=row, joint_source_port_mm=row['end_mm'],
                joint_extension_port_mm=[end[0]-35.5,end[1],end[2]],
                MAIN_extension_route_OPEN=True, removal_body_translations_mm=[[-30,0,0],[0,0,60]] if side_first else [[0,0,60]])


def main():
    import FreeCAD as A
    import Part
    started = datetime.now(timezone.utc)
    tick = time.monotonic()
    deadline=datetime.fromisoformat('2026-10-06T07:00:00+00:00')
    assert started<deadline and not OUT.exists() and not NATIVE.exists()
    plan=recipe(SIDE_FIRST)
    paths=[SOURCE,BASE/'whole-harness-board-plan.json',Path(__file__),
           ROOT/'tools/cad/whole_cat_source_bay_plan.py',
           ROOT/'hardware/reference/wago-inline-2212411/source.json']
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in paths}
    graph=json.loads(paths[1].read_text(encoding='utf-8'))
    assert sha(SOURCE)==graph['current_candidate_native_sha256']
    wago=json.loads(paths[-1].read_text(encoding='utf-8'))
    assert wago['dimensions_mm_width_height_depth']==[8.1,8.9,35.5]
    assert wago['strip_mm']==11
    assert all(wago['copper_stranded_mm2'][0] <= area <= wago['copper_stranded_mm2'][1] for area in [1.31,.823])
    d=A.openDocument(str(SOURCE))
    try:
        group=d.addObject('App::DocumentObjectGroup','FPIServiceHypothesis')
        joint=d.addObject('Part::Box','PiQuickRelease_CP2')
        joint.Length=35.5; joint.Width=8.1; joint.Height=8.9
        end=plan['joint_source_port_mm']
        joint.Placement=A.Placement(A.Vector(end[0],end[1]+4.05,end[2]-4.45),A.Rotation(A.Vector(0,0,1),180))
        # Rz180 maps both transverse dimensions negative; height remains+Z.
        group.addObject(joint)
        joint.addProperty('App::PropertyString','ElectricalRole')
        joint.ElectricalRole='Candidate replaces ONE W077/W078 solder join; NOT XB11, NOT selected'
        pieces={}
        edges=[]
        for seg in plan['factory_output']['segments']:
            if seg['kind']=='line':
                edges.append(Part.makeLine(A.Vector(*seg['start_mm']),A.Vector(*seg['end_mm'])))
            else:
                edges.append(Part.Arc(A.Vector(*seg['start_mm']),A.Vector(*seg['mid_mm']),A.Vector(*seg['end_mm'])).toShape())
        path=Part.Wire(edges)
        profile=Part.Wire(Part.makeCircle(1.7,A.Vector(-24,41.25,53),A.Vector(0,0,-1)))
        wire=path.makePipeShell([profile],True,False)
        strip=Part.makeCylinder(math.sqrt(1.31/math.pi),11,A.Vector(*end),A.Vector(-1,0,0))
        for name,s in [('W077_FACTORY_CP2',wire),('W077_FACTORY_STRIP_CP2',strip)]:
            ob=d.addObject('Part::Feature',name); ob.Shape=s;group.addObject(ob);pieces[name]=s
        d.recompute()
        pieces[joint.Name]=joint.Shape.copy()
        fixed={o.Name:o.Shape.copy() for o in d.Objects if 'Shape' in o.PropertiesList
            and not o.Shape.isNull() and o.Name not in pieces and o.Name not in ['TorsoEnvelope','BatteryNominal']
            and (any(p.Name in ['InteriorReservations','HarnessCandidate','S0TerminalCandidates',
              'S1TerminalCandidates','ServiceReservations','ATOStackCandidates'] for p in o.InList)
              or 'Category' in o.PropertiesList and o.Category!='electronics')}
        contacts=[];errors=[];tested=0; action_reservation_overlaps=[]
        excluded={'W077_FACTORY_CP2':{'F_PI_CP2'},'W077_FACTORY_STRIP_CP2':{'PiQuickRelease_CP2'}}
        def check(name,s,others,exclusions=(),service_motion=False):
            nonlocal tested
            assert s.isValid() and len(s.Solids)==1
            for owner,q in others.items():
                if owner in exclusions or not s.BoundBox.intersect(q.BoundBox):continue
                tested+=1
                try:
                    assert q.isValid(), 'Invalid input BRep'
                    c=s.common(q);assert c.isValid(), 'Invalid common BRep'
                    if c.Volume>1e-5:
                        row=dict(pair=[name,owner],volume_mm3=c.Volume)
                        if service_motion and owner.startswith('Access_'):
                            row['basis']='Two mutually-exclusive maintenance actions; NOT physical part clearance'
                            action_reservation_overlaps.append(row)
                        else:contacts.append(row)
                except Exception as error:errors.append(dict(pair=[name,owner],error=str(error)))
                assert datetime.now(timezone.utc)<deadline
        for name,s in pieces.items():check(name,s,fixed,excluded.get(name,set()))
        check('W077_FACTORY_CP2',wire,{'PiQuickRelease_CP2':pieces[joint.Name]})
        # Exact swept rectangle of the nominal axis-aligned body, NOT lid
        # opening. Both loose leads must first be parked, not omitted as a pass.
        body=d.getObject('F_PI_CP2').Shape;b=body.BoundBox
        assert abs(body.Volume-b.XLength*b.YLength*b.ZLength)<1e-5
        lift_contacts_before=len(contacts)
        if SIDE_FIRST:
            swept=Part.makeBox(b.XLength+30,b.YLength,b.ZLength,A.Vector(b.XMin-30,b.YMin,b.ZMin))
            check('F_PI_BODY_SIDE30_AFTER_LEAD_PARKING_OPEN',swept,fixed,
                {'F_PI_CP2','Access_F_PI','W043_SHORT_CP2','W043_SHORT_STRIP_CP2'},True)
            swept=Part.makeBox(b.XLength,b.YLength,b.ZLength+60,A.Vector(b.XMin-30,b.YMin,b.ZMin))
        else:
            swept=Part.makeBox(b.XLength,b.YLength,b.ZLength+60,A.Vector(b.XMin,b.YMin,b.ZMin))
        check('F_PI_BODY_LIFT60_AFTER_LEAD_PARKING_OPEN',swept,fixed,
              {'F_PI_CP2','Access_F_PI','W043_SHORT_CP2','W043_SHORT_STRIP_CP2'},SIDE_FIRST)
        lift_contacts=contacts[lift_contacts_before:]
        remaining=[name for name,s in pieces.items() if s.cut(d.getObject('TorsoEnvelope').Shape).Volume>1e-5]
        result=dict(status='TWO_RELEASE_STATIC_SOURCE_JOIN_CANDIDATE_SERVICE_OPEN' if not(contacts or errors or remaining) else 'TWO_RELEASE_HYPOTHESIS_REQUIRES_SHARED_CHANGE',
            selected=False,physical_pass=False,W1_complete=False,W5_complete=False,
            source_sha256=pins,recipe=plan,contacts=contacts,errors=errors,
            exact_pairs_tested=tested,outside=remaining,body_lift_contacts=lift_contacts,
            action_reservation_overlaps=action_reservation_overlaps,
            routine_releases=[dict(owner='P_SYS.2',end='W043 bare11..14mm; isolate and lever-release'),
                dict(owner='PiQuickRelease source side',end='W077 factory lead; lever-release11mm')],
            not_74_WAGO_wire_releases=True,
            topology=dict(retained_edges=['W043','W077','W078'],changed_physical_join='SPLICE_PI solder -> candidate2212411',
                P_AUX_XB11_NOT_changed=True,no_added_power_net=True,F_PI_input_below50_retained=True),
            candidate_stock_delta=dict(inline2212411_installed=1,solder_join_removed=1,
                old_solder_sleeves_not_double_counted=True,ties_and_mount_not_selected=True),
            service_steps=['No powered service; phase2 source isolation and absence-of-voltage verification.',
                'Remove dorsal shell only, leave main distribution mounted.',
                'Open P_SYS.2 and PiQuickRelease SOURCE lever, withdraw only these two factory ends.',
                'Release insulation restraints and park both bare ends insulated; exact length/radius/path OPEN.',
                'Release F_PI dock clips/tool access OPEN; shift body-30X first, THEN lift60Z; necessary body corridor only.' if SIDE_FIRST else 'Release F_PI dock clips/tool access OPEN, lift body60mm through the checked necessary corridor.',
                'Open lid outside assembled bank; reverse sequence and recheck markings/retention.'],
            open=['Factory end withdrawal and constant-length insulated parking, especially W043 near P_SYS',
                'Exact lever access and dock clips/tools/supports', 'Full W078 MAIN extension/terminal/length/restraints',
                'Output join/lead installation with unchanged whole harness and cover removal',
                'Single selected stock/export and E3 coordination'],
            old_in_place_lid_conflict_NOT_waived=True,body_corridor_not_complete_service=True,
            started_utc=started.isoformat(),finished_utc=datetime.now(timezone.utc).isoformat(),
            worker_wall_seconds=round(time.monotonic()-tick,3))
        if not(errors or remaining):
            d.saveAs(str(NATIVE));result['candidate_native_sha256']=sha(NATIVE)
            A.closeDocument(d.Name);d=A.openDocument(str(NATIVE))
            assert d.getObject('PiQuickRelease_CP2').Shape.isValid()
            result['saved_reopen']=True
        OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        assert all(sha(ROOT/p)==h for p,h in pins.items())
        print(result['status'],'pairs',tested,'contacts',contacts,'outside',remaining,'errors',errors,flush=True)
    finally:A.closeDocument(d.Name)


def lid_inward():
    """Change opening direction, not position, after two failed removal routes.

Keep BOTH original exit points, the short prefuse and the solder topology.
This tests an in-place approach; generic lid/tool budget is not hinge geometry.
"""
    import FreeCAD as A
    started=datetime.now(timezone.utc);tick=time.monotonic()
    deadline=datetime.fromisoformat('2026-10-06T07:00:00+00:00')
    output=BASE/'fpi-inward-lid-plan.json';native=BASE/'FPIInwardCandidate.FCStd'
    assert started<deadline and not output.exists() and not native.exists()
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in [SOURCE,Path(__file__),BASE/'branch-source-static-checks.json']}
    d=A.openDocument(str(SOURCE))
    try:
        body=d.getObject('F_PI_CP2');access=d.getObject('Access_F_PI')
        before=body.Placement
        local=[A.Vector(51,10.125,10),A.Vector(0,10.125,10)]
        exits=[before.multVec(p) for p in local]
        rotation=A.Rotation(A.Vector(0,0,1),-90).multiply(before.Rotation)
        after=A.Placement(exits[0]-rotation.multVec(local[0]),rotation)
        body.Placement=after
        access.Placement=after.multiply(before.inverse()).multiply(access.Placement)
        d.recompute()
        assert all((body.Placement.multVec(p)-old).Length<1e-7 for p,old in zip(local,exits))
        fixed={o.Name:o.Shape.copy() for o in d.Objects if 'Shape' in o.PropertiesList
            and not o.Shape.isNull() and o.Name not in [body.Name,access.Name,'TorsoEnvelope','BatteryNominal']
            and (any(p.Name in ['InteriorReservations','HarnessCandidate','S0TerminalCandidates',
                'S1TerminalCandidates','ServiceReservations','ATOStackCandidates'] for p in o.InList)
                or 'Category' in o.PropertiesList and o.Category!='electronics')}
        contacts=[];action=[];errors=[];tested=0
        for ob in [body,access]:
            s=ob.Shape;assert s.isValid() and len(s.Solids)==1
            for name,q in fixed.items():
                if not s.BoundBox.intersect(q.BoundBox):continue
                tested+=1
                try:
                    assert q.isValid();common=s.common(q);assert common.isValid()
                    if common.Volume>1e-5:
                        row=dict(pair=[ob.Name,name],volume_mm3=common.Volume)
                        if ob==access and name.startswith('Access_'):action.append(row)
                        else:contacts.append(row)
                except Exception as error:errors.append(dict(pair=[ob.Name,name],error=str(error)))
                assert datetime.now(timezone.utc)<deadline
        result=dict(status='INWARD_LID_NOMINAL_APPROACH_CLEAR' if not(contacts or errors) else 'INWARD_LID_APPROACH_REQUIRES_SHARED_CHANGE',
            selected=False,physical_pass=False,W1_complete=False,W5_complete=False,
            source_sha256=pins,body_rotation_z_delta_deg=-90,unchanged_exit_points_mm=[list(p) for p in exits],
            unchanged_short_input=True,unchanged_output_solder_topology=True,new_connectors=0,
            exact_pairs_tested=tested,contacts=contacts,errors=errors,mutually_exclusive_service_budgets=action,
            nominal_opening_direction=list(rotation.multVec(A.Vector(0,0,1))),
            cause_change='Lid opens inward in place, NOT vertical/side removal of oprawka past fixed MTA/S0',
            actual_supplier_hinge_motion_OPEN=True,cover_removal_and_native_mount_OPEN=True,
            own_input_wire_contact_NOT_waived=True,
            remaining=['Exact or explicit replaceable lid/clip tool approach','Full output and other branch leads','Native supports/restraints and common assembly/stock'],
            started_utc=started.isoformat(),finished_utc=datetime.now(timezone.utc).isoformat(),worker_wall_seconds=round(time.monotonic()-tick,3))
        if not(contacts or errors):
            d.saveAs(str(native));result['candidate_native_sha256']=sha(native)
            A.closeDocument(d.Name);d=A.openDocument(str(native))
            assert d.getObject('F_PI_CP2').Shape.isValid();result['saved_reopen']=True
        output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        assert all(sha(ROOT/p)==h for p,h in pins.items())
        print(result['status'],'pairs',tested,'contacts',contacts,'errors',errors,flush=True)
    finally:A.closeDocument(d.Name)


if __name__=='__main__':
    lid_inward() if '--inplace-inward' in sys.argv else main()
