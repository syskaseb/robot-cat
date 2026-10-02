"""Resolve actual G1 mesh pinch: cylinder tangent to seat top at R1.7.

R1.8 opens a finite U mouth, rather than two faces touching along a line.
No mesh face deletion, no alteration of P0 or unchanged DATA/W061 features.
"""
from datetime import datetime,timezone
import json,shutil,sys,tempfile
from pathlib import Path
import main_input_return_finish_r3 as F
import body_ground_routes_r1 as M

def main():
    import FreeCAD as A
    import Part
    F.CAD.mkdir(exist_ok=True);F.OUT.mkdir(exist_ok=True)
    source=F.NATIVE/'DeckMainInput.FCStd';dest=F.CAD/'DeckMainInput.FCStd'
    assert not dest.exists()
    begin=datetime.now(timezone.utc);d=A.openDocument(str(source));docname=d.Name
    try:
        d.saveAs(str(dest));p=d.MainInputParameters;assert abs(p.GrooveRadius.Value-1.7)<1e-6
        p.GrooveRadius=1.8;d.recompute();s=d.MainInputDeck.Shape.copy()
        assert s.isValid() and len(s.Solids)==1 and not s.check(True)
        volume=s.Volume;p.GrooveRadius=1.81;d.recompute();probe=d.MainInputDeck.Shape.Volume
        assert abs(probe-volume)>1e-6
        p.GrooveRadius=1.8;d.recompute();assert abs(d.MainInputDeck.Shape.Volume-volume)<1e-5
        d.save();s.exportBrep(str(F.CAD/'Deck_WORLD.brep'))
    finally:A.closeDocument(docname)
    with tempfile.TemporaryDirectory(prefix='robot-cat-input-U-mouth-') as td:
        q=Path(td)/dest.name;shutil.copy2(dest,q);d=A.openDocument(str(q));docname=d.Name
        try:
            d.recompute();s=d.MainInputDeck.Shape
            assert s.isValid() and len(s.Solids)==1 and not s.check(True) and abs(s.Volume-volume)<1e-5
        finally:A.closeDocument(docname)
    end=datetime.now(timezone.utc)
    M.save(F.OUT/'deck-mouth-checks.json',dict(status='FINITE_U_MOUTH',groove_radius_mm=1.8,
        old_tangent_radius_mm=1.7,seat_top_mm=115.2,wire_centre_z_mm=113.5,
        minimum_floor_mm=2.9,radial_wire_play_mm=.3,parameter_probe_mm3=[volume,probe,volume],
        added_constrained_sketches=3,strict_BOP_errors=0,relocated_reopen=True,
        source_sha256={source.relative_to(F.ROOT).as_posix():M.sha(source)},builder_sha256=M.sha(Path(__file__)),
        started_utc=begin.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds(),physical_pass=False))
    F.DECK_BREP=F.CAD/'Deck_WORLD.brep';F.DECK_NATIVE=dest;F.DECK_CHECKS=F.OUT/'deck-mouth-checks.json'
    F.main()

if __name__=='__main__':
    sys.path.insert(0,str(F.ROOT/'tools/cad'));main()
