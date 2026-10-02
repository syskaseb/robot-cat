"""Close only changed S0 hardware/wire/restraint pairs and record bench order.

This local interface is NOT a new selected print set or complete W5.
Native Deck proof is reconciled separately once its worker finishes.
"""
from pathlib import Path
from datetime import datetime, timezone
import sys, json
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'tools/cad'), str(ROOT/'tools/electronics')]
from servo_fuse_inputs_r1 import save, sha
LAYOUT = ROOT/'hardware/electronics/full-cat/source-switch-layout-r6'
REST = ROOT/'hardware/electronics/full-cat/source-switch-restraints-r2'
MOUNT = ROOT/'hardware/electronics/full-cat/source-switch-mount-finish-r4'
OUT = ROOT/'hardware/electronics/full-cat/source-switch-assembly-finish-r3'

def main():
    import FreeCAD as A
    import Part
    import main_positive_input_r1 as C
    start = datetime.now(timezone.utc)
    OUT.mkdir(parents=True, exist_ok=True)
    assert not (OUT/'checks.json').exists(), 'Preserve completed evidence.'
    hashes = {}
    def load(p):
        hashes[p.relative_to(ROOT).as_posix()] = sha(p)
        s = Part.Shape(); s.read(str(p)); return s
    reports = []
    for folder in (LAYOUT, REST, MOUNT):
        p = folder/'checks.json'; hashes[p.relative_to(ROOT).as_posix()] = sha(p)
        meta = json.loads(p.read_text(encoding='utf-8'))
        assert not meta['hits'] and not meta['errors'], str(folder)
        for name, h in meta['source_sha256'].items():
            assert sha(ROOT/name) == h, name
        reports.append(meta)
    layout, rest, mount = reports
    wires = {p.stem:load(p) for p in LAYOUT.glob('W*_DESIGN.brep')}
    restraints = {p.stem:load(p) for p in REST.glob('*_DESIGN.brep')}
    hardware = {p.stem:load(p) for p in MOUNT.glob('M*_DESIGN.brep') if 'tool' not in p.stem}
    deck = load(REST/'Deck_candidate_UNSELECTED.brep')
    m2={}
    for x in (-87.5,-37):
        deck=deck.fuse(Part.makeCylinder(1.2,4,A.Vector(x,92,105)))
        deck=deck.cut(Part.makeCylinder(1.2,4.2,A.Vector(x+8,92,104.9)))
        def cyl(z,r,h):return Part.makeCylinder(r,h,A.Vector(x+8,92,z))
        m2[f'M2bolt_{x}']=cyl(97.3,1,12).fuse(cyl(109.3,1.9,2))
        m2[f'M2washers_{x}']=cyl(100.7,2.5,.3).cut(cyl(100.6,1.1,.5)).fuse(cyl(109,2.5,.3).cut(cyl(108.9,1.1,.5)))
        m2[f'M2nut_{x}']=cyl(99.1,2.31,1.6).cut(cyl(99,1,1.8))
    assert deck.isValid() and len(deck.Solids)==1
    deck.exportBrep(str(OUT/'Deck_candidate_UNSELECTED.brep'))
    for n,s in m2.items():s.exportBrep(str(OUT/(n+'_DESIGN.brep')))
    native_mount = load(ROOT/'hardware/cad/studies/source-switch-mount-finish-r4/Mount_WORLD.brep')
    hits, errors, access, pairs = [], [], [], 0
    def check(n,s,m,t,temporary=False):
        nonlocal pairs
        if not s.BoundBox.intersect(t.BoundBox): return
        for a in s.Solids:
            for b in t.Solids:
                if not a.BoundBox.intersect(b.BoundBox): continue
                pairs += 1
                try:
                    v = a.common(b).Volume
                    if v > 1e-5:
                        row = dict(part=n, owner=m, hit_mm3=v)
                        if temporary and m not in ('NativeMount','FinalDeck'):
                            row['condition'] = 'Fit/tighten mount to REMOVED Deck before wires, cover and P0/BUS enclosure; not in-place access.'
                            access.append(row)
                        else: hits.append(row)
                except Exception as ex: errors.append(dict(part=n,owner=m,error=str(ex)))
    for n,s in wires.items():
        for m,t in hardware.items(): check(n,s,m,t)
    for n,s in restraints.items():
        for m,t in {**hardware,**m2}.items(): check(n,s,m,t)
    for n,s in m2.items():
        check(n,s,'NativeMount',native_mount)
        check(n,s,'FinalDeck',deck)
    # M2 tools only. M6/M10 tools and bench conditions are pinned in mount R2.
    owners, oldhash = C.current_owners()
    owners.pop('Deck_R41'); owners.pop('MAIN_R40')
    owners['FinalDeck'] = deck
    owners['NativeMount'] = native_mount
    owners['MAIN_R44'] = load(ROOT/'hardware/cad/studies/main-positive-native-r2/MAIN_WORLD.brep')
    owners.update(wires); owners.update(restraints); owners.update(hardware)
    for x in (-87.5,-37):
        head = Part.makeCylinder(2.2,30,A.Vector(x+8,92,111.3))
        nut = Part.makeCylinder(3.5,25,A.Vector(x+8,92,74.1)).cut(
            Part.makeCylinder(1.2,25.2,A.Vector(x+8,92,74)))
        for side,s in [('head',head),('nut',nut)]:
            n=f'M2_{side}_tool_{x}'
            for m,t in owners.items(): check(n,s,m,t,True)
            s.exportBrep(str(OUT/(n+'_DESIGN.brep')))
    end = datetime.now(timezone.utc)
    result = dict(status='REJECTED_CHANGED_INTERFACE' if hits or errors else 'LOCAL_SOURCE_ASSEMBLY_CLOSED_NEEDS_NATIVE_SELECTION',
        hits=hits,errors=errors,pairs=pairs,M2_temporary_tool_contacts=access,
        inherited_M6_M10_tool_contacts=mount['tool_access_contacts'],
        nominal_wire_blanks_mm={n:r['nominal_candidate_blank_mm'] for n,r in layout['lengths'].items()},
        extra_fasteners=mount['actual_nominal_SKUs'],extra_T18I=2,
        added_M2=dict(screws_M2x12=2,washers_DIN125_M2=4,nuts_DIN934_M2=2),
        deck_bolt_xy=mount['deck_bolt_xy'],
        M2_tool_reserve=dict(nut_radius_mm=3.5,nut_reach_mm=25,head_radius_mm=2.2,head_reach_mm=30,not_exact_tool_SKU=True),
        P_SYS_physical_labels_plus_X=layout['P_SYS_labels_plus_X'],
        label_change='Swap physical .1/.2 labels AND replace W043 geometry together; electrical graph/net unchanged.',
        assembly_order=[
            'Battery disconnected. Keep Deck removed from P0. Trial exact switch against provisional casing/stud/flange datums.',
            'Mount S0 with two M6x20, four M6 washers and two M6 nuts BEFORE fitting ring terminals.',
            'Attach mount to removed Deck with two M2x12, four M2 washers and two M2 nuts; tighten before wires and upper cover.',
            'Pre-thread two W066 T18I through integral cradles; P_SYS tunnel remains above Deck. Do not cinch empty cradles.',
            'Keep F0 W076 factory lead intact, trim only after measuring its delivered length and trial routing. Fit TE130207 IN.',
            'Fit TE130207 OUT to HELU23802 W066. Strip/crimp per pinned TE instructions, not guessed conductor dimensions.',
            'Fit two M10 washers/nuts and tighten on removed Deck BEFORE P0/BUS installation; actual torque/creep test in phase2.',
            'Route W066 through both cradles to P_SYS.1 atX-84. Keep W04340mm to P_SYS.2 atX-76.5 and tied F_PI housing.',
            'Relabel physical P_SYS ports .1,.2,.3,.4,.5 west-to-east together with W043 replacement; verify net labels before closing.',
            'Restore existing F0 relief and secure W066 ties without crushing insulation. Install Deck/P0/BUS/cover only afterwards.',
            'For removal: disconnect battery, open cover and detach relevant source leads before undoing obstructed mount hardware.'
        ],
        prototype_conditions=mount['prototype_conditions']+[
            'W07680/W066330/W04340 are nominal trial blanks, NOT delivered measurements or physical cut instructions.',
            'Preserved R48 remains selected; no new Deck/mount or wire allocation selected by this report.',
            'No additional lower-shell cut is established by current family reserve checks. Check delivered key/body before phase2 closure.'
        ],
        selected=False,W5_complete=False,physical_pass=False,
        source_sha256={**oldhash,**hashes},script_sha256=sha(Path(__file__)),
        started_utc=start.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-start).total_seconds())
    save(OUT/'checks.json',result)
    print(json.dumps({k:result[k] for k in ('status','hits','errors','pairs','M2_temporary_tool_contacts','worker_wall_seconds')}),flush=True)

if __name__ == '__main__': main()
