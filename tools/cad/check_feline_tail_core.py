"""Check whether obsolete wire galleries can retire without losing tail core.

Uses the original editable servo/bearing support, not an arbitrary cube cut.
Any added core material rejects reuse; no geometry selection inferred.
"""
import json
import time
import FreeCAD as A
from check_main_p0_placement import ROOT,SavedShapes,sha
from plan_feline_layout import MODEL,OUT


def main():
    tick=time.monotonic();reader=SavedShapes()
    source=ROOT/'hardware/cad/modules/tail/TailSupport.FCStd'
    core=reader.shape(source,'ServoSupport34');core.translate(A.Vector(0,0,15))
    old=reader.shape(MODEL,'Ref_Material_tail_MG92BMount29_0_0')
    added=core.cut(old);removed=old.cut(core)
    assert added.isValid() and removed.isValid()
    result=dict(status='ORIGINAL_TAIL_CORE_SUBSET_WIRING_REPLACEMENT_REQUIRED' if added.Volume<1e-5 else 'ORIGINAL_TAIL_CORE_NOT_PROVEN_SUBSET',
        selected=False,physical_pass=False,original_native=source.relative_to(ROOT).as_posix(),
        original_object='ServoSupport34',world_translation_mm=[0,0,15],
        replaces='Ref_Material_tail_MG92BMount29_0_0',
        added_material_mm3=added.Volume,removed_material_mm3=removed.Volume,
        core_valid=core.isValid(),core_solids=len(core.Solids),
        requires=['Preserve servo insertion/fastener/bearing core datums',
            'Replace old stationary-wire restraint with new compact independent grip',
            'Native source links and new grip check before selection',
            'All transformed bank24ends/4MTA/neck/source cases and complete looms'],
        source_sha256={**reader.hashes,__import__('pathlib').Path(__file__).relative_to(ROOT).as_posix():sha(__import__('pathlib').Path(__file__))},
        worker_seconds=round(time.monotonic()-tick,3))
    (OUT/'tail-core-subset.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','added_material_mm3','removed_material_mm3','worker_seconds')}),flush=True)


if __name__=='__main__':main()
