"""Repair overlapping cut-tool topology; preserve full R6 layout and evidence.

R6 failed strict BOP after export. Its overlapping tie tools were a Compound,
not a Boolean union. R7 unites those tools and avoids automatic refinement
of the two new Deck operations. This is a repair hypothesis until checked.
Contact identities are saved incrementally, BEFORE any final strict check.
"""
from pathlib import Path

parent = Path(__file__).with_name('servo_fuse_parent_complete_layout_r6.py')
ns = {'__file__': str(parent), '__name__': 'r6_definition_only'}
exec(compile(parent.read_text(encoding='utf-8').rsplit('exec(compile', 1)[0], str(parent), 'exec'), ns)
code = ns['code'].replace('servo-fuse-parent-complete-layout-r6', 'servo-fuse-parent-complete-layout-r7')


def replace(old, new):
    global code
    assert code.count(old) == 1, old[:100]
    code = code.replace(old, new)


replace("    V = A.Vector", "    V = A.Vector\n    pin(ROOT/'tools/electronics/servo_fuse_parent_complete_layout_r6.py')\n    pin(ROOT/'hardware/electronics/full-cat/servo-fuse-parent-complete-layout-r6/native-failure.json')")
replace("fused.Shapes=[previous]+pads;fused.Refine=True", "fused.Shapes=[previous]+pads;fused.Refine=False")
replace("tools=d.addObject('Part::Compound','AllMainTiePassTools');tools.Links=slots",
        "tools=d.addObject('Part::MultiFuse','AllMainTiePassTools');tools.Shapes=slots;tools.Refine=False")
replace("previous.Base=fused;previous.Tool=tools;previous.Refine=True", "previous.Base=fused;previous.Tool=tools;previous.Refine=False")
replace("    owners['CandidateDeck']=deck", """    try:
        strict_native = deck.check(True)
    except ValueError as exc:
        strict_native = [str(exc)]
    save(OUT/'native-validation.json',dict(strict_BOP_report=strict_native,
        single_solid=len(deck.Solids)==1,closed_STL=True,relocated_reopen=True,
        parameter_volumes_mm3=[volume,probe,volume],selected=False,physical_pass=False,
        script_sha256=sha(Path(__file__)),source_sha256=pins))
    if strict_native:
        raise ValueError('R7 native topology still invalid: '+str(strict_native))
    print('STRICT_NATIVE_VALIDATED',flush=True)
    owners['CandidateDeck']=deck""")
replace("        for m,t in owners.items():check(n,s,m,t)", """        for m,t in owners.items():check(n,s,m,t)
        save(OUT/'shared-fit-progress.json',dict(last_part=n,hits=hits,errors=errors,pairs=pairs,
             complete=False,selected=False,physical_pass=False))""")
replace("    ended=datetime.now(timezone.utc)", """    save(OUT/'shared-fit-progress.json',dict(hits=hits,errors=errors,pairs=pairs,
         complete=True,selected=False,physical_pass=False))
    ended=datetime.now(timezone.utc)""")
replace('strict_BOP_report=deck.check(True)', 'strict_BOP_report=strict_native')
exec(compile(code, str(Path(__file__).resolve()), 'exec'))
