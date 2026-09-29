"""Reconcile all selected fuse planning boxes with current open-deck WAGO.

Pure box arithmetic, no CAD mutation. Positive reservation overlap is a layout
conflict, not a claim that supplier BReps physically intersect.
"""
import hashlib
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'hardware/electronics/full-cat/f-pwm-axial-r1'
SOURCES = {
    'layout': 'hardware/electronics/power-platform/open-deck-p0/layout.json',
    'fuses': 'hardware/electronics/full-cat/fuse-one-batch-r1/fixed-zones.json',
    'pwm': 'hardware/electronics/full-cat/f-pwm-axial-r1/card.json',
}


def gap(a, b):
    return math.sqrt(sum(max(0, a[i]-b[i+3], b[i]-a[i+3])**2 for i in range(3)))


def volume(a, b):
    return math.prod(max(0, min(a[i+3], b[i+3])-max(a[i], b[i])) for i in range(3))


def main():
    data = {k: json.loads((ROOT/v).read_text(encoding='utf-8')) for k, v in SOURCES.items()}
    wagos = {}
    for c in data['layout']['components']:
        if c['kind'] != 'WAGO':
            continue
        x0, y0, x1, y1 = c['footprint_xyxy_mm']
        wagos[c['id']] = [21+x0, y0, 109, 21+x1, y1, 109+c['planning_height_mm']]
    assert len(wagos) == 17 and wagos['P_REAR'] == [2.5, -11, 109, 39.5, 11, 120]
    fuses = {r['ref']: r['body_bbox_world_mm'] for r in data['fuses']['rows']}
    fuses['F_PWM'] = data['pwm']['mount_plan_world_mm']['under_deck_sleeved_fuse_planning_bbox']
    assert len(fuses) == 6
    rows = [{'fuse': f, 'wago': w, 'planning_overlap_mm3': volume(a, b),
             'planning_gap_mm': gap(a, b)} for f, a in fuses.items() for w, b in wagos.items()]
    conflicts = [r for r in rows if r['planning_overlap_mm3'] > 0]
    assert len(rows) == 102
    bounds = {f: gap(wagos['P_REAR'], fuses[f]) for f in ['F_PWM', 'F_AUX']}
    report = {
        'status': 'CURRENT_FRAME_LAYOUT_RECONCILED_NOT_ACTUAL_COMPONENT_COLLISION_PASS',
        'source_sha256': {k: hashlib.sha256((ROOT/v).read_bytes()).hexdigest() for k,v in SOURCES.items()},
        'checker_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'current_wago_world_reservations': wagos,
        'fuse_world_reservations': fuses,
        'pairs_checked': len(rows), 'conflicts': conflicts,
        'p_rear_unfused_distance_lower_bounds_mm': bounds,
        'rows': rows,
        'decision': 'Old fixed-zones WAGO-clear statements do not qualify this open-deck layout. Relocate conflicted fuse reservations and F_PWM/F_AUX as one coherent layout before cutting another Deck. Keep P0 WAGO unchanged.',
        'scope_limits': 'Rounded purchased-component planning boxes, not exact BRep. No installed connector, lever, conductor, tie or full robot collision qualification. Clear rows do not imply full assembly PASS. F_COIL inherited name is not authority to reintroduce GUARD.',
        'new_stl_count': 0, 'physical_pass': False,
    }
    (OUT/'layout-reconciliation.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    im = Image.new('RGB', (1080, 940), '#faf8f2')
    d = ImageDraw.Draw(im)
    def xy(x, y): return (int(110+(x+94)*3.7), int(80+(95-y)*3.7))
    d.rectangle((*xy(-94,95), *xy(136,-95)), outline='#222222', width=2)
    for name, b in wagos.items():
        d.rectangle((*xy(b[0],b[4]), *xy(b[3],b[1])), fill='#c8e1f1', outline='#24577a')
        d.text(xy(b[0],b[4]), name, fill='#163047')
    for name,b in fuses.items():
        d.rectangle((*xy(b[0],b[4]), *xy(b[3],b[1])), outline='#be422c', width=3)
        d.text(xy(b[0],b[4]+4), name+' Z'+str(b[2]), fill='#a22a1d')
    d.text((25,20), 'CURRENT OPEN-DECK: blue WAGO / red fuse planning boxes; XY projection', fill='black')
    d.text((25,825), 'Projection overlap alone is NOT 3D collision. Report includes Z and all102 pairs.', fill='black')
    d.text((25,850), 'Planning reservations only; no hardware/print PASS. No STL modified.', fill='black')
    im.save(OUT/'layout-reconciliation.png')
    print(json.dumps({'conflicts': conflicts, 'unfused_lower_bounds_mm': bounds}))


if __name__ == '__main__':
    main()
