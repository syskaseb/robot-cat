"""Separate prototype integration decision; NEVER changes a failed BOP report.

The inherited shell is not BOP-clean. Matching error-class counts alone is NOT
proof that error locations are unchanged. Mesh clearance plus no added solid
volume only supports this bounded AUX prototype, not manufacturing release.
"""
from collections import Counter
from pathlib import Path
import hashlib
import json
import sys
from aux35 import OUT,SOURCE,SOURCE_SHA,MASTER

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def classes(messages):
    return dict(Counter(line for text in messages for line in text.splitlines() if line.startswith('Error in ')))

def baseline():
    import FreeCAD as A
    import Part
    p=read(SOURCE/'assembly-plan.json');assert sha(SOURCE/p['cad_filename'])==SOURCE_SHA
    assert read(SOURCE/'shape-cache/index.json')['source_sha256']==SOURCE_SHA
    path=SOURCE/'shape-cache/ShellMounted20.brep'
    s=Part.Shape();s.read(str(path));errors=[]
    try:s.check(True)
    except Exception as exc:errors.append(str(exc))
    report=dict(source_checkpoint_sha256=SOURCE_SHA,source_brep_sha256=sha(path),valid=s.isValid(),
                volume_mm3=s.Volume,errors=errors,error_classes=classes(errors),mechanical_release=False)
    (OUT/'shell-source-bop.json').write_text(json.dumps(report,indent=2),encoding='utf8',newline='\n')
    print(json.dumps(report,indent=2))

def main():
    fit=read(OUT/'fit-audit.json');mesh=read(OUT/'mesh-proof.json');old=read(OUT/'shell-source-bop.json')
    assert fit['master_sha256']==mesh['master_sha256']==sha(MASTER)
    assert fit['source_checkpoint_sha256']==mesh['source_checkpoint_sha256']==old['source_checkpoint_sha256']==SOURCE_SHA
    shell=next(p for p in fit['native_parts'] if p['name']=='Shell35')
    counts=classes(shell['bop_errors']);assert counts==old['error_classes'] and counts
    assert not fit['geometric_checks_passed'],'Strict full-BOP failure is deliberately preserved'
    assert len(fit['native_parts'])==9 and len(fit['sketches'])==11
    assert all(s['fully_constrained'] for s in fit['sketches'])
    assert all(p['valid'] and p['solids']==1 and p['status']=='Valid' and p['fits_256'] for p in fit['native_parts'])
    assert all(not p['bop_errors'] for p in fit['native_parts'] if p['name']!='Shell35')
    assert all(r['added_material_mm3']<.001 and r['removed_volume_mm3']>0 for r in fit['subtractive_changes'] if r['name']!='Part__Feature038')
    deck=next(r for r in fit['subtractive_changes'] if r['name']=='Part__Feature038')
    assert abs(deck['removed_volume_mm3']-13.5716802635)<1e-6
    assert mesh['deck_subtractive_change']['added_mm3']<.01
    assert abs(mesh['deck_subtractive_change']['removed_mm3']-13.5716802635)<.01
    assert not fit['rest_interferences']
    assert all(min(r['post_to_support_mm2'],r['post_to_pcb_mm2'],r.get('gap_to_deck_mm2',30),r.get('gap_to_bridge_mm2',30))>15 and r['shaft_interference_mm3']<1e-6 for r in fit['contacts'])
    assert all(not r['hits'] for r in fit['cable_reserves']+fit['bench_insertion_samples'])
    assert all(r['pin_to_pcb_mm3']<1e-6 for r in fit['terminal_checks'])
    assert mesh['required_clearance_passed'] and not mesh['mechanical_release']
    report=dict(master_sha256=sha(MASTER),source_checkpoint_sha256=SOURCE_SHA,
        evidence_sha256={n:sha(OUT/n) for n in ['fit-audit.json','mesh-proof.json','shell-source-bop.json']},
        prototype_integration_allowed=True,strict_BOP_passed=False,mechanical_release=False,
        new_PETG_spacers_BOP_clean=True,legacy_shell_error_classes=counts,
        shell_errors_repaired=False,identical_error_locations_proven=False,
        coarse_shell_mesh_difference_passed=mesh['shell_mesh_difference_gate_passed'],
        deck_difference_method='Native coplanar cut returned impossible volume; retained as failure. Independent manifold difference and analytical 2x cylindrical through-hole volume required instead.',
        scope=__doc__,next_gate='Repair legacy shell BRep before production; physical PETG, board stress, wiring/heat tests remain mandatory.')
    (OUT/'prototype-scope.json').write_text(json.dumps(report,indent=2),encoding='utf8',newline='\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':baseline() if '--baseline' in sys.argv else main()
