"""Save a native working Deck for the T251 replacement pigtail reservation.

Diagnostic until full wiring and underside installation are finished.
"""
import json
import hashlib
import shutil
import tempfile
from pathlib import Path
import FreeCAD as App
import MeshPart
from deck_f_pwm_axial_r1 import rectangle
from open_deck_p0_supports import sketch, feature

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/cad/studies/fuse-layout-repair-r1'
SOURCE=ROOT/'hardware/cad/studies/deck-f-pwm-axial-r1/DeckP10AxialFPWM.FCStd'


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    plan=json.loads((OUT/'plan.json').read_text())
    checked=json.loads((OUT/'checks.json').read_text())
    assert not checked['hits'] and all(checked['four_corners_in_deck_midplane'] if 'four_corners_in_deck_midplane' in checked else checked['four_corners_in_material'])
    slots=plan['replacements']['F_PWM']['tie_slots']
    assert len(slots)==8
    doc=App.openDocument(str(SOURCE))
    model=OUT/'DeckP10RelocatedFPWM.FCStd'
    stl=OUT/'DeckP10_relocated_f_pwm_DIAGNOSTIC_x1.stl'
    try:
        previous=doc.Deck.Shape.copy()
        sk=sketch(doc.Deck,'RelocatedPWMTieSlots','Parameters.DeckThickness')
        for x,y in slots: rectangle(sk,x-21,y)
        assert sk.FullyConstrained and sk.solve()==0
        feature(doc.Deck,'Pocket','RelocatedPWMTieThrough',sk,'Parameters.DeckThickness')
        doc.recompute()
        doc.saveAs(str(model))  # recoverable native source before Boolean/export
        shape=doc.Deck.Shape
        assert shape.isValid() and shape.isClosed() and len(shape.Solids)==1
        assert not shape.check(True)
        removed=previous.cut(shape).Volume
        added=shape.cut(previous).Volume
        assert abs(removed-256)<0.01 and abs(added)<1e-6
        mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=0.1,AngularDeflection=0.15,Relative=False)
        assert mesh.isSolid()
        mesh.write(str(stl))
        expected=shape.Volume
    finally: App.closeDocument(doc.Name)
    with tempfile.TemporaryDirectory(prefix='robotcat-relocated-pwm-') as temp:
        copy=Path(temp)/model.name
        shutil.copy2(model,copy)
        reopen=App.openDocument(str(copy))
        try:
            reopen.recompute()
            assert abs(reopen.Deck.Shape.Volume-expected)<1e-6
            assert reopen.Deck.Shape.isValid()
        finally: App.closeDocument(reopen.Name)
    report={'status':'NATIVE_WORKING_CANDIDATE_NOT_SELECTED_OR_ROUTE_PASS',
            'source_sha256':sha(SOURCE),'plan_sha256':sha(OUT/'plan.json'),
            'model_sha256':sha(model),'stl_sha256':sha(stl),
            'removed_mm3':removed,'added_mm3':added,'new_slots':8,
            'fully_constrained_sketch':True,'relocated_reopen_recompute':True,
            'new_stl_count':1,'quantity':1,'replacement_not_additional':True,
            'orientation':'Same flat Deck orientation as R5, PETG, 230x190x4 nominal plate; slicer deferred to phase2',
            'limits':'No final XP01 route/underdeck hardware/strap lock qualification; old unused slots retained. R5 unchanged. No physical PASS.'}
    (OUT/'native-checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))


if __name__=='__main__': main()
