"""One open-top CP2 working assembly and shared harness contract.

Sources remain read-only. Route corridors are planning allowances, not copper
geometry, print releases or proof of electrical safety. No GUI dependencies.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import copy
import hashlib
import json
import math
import time

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'hardware/cad/studies/whole-cat-packaging/cp2'
OUT = BASE / 'open-prototype'
MOUNT = BASE / 'neck-support/main-mount-sequence'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def assign_group(roles):
    """Physical corridor assignment, not a new electrical connection."""
    text = '|'.join(roles)
    if any(r.startswith(('MAIN.', 'PI_USB_C.', 'SPLICE_PI.')) for r in roles):
        return 'MAIN_PI'
    if any(r.startswith(('BAT.', 'F0.', 'S0.', 'S1.', 'POST_F0.')) for r in roles):
        return 'SOURCE_SWITCH'
    if any(r.startswith(('F_PI.', 'F_AUX.', 'F_HY.', 'F_HP.', 'F_TY.')) for r in roles):
        return 'AUX_BRANCHES'
    for leg in ['FL', 'FR', 'RL', 'RR']:
        if any(r.startswith((leg, 'F_'+leg, 'D_'+leg)) for r in roles):
            return leg
    if any(r.startswith(('TAIL', 'C_TY.', 'G_TAIL.', 'TY.', 'JR.')) for r in roles):
        return 'TAIL'
    if any(r.startswith(('HEAD', 'C_HP.', 'C_HY.', 'HP.', 'HY.', 'JH.')) for r in roles):
        return 'HEAD'
    if any(r.startswith(('BUS.', 'USB')) for r in roles):
        return 'USB_BUS'
    return 'LOGIC_AUX'


def endpoint_plan(graph, mount, pi_origin, pi_rotation_identity):
    assert pi_rotation_identity, 'Re-derive Pi plug transform if board rotation changes'
    # Local tail coordinates from pi_power_usb_r1 + r2/r3/r4: PCB datum
    # (-19,-28,45+PI_RISE), red(-9.4,-53,48.2+PI_RISE), black(-12.6,...).
    # PI_RISE cancels. These are inherited cable allowances, NOT supplier pins.
    local = {'PI_USB_C.VBUS': [9.6,-25,3.2], 'PI_USB_C.GND': [6.4,-25,3.2]}
    datums = {}
    for row in mount['affected_main_ends']:
        datums[row['role']] = dict(point_mm=row['point_mm'], departure=[0,0,1],
            basis='Retained MAIN prototype pad at current neck mount; delivered4853 pad OPEN')
    for role, point in local.items():
        datums[role] = dict(point_mm=[a+b for a,b in zip(pi_origin,point)],
            departure=[0,-1,0], local_point_mm=point, pi_origin_mm=pi_origin,
            basis='Inherited K1474 tail/plug allowance translated with current Pi PCB datum; physical fit phase2')
    # A deliberately accessible shared splice bay, not a box centre or an
    # alleged supplier terminal. Both names describe the SAME solder overlap.
    splice = [datums['MAIN.VIN']['point_mm'][0],94,53]
    for role in ['SPLICE_PI.16','SPLICE_PI.18']:
        datums[role] = dict(point_mm=splice, departure=[0,0,1],
            basis='New prototype solder-overlap centre in outer +Y bay; not a connector pin',
            solder_overlap_mm=8, sleeve_blank_mm=20, sleeve_SKU='RNF-100-3/16-0-STK',
            installed_connection_count=1, grip='Two separate ties on intact insulation either side; mount pending')
    rows = copy.deepcopy(graph['body_conductors'])
    for row in rows:
        row['ends'] = [dict(role=e['role'], **datums[e['role']]) if e['role'] in datums else e
                       for e in row['ends']]
        row['bound_end_count'] = sum('point_mm' in e for e in row['ends'])
        row['corridor_group'] = assign_group([row['a'],row['b']])
        if row['bound_end_count']==2:
            row['straight_distance_only_mm'] = math.dist(*[e['point_mm'] for e in row['ends']])
        if any(e['role'] in datums for e in row['ends']):
            row['route_status'] = 'ENDPOINT_PLAN_ONLY; no inherited route acceptance'
        row['actual_cut_mm'] = None
    return datums, rows


def factory_splice_budget(start, end):
    """Analytical two R6 bends, downward lead then horizontal then upward.

    First/last3mm are a molded lead exit / solder approach, NOT insulation
    grips. Restraints need separate straight insulated sections on assembly.
    """
    assert abs(start[2]-end[2]) < 1e-6
    h=math.dist(start[:2],end[:2]); radius=6; straight=h-2*radius
    assert straight>9
    centreline=3+math.pi*radius+straight+3
    return dict(id='W077',centreline_mm=centreline,
        including_8mm_strip_mm=centreline+8, factory_minimum_mm=84.5,
        available_margin_mm=84.5-centreline-8,
        OD_mm=3.4,R_mm=radius,OD_R_exit_basis='Project allowance, not manufacturer bend specification',
        first_last3mm_are_NOT_insulation_grips=True,static_clearance_checked=False,
        trim_only_after_dry_fit=True)


CORRIDORS = {
    # Shared planned bundle spaces, not rigid ducts or a closed-body guarantee.
    # Upper crossovers are permitted only for the open trial configuration.
    'FL': [-70,56,150,-10,68,170], 'FR': [-70,-68,150,-10,-56,170],
    'RL': [42,56,150,112,68,170], 'RR': [42,-68,150,112,-56,170],
    'LOGIC_AUX': [-45,-10,153,112,10,171],
    'MAIN_PI': [-65,-48,65,70,-30,75],
    'HEAD': [-124,-60,125,-106,-20,145],
    'TAIL': [138,-12,145,158,12,165],
    'USB_BUS': [68,-46,65,125,-30,77],
    'AUX_BRANCHES': [-45,76,110,110,92,130],
    'SOURCE_SWITCH': [-108,-72,38,144,44,125],
}


def factory_wire_shape(A, Part, start, end):
    """R6 two-bend nominal geometry for the changed F_PI output only."""
    from whole_cat_source_bay_plan import Route
    delta=[end[0]-start[0],end[1]-start[1],0]
    h=math.hypot(delta[0],delta[1]);u=[v/h for v in delta]
    r=Route('W077',start,[0,0,-1],3.4,6,8,['F_PI.out','SPLICE_PI.16'])
    # These internal approaches intentionally do not satisfy a grip length.
    def short(length):
        target=[v+length*t for v,t in zip(r.p,r.u)]
        r.row['segments'].append(dict(kind='line',start_mm=r.p,end_mm=target,length_mm=length))
        r.p=target
    short(3);r.turn(u,6);r.line(h-12);r.turn([0,0,1],6);short(3)
    recipe=r.finish(end,[0,0,1])
    edges=[Part.makeLine(A.Vector(*s['start_mm']),A.Vector(*s['end_mm'])) if s['kind']=='line'
        else Part.Arc(A.Vector(*s['start_mm']),A.Vector(*s['mid_mm']),A.Vector(*s['end_mm'])).toShape()
        for s in recipe['segments']]
    wire=Part.Wire(edges)
    shape=wire.makePipeShell([Part.Wire([Part.makeCircle(1.7,A.Vector(*start),A.Vector(0,0,-1))])],True,False)
    assert shape.isValid() and len(shape.Solids)==1 and not shape.check(True)
    return shape,recipe


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--inventory',action='store_true')
    args=parser.parse_args()
    import FreeCAD as A
    import Part
    started=datetime.now(timezone.utc); tick=time.monotonic()
    sources=[BASE/'BoardDatumCandidate.FCStd', BASE/'whole-harness-board-plan.json',
        MOUNT/'NeckMainMount.FCStd',MOUNT/'checks.json',
        BASE/'neck-support/coupled/RightRiser_candidate.stl',
        MOUNT/'LeftRiserWithMain_candidate.stl',
        ROOT/'tools/electronics/pi_power_usb_r1.py', ROOT/'tools/electronics/pi_power_usb_r2.py',
        ROOT/'tools/electronics/pi_power_usb_r3.py', ROOT/'tools/electronics/pi_power_usb_r4.py',
        ROOT/'hardware/reference/fhac0001zxj-2026-10-02/README.md',
        ROOT/'hardware/electronics/full-cat/main-positive-wiring-card-r1/interface.json',Path(__file__)]
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in sources}
    graph=load(sources[1]);mount=load(sources[3])
    assert sha(sources[2])==mount['native_sha256']
    d=A.openDocument(str(sources[0]));m=A.openDocument(str(sources[2]))
    try:
        pi=d.getObject('Pi4_CP2'); assert pi
        pi_origin=list(pi.Placement.Base)
        rot=pi.Placement.Rotation
        identity=all((rot.multVec(A.Vector(*v))-A.Vector(*v)).Length<1e-7
                     for v in [[1,0,0],[0,1,0],[0,0,1]])
        inventory=[dict(name=o.Name,bounds_mm=[o.Shape.BoundBox.XMin,o.Shape.BoundBox.YMin,
            o.Shape.BoundBox.ZMin,o.Shape.BoundBox.XMax,o.Shape.BoundBox.YMax,o.Shape.BoundBox.ZMax])
            for o in d.Objects if 'Shape' in o.PropertiesList and not o.Shape.isNull()
            and o.Name.endswith('_CP2')]
        if args.inventory:
            print(json.dumps(dict(pi_origin_mm=pi_origin,pi_rotation_identity=identity,
                                  components=inventory),ensure_ascii=False),flush=True); return
        assert not OUT.exists(), 'Preserve result; no unchanged rebuild'
        datums,rows=endpoint_plan(graph,mount,pi_origin,identity)
        assert len(rows)==len({r['id'] for r in rows})==80
        assert {(r['id'],r['a'],r['b'],r['net']) for r in rows}=={
            (r['id'],r['a'],r['b'],r['net']) for r in graph['body_conductors']}
        fpi=next(r for r in rows if r['id']=='W077')
        factory=next(e['point_mm'] for e in fpi['ends'] if e['role']=='F_PI.out')
        budget=factory_splice_budget(factory,datums['SPLICE_PI.16']['point_mm'])
        assert budget['available_margin_mm']>0
        boundaries=copy.deepcopy(graph['distribution_boundary'])
        for row in boundaries:
            row['corridor_group']=assign_group(row['ends'])
            for role in row['ends']:
                if role in datums:row['resolved_datums'][role]=datums[role]
            row['ends_bound']=len(row['resolved_datums'])
        corridor_group=d.addObject('App::DocumentObjectGroup','SharedBundleReservations')
        for label,b in CORRIDORS.items():
            ob=d.addObject('Part::Feature','Corridor_'+label)
            ob.Shape=Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
            ob.addProperty('App::PropertyString','Status')
            ob.Status='PLANNING SPACE ONLY; not a wire, support or clearance PASS'
            corridor_group.addObject(ob)
        pipe,recipe=factory_wire_shape(A,Part,factory,datums['SPLICE_PI.16']['point_mm'])
        targets=[o for o in d.Objects if 'Shape' in o.PropertiesList and not o.Shape.isNull()
                 and (o.Name.startswith(('P0_','Head_','Tail','MTA_','F_','W0','XA','Factory_','Joint_'))
                      or o.Name.endswith('_CP2')) and not o.Name.startswith('Access_')
                 and o.Name!='MAIN4853_CP2']
        hits=[];errors=[];tested=0
        for ob in targets:
            if not pipe.BoundBox.intersect(ob.Shape.BoundBox):continue
            tested+=1
            try:
                assert ob.Shape.isValid(),'Invalid source BRep'
                common=pipe.common(ob.Shape);assert common.isValid(),'Invalid Boolean'
                if common.Volume>1e-5:hits.append(dict(part=ob.Name,volume_mm3=common.Volume,
                    reservation_or_material='Mixed actual P0 and named commercial reserves; not delivered-part fit'))
            except Exception as exc:errors.append(dict(part=ob.Name,error=str(exc)))
        factory_proof=dict(recipe=recipe,exact_pairs_tested=tested,contacts=hits,errors=errors,
            scope='Changed nominal factory output only; grips/insulation/new joint and MAIN path OPEN',
            status='STATIC_FPI_FACTORY_OUTPUT_CLEAR' if not(hits or errors) else 'FPI_OUTPUT_SHARED_LAYOUT_CHANGE_NEEDED')
        ob=d.addObject('Part::Feature','W077_PrototypeCandidate');ob.Shape=pipe
        old=d.getObject('MAIN4853_CP2');old.Placement.Base+=A.Vector(34,0,4.52)
        if old.ViewObject:old.ViewObject.Visibility=False
        group=d.addObject('App::DocumentObjectGroup','CurrentNeckMainReferences')
        for name,source in [('LeftRiserWithMain',m.LeftRiser),('RightRiser',m.RightRiser),
                            ('MainSupplierFamily',m.MainSupplierFamily)]:
            ob=d.addObject('Part::Feature',name);ob.Shape=source.Shape.copy()
            ob.addProperty('App::PropertyString','SourceDocument');ob.SourceDocument=str(sources[2].relative_to(ROOT))
            ob.addProperty('App::PropertyString','Status');ob.Status='READ_ONLY_REFERENCE; not another print'
            group.addObject(ob)
        # No source edit or fake print: saved world-space reference snapshots.
        ports=d.addObject('App::DocumentObjectGroup','PrototypeNamedDatums')
        for role,datum in datums.items():
            ob=d.addObject('Part::Feature','Datum_'+role.replace('.','_'))
            ob.Label=role;ob.Shape=Part.makeSphere(1,A.Vector(*datum['point_mm']))
            ob.addProperty('App::PropertyString','Basis');ob.Basis=datum['basis'];ports.addObject(ob)
        torso=d.getObject('TorsoEnvelope')
        if torso and torso.ViewObject:torso.ViewObject.Visibility=False
        # Service reservations are omitted from the preview only. Their earlier
        # failures remain in source proofs, not converted into positive checks.
        for ob in d.Objects:
            if ob.Name.startswith('Access_') and ob.ViewObject:ob.ViewObject.Visibility=False
        OUT.mkdir()
        native=OUT/'OpenPrototype.FCStd';d.saveAs(str(native))
        name=d.Name;A.closeDocument(name);d=A.openDocument(str(native))
        assert (d.Pi4_CP2.Placement.Base-A.Vector(*pi_origin)).Length<1e-7
        assert d.LeftRiserWithMain.Shape.isValid() and d.MainSupplierFamily.Shape.isValid()
        assert all(sha(ROOT/p)==h for p,h in pins.items()),'Source changed during checkpoint'
        methods={
            'boards':'Screws and insulating spacers at actual board holes; retain known mounts; no unsupported/glued hot boards',
            'distribution':'Separate screw-mounted PETG tie rails; each installed WAGO/oprawka mechanically retained; no complete-cassette removal requirement',
            'battery':'Retained supported P0 tray and two straps; shell is not battery support',
            'wires':'Shared bundles tied on intact insulation, edge sleeves and free slack at moving joints; solder is not a load path',
            'repair':'Power off; allow neighbouring module removal and replacement of ties; no independent 74-wire disconnect requirement',
            'source':'Retain F0/S0/manual S1 and short protected branch rules; missing E3 data not waived'}
        assignments={}
        for row in rows:assignments.setdefault(row['corridor_group'],[]).append(row['id'])
        result=dict(status='OPEN_PROTOTYPE_SHARED_LAYOUT_CHECKPOINT',selected=False,
            physical_pass=False,W1_complete=False,W5_complete=False,
            source_sha256=pins,native=native.relative_to(ROOT).as_posix(),native_sha256=sha(native),
            current_sources=dict(base=sources[0].relative_to(ROOT).as_posix(),neck_main=sources[2].relative_to(ROOT).as_posix(),
                right_print=sources[4].relative_to(ROOT).as_posix(),left_print=sources[5].relative_to(ROOT).as_posix(),
                fuse_bank='Retain R47 design; new placement/mounting qualification OPEN',historical_selection='R53; NOT current whole-prototype release'),
            topology_unchanged=True,upper_shell_required_for_first_trial=False,
            print_selection_complete=False,no_new_print_geometry=True,mount_methods=methods,
            main_datums=datums,F_PI_factory_splice_budget=budget,
            F_PI_output_proof=factory_proof,
            body_conductors=rows,distribution_boundary=boundaries,corridor_assignments=assignments,
            shared_corridors_mm=CORRIDORS,
            corridor_policy='Planning spine plus endpoint tails; not complete routes. Upper bundles may exceed cosmetic roof for open trials. Move/cut ties for fuse service; no sealed-shell qualification.',
            bound_body_ends=sum(r['bound_end_count'] for r in rows),
            missing_body_endpoint_roles=sorted({e['role'] for r in rows for e in r['ends'] if 'point_mm' not in e}),
            components=inventory,assembly_order=[
                'P0 frame/legs and retained battery support; keep both sides accessible',
                'Bench solder and insulate MAIN; neck risers and MAIN before S0',
                'Pi/BUS/logic boards on actual-hole spacers, then source switches/fuse assemblies',
                'Distribution and R47 bank retained with simple tie rails; wire before obstructing neighbour modules',
                'Complete marked bundles, strain relief and motion slack, then head/tail assemblies',
                'Local underside/terminal guards; leave upper cosmetic torso shell off',
                'Phase2 dry-fit, trim and electrical checks before any power or movement'],
            acceptance_not_waived=['E3 protection','battery retention','wiring polarity/insulation/current capability',
                'load-bearing head/tail supports','moving joints and edge clearance','256cube including print margin'],
            next_gate='One shared set of screw-mounted tie rails/board supports; verify affected bays incl F_PI solder branch and all MAIN exits before print selection',
            confirmed_result_ids=['M1','E4','A1'],result_count=3,result_denominator=20,
            counts_are_verified_minimum_not_effort_percent=True,
            started_utc=started.isoformat(),finished_utc=datetime.now(timezone.utc).isoformat(),
            worker_wall_seconds=round(time.monotonic()-tick,3),saved_reopen=True)
        (OUT/'layout.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(result['status'],'body',len(rows),'ends',result['bound_body_ends'],
              'FPI margin',round(budget['available_margin_mm'],3),'native saved/reopened',flush=True)
    finally:
        A.closeDocument(d.Name);A.closeDocument(m.Name)


if __name__=='__main__':main()
