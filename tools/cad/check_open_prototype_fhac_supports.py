"""One fresh/relocated reopen and mating-slot trial for current fixtures."""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from open_prototype_fhac_supports import ROOT, OUT, MODEL, PROOF, PLAN, read, sha


def main():
    import FreeCAD as A
    proof=read(PROOF)
    assert proof['status']=='FIVE_HOLDER_FIXTURES_NOMINAL_PREPARATION_CHECKED'
    assert not proof['contacts'] and not proof['errors']
    path=Path(sys.argv[2]) if '--fresh-copy' in sys.argv else MODEL
    assert sha(path)==proof['native_sha256']
    d=A.openDocument(str(path))
    bodies=[d.SideDistributionRail,d.SourceLeftCarrier,d.SourceRightCarrier]
    def check():
        d.recompute()
        for b in bodies:
            assert b.Shape.isValid() and len(b.Shape.Solids)==1 and not b.Shape.check(True),b.Name
            assert all('Invalid' not in o.State and 'Touched' not in o.State for o in b.Group),b.Name
            assert all(s.FullyConstrained and s.solve()==0 for s in b.Group if s.TypeId=='Sketcher::SketchObject'),b.Name
        for n in ('SideRail1','SideRail2'):
            link=d.getObject(n);assert link.LinkedObject==d.SideDistributionRail
            assert abs(link.Shape.Volume-d.SideDistributionRail.Shape.Volume)<1e-5
        for n in ('SourceRailTiePlan','LeftFootTiePassPlan','RightFootTiePassPlan',
                'LeftFrontTiePassPlan','RightFrontTiePassPlan','CurrentPiTiePassPlan'):
            sk=d.getObject(n)
            assert abs(sk.Constraints[10].Value-d.Parameters.SourceFixtureSlotWidth.Value)<1e-7,n
        assert d.getObject('PiSpliceInsulationSaddle') is None,'Historical saddle replaced, not duplicated'
        assert d.getObject('W077_RouteReference') is None,'Old over-ATO route must not remain current'
        assert d.getObject('W077_RouteReference_CurrentReference') is not None
        return [b.Shape.Volume for b in bodies]
    initial=check()
    for b,v in zip(bodies,initial):assert abs(v-proof['native_bodies'][b.Name]['volume_mm3'])<1e-5,b.Name
    d.Parameters.SourceFixtureSlotWidth=3.2;changed=check()
    assert all(a>b for a,b in zip(changed,initial)),(initial,changed)
    d.Parameters.SourceFixtureSlotWidth=3.5;restored=check()
    assert all(abs(a-b)<1e-5 for a,b in zip(restored,initial))
    A.closeDocument(d.Name)
    if '--fresh-copy' in sys.argv:
        print('Relocated native reopen:3 bodies/mating slots/links restored; old Pi route/saddle absent',flush=True)
        return
    with tempfile.TemporaryDirectory(prefix='robot-cat-source-fixture-') as taskdir:
        copy=Path(taskdir)/MODEL.name;shutil.copy2(MODEL,copy)
        run=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--fresh-copy',str(copy)],
            cwd=taskdir,check=True,text=True,capture_output=True)
        print(run.stdout.strip(),flush=True)
    assert sha(MODEL)==proof['native_sha256']
    record=dict(status='CURRENT_SOURCE_FIXTURES_RELOCATED_NATIVE_REOPEN_CHECKED',
        native_sha256=sha(MODEL),source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in
            (MODEL,PROOF,PLAN,Path(__file__))},
        initial_volumes_mm3=initial,changed_volumes_mm3=changed,restored_volumes_mm3=restored,
        trial='SourceFixtureSlotWidth3.5->3.2->3.5 affects rail and both carriers, restored',
        relocated_fresh_process=True,source_unchanged=True,
        selected=False,stage_completed=False,physical_pass=False)
    (OUT/'fhac-mount-verification.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(record['status'],flush=True)


if __name__=='__main__':main()
