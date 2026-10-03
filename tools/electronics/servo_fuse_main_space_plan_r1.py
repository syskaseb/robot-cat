"""One conservative space plan for all four main holders, not another blind fit.

Use exactly the R8 retained-owner recipe. Immutable owners remain obstacles;
the already authorized removable cover is reported separately. Bounding-box
clearance is sufficient (not necessary) for static room and proves neither
routes, attachment nor service. Do not select this report as a print set.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, math, sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'tools/electronics'), str(ROOT/'tools/cad')]
from servo_fuse_inputs_r1 import save, sha
OUT = ROOT/'hardware/electronics/full-cat/servo-fuse-main-space-plan-r1'


def main():
    import FreeCAD as A
    import Part
    started = datetime.now(timezone.utc)
    result = ROOT/'hardware/electronics/full-cat/servo-fuse-parent-complete-layout-r8/checks.json'
    assert result.exists(), 'Receive sole R8 worker before starting'
    OUT.mkdir(parents=True, exist_ok=True)
    assert not (OUT/'checks.json').exists(), 'Preserve completed planning evidence'
    pins = {}
    def pin(p): pins[p.relative_to(ROOT).as_posix()] = sha(p)
    def load(p):
        pin(p)
        return Part.read(str(p))
    def bounds(s):
        return [getattr(s.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]
    pin(result)
    script = ROOT/'tools/electronics/servo_fuse_parent_complete_layout_r8.py'
    ns = {'__file__': str(script), '__name__': 'space_recipe_definition_only'}
    exec(compile(script.read_text(encoding='utf-8'),str(script),'exec'),ns)
    for rev in (5,6,7,8): pin(ROOT/f'tools/electronics/servo_fuse_parent_complete_layout_r{rev}.py')
    code = ns['code']
    owner_code = code[code.index('    # Reuse exact retained source recipe'):code.index('    basepath=')]
    context = dict(ROOT=ROOT,Part=Part,pin=pin,load=load,pins=pins,sha=sha,Path=Path)
    # Keep the original function indentation AND embedded replacement string;
    # dedenting the latter changes the retained helper's own Python recipe.
    exec(compile('def receive_owners():\n'+owner_code+'\n    return owners\n',
                 'retained_R8_owner_recipe','exec'),context)
    owners = context['receive_owners']()
    # Native source Deck, not the failed-space R8 saddle layout. Rebuilding
    # any future mounting must retain all existing features and obstacles.
    owners['RetainedDeck'] = load(ROOT/'hardware/cad/studies/servo-fuse-parent-feed-grips-native-r2/Deck_WORLD.brep')
    cover = load(ROOT/'hardware/cad/studies/servo-fuse-cover-native-r4/Cover_WORLD.brep')
    boxes = [(n,bounds(s)) for n,s in owners.items()]
    save(OUT/'owners.json',dict(owners=[dict(id=n,bounds_mm=b) for n,b in boxes],
        cover_bounds_mm=bounds(cover),source_sha256=pins))
    print('ALL_RETAINED_OWNER_BOXES_SAVED',len(boxes),flush=True)
    clearance = .8  # Project prototype allowance, not manufacturer tolerance.
    def intersects(a,b,c=0):
        return all(a[i] < b[i+3]+c and a[i+3] > b[i]-c for i in range(3))
    orientations = [('axis_X_upright',[35,16,22]),('axis_X_rolled',[35,22,16]),
                    ('axis_Y_upright',[16,35,22]),('axis_Y_rolled',[22,35,16])]
    candidates = []
    for label,size in orientations:
        for x in range(-74,119,4):
            for y in range(-84,85,4):
                for bottom in (110,114,118,122):
                    b=[x-size[0]/2,y-size[1]/2,bottom,x+size[0]/2,y+size[1]/2,bottom+size[2]]
                    if b[0]<-94 or b[3]>136 or b[1]<-100 or b[4]>100 or b[5]>139: continue
                    if any(intersects(b,bb,clearance) for _,bb in boxes): continue
                    candidates.append(dict(orientation=label,centre_mm=[x,y,bottom+size[2]/2],
                        dimensions_mm=size,bounds_mm=b,body_static_bbox_clearance_mm=clearance,
                        cover_may_need_change=intersects(b,bounds(cover),clearance)))
        print('SPACE_ORIENTATION_DONE',label,len(candidates),flush=True)
    ranked = {}
    for leg,x,y in [('FL',-82.5,49.5),('FR',-82.5,-49.5),('RL',25.5,49.5),('RR',25.5,-49.5)]:
        rows=[]
        for row in candidates:
            if row['centre_mm'][1]*y<=0: continue
            b=row['bounds_mm']; axis=0 if row['orientation'].startswith('axis_X') else 1
            for face in (b[axis],b[axis+3]):
                port=list(row['centre_mm']);port[axis]=face
                distance=math.dist(port,[x,y,113.5])
                # Optimistic lower bound only: excludes arc overhead and source
                # lead. Actual tangent/radius/100mm usable assumption still gate.
                if distance+11+10>100: continue
                rows.append(dict(**row,output_face_mm=port,
                    straight_line_lower_bound_mm=distance,
                    source_and_output_routes_verified=False,native_mount_verified=False))
        rows.sort(key=lambda r:r['straight_line_lower_bound_mm'])
        ranked[leg]=rows[:40]
    ended=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='CONSERVATIVE_ROOM_FOUND' if all(ranked.values()) else 'CONSERVATIVE_BOX_PLAN_INSUFFICIENT',
        selected=False,physical_pass=False,W5_complete=False,clearance_mm=clearance,
        candidates_total=len(candidates),ranked_by_leg=ranked,
        limits=['Bounding-box exclusion can falsely reject cavities; no zero-space conclusion from no candidates.',
            'Cover may change; no other retained owner, bank support or wire is omitted.',
            'No routing, radius, actual factory lead length, mounting or removal PASS.'],
        started_utc=started.isoformat(),finished_utc=ended.isoformat(),
        worker_wall_seconds=(ended-started).total_seconds(),source_sha256=pins,script_sha256=sha(Path(__file__))))
    print(json.dumps(dict(candidates=len(candidates),ranked={k:len(v) for k,v in ranked.items()})),flush=True)


if __name__=='__main__': main()
