"""Check only changed16 DATA wires against the complete retained joint scope."""
from pathlib import Path
from datetime import datetime, timezone
import json, re, math
from w5_data_outward_plan import ROOT, recipes
from servo_fuse_inputs_r1 import save, sha

OUT = ROOT/'hardware/electronics/full-cat/w5-data-outward-r1'


def main():
    import FreeCAD as A, Part
    import w5_ground_network_r1 as sweep
    from w5_ground_entries_r1 import owners, RECEIVED
    from w5_exact_separation import separated
    begin = datetime.now(timezone.utc)
    assert not (OUT/'checks.json').exists()
    OUT.mkdir(parents=True, exist_ok=True)
    fixed, pins = owners(A, Part, json.loads(RECEIVED.read_text(encoding='utf-8')))
    rows = recipes(); wires = {r['wire'] for r in rows}
    joint = ROOT/'hardware/electronics/full-cat/w5-joint-upper-harness-r1'
    receipt = json.loads((joint/'checks.json').read_text(encoding='utf-8'))
    # Replace all old ground wires with the CURRENT complete planning shapes.
    replaced = wires | {w for w, role in receipt['roles'].items() if role == 'G'}
    obligations = []
    for key in list(fixed):
        if key.startswith('R53BUS/G2shared/') or any(re.search(r'(?<![A-Za-z0-9])'+re.escape(w)+r'(?![A-Za-z0-9])', key) for w in replaced):
            obligations.append(key); del fixed[key]
    for w, role in receipt['roles'].items():
        if role != 'G': continue
        p = joint/(w+'_WORLD.brep') if w != 'W061' else ROOT/'hardware/electronics/full-cat/w5-ground-facing-plan-r1/W061_BRIDGE_WORLD.brep'
        fixed[w] = Part.read(str(p)); pins.append(p)
    upper = ROOT/'hardware/electronics/full-cat/w5-leg-ground-upper-rail-r1'
    for leg in ('FL','FR','RL','RR'):
        del fixed[leg+'_G_NEW_BODY']
        p = upper/(leg+'_G_BODY_WORLD.brep'); fixed[leg+'_G_UPPER_BODY'] = Part.read(str(p)); pins.append(p)
        name = 'D_'+leg+'_design'; s = fixed[name].copy()
        s.rotate(A.Vector(3 if leg.startswith('F') else 111, 40 if leg.endswith('L') else -40, 113.5), A.Vector(0,0,1), 180)
        fixed[name] = s
    # Same prototype envelope as the prior DATA candidate, not supplier radius.
    sweep.profile = lambda wire: dict(OD_mm=2 if wire == 'W002' else 2.4, radius_mm=10)
    built = {}; lengths = []; files = []; errors = []
    for r in rows:
        path, shape = sweep.from_recipe(A, Part, r); w = r['wire']; built[w] = shape
        for suffix, s in [('WORLD',shape),('CENTERLINE_WORLD',path)]:
            p = OUT/(w+'_'+suffix+'.brep'); s.exportBrep(str(p)); files.append(p)
        nominal = path.Length+r['strip_mm']+r.get('retained_moving_candidate_mm',0)
        lengths.append(dict(wire=w, nominal_mm=nominal, trial_blank_mm=math.ceil((nominal+30)/10)*10,
            fits_factory_300mm_if_W002=nominal+30<=300 if w=='W002' else None,
            fits_loom_900mm=nominal+30<=900 if 'retained_moving_candidate_mm' in r else None))
    printed = {'SourceDeck','SourceCarrier','SourceCover','SourcePlatform','SourceBankLeft','BankRight','SourceWestHood','SourceEastHood'}
    hits = []; pending = []; pairs = 0
    for i,(w,s) in enumerate(built.items()):
        for owner,t in [*fixed.items(),*list(built.items())[:i]]:
            if not s.BoundBox.intersect(t.BoundBox): continue
            if owner in printed:
                pending.append(dict(wire=w, owner=owner, bounds_only=True)); continue
            try:
                volume = 0
                for a in s.Solids:
                    for b in t.Solids:
                        if a.BoundBox.intersect(b.BoundBox) and not separated(a,b):
                            pairs += 1; volume += a.common(b).Volume
                if volume > 1e-6: hits.append(dict(wire=w, owner=owner, volume_mm3=volume))
            except Exception as exc: errors.append(dict(wire=w, owner=owner, error=str(exc)))
        print('DATA_CHECKED',w,len(hits),flush=True)
    finish = datetime.now(timezone.utc)
    pins.extend([Path(__file__),ROOT/'tools/electronics/w5_data_outward_plan.py',
        ROOT/'tools/electronics/w5_leg_fanouts_r1.py',ROOT/'tools/electronics/w5_ground_network_r1.py',
        ROOT/'hardware/electronics/full-cat/w5-leg-fanouts-r5/intent.json',
        ROOT/'hardware/electronics/full-cat/w5-bus-pair-r52-r4/intent.json',
        ROOT/'hardware/electronics/power-platform/wiring-p0.json',joint/'checks.json'])
    save(OUT/'checks.json',dict(status='COMPLETE_DATA16_CANDIDATE_NOT_SELECTED',routes=rows,lengths=lengths,
        checked_changed_wires=16,whole_joint_scope=49,retained_ground_known_contacts=18,
        hits=hits,errors=errors,pairs=pairs,native_interfaces_pending=pending,replacement_obligations=obligations,
        native_rotated_block_mounts_pending=True,motion_qualified=False,selected=False,W5_complete=False,physical_pass=False,
        started_utc=begin.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-begin).total_seconds(),
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in dict.fromkeys(pins)},
        files={p.relative_to(ROOT).as_posix():sha(p) for p in files}))
    print('DATA_DONE',len(built),len(hits),len(errors),flush=True)


if __name__ == '__main__': main()
