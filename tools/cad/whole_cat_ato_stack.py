"""Explicit twelve-holder/24-end planning stack, not selected hardware or mounts.

Replace only gross fuse reservations in a SEPARATE CP2 candidate. Catalogue
sizes stay distinct from provisional seating, blade axes and ATO cap height.
Do not rerun a completed recipe merely to get a different timestamp.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import itertools
import json
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'hardware/cad/studies/whole-cat-packaging/cp2'
NATIVE = BASE / 'WholeCatInterior.FCStd'
CANDIDATE = BASE / 'ATOStackCandidate.FCStd'
RECEIPT = BASE / 'ato-stack-checks.json'
BODY = ROOT / 'hardware/electronics/full-cat/source-switch-selected-r1/body-harness.json'
REFERENCE = ROOT / 'hardware/reference/servo-holder-p0-2026-09-24/ENVELOPE.md'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write(p, data):
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def receive():
    import FreeCAD as A
    proof = json.loads(RECEIPT.read_text(encoding='utf-8'))
    assert sha(CANDIDATE) == proof['candidate_native_sha256']
    assert sha(NATIVE) == proof['retained_native_sha256']
    d = A.openDocument(str(CANDIDATE)); d.recompute()
    for row in proof['components']:
        s = d.getObject(row['name']).Shape
        assert s.isValid() and len(s.Solids) == 1
        assert abs(s.Volume-row['volume_mm3']) < 1e-6
    assert len(proof['terminal_datums']) == 24
    assert len({r['wire_id'] for r in proof['terminal_datums']}) == 24
    proof['fresh_reopen'] = dict(valid_boxes=len(proof['components']),
        terminal_datums=24, original_native_unchanged=True,
        checked_utc=datetime.now(timezone.utc).isoformat())
    write(RECEIPT, proof); A.closeDocument(d.Name)
    print('FRESH_REOPEN_OK', len(proof['components']), 'nominal stack boxes;24 identified ends', flush=True)


def main():
    import FreeCAD as A
    import Part
    start = datetime.now(timezone.utc); tick = time.monotonic()
    assert start < datetime.fromisoformat('2026-10-06T07:00:00+00:00'), 'Work window ended'
    assert not RECEIPT.exists(), 'Receive existing result; no unchanged rerun'
    before = sha(NATIVE)
    wires = json.loads(BODY.read_text(encoding='utf-8'))['conductors']
    d = A.openDocument(str(NATIVE))
    replaced = {f'F_{side}{i}_CP2' for side in 'LR' for i in range(1, 7)}
    for name in sorted(replaced):
        assert d.getObject(name)
        d.removeObject('Access_'+name); d.removeObject(name)
    p = d.addObject('App::FeaturePython', 'ATOStackDatums')
    p.Label = 'Nominalny stos ATO: nie pomiar, nie mocowanie'
    for name, value in [('FlangeTop',126),('SeatingOffset',0),('TerminalOffset',7),('ATOHeight',18.8)]:
        p.addProperty('App::PropertyLength', name); setattr(p,name,value)
    p.addProperty('App::PropertyString','DimensionBasis')
    p.DimensionBasis = ('MTA flange28x15/body depth28.5 and TE lengths from ENVELOPE.md; '
        'flangeZ126, seatinge0, axes+/-7 and ATO protrusion18.8 are PROTOTYPE assumptions')
    group = d.addObject('App::DocumentObjectGroup','ATOStackCandidates')
    service_group = d.getObject('ServiceReservations')
    changed, access, rows, terminal_datums = {}, {}, [], []

    def box(name, xyz, size, z_expression, category, basis, service=False):
        o = d.addObject('Part::Box', name)
        o.Length,o.Width,o.Height = size
        o.Placement.Base = A.Vector(*xyz)
        o.setExpression('Placement.Base.z', z_expression)
        o.addProperty('App::PropertyString','EvidenceKind');o.EvidenceKind=category
        o.addProperty('App::PropertyString','DimensionBasis');o.DimensionBasis=basis
        (service_group if service else group).addObject(o)
        d.recompute()
        (access if service else changed)[name] = o.Shape.copy()
        bb=o.Shape.BoundBox
        rows.append(dict(name=name, category=category, volume_mm3=o.Shape.Volume,
            bbox_mm=[bb.XMin,bb.YMin,bb.ZMin,bb.XMax,bb.YMax,bb.ZMax],dimension_basis=basis))
        return o

    for side, y, centres in [('L',58,[-53,-23,7,37,67,97]),('R',-58,[-53,-21,11,43,75,107])]:
        sign=1 if side=='L' else -1
        for i,x in enumerate(centres,1):
            leg=('F' if i<=3 else 'R')+side
            fuse=f'F_{leg}{(i-1)%3+1}'
            prefix=f'F_{side}{i}_CP2'
            box(prefix+'_Housing',[x-14,y-7.5,0],[28,15,28.5],
                'ATOStackDatums.FlangeTop-28.5 mm','supplier_bounding_reservation',
                'Whole MTA housing/flange bounding reserve28x15x28.5, NOT exact hollow/latch solid')
            ato=box(prefix+'_ATO',[x-9.55,y-2.55,0],[19.1,5.1,18.8],
                'ATOStackDatums.FlangeTop','provisional_component_reservation',
                'Inherited ATO19.1x5.1x18.8 prototype reserve; exposed height/seating NOT supplier verified')
            ato.setExpression('Height','ATOStackDatums.ATOHeight')
            for role,dy,length,h in [('IN',7,23.749,9.8552),('OUT',-7,21.717,5.080)]:
                terminal=fuse+'.'+role.lower()
                matches=[w for w in wires if terminal in (w['a'],w['b'])]
                assert len(matches)==1, (terminal,matches)
                zexpr=f'ATOStackDatums.FlangeTop-28.5 mm+ATOStackDatums.SeatingOffset-{length+.381} mm'
                ob=box(prefix+'_'+role,[x-5.1943,y+sign*dy-(h+.381)/2,0],
                    [10.3886,h+.381,length+.381],zexpr,'conditional_terminal_reservation',
                    f'TE {"4-520448-2" if role=="IN" else "2-520184-2"}: catalogue length/width plus0.381 length tolerance; seatinge0/axes+/-7 UNKNOWN')
                ob.setExpression('Placement.Base.y',f'{y} mm+{sign*(1 if role=="IN" else -1)}*ATOStackDatums.TerminalOffset-{(h+.381)/2} mm')
                d.recompute()
                point=[x,y+sign*dy,ob.Shape.BoundBox.ZMin]
                terminal_datums.append(dict(holder=fuse,role=role,native=ob.Name,
                    wire_id=matches[0]['id'],a=matches[0]['a'],b=matches[0]['b'],
                    insulation_mouth_mm=point,wire_departure=[0,0,-1],
                    straight_grip_design_mm=9,route_and_restraint_qualified=False))
            box('Access_'+prefix,[x-14,y-13,0],[28,26,45],
                'ATOStackDatums.FlangeTop+ATOStackDatums.ATOHeight','service_reservation',
                '45mm vertical ATO pull/tool budget from EXPOSED top; dorsal cover removed; WAGO stay connected',True)
    d.recompute()
    # Re-read expression-driven shapes after all datums have been assigned.
    for name in changed: changed[name]=d.getObject(name).Shape.copy()
    for name in access: access[name]=d.getObject(name).Shape.copy()
    all_new={**changed,**access}
    assert all(s.isValid() and len(s.Solids)==1 for s in all_new.values()), 'Invalid stack before contact checks'
    baseline={n:d.getObject(n).Shape.BoundBox.ZMin for n in all_new}
    p.FlangeTop=127;d.recompute()
    assert all(abs(d.getObject(n).Shape.BoundBox.ZMin-baseline[n]-1)<1e-7 for n in all_new)
    p.FlangeTop=126;d.recompute()
    assert all(abs(d.getObject(n).Shape.BoundBox.ZMin-baseline[n])<1e-7 for n in all_new)
    candidate_names=set(changed)|set(access)
    fixed={o.Name:o.Shape.copy() for o in d.Objects if 'Shape' in o.PropertiesList
        and o.Name not in candidate_names and o.Name not in ['TorsoEnvelope','BatteryNominal']
        and (any(parent.Name in ['InteriorReservations','HarnessCandidate','S0TerminalCandidates',
             'S1TerminalCandidates','ServiceReservations'] for parent in o.InList)
             or 'Category' in o.PropertiesList and o.Category!='electronics')}
    hits,errors,outside=[],[],[]; tested=0

    def check(na,a,nb,b):
        nonlocal tested
        if not a.BoundBox.intersect(b.BoundBox):return
        tested+=1
        try:
            assert a.isValid() and b.isValid(),'Invalid input'
            c=a.common(b); assert c.isValid(),'Invalid common'
            if c.Volume>1e-5:
                kind='reservation_overlap_not_proven_physical_collision'
                if nb in fixed and 'Category' in d.getObject(nb).PropertiesList:kind='nominal_reserve_intersects_retained_shape'
                hits.append(dict(pair=[na,nb],volume_mm3=c.Volume,evidence_kind=kind))
        except Exception as e:errors.append(dict(pair=[na,nb],error=str(e)))

    for na,a in all_new.items():
        for nb,b in fixed.items():check(na,a,nb,b)
    for na,nb in itertools.combinations(all_new,2):check(na,all_new[na],nb,all_new[nb])
    torso=d.getObject('TorsoEnvelope').Shape
    for name,s in changed.items():
        bb=s.BoundBox
        budget=Part.makeBox(bb.XLength+4.8,bb.YLength+4.8,bb.ZLength+4.8,
            A.Vector(bb.XMin-2.4,bb.YMin-2.4,bb.ZMin-2.4))
        try:
            result=budget.cut(torso);assert result.isValid(),'Invalid enclosure cut'
            if result.Volume>1e-5:outside.append(dict(name=name,volume_mm3=result.Volume))
        except Exception as e:errors.append(dict(pair=[name,'TorsoEnvelope'],error=str(e)))
    # A useful common datum drives all twelve housings,24 ends and12 access
    # budgets. Restore before saving; no head/tail/P0/selected source mutation.
    for row in rows:
        s=d.getObject(row['name']).Shape;assert s.isValid() and len(s.Solids)==1
        row['volume_mm3']=s.Volume
    d.saveAs(str(CANDIDATE));A.closeDocument(d.Name)
    assert sha(NATIVE)==before
    write(RECEIPT,dict(status='NOMINAL_STACK_REQUIRES_CHANGE' if hits or outside or errors else 'NOMINAL_STACK_CLEAR_NOT_SELECTED',
        selected=False,physical_pass=False,W1_complete=False,W5_complete=False,
        components=rows,terminal_datums=terminal_datums,contacts=hits,outside=outside,errors=errors,
        changed_datums=dict(flange_top_mm=126,panel_top_mm=124,panel_underside_mm=122,
            housing_bottom_mm=97.5,IN_insulation_end_mm=73.37,OUT_insulation_end_mm=75.402,
            nominal_ATO_top_mm=144.8,extraction_top_mm=189.8),
        prototype_assumptions=['Flange top126','TE seatinge0','Blade axes+/-7Y',
            'ATO protrusion18.8; actual seated cap unknown','Housing boxes NOT exact material'],
        catalogue_basis='MTA/TE ENVELOPE.md; no guessed hollow/latch or measured seating',
        fixed_geometry_count=len(fixed),exact_BRep_pairs_tested=tested,
        parameter_check='FlangeTop126->127 moves all60boxes +1Z; restore126',
        assembly=['Battery disconnected/absent','Remove dorsal cover',
            'WAGO remain connected for12 ATO pulls; cover/tool/retention physical fit still to qualify',
            'Holder/24TE complete installation and restraints remain OPEN'],
        invalidated_interfaces=['Gross64mm fuse boxes and old access origins in THIS candidate only',
            'No CP2/R53 native mounts or routes selected by this candidate'],
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in [BODY,REFERENCE,Path(__file__)]},
        prior_failed_attempt='Invalid quantity expressions without mm units; stopped at parameter assertion before receipt/export. Separate minimal unit-expression probe established correction; no physical geometry accepted.',
        retained_native_sha256=before,candidate_native_sha256=sha(CANDIDATE),
        started_utc=start.isoformat(),finished_utc=datetime.now(timezone.utc).isoformat(),
        worker_wall_seconds=round(time.monotonic()-tick,3)))
    print('ATO stack:',len(hits),'reservation overlaps,',len(outside),'outside,',len(errors),'errors; no selection',flush=True)


if __name__=='__main__':
    receive() if '--receive' in sys.argv else main()
