"""Bank removal without opening the obstructed installed P-WAGO levers.

Prewire loose P-WAGO before fastening to Deck. After ATO/holder release,
cut input ties and move TE-IN inward5.5mm. Construct equal-length paths
with unchanged WAGO ends, preserving nominalR12.4. This is a sampled
geometric proposal, not physical cable-deformation qualification.
"""
from pathlib import Path
from datetime import datetime, timezone
import math, json, sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'tools/electronics')]
from servo_fuse_inputs_r1 import save, sha
OUT = ROOT / 'hardware/electronics/full-cat/servo-fuse-bank-connected-release-r1'


def main():
    import FreeCAD as A
    import Part
    import servo_fuse_side_bank_r10 as layout
    begin = datetime.now(timezone.utc)
    OUT.mkdir(parents=True, exist_ok=True)
    assert not (OUT / 'checks.json').exists(), 'Preserve completed construction'
    source = ROOT / 'tools/electronics/servo_fuse_side_bank_r8.py'
    code = source.read_text(encoding='utf-8')
    code = code[code.index('def input_path('):code.index('\ndef current_owners(')]
    code = code.replace('R=12.4):', 'R=12.4, turn_y=85.5):')
    code = code.replace('assert p.z>end[2]', 'assert p.z>end[2]-10')
    code = code.replace('side*p.y<85.5', 'side*p.y<turn_y').replace('side*85.5', 'side*turn_y')
    code = code.replace('line(A.Vector(p.x,p.y,end[2]));arc(dz,u,math.pi/2)',
                        'line(A.Vector(p.x,p.y,end[2]-10));arc(dz,u,math.pi/2)')
    code = code.replace('line(A.Vector(p.x,side*stop,p.z));arc(u,up,math.pi/2)',
                        'line(A.Vector(p.x,side*stop,p.z));arc(u,up,math.pi/2);line(A.Vector(*end))')
    ns = {'math': math}; exec(code, ns)
    route = ns['input_path']
    route_meta = ROOT / 'hardware/electronics/full-cat/servo-fuse-side-bank-r11/checks.json'
    spec = json.loads(route_meta.read_text(encoding='utf-8'))
    save(OUT / 'intent.json', dict(started_utc=begin.isoformat(), selected=False,
         unchanged_WAGO_ends=True, unchanged_installed_paths=True,
         withdrawal_input_TE_mm=5.5, fixed_length=True, nominal_radius_mm=12.4,
         physical_pass=False, W5_complete=False,
         sequence='Prewire loose WAGO and fasten it only with levers closed. For bank removal, remove ATO/unclip holders/raise10mm first, cut24 bank ties, free input ends inward without opening WAGO. Output TE remain stationary.'))
    print('LOAD_CURRENT_OWNERS', flush=True)
    owners, hashes, _ = layout.current_owners()

    def load(p):
        hashes[p.relative_to(ROOT).as_posix()] = sha(p)
        return Part.read(str(p))

    hashes[source.relative_to(ROOT).as_posix()] = sha(source)
    hashes[route_meta.relative_to(ROOT).as_posix()] = sha(route_meta)
    for n in list(owners):
        if any(f in n for f in ('/servo-fuse-bank-restraints-r2/', '/servo-fuse-bank-restraints-fit-r2/')):
            del owners[n]  # removed24 input/output ties; PETG banks replaced below
    owners['R49Deck'] = load(ROOT / 'hardware/cad/studies/servo-fuse-deck-native-r1/Deck_WORLD.brep')
    for p in (ROOT / 'hardware/cad/studies/servo-fuse-bank-clip-access-r1').glob('*_WORLD.brep'):
        owners[p.stem] = load(p)
    # Holder shells/ATO are raised/removed before this motion. Stationary
    # output TE remain, while the input TE follow the already checked5.5mm
    # service-r3 release corridor, not their old occupied positions.
    for p in (ROOT / 'hardware/electronics/full-cat/servo-fuse-side-bank-r11').glob('F_*_OUT_DESIGN.brep'):
        owners[p.stem] = load(p)
    hits, errors, records = [], [], []
    pairs = 0

    def check(phase, n, s, m, t):
        nonlocal pairs
        if not s.BoundBox.intersect(t.BoundBox): return
        pairs += 1
        try:
            c = s.common(t)
            if c.Volume > 1e-5:
                hits.append(dict(phase=phase, part=n, owner=m, hit_mm3=c.Volume,
                                 bounds_mm=[getattr(c.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]))
                c.exportBrep(str(OUT / (phase + '_' + n + '_HIT_' + str(len(hits)) + '.brep')))
        except Exception as exc:
            errors.append(dict(phase=phase, part=n, owner=m, error=str(exc)))

    for fraction in (0.5, 1.0):
        tubes = {}
        phase = 'release_' + str(fraction)
        print(phase, flush=True)
        for row in spec['lengths']:
            name = row['id']; pose = spec['placements'][name]
            start, end = pose['start'], list(pose['end'])
            side = 1 if end[1] > 0 else -1
            end[1] -= side * 5.5 * fraction
            if name == 'W046': end[2] += 2  # R11 raised turnaround, retained8mm grip
            delay = 13 - 4 * int(pose['holder'] and next(e for e in (row['a'],row['b']) if e.startswith('F_')).split('.')[0][-1])
            def path(lift):
                p = route(A, Part, start, end, side, lift=lift, delay=delay, turn_y=85.5-5.5*fraction)
                if name == 'W046':
                    p = Part.Wire(p.Edges[:-1] + [Part.makeLine(p.Edges[-1].valueAt(p.Edges[-1].FirstParameter), A.Vector(end[0],end[1],end[2]-2))])
                return p
            lo, hi = -5.0, 15.0
            target = row['path_mm']
            assert path(lo).Length <= target and path(hi).Length >= target
            for _ in range(45):
                mid = (lo + hi) / 2
                if path(mid).Length < target: lo = mid
                else: hi = mid
            p = path((lo+hi)/2)
            assert abs(p.Length-target) < 1e-6
            assert all(abs(e.Curve.Radius-12.4)<1e-6 for e in p.Edges if hasattr(e.Curve,'Radius'))
            s = p.makePipeShell([Part.Wire([Part.makeCircle(1.55, A.Vector(*start), A.Vector(0,side,0))])], True, False)
            assert s.isValid() and len(s.Solids) == 1
            p.exportBrep(str(OUT / (phase+'_'+name+'_CENTERLINE.brep')))
            s.exportBrep(str(OUT / (phase+'_'+name+'_DESIGN.brep')))
            tubes[name] = s
            records.append(dict(phase=phase, wire=name, target_length_mm=target,
                                path_length_mm=p.Length, lift_mm=(lo+hi)/2,
                                TE_end_mm=[end[0],end[1],end[2]-(2 if name=='W046' else 0)],
                                fixed_WAGO_end_mm=start, turn_y_mm=85.5-5.5*fraction))
        for name,s in tubes.items():
            print(phase+' '+name, flush=True)
            for owner,t in owners.items(): check(phase,name,s,owner,t)
        for i,(name,s) in enumerate(tubes.items()):
            for other,t in list(tubes.items())[i+1:]: check(phase,name,s,other,t)
    endtime = datetime.now(timezone.utc)
    save(OUT / 'checks.json', dict(status='CONNECTED_INPUT_RELEASE_CONFLICTS' if hits or errors else 'SAMPLED_EQUAL_LENGTH_CONNECTED_INPUT_RELEASE_CLEAR',
         selected=False, physical_pass=False, W5_complete=False, hits=hits, errors=errors,
         pairs=pairs, paths=records, sampled_fractions=[0.5,1.0], continuous_deformation_qualified=False,
         source_sha256=hashes, script_sha256=sha(Path(__file__)),
         started_utc=begin.isoformat(), finished_utc=endtime.isoformat(), worker_wall_seconds=(endtime-begin).total_seconds()))
    print(json.dumps(dict(hits=hits, errors=errors, pairs=pairs)), flush=True)


if __name__ == '__main__': main()
