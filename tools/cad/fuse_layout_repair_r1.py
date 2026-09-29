"""One replacement layout for the two demonstrated current-frame conflicts.

Save the design plan before mesh checks. No source/STL mutation here: accept
the locations only as input to a native Deck revision after these checks.
"""
import hashlib
import json
from pathlib import Path
import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'hardware/cad/studies/fuse-layout-repair-r1'
SOURCES = {
    'deck': 'hardware/cad/studies/deck-f-pwm-axial-r1/DeckP10_axial_f_pwm_candidate_x1.stl',
    'cover': 'hardware/cad/studies/upper-cover-mount-r1/RaisedUpperCover_mount_x1.stl',
    'carrier': 'hardware/cad/studies/full-cat-board-carrier/service-access-r1/CarrierServicePorts_candidate_x1.stl',
    'layout': 'hardware/electronics/full-cat/f-pwm-axial-r1/layout-reconciliation.json',
}


def overlap(a,b):
    return all(min(a[i+3], b[i+3]) > max(a[i], b[i]) for i in range(3))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    layout = json.loads((ROOT/SOURCES['layout']).read_text())
    plan = {
        'status': 'DESIGN_REQUIREMENTS_NOT_DELIVERED_DIMENSIONS',
        'source_sha256': {k: hashlib.sha256((ROOT/v).read_bytes()).hexdigest() for k,v in SOURCES.items()},
        'replacements': {
            'F_HP': {'bbox': [0,-10.6,93,20,10.6,105],
                     'tie_slots': [],
                     'existing_slots_reused': [[4,-12.5],[4,12.5],[16,-12.5],[16,12.5]],
                     'meaning': 'Move existing FHAC body below Deck instead of occupying P_REAR above it; reuse existing four strap slots. Underside robot parts and full leads still require final installation check.'},
            'F_PWM': {'bbox': [25,-26,99,75,-20,105],
                      'tie_slots': [[x,y] for x in [28,44,56,72] for y in [-28,-18]],
                      'meaning': 'Whole50x6x6 insulated pigtail DESIGN allowance. Two body ties x44/56, independent wires x28/72. Fuse centred50,-23,102; cylindrical shape conservatively boxed. Four strap loops require eight slots, not four.'},
        },
        'top_tie_lock_design_boxes': [[x-2.5,-27,109,x+2.5,-19,115] for x in [28,44,56,72]],
        'limitations': ['Tie lock height6mm is a design allocation, not manufacturer measurement.',
                        'Actual WAGO wire exit/near cavity, full bends and <=50mm path remain to be specified.',
                        'No native slots cut and no new print created by this script.',
                        'FHAC leads, installed board headers and exact bought hardware are not represented.'],
        'new_stl_count': 0, 'physical_pass': False,
    }
    (OUT/'plan.json').write_text(json.dumps(plan, indent=2)+'\n')
    meshes = {k: trimesh.load_mesh(ROOT/SOURCES[k]) for k in ['deck','cover','carrier']}
    meshes['carrier'].apply_translation([21,0,144])
    assert all(m.is_watertight for m in meshes.values())
    boxes = {k:r['bbox'] for k,r in plan['replacements'].items()}
    boxes.update({f'PWM_lock_{i}':b for i,b in enumerate(plan['top_tie_lock_design_boxes'])})
    rows=[]
    for name,b in boxes.items():
        shape=trimesh.creation.box(extents=np.array(b[3:])-np.array(b[:3]))
        shape.apply_translation((np.array(b[3:])+np.array(b[:3]))/2)
        for target,m in meshes.items():
            v=0.0
            if overlap(b, np.r_[m.bounds[0],m.bounds[1]]):
                v=float(trimesh.boolean.intersection([shape,m],engine='manifold').volume)
            rows.append({'item':name,'target':target,'volume_mm3':v})
        for target,other in layout['current_wago_world_reservations'].items():
            if overlap(b,other): rows.append({'item':name,'target':target,'planning_overlap':True})
        for target,other in layout['fuse_world_reservations'].items():
            if target not in plan['replacements'] and overlap(b,other):
                rows.append({'item':name,'target':target,'planning_overlap':True})
    slots=[p for r in plan['replacements'].values() for p in r['tie_slots']]
    probes=np.array([[x+dx,y+dy,107] for x,y in slots for dx in [-2,2] for dy in [-1,1]])
    material=meshes['deck'].contains(probes).reshape(len(slots),4).all(axis=1).tolist()
    hits=[r for r in rows if r.get('volume_mm3',0)>1e-5 or r.get('planning_overlap')]
    result={'status':'LIMITED_RELOCATION_SCREEN', 'rows':rows,'hits':hits,
            'slot_centres':slots,'four_corners_in_material':material,
            'new_stl_count':0,'route_qualified':False,'physical_pass':False}
    (OUT/'checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'hits':hits,'slot_material':material}))


if __name__=='__main__': main()
