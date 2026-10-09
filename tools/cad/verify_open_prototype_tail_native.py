"""Fresh process, relocated self-contained native tail checkpoint verification."""
from pathlib import Path
from datetime import datetime,timezone
import json,tempfile,shutil,time
import FreeCAD as A
from check_main_p0_placement import sha
from open_prototype_tail_mount import ROOT,OUT
from open_prototype_tail_assembly import solid_centre


def run():
    assert not A.listDocuments()
    tick=time.monotonic();model=OUT/'TailAssemblyCurrent.FCStd'
    proof=json.loads((OUT/'tail-assembly-checks.json').read_text())
    assert proof['status']=='CURRENT_TAIL_MECHANICS_NOMINAL_GEOMETRY_PREPARED'
    assert sha(model)==proof['model_sha256']
    r=dict(status='PENDING',physical_pass=False,source_sha256={model.relative_to(ROOT).as_posix():sha(model),
       (OUT/'tail-assembly-checks.json').relative_to(ROOT).as_posix():sha(OUT/'tail-assembly-checks.json'),
       Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))})
    with tempfile.TemporaryDirectory(prefix='robot-cat-tail-fresh-') as td:
        copy=Path(td)/model.name;shutil.copy2(model,copy)
        doc=A.openDocument(str(copy));doc.recompute()
        for n in ('LowerCarrier','TailRiser','RaisedTailBridge','RaisedTailSupport'):
            s=doc.getObject(n).Shape
            assert s.isValid() and len(s.Solids)==1 and not s.check(True),n
        links=[o for o in doc.Objects if o.TypeId=='App::Link']
        assert links
        for o in links:assert o.getLinkedObject().Document==doc,o.Name
        aliases={'TailRoot29':'SupportedRoot34','TailLowerRetainer':'LowerRetainerPETG',
                 'MG92BMount29':'RaisedTailSupport','TailBridge29':'RaisedTailBridge','PrintedHornR2':'PrintedHornR2'}
        aliases.update({f'TailCartridge{k}{i}':f'Cartridge{k}{i}' for k in ('Bolt','Nut') for i in range(4)})
        objects={n:doc.getObject(aliases.get(n,'Current_'+n)) for n in proof['tail_identities']}
        assert all(o is not None and o.Shape.isValid() for o in objects.values())
        initial={n:o.Shape.copy() for n,o in objects.items()}
        z=doc.RaisedTailBridge.Shape.BoundBox.ZMin
        doc.TailParameters.TailRise=16;doc.recompute()
        assert abs(doc.RaisedTailBridge.Shape.BoundBox.ZMin-z-1)<1e-6
        assert abs(doc.TailRiser.Shape.BoundBox.ZLength-20)<1e-6
        assert all(abs(o.Shape.BoundBox.ZMin-initial[n].BoundBox.ZMin-1)<1e-5 for n,o in objects.items())
        doc.TailParameters.TailRise=15;doc.recompute()
        assert abs(doc.RaisedTailBridge.Shape.BoundBox.ZMin-z)<1e-6
        for angle in (-30,0,30):
            doc.TailParameters.TailYaw=angle;doc.recompute()
            assert (doc.TailRotor.Placement.multVec(A.Vector(171,-6,0))-A.Vector(171,-6,0)).Length<1e-6
            assert doc.TailRotor.Placement.Rotation.isSame(A.Rotation(A.Vector(0,0,1),angle),1e-7)
            for n in proof['moving_identities']:
                actual=objects[n].Shape.copy();actual.Placement=doc.TailRotor.Placement*actual.Placement
                expected=initial[n].copy();expected.rotate(A.Vector(171,-6,0),A.Vector(0,0,1),angle)
                assert (solid_centre(actual)-solid_centre(expected)).Length<1e-5,n
        doc.TailParameters.TailYaw=0;doc.recompute()
        assert all(abs(o.Shape.BoundBox.ZMin-initial[n].BoundBox.ZMin)<1e-5 for n,o in objects.items())
        r.update(status='FRESH_RELOCATED_NATIVE_REOPEN_CHECKED',external_link_count=0,local_links=len(links),
           assembly_physical_tail_identities=len(proof['tail_identities']),native_rise_restore=True,native_yaw_restore=True,
           all_61_rise_restored=True,localized_moving_parts_checked=len(proof['moving_identities']))
        A.closeDocument(doc.Name)
    assert sha(model)==r['source_sha256'][model.relative_to(ROOT).as_posix()]
    r.update(worker_seconds=round(time.monotonic()-tick,3),finished_utc=datetime.now(timezone.utc).isoformat())
    (OUT/'tail-reopen-checks.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(r))


if __name__=='__main__':run()
