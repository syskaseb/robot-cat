"""One reusable negative gate for coupled station allocation before detailed CAD.

Explicit component reservations against the real saved torso and whole-component
allowances. A failed reservation is NOT a measured component collision. Nothing
is saved to the native documents; missing routes prevent layout acceptance.
"""
from datetime import datetime, timezone
from pathlib import Path
import json
import time

import FreeCAD as A
import Part
from open_prototype_entry_chambers import CONTEXT
from open_prototype_wiring_endpoints import ROOT, BASE, read, sha

OUT = BASE / 'wiring-checkpoint'
DEST = OUT / 'coupled-station-gate.json'
MAP = OUT / 'obstacle-map-current.json'


def box(centre, size):
    return Part.makeBox(*size, A.Vector(*[c-d/2 for c,d in zip(centre,size)]))


def main():
    assert not DEST.exists(), 'Receive the gate; do not repeat an unchanged layout'
    tick=time.monotonic()
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in (CONTEXT, MAP, Path(__file__))}
    doc=A.openDocument(str(CONTEXT))
    result=dict(status='PARTIAL_COUPLED_RESERVATION_GATE_NOT_LAYOUT_ACCEPTANCE',
        selected=False, stage_completed=False, physical_pass=False,
        source_sha256=pins, reservations=[], errors=[],
        geometry_basis='Valid primitive reservations and saved torso BRep. Intersections reject allocation budgets, not prove delivered-part contact.',
        open_items=['All20 station allocation', 'Both exits of every holder and whole routes',
                    'S1 rings/tools/control and native mounting', 'Independent cable restraints',
                    'MTA delivered lead lengths', 'U1/S0 delivery datums', 'Mount/stock/export'])
    scene=[]
    def put(name,centre,size,basis):
        scene.append((name,box(centre,size),dict(centre_mm=centre,size_mm=size,basis=basis)))
    try:
        torso=doc.TorsoEnvelope.Shape
        assert torso.isValid() and len(torso.Solids)==1
        objects=read(MAP)['objects']
        # Copied reservation dimensions, not the previously assumed11mm MTA.
        for role,centre in [('RL',[5,0,70]),('RR',[42,0,70]),
                            ('FL',[116,40,70]),('FR',[153,40,70])]:
            obj=next(r for r in objects if r['name']==f'MTA_{role}_CP2')
            b=obj['bounds_mm']; size=[b[k+3]-b[k] for k in range(3)]
            assert all(abs(x-y)<1e-6 for x,y in zip(size,[35,22,16]))
            put('MTA_'+role,centre,size,'Copied current MTA reservation35x22x16, source+X/output-X; tails OPEN')
        for name,centre in [('P_SYS',[126,-33,117]),
                            ('P_REAR',[56.877,-33,139]),('P_FRONT',[169.523,-33,139])]:
            put(name,centre,[37,11,22],'615 rotatedX90; input below, unmeasured cavity datum')
        for name,x,z in [('F_HY',-50,128),('F_HP',-25,128),('F_TY',0,128),
                          ('F_AUX',56.877,128),('F_PI',139,106)]:
            put(name,[x,10,z+1],[20.25,51,22],'FHAC body reservation axis+Y, inputY-15.5/output35.5; tails OPEN')
        put('S1_body',[126.2,-55.5,61],[24,37,42],
            'Mirror original S1 aroundZ then lower24mm; rings/control/access are NOT qualified')
        modules=[r for r in objects if r['basis'].startswith('Canonical whole-component/reference envelope') or
                 r['name'] in ('U1UnknownModuleReservation',)]
        assert len(modules)==10, 'Whole-component scope must not silently disappear'
        result['module_reservation_names']=[r['name'] for r in modules]
        for name,shape,metadata in scene:
            assert shape.isValid() and len(shape.Solids)==1
            outside=shape.cut(torso)
            assert outside.isValid(), 'Invalid subtraction is not clearance'
            overlaps=[]
            for other,s,_ in scene:
                if other>=name: continue
                hit=shape.common(s);assert hit.isValid()
                if hit.Volume>1e-6:overlaps.append(dict(reservation=other,volume_mm3=round(hit.Volume,6)))
            module_overlaps=[]
            for r in modules:
                b=r['bounds_mm'];s=box([(b[k]+b[k+3])/2 for k in range(3)],
                                      [b[k+3]-b[k] for k in range(3)])
                hit=shape.common(s);assert hit.isValid()
                if hit.Volume>1e-6:module_overlaps.append(dict(reservation=r['name'],volume_mm3=round(hit.Volume,6)))
            row=dict(name=name,**metadata,outside_torso_mm3=round(outside.Volume,6),
                     shared_reservation_overlaps=overlaps,module_reservation_overlaps=module_overlaps)
            result['reservations'].append(row)
            print(json.dumps(row),flush=True)
        result['failed_reservations']=[r['name'] for r in result['reservations']
            if r['outside_torso_mm3']>1e-6 or r['shared_reservation_overlaps'] or r['module_reservation_overlaps']]
        # Even0failed is not acceptance: routes/actual stations/access are open.
    except Exception as exc:
        result['errors'].append(str(exc))
        raise
    finally:
        A.closeDocument(doc.Name)
        result.update(worker_seconds=round(time.monotonic()-tick,3),
                      finished_utc=datetime.now(timezone.utc).isoformat())
        DEST.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    assert all(sha(ROOT/p)==h for p,h in pins.items())
    print(json.dumps(dict(status=result['status'],failed=result['failed_reservations'],
                          seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':main()
