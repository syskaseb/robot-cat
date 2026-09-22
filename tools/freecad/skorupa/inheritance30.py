"""Check inherited world BReps, allowing only bounded serialization roundoff.

This is a token-by-token comparison, not a topological/geometric equivalence
solver. Non-numeric tokens and token counts must match exactly; alignment
whitespace is ignored. It only proves
that the 249 parts not intentionally replaced in v30 retained their serialized
representation within 1e-9 absolute / 1e-12 relative numeric tolerance.
"""
from pathlib import Path
import hashlib
import json
import math
import re

ROOT = Path(__file__).resolve().parents[3]
NUMBER = re.compile(r"(?<![A-Za-z_])[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][-+]?\d+)?")


def compare_text(a, b):
    if a == b:
        return dict(byte_identical=True, changed_numbers=0, max_absolute_delta=0.)
    assert NUMBER.sub('#', a).split() == NUMBER.sub('#', b).split(), 'Non-numeric structure differs'
    va, vb = NUMBER.findall(a), NUMBER.findall(b)
    assert len(va) == len(vb), 'Numeric token count differs'
    count, peak = 0, 0.
    for ta, tb in zip(va, vb):
        if ta == tb:
            continue
        x, y = float(ta), float(tb)
        assert math.isfinite(x) and math.isfinite(y), 'Non-finite token'
        assert math.isclose(x, y, abs_tol=1e-9, rel_tol=1e-12), (ta, tb)
        count += 1
        peak = max(peak, abs(x-y))
    return dict(byte_identical=False, changed_numbers=count, max_absolute_delta=peak)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    old, new = (ROOT/'hardware/skorupa'/r for r in ['v29', 'v30'])
    plans = [json.loads((p/'assembly-plan.json').read_text()) for p in [old, new]]
    for p, plan, filename in zip([old, new], plans,
                                 ['Kot_v29_OGON_PROTOTYP.FCStd', 'Kot_v30_ELEKTRONIKA.FCStd']):
        assert sha(p/filename) == plan['source_sha256']
        assert json.loads((p/'shape-cache/index.json').read_text())['source_sha256'] == plan['source_sha256']
    replaced = {'IMU', 'ShellMounted20', 'Part__Feature038'}
    names = {r['name'] for r in plans[0]['components']} - replaced
    assert len(names) == 249
    rows = []
    for name in sorted(names):
        files = [p/'shape-cache'/(name+'.brep') for p in [old, new]]
        result = compare_text(*(p.read_text(encoding='ascii') for p in files))
        rows.append(dict(name=name, source_BRep_sha256=sha(files[0]),
                         target_BRep_sha256=sha(files[1]), **result))
    report = dict(source_sha256=plans[1]['source_sha256'], inherited_from_sha256=plans[0]['source_sha256'],
                  verified=True, absolute_tolerance=1e-9, relative_tolerance=1e-12,
                  byte_identical=sum(r['byte_identical'] for r in rows),
                  max_absolute_delta=max(r['max_absolute_delta'] for r in rows),
                  inherited_parts=len(rows), parts=rows, scope=__doc__)
    (new/'inheritance-check.json').write_text(json.dumps(report, indent=2), encoding='utf8')
    print(json.dumps({k:v for k,v in report.items() if k!='parts'}, indent=2))


if __name__ == '__main__':
    main()
