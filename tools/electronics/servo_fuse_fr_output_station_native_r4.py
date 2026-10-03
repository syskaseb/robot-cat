"""Recover R3's saved valid solid after its non-closed tessellation.

Remove only redundant boolean seams in the native final feature. Prove
unchanged occupied geometry by symmetric difference, preserve editable
clearance parameters and inherited47-pair static proof. No mesh repair,
collision waiver or heavy reconstruction of the accepted Deck.
"""
from pathlib import Path
from datetime import datetime,timezone
import sys,json,math,shutil,tempfile
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-fr-output-station-native-r4'
CAD=ROOT/'hardware/cad/studies/servo-fuse-fr-output-station-native-r4'

def main():
    import FreeCAD as A
    import MeshPart
    start=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists()
    pins={}
    def pin(p):pins[p.relative_to(ROOT).as_posix()]=sha(p)
    prior=ROOT/'hardware/electronics/full-cat/servo-fuse-fr-output-station-native-r3/preflight.json';pin(prior)
    r=json.loads(prior.read_text(encoding='utf-8'));assert not r['hits'] and not r['errors']
    assert r['fixture_single_solid'] and not r['fixture_strict_BOP'] and r['pairs']==47
    for rel,h in r['source_sha256'].items():assert sha(ROOT/rel)==h,rel;pin(ROOT/rel)
    for rev in range(1,4):pin(ROOT/f'tools/electronics/servo_fuse_fr_output_station_native_r{rev}.py')
    base=ROOT/'hardware/cad/studies/servo-fuse-fr-output-station-native-r3/FRGuardOutputStation.FCStd';pin(base)
    d=A.openDocument(str(base));dest=CAD/'FRGuardOutputStation.FCStd';attempts=[]
    try:
        f=d.FRGuardOutputFinished;p=d.OutputGripParameters
        d.recompute();before=f.Shape.copy();assert before.isValid() and len(before.Solids)==1 and not before.check(True)
        f.Refine=True;d.recompute();s=f.Shape.copy();assert s.isValid() and len(s.Solids)==1 and not s.check(True)
        diff=before.cut(s).Volume+s.cut(before).Volume;assert diff<1e-5,diff
        vol=s.Volume;p.Clearance=.3;d.recompute();probe=f.Shape.Volume;assert abs(probe-vol)>1e-4
        p.Clearance=.2;d.recompute();assert abs(f.Shape.Volume-vol)<1e-5
        s=f.Shape.copy();d.saveAs(str(dest));s.exportBrep(str(CAD/'Guard_WORLD.brep'))
        mesh=None
        for linear,angular in ((.08,.15),(.03,.1)):
            candidate=MeshPart.meshFromShape(Shape=s,LinearDeflection=linear,AngularDeflection=angular,Relative=False)
            row=dict(linear_deflection_mm=linear,angular_deflection_rad=angular,solid=candidate.isSolid(),components=candidate.countComponents(),facets=candidate.CountFacets)
            attempts.append(row);print('FR_GUARD_MESH',json.dumps(row),flush=True)
            if row['solid'] and row['components']==1:mesh=candidate;break
        save(OUT/'tessellation.json',dict(selected=False,physical_pass=False,attempts=attempts,symmetric_difference_mm3=diff,
            source_sha256=pins,script_sha256=sha(Path(__file__)),finished_utc=datetime.now(timezone.utc).isoformat()))
        if mesh is None:return
        mesh.rotate(0,math.pi/2,0);bb=mesh.BoundBox;dims=[bb.XLength,bb.YLength,bb.ZLength]
        assert dims[0]+10<256 and dims[1]+10<256 and dims[2]<256
        mesh.translate(-bb.XMin,-bb.YMin,-bb.ZMin);mesh.write(str(CAD/'Guard_UNSELECTED.stl'))
    finally:A.closeDocument(d.Name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-fr-output-r4-') as td:
        q=Path(td)/dest.name;shutil.copy2(dest,q);re=A.openDocument(str(q))
        try:re.recompute();assert abs(re.FRGuardOutputFinished.Shape.Volume-vol)<1e-5
        finally:A.closeDocument(re.Name)
    save(OUT/'checks.json',dict(status='FR_OUTPUT_NATIVE_STATIC_COMPLETE_SERVICE_OPEN',selected=False,physical_pass=False,W5_complete=False,
        pairs=r['pairs'],hits=[],errors=[],ties=r['ties'],source_sha256=pins,script_sha256=sha(Path(__file__)),
        native=dict(file=dest.relative_to(ROOT).as_posix(),final='FRGuardOutputFinished',single_solid=True,strict_BOP_errors=0,
            closed_STL=True,relocated_reopen=True,parameter_mm=[.2,.3,.2],volumes_mm3=[vol,probe,vol],dimensions_mm=dims,symmetric_difference_mm3=diff),
        stock_delta=dict(replacement_print='FRGuard',additional_prints=0,additional_T18I=3,new_fasteners=0),
        recipe=['Mount existing guard attachment with its SAME2M3x8/nuts on the unpowered removed bank before routing.',
            'Prewire both UNTINNED bare ends into separate221412 cages; nominal11mm strip. Seat housing in its open tray and close housing tie.',
            'Lay each insulation end in its separate6mm side groove, close its OWN T18I through actual slots. No shared grip substituted.',
            'Guard remains attached for whole-bank removal; module disconnection/lever access still OPEN.'],
        phase2=['Delivered housing/wire/tie fit, cantilever stiffness/PETG creep/pull and electrical/thermal trials, not physical PASS.'],
        open=['RL/RR outputs, other nativeWAGO grips,4RRclips and full assembly-removal/stock/E3/selection.'],
        started_utc=start.isoformat(),finished_utc=datetime.now(timezone.utc).isoformat(),worker_wall_seconds=(datetime.now(timezone.utc)-start).total_seconds()))
    print('FR_OUTPUT_NATIVE_RECOVERED',flush=True)
if __name__=='__main__':main()
