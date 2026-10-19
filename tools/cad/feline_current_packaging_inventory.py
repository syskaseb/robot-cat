"""Read-only world-frame inventory, not a collision or validity re-test.

Use the same overlaid shapes as the latest receiver, never historical boxes.
Bounds identify shared space only; they are not proof of contact or clearance.
"""
import json
import time
from collections import defaultdict
from feline_case_zone_allocation import current_world
from plan_feline_layout import OUT


def main():
    tick = time.monotonic()
    world, fixed = current_world()
    rows = []
    groups = defaultdict(list)
    for name, shape in fixed.items():
        bb = shape.BoundBox
        bounds = [[bb.XMin, bb.YMin, bb.ZMin], [bb.XMax, bb.YMax, bb.ZMax]]
        meta = world.meta.get(name, {})
        kind = ('planning_reservation' if name.startswith('StructureReserve:') or
                meta.get('kind') == 'rectangular_reservation' else meta.get('kind', 'material'))
        row = dict(name=name, bounds_mm=bounds, centre_mm=list(bb.Center),
                   dimensions_mm=[bb.XLength, bb.YLength, bb.ZLength],
                   role=meta.get('role'), group=meta.get('group'), kind=kind)
        rows.append(row)
        if '_CP2_' in name and name.startswith('Ref_Material_F_'):
            groups['bank_purchased_all'].append(row)
            groups['bank_' + name.split('_CP2_')[0].split('Ref_Material_F_')[1]].append(row)
    extents = {}
    for key, items in groups.items():
        extents[key] = dict(count=len(items), bounds_mm=[
            [min(r['bounds_mm'][0][i] for r in items) for i in range(3)],
            [max(r['bounds_mm'][1][i] for r in items) for i in range(3)]])
    result = dict(status='CURRENT_OVERLAID_WORLD_BOUNDS_INVENTORY_NOT_COLLISION_PROOF',
                  source_sha256=world.pins, fixed=rows, bank_extents=extents,
                  N01_complete=False, physical_pass=False,
                  worker_seconds=round(time.monotonic()-tick, 3))
    dest = OUT / 'n01-current-packaging-inventory.json'
    dest.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps(dict(worker_seconds=result['worker_seconds'], count=len(rows), bank_extents=extents)), flush=True)
    for r in rows:
        if r['name'].startswith(('Ref_Material_F_', 'StructureReserve:Bank', 'CurrentMAIN', 'MAINUpper')):
            print(json.dumps(r), flush=True)


if __name__ == '__main__':
    main()
