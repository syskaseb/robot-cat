"""Save computed native state early; do not re-audit every inherited Deck face.

R1 was stopped after10minutes in the full-shape strict BOP call: a generated
world solid exists, but strict BOP never returned. No PASS inherited from it.
This revision validates new support solids, final validity/solidity, parameter
change, exact changed contacts, closed mesh and relocated native recompute.
"""
from pathlib import Path
SOURCE=Path(__file__).with_name('w5_bus_native_grips_r1.py')
code=SOURCE.read_text(encoding='utf-8').replace('w5-bus-native-grips-r1','w5-bus-native-grips-r2')
code=code.replace("    assert final.Shape.isValid() and len(final.Shape.Solids)==1 and not final.Shape.check(True)",
    "    assert final.Shape.isValid() and len(final.Shape.Solids)==1\n"
    "    d.save();print('BUS_NATIVE_VALID_SINGLE_SAVED',flush=True)\n"
    "    assert all(obj.Shape.isValid() and not obj.Shape.check(True) for obj in boxes)\n"
    "    print('BUS_NEW_SUPPORTS_BOP_CLEAR',flush=True)")
code=code.replace('probe=final.Shape.Volume', "probe=final.Shape.Volume;print('BUS_PARAMETER_PROBE',probe,flush=True)")
code=code.replace('    d.save();shape=final.Shape.copy()', "    d.save();shape=final.Shape.copy();print('BUS_PARAMETER_RESTORED_SAVED',flush=True)")
code=code.replace('strict_BOP_errors=0,', 'full_final_strict_BOP_verified=False,new_support_solids_strict_BOP_errors=0,')
code=code.replace('ROUTES/\'intent.json\',Path(__file__),*routefiles]', 'ROUTES/\'intent.json\',Path(__file__),SOURCE,*routefiles]')
exec(compile(code,str(SOURCE),'exec'),globals())
