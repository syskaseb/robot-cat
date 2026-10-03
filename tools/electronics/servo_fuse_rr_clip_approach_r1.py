"""Four clip-tool approaches against the CURRENT complete static construction.

Run after all R3/R4 native results. Check a0.8x3mm nominal flat tool from above,
not a finger or a claim that a PETG latch will flex. Only contact with the
explicit four existing lip/column stocks is intentional; no whole-Deck waiver.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, math, sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/electronics'))
from servo_fuse_inputs_r1 import sha, save


def main():
    import FreeCAD as A
    import Part
    from servo_fuse_rolled_cradles_native_r1 import retained_owners
    start = datetime.now(timezone.utc)
    out = ROOT / 'hardware/electronics/full-cat/servo-fuse-rr-clip-approach-r1'
    out.mkdir(parents=True, exist_ok=True)
    assert not (out / 'checks.json').exists(), 'Preserve completed results'
    pins = {}
    V = A.Vector

    def pin(p):
        pins[p.relative_to(ROOT).as_posix()] = sha(p)

    def load(p):
        pin(p)
        return Part.read(str(p))

    def read(rel):
        p = ROOT / rel
        pin(p)
        return json.loads(p.read_text(encoding='utf-8'))

    def box(b):
        return Part.makeBox(b[3]-b[0], b[4]-b[1], b[5]-b[2], V(*b[:3]))

    def bounds(s):
        return [getattr(s.BoundBox, k) for k in ('XMin', 'YMin', 'ZMin', 'XMax', 'YMax', 'ZMax')]

    final = read('hardware/electronics/full-cat/servo-fuse-rear-output-stations-parameter-r4/checks.json')
    fit = read('hardware/electronics/full-cat/servo-fuse-rear-output-stations-native-r3/checks.json')
    assert not fit['hits'] and not fit['errors'] and not fit['mount_failures']
    assert len(final['exports']) == 4 and all(r['relocated_reopen'] for r in final['exports'])
    # Expand the existing exact owner recipe without executing its builder.
    definition = ROOT / 'tools/electronics/servo_fuse_rear_output_stations_native_r3.py'
    for rev in (1, 2, 3):
        pin(ROOT / f'tools/electronics/servo_fuse_rear_output_stations_native_r{rev}.py')
    ns = dict(__file__=str(definition), __name__='clip_owner_definition_only')
    exec(compile(definition.read_text(encoding='utf-8'), str(definition), 'exec'), ns)
    text = ns['code']
    recipe = text[text.index('    # Reuse exactly the R8 owner recipe'):text.index('    stocks=[]')]
    ctx = dict(ROOT=ROOT, A=A, Part=Part, json=json, math=math,
               V=V, pin=pin, load=load, retained_owners=retained_owners)
    exec(compile('def receive():\n'+recipe+'\n    return owners\n', 'current_clip_owners', 'exec'), ctx)
    owners = ctx['receive']()
    keys = dict(Deck='CandidateDeck', BankRight='Bank/RightClipAccessFinished_WORLD',
                Cover='ModifiableCover', BankLeft='Bank/LeftClipAccessFinished_WORLD')
    for row in final['exports']:
        cad = ROOT / row['file']
        pin(cad)
        owners[keys[row['tag']]] = load(cad.parent / (row['tag']+'_WORLD.brep'))
    folder = ROOT / 'hardware/electronics/full-cat/servo-fuse-rear-output-stations-native-r3'
    for p in folder.glob('*Tie*_DESIGN.brep'):
        owners['CurrentRear/'+p.stem] = load(p)
    # These boxes are exactly the retained native R7 four columns/lips.
    # Excluding their actual stock admits intended tool contact, not clearance
    # through any other Deck fixture, the purchased MTA body or a cable.
    clip_source = ROOT / 'tools/electronics/servo_fuse_rolled_cradles_native_r7.py'
    pin(clip_source)
    clip_intent = read('hardware/electronics/full-cat/servo-fuse-rolled-cradles-native-r7/clip-intent.json')
    assert len(clip_intent['clips']) == 4
    clips = [box(r[key]) for r in clip_intent['clips'] for key in ('column_mm','lip_mm','anchor_mm')]
    intended = clips[0].multiFuse(clips[1:])
    deck = owners['CandidateDeck']
    probes, hits, errors, pairs = [], [], [], 0

    def check(ident, phase, tool):
        nonlocal pairs
        local = []
        for owner, s in owners.items():
            if not tool.BoundBox.intersect(s.BoundBox):
                continue
            pairs += 1
            try:
                c = tool.common(s)
                if owner=='CandidateDeck' and c.Volume>1e-5:
                    # Subtract explicit intended stock from the SMALL witness,
                    # not an expensive global Cut of the complete native Deck.
                    c = c.cut(intended)
                if c.Volume > 1e-5:
                    row = dict(tool=ident, phase=phase, owner=owner, volume_mm3=c.Volume, bounds_mm=bounds(c))
                    hits.append(row)
                    local.append(row)
                    c.exportBrep(str(out/f'HIT_{len(hits)}.brep'))
            except Exception as exc:
                errors.append(dict(tool=ident, phase=phase, owner=owner, error=str(exc)))
        return local

    for k, y in enumerate((-82, -77)):
        for side, x in [('L', 27.95), ('R', 63.25)]:
            ident = f'RRClip{k}{side}'
            #0.8mm thickness in X,3mm width in Y; short vertical approach.
            b = [x,y-1.5,130.3,x+.8,y+1.5,147]
            tool = box(b)
            tool.exportBrep(str(out/(ident+'_TOOL_APPROACH.brep')))
            intended_contact = tool.common(deck.common(intended)).Volume
            local = check(ident, 'tool_approach', tool)
            clip = next(r for r in clip_intent['clips'] if r['index']==k and r['side']==side)
            # A conservative nominal outward envelope, NOT a PETG solution.
            #3.4mm clears the3mm lip overlap with0.4mm gap. The explicit root
            # stock belongs to this clip; all surrounding stock stays checked.
            cb, lb = clip['column_mm'], clip['lip_mm']
            sweep = [min(cb[0],lb[0]), min(cb[1],lb[1]), min(cb[2],lb[2]),
                     max(cb[3],lb[3]), max(cb[4],lb[4]), max(cb[5],lb[5])]
            sweep[0 if side=='L' else 3] += -3.4 if side=='L' else 3.4
            nominal_motion = box(sweep)
            nominal_motion.exportBrep(str(out/(ident+'_NOMINAL_RELEASE_ENVELOPE.brep')))
            release_hits = check(ident, 'nominal_outward_clip_envelope', nominal_motion)
            probes.append(dict(id=ident, bounds_mm=b, intended_clip_contact_mm3=intended_contact,
                               clear_approach=not local, clear_nominal_release=not release_hits,
                               outward_PROJECT_mm=3.4, PETG_deflection_qualified=False))
            print('RR_CLIP_APPROACH_AND_RELEASE', ident, len(local), len(release_hits), flush=True)
    save(out/'checks.json', dict(
        status='RR_NOMINAL_TOOL_APPROACH_CONFLICTS' if hits or errors else 'RR_NOMINAL_TOOL_APPROACH_CLEAR_LATCH_ACTION_PHASE2',
        selected=False, physical_pass=False, W5_complete=False,
        tool_assumption_mm={'thickness':.8, 'width':3, 'approach_top_Z':147},
        fixture_change=False, probes=probes, hits=hits, errors=errors, pairs=pairs,
        actual_latch_deflection_qualified=False, WAGO_lever_qualified=False, shared_bank_release_qualified=False,
        allowed_contact='Only the explicit existing four lip/column/root stocks; all other Deck checked. No elastic/strength or full screwdriver-shaft claim.',
        source_sha256=pins, script_sha256=sha(Path(__file__)),
        started_utc=start.isoformat(), finished_utc=datetime.now(timezone.utc).isoformat(),
        worker_wall_seconds=(datetime.now(timezone.utc)-start).total_seconds()))
    print(json.dumps(dict(tools=4, hits=len(hits), errors=len(errors), pairs=pairs)), flush=True)


if __name__ == '__main__':
    main()
