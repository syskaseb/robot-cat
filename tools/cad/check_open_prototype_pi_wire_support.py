"""Changed mating-slot trial and relocated fresh-process native reopen."""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from open_prototype_pi_wire_support import MODEL, PROOF, OUT, ROOT, read, sha


def main():
    import FreeCAD as A
    proof=read(PROOF)
    path=Path(sys.argv[2]) if '--fresh-copy' in sys.argv else MODEL
    assert sha(path)==proof['native_sha256']
    d=A.openDocument(str(path));d.recompute()
    bodies=[d.SideDistributionRail,d.PiSpliceInsulationSaddle]
    def check():
        d.recompute()
        for b in bodies:
            assert b.Shape.isValid() and len(b.Shape.Solids)==1 and not b.Shape.check(True)
            assert all('Invalid' not in o.State and 'Touched' not in o.State for o in b.Group)
            assert all(s.FullyConstrained and s.solve()==0 for s in b.Group if s.TypeId=='Sketcher::SketchObject')
        for name in ('SideRail1','SideRail2'):
            link=d.getObject(name)
            assert link.LinkedObject==d.SideDistributionRail
            assert abs(link.Shape.Volume-d.SideDistributionRail.Shape.Volume)<1e-6
        # Same parameter edits the actual mating rail and support slots.
        for name in ('SpliceRailTiePlan','SpliceFootTiePlan'):
            sk=d.getObject(name)
            assert abs(sk.Constraints[10].Value-d.Parameters.SpliceTieSlotWidth.Value)<1e-7
        return [b.Shape.Volume for b in bodies]
    initial=check()
    for b,v in zip(bodies,initial):assert abs(v-proof['native_bodies'][b.Name]['volume_mm3'])<1e-5
    d.Parameters.SpliceTieSlotWidth=3.2;after=check()
    assert all(v>old for v,old in zip(after,initial)),(initial,after)
    d.Parameters.SpliceTieSlotWidth=3.5;restored=check()
    assert all(abs(v-old)<1e-5 for v,old in zip(restored,initial))
    A.closeDocument(d.Name)
    if '--fresh-copy' in sys.argv:
        print('Relocated fresh-process: both native mating slots/links/trial/restoration preserved',flush=True)
        return
    with tempfile.TemporaryDirectory(prefix='robot-cat-pi-saddle-') as taskdir:
        copy=Path(taskdir)/MODEL.name;shutil.copy2(MODEL,copy)
        result=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--fresh-copy',str(copy)],
            cwd=taskdir,check=True,text=True,capture_output=True)
        print(result.stdout.strip(),flush=True)
    assert sha(MODEL)==proof['native_sha256'],'Read-only verification never saves parameter trials to source'
    verified=dict(status='NATIVE_PI_SADDLE_RELOCATED_REOPEN_AND_MATING_TRIAL_CHECKED',
        selected=False,stage_completed=False,physical_pass=False,native_sha256=sha(MODEL),
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (MODEL,PROOF,Path(__file__))},
        trial='SpliceTieSlotWidth3.5->3.2->3.5 changed BOTH mating slot widths and rail links, restored',
        initial_volumes_mm3=initial,changed_volumes_mm3=after,restored_volumes_mm3=restored,
        relocated_fresh_process=True,source_unchanged=True)
    (OUT/'pi-wire-support-verification.json').write_text(json.dumps(verified,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(verified['status'],flush=True)


if __name__=='__main__':main()
