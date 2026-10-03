"""Read the current installed or explicitly released owner recipe, no builder.

The accepted native files remain authoritative. Do not overwrite an earlier
proof or treat released terminals as the installed full construction.
"""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

def receive(released=False):
    from servo_fuse_inputs_r1 import sha
    p=ROOT/'tools/electronics/servo_fuse_bank_fixed_rr_lift_r6.py'
    ns=dict(__file__=str(p),__name__='current_owner_definition')
    exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),ns)
    code=ns['code']
    marker="    save(OUT/'owner-census.json'" if released else '    omitted=[]'
    code=code[:code.index(marker)]+'    return owners,module,pins\n'
    code=code.replace("    assert not (OUT/'checks.json').exists(),'Preserve result'",'    # Read-only receipt; existing checks are preserved.')
    marker="    ns=dict(__file__=str(loader),__name__='owners_only');"
    assert marker in code
    code=code.replace(marker,"    code=code.replace(\"    assert not (out / 'checks.json').exists(), 'Preserve completed results'\",'    # Read-only clip-owner receipt.')\n"+marker)
    ctx=dict(__file__=str(p),__name__='read_current_owners_only')
    exec(compile(code,str(p),'exec'),ctx)
    owners,module,pins=ctx['main']();pins[p.relative_to(ROOT).as_posix()]=sha(p)
    pins[Path(__file__).relative_to(ROOT).as_posix()]=sha(Path(__file__))
    return owners,module,pins
