"""One coupled F_PI/F_AUX short-input plan; no extension waives prefuse limits.

Preserve the four MTA layout and full ATO stack. Reassign two source receivers
with both branch exits and transformed access budgets before native mounts.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import itertools
import json
import math
import time
import sys
from whole_cat_source_bay_plan import Route, add, scale
from whole_cat_interior import splice_inventory

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'hardware/cad/studies/whole-cat-packaging/cp2'
SOURCE = BASE / 'MTAHorizontalCandidate.FCStd'
OUT = BASE / 'branch-source-common-checks.json'
NATIVE = BASE / 'BranchSourceCandidate.FCStd'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def recipe(layered=False):
    pi_y=41.25 if layered else 40
    pi = Route('W043', [-24,pi_y,104], [0,0,1], 3.4, 6, 14, ['F_PI.in','P_SYS.2'])
    pi.line(9); pi.turn([0,-1,0], 6); pi.line(pi_y-6-23.5)
    rows = [pi.finish([-24,23.5,119], [0,-1,0])]
    start, target = ([87.5,-17,137.5], [72.5,-17,137.5]) if layered else ([102.5,-12,124], [72.5,-17,115.5])
    delta = [0, -5, -8.5]
    h = math.sqrt(5**2 + 8.5**2)
    theta = math.acos(1 - h / 12)
    advance = 12 * math.sin(theta)
    leading = start[0] - target[0] - advance - 9
    if not layered:assert leading >= 9, leading
    aux = Route('XA01', start, [-1,0,0], 3.4, 6, 14, ['F_AUX.in','P_REAR.5'])
    if layered:
        # One15mm straight satisfies both9mm runouts; do not double-count
        # two collinear end reservations as an artificial18mm minimum.
        aux.line(15)
    else:
        aux.line(leading); aux.shift(delta,6); aux.line(9)
    rows.append(aux.finish(target,[-1,0,0]))
    assert all(row['nominal_blank_mm'] <= 50 for row in rows)
    return dict(F_PI=dict(exit_mm=[-24,pi_y,104], length=51,
        rotation='Rz180*Ry-90: input+Z, output-Z, lid+X'),
        F_AUX=dict(exit_mm=start, origin_mm=[start[0],start[1]-10.125,start[2]-10],
            output_exit_mm=[start[0]+51,start[1],start[2]]),
        P_FRONT=dict(origin_mm=[-26.5,-11,129.5], entry='+Y', centre_mm=[-8,0,135]),
        G2=None if layered else dict(origin_mm=[114,-9.5,61], centre_mm=[129,0,65.5]),
        P_REAR=dict(origin_mm=[50.5,18.5,132], rotation_z=-90) if layered else None,
        routes=rows,
        cause_change='Move P_REAR/F_AUX together above rear MTA, not into rear tail mount; retain G2 clear of S1 tools' if layered else 'Initial branch-only level allocation',
        assumptions='FHAC exits/OD3.4/R6 and WAGO port pitch provisional; physical cut after fit',
        constraints='F_PI/XA01 <=50mm includes14mm entry strip; no extra prefuse splice',
        pending_outputs=['F_PI.out -> insulated Pi solder splice -> MAIN.VIN',
            'F_AUX.out -> AUX.VIN; actual pad and factory lead budget required'])


def main():
    import FreeCAD as A
    import Part
    start = datetime.now(timezone.utc); tick = time.monotonic()
    save_static='--save-static-layer' in sys.argv
    layered='--layered-sources' in sys.argv or save_static
    output=BASE/'branch-source-static-checks.json' if save_static else BASE/'branch-source-layered-checks.json' if layered else OUT
    deadline = datetime.fromisoformat('2026-10-06T07:00:00+00:00')
    assert start < deadline and not output.exists(), 'No unchanged retry/deadline'
    plan = recipe(layered)
    reused=None
    if save_static:
        reused=json.loads((BASE/'branch-source-layered-checks.json').read_text(encoding='utf-8'))
        assert reused['recipe']==plan and not reused['outside'] and not reused['errors']
        assert reused['contacts'] and all(c['pair'][0]=='Access_F_PI' for c in reused['contacts'])
        assert sha(SOURCE)==reused['source_sha256'][SOURCE.relative_to(ROOT).as_posix()]
    inputs = [SOURCE, BASE/'whole-harness-shared-plan.json', Path(__file__),
        ROOT/'tools/cad/whole_cat_source_bay_plan.py', ROOT/'tools/cad/whole_cat_interior.py']
    pins = {p.relative_to(ROOT).as_posix():sha(p) for p in inputs}
    d = A.openDocument(str(SOURCE))
    changed = {}; service = set(); exclude = {}
    try:
        def relocate(name, placement):
            ob=d.getObject(name); old=ob.Placement
            ob.Placement=placement
            changed[name]=ob.Shape.copy()
            access=d.getObject('Access_'+name.removesuffix('_CP2'))
            if access:
                access.Placement=placement.multiply(old.inverse()).multiply(access.Placement)
                changed[access.Name]=access.Shape.copy();service.add(access.Name)
                exclude[access.Name]={name}
        rot=A.Rotation(A.Vector(0,0,1),180).multiply(A.Rotation(A.Vector(0,1,0),-90))
        # Local exit at[51,10.125,10], not bbox centre. Lid opens+X.
        origin=A.Vector(*plan['F_PI']['exit_mm'])-rot.multVec(A.Vector(51,10.125,10))
        relocate('F_PI_CP2', A.Placement(origin,rot))
        relocate('F_AUX_CP2',A.Placement(A.Vector(*plan['F_AUX']['origin_mm']),A.Rotation()))
        for role in ['P_FRONT','G2','P_REAR']:
            if plan[role] is None:continue
            rotation=A.Rotation(A.Vector(0,0,1),plan[role].get('rotation_z',0))
            relocate(role+'_CP2',A.Placement(A.Vector(*plan[role]['origin_mm']),rotation))
        # Correct logical allocation only in this new unselected candidate.
        xb=d.getObject('Splice_L1_CP2')
        xb.Label='XB11 AUX6 to F_HY input; NOT Pi solder joint'
        for prop in ['ElectricalRole','CircuitEnds']:
            if prop not in xb.PropertiesList:xb.addProperty('App::PropertyString',prop)
        xb.ElectricalRole='XB11';xb.CircuitEnds='P_AUX.2 -> F_HY.in, via HELU23502 extension'
        wire_group=d.getObject('HarnessCandidate')
        for row in plan['routes']:
            edges=[]
            for segment in row['segments']:
                if segment['kind']=='line':
                    edges.append(Part.makeLine(A.Vector(*segment['start_mm']),A.Vector(*segment['end_mm'])))
                else:
                    edges.append(Part.Arc(A.Vector(*segment['start_mm']),
                        A.Vector(*segment['mid_mm']),A.Vector(*segment['end_mm'])).toShape())
            path=Part.Wire(edges)
            profile=Part.Wire(Part.makeCircle(row['OD_mm']/2,
                A.Vector(*row['start_mm']),A.Vector(*row['segments'][0]['tangent'])))
            shape=path.makePipeShell([profile],True,False)
            name=row['id']+'_SHORT_CP2'
            ob=d.addObject('Part::Feature',name);ob.Shape=shape;wire_group.addObject(ob)
            changed[name]=shape
            own=['F_PI_CP2','P_SYS_CP2'] if row['id']=='W043' else ['F_AUX_CP2','P_REAR_CP2']
            exclude[name]=set(own)
            strip=Part.makeCylinder(math.sqrt(1.31/math.pi),14,
                A.Vector(*row['end_mm']),A.Vector(*row['end_tangent']))
            sn=row['id']+'_SHORT_STRIP_CP2'
            ob=d.addObject('Part::Feature',sn);ob.Shape=strip;wire_group.addObject(ob)
            changed[sn]=strip;exclude[sn]=set(own+[name]);exclude[name].add(sn)
        d.recompute()
        for name in changed:changed[name]=d.getObject(name).Shape.copy()
        fixed={o.Name:o.Shape.copy() for o in d.Objects if 'Shape' in o.PropertiesList
            and o.Name not in changed and o.Name not in ['TorsoEnvelope','BatteryNominal']
            and (any(p.Name in ['InteriorReservations','HarnessCandidate','S0TerminalCandidates',
                'S1TerminalCandidates','ServiceReservations','ATOStackCandidates'] for p in o.InList)
                or 'Category' in o.PropertiesList and o.Category!='electronics')}
        contacts=[];outside=[];errors=[];tested=0
        def compare(na,a,nb,b):
            nonlocal tested
            if nb in exclude.get(na,set()) or na in exclude.get(nb,set()):return
            if not a.BoundBox.intersect(b.BoundBox):return
            tested+=1
            try:
                assert a.isValid() and b.isValid(), 'Invalid BRep input'
                c=a.common(b)
                assert c.isValid(), 'Invalid common'
                if c.Volume>1e-5:contacts.append(dict(pair=[na,nb],volume_mm3=c.Volume,
                    basis='Actual pipe/retained shape versus named provisional reservation, not supplier material fit'))
            except Exception as error:errors.append(dict(pair=[na,nb],error=str(error)))
        for name,shape in changed.items():
            assert shape.isValid() and len(shape.Solids)==1, name
            if not reused:
                for other,static in fixed.items():compare(name,shape,other,static)
            if name not in service and not reused:
                remaining=shape.cut(d.getObject('TorsoEnvelope').Shape)
                assert remaining.isValid()
                if remaining.Volume>1e-5:outside.append(dict(name=name,volume_mm3=remaining.Volume))
            assert datetime.now(timezone.utc)<deadline, 'Deadline during shared gate'
        if reused:
            contacts=reused['contacts'];tested=reused['exact_BRep_pairs_tested']
        else:
            for na,nb in itertools.combinations(changed,2):compare(na,changed[na],nb,changed[nb])
        clear=not(contacts or outside or errors)
        proof=dict(status='STATIC_TWO_SHORT_INPUTS_CLEAR_SERVICE_OPEN' if reused else 'TWO_SHORT_INPUTS_SHARED_CLEAR' if clear else 'TWO_SHORT_INPUTS_SHARED_REQUIRES_CHANGE',
            selected=False,physical_pass=False,W1_complete=False,W5_complete=False,
            source_sha256=pins, recipe=plan, exact_BRep_pairs_tested=tested,
            contacts=contacts,outside=outside,errors=errors, changed_parts=sorted(changed),
            retained_MTA_and_ATO_not_rerun=True, current_splice_identity=splice_inventory(),
            outputs_and_all_other_wires_remain_OPEN=True,
            invalidated_routes=['W041/W042/W064 target P_FRONT changed',
                'W044/W052/W065 target P_REAR changed' if layered else 'W003/W061/W062/W063 and AUX references to G2 changed',
                'W077/W078 and XA02 output factory leads changed'],
            native_supports_and_grips_OPEN=True, entry_levers_and_fuse_lid_motion_provisional=True)
        if reused:
            proof['static_body_pipe_and_strip_contacts']=[]
            proof['gate_reused_not_rerun']=dict(recipe_identical=True,
                checked_gate_sha256=sha(BASE/'branch-source-layered-checks.json'),
                service_conflict_NOT_waived=True, all_FHAC_service_qualified=False)
        if clear or reused:
            d.saveAs(str(NATIVE));proof['candidate_native_sha256']=sha(NATIVE)
            expected={n:dict(volume=s.Volume,bbox=[s.BoundBox.XMin,s.BoundBox.YMin,s.BoundBox.ZMin,
                s.BoundBox.XMax,s.BoundBox.YMax,s.BoundBox.ZMax]) for n,s in changed.items()}
            A.closeDocument(d.Name);d=A.openDocument(str(NATIVE))
            for n,row in expected.items():
                s=d.getObject(n).Shape
                assert s.isValid() and len(s.Solids)==1 and abs(s.Volume-row['volume'])<1e-6
            assert d.getObject('Splice_L1_CP2').CircuitEnds.startswith('P_AUX.2')
            proof['saved_reopen']=dict(valid_changed_parts=len(expected),volumes_retained=True,
                corrected_XB11_circuit=True, supports_NOT_created=True)
        proof.update(started_utc=start.isoformat(),finished_utc=datetime.now(timezone.utc).isoformat(),
            worker_wall_seconds=round(time.monotonic()-tick,3))
        output.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        assert all(sha(ROOT/p)==h for p,h in pins.items())
        print(proof['status'],'pairs',tested,'contacts',contacts,'outside',outside,'errors',errors,flush=True)
    finally:
        A.closeDocument(d.Name)


def inspect_blockers():
    """Read named blocking regions once; their bboxes are not new collisions."""
    import FreeCAD as A
    output=BASE/'branch-source-blocking-regions.json'
    assert not output.exists()
    failed=json.loads(OUT.read_text(encoding='utf-8'))
    names=sorted({r['pair'][1] for r in failed['contacts']})
    d=A.openDocument(str(SOURCE))
    try:
        rows=[]
        for name in names:
            ob=d.getObject(name);s=ob.Shape;b=s.BoundBox
            xyz=[list(v) for v in s.tessellate(.5)[0]]
            rows.append(dict(name=name,label=ob.Label,
                bounds_mm=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax],
                sampled_extents_mm=[min(p[i] for p in xyz) for i in range(3)]+[max(p[i] for p in xyz) for i in range(3)],
                evidence='Named obstacle region only; sampled extents/bbox NOT a material collision proof'))
        output.write_text(json.dumps(dict(source_native_sha256=sha(SOURCE),
            first_failed_gate_sha256=sha(OUT),regions=rows),indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        print(json.dumps(rows,ensure_ascii=False),flush=True)
    finally:A.closeDocument(d.Name)


if __name__=='__main__':
    inspect_blockers() if '--inspect-blockers' in sys.argv else main()
