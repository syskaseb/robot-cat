"""Receive one owner per retained strap; check changed material locally.

R1 was interrupted when source review identified duplicate retained straps.
Do not redesign stations because of self contacts. Do not recompute the
whole Deck merely to check two local planned slot intersections; native
whole-owner integration remains explicitly required afterwards.
"""
from pathlib import Path
P=Path(__file__).with_name('w5_remote_end_layout.py')
code=P.read_text(encoding='utf-8').replace("OUT=BASE/'w5-remote-end-layout-r1'","OUT=BASE/'w5-remote-end-layout-r2'")


def replace(old,new):
    global code
    assert code.count(old)==1,old
    code=code.replace(old,new)


replace("    fixed, printed, ends, family, rows, inherited, _, _=scope.load_scope(A,Part)",
        "    print('REMOTE_LOAD_FIXED_START',flush=True)\n    fixed, printed, ends, family, rows, inherited, _, _=scope.load_scope(A,Part)\n    print('REMOTE_LOAD_FIXED_DONE',len(fixed),flush=True)")
replace("    materials.update({'Fixed/'+k:s for k,s in fixed.items()})",
        """    for key in list(fixed):
        if key.startswith(('Input/MAIN_input_tie_','R53BUS/Plug/')):
            fixed.pop(key)
    materials.update({'Fixed/'+k:s for k,s in fixed.items()})""")
replace("    materials,pins,central,cache=current(A,Part)",
        "    materials,pins,central,cache=current(A,Part)\n    print('REMOTE_CURRENT_MATERIALS',len(materials),flush=True)")
replace("        materials[bp[name]['owner']]=owner.fuse(seat).cut(cuts[name])",
        "        print('REMOTE_ROOT_BEARING',name,v,flush=True)")
replace("                    c=a.common(b)\n                    if c.Volume>1e-6:",
        """                    c=a.common(b)
                    # A local intersection witness is sufficient to preflight
                    # a proposed slot. Final native full-owner result is NOT
                    # inferred, exported or claimed by this receipt.
                    for group in ('BAT','AUX'):
                        if owner==bp[group]['owner'] and not label.endswith('Seat') and c.Volume>1e-6:
                            c=c.cut(cuts[group])
                    if c.Volume>1e-6:""")
replace("    for wire in ('W001','W002','W003','XA05'):\n        for owner in ('Fixed/Source/Bridge','CompleteDeck'):check(wire,materials[wire],owner,materials[owner])",
        """    # Unchanged wire/parent pairs inherit their existing actual material
    # receipts. Each added seat was checked against every actual wire above.
    for group in ('BAT','AUX'):
        for label,s in proposed_shapes.items():
            if label.startswith(group) and not label.endswith('Seat'):
                check(label,s,group+'Seat',proposed_shapes[group+'Seat'])
    print('REMOTE_LOCAL_CHECKS_DONE',pairs,len(hits),len(errors),flush=True)""")
replace("    for p in (Path(__file__),OUT/'blueprint.json',ROOT/'tools/electronics/w5_bus_restraints_r3.py',",
        "    for p in (Path(__file__),ROOT/'tools/electronics/w5_remote_end_layout.py',BASE/'w5-remote-end-layout-r1/execution-observation.json',OUT/'blueprint.json',ROOT/'tools/electronics/w5_bus_restraints_r3.py',")
context=dict(__file__=str(Path(__file__).resolve()),__name__='remote_received_definition')
exec(compile(code,str(Path(__file__).resolve()),'exec'),context)
if __name__=='__main__':context['main']()
