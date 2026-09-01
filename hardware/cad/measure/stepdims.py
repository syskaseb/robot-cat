"""Pull hole patterns out of a STEP file without a CAD kernel.

STEP stores holes as analytic CIRCLE entities, so their radius and centre are
exact numbers in the file -- no meshing, no tolerance, no eyeballing an STL.
"""
import collections, math, re, sys

def load(path):
    txt = open(path, encoding='utf-8', errors='replace').read()
    txt = txt.split('DATA;', 1)[1]
    ents = {}
    for stmt in txt.split(';'):
        s = ' '.join(stmt.split())
        m = re.match(r"#(\d+)\s*=\s*([A-Z_0-9]+)\s*\((.*)\)\s*$", s)
        if m:
            ents[int(m.group(1))] = (m.group(2), m.group(3))
    return ents

def vec(ents, i):
    t, a = ents.get(i, (None, ''))
    if t not in ('CARTESIAN_POINT', 'DIRECTION'):
        return None
    m = re.search(r"\(([^()]*)\)", a)
    if not m:
        return None
    try:
        v = tuple(float(x) for x in m.group(1).split(','))
    except ValueError:
        return None
    return v if len(v) == 3 else None

def circles(ents):
    out = []
    for i, (t, a) in ents.items():
        if t != 'CIRCLE':
            continue
        parts = [p.strip() for p in re.split(r",(?![^(]*\))", a)]
        try:
            ax, r = int(parts[1].lstrip('#')), float(parts[2])
        except (ValueError, IndexError):
            continue
        refs = [int(x) for x in re.findall(r"#(\d+)", ents.get(ax, ('', ''))[1])]
        c = vec(ents, refs[0]) if refs else None
        d = vec(ents, refs[1]) if len(refs) > 1 else (0., 0., 1.)
        if c:
            out.append((round(r * 2, 3), c, d))
    return out

def bbox(ents):
    pts = [v for i, (t, _) in ents.items()
           if t == 'CARTESIAN_POINT' and (v := vec(ents, i))]
    return [(min(p[k] for p in pts), max(p[k] for p in pts)) for k in range(3)]

def square_patterns(cs, tol=0.05):
    """Groups of 4 same-diameter, same-plane circles on a common bolt circle."""
    found = []
    byplane = collections.defaultdict(list)
    for dia, c, d in cs:
        ax = max(range(3), key=lambda k: abs(d[k]))
        byplane[(dia, ax, round(c[ax], 2))].append(c)
    for (dia, ax, lvl), pts in byplane.items():
        u = sorted(set(tuple(round(v, 3) for v in p) for p in pts))
        if len(u) != 4:
            continue
        o = [sum(p[k] for p in u) / 4 for k in range(3)]
        rs = [math.dist(p, o) for p in u]
        if max(rs) - min(rs) < tol:
            found.append((dia, 'XYZ'[ax], lvl, round(sum(rs) / 4, 3),
                          tuple(round(v, 2) for v in o)))
    return sorted(found)

if __name__ == '__main__':
    for path in sys.argv[1:]:
        ents = load(path)
        cs = circles(ents)
        b = bbox(ents)
        print(f'\n=== {path} ===')
        print('  bbox mm: ' + '  '.join(
            f'{ax}={hi - lo:.2f}' for ax, (lo, hi) in zip('XYZ', b)))
        print(f'  {len(ents)} entities, {len(cs)} circles')
        print('  diameters: ' + ', '.join(
            f'{d}x{n}' for d, n in sorted(collections.Counter(c[0] for c in cs).items())))
        print('  --- 4-hole square patterns (bolt circles) ---')
        for dia, ax, lvl, r, o in square_patterns(cs):
            print(f'    d={dia:5.2f} mm   R={r:6.3f} (circle Ø{2*r:.2f})   '
                  f'normal {ax}, at {ax}={lvl:7.2f}   centre {o}')
