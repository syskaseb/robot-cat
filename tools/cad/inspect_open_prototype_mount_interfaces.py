"""Read actual saved hole surfaces/frames once; never turn reservations into parts."""
from pathlib import Path
from datetime import datetime, timezone
import json
import time
import sys
from correct_open_prototype_plan_reference import sha, bounds

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype'
NATIVE = BASE / 'OpenPrototypePlan.FCStd'
HASH = 'ce59a37562e841bb3daf90b4249c52d674b97307871043772d5dba66dea39b5f'


def main():
    if sys.argv[1:] == ['--compact-existing']:
        # Pure mechanical compaction of our generated inventory; no CAD read,
        # recompute or repeated tests. Drop unrelated legacy leg snapshots.
        output = BASE / 'mounting-checkpoint/mount-interface-inventory.json'
        result = json.loads(output.read_text(encoding='utf-8'))
        wanted = {'Pi4_CP2','BUS_CP2','Monitor_CP2','PWM9685_CP2','PWM1608_CP2','AUX4092_CP2',
                  'P0_FrameFront20','P0_FrameRear20','P0_SideLeft22','P0_SideRight22','BatteryTray'}
        result['unrelated_legacy_rows_removed'] = sum(r['name'] not in wanted for r in result['rows'])
        result['rows'] = [r for r in result['rows'] if r['name'] in wanted]
        result['script_sha256'] = sha(Path(__file__))
        output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print('Retained',len(result['rows']),'mount-interface rows; no CAD rerun',flush=True)
        return
    assert not sys.argv[1:]
    import FreeCAD as A
    import Part
    tick = time.monotonic()
    output = BASE / 'mounting-checkpoint/mount-interface-inventory.json'
    assert not output.exists(), 'Reuse saved inventory, no unchanged repetition'
    assert sha(NATIVE) == HASH
    d = A.openDocument(str(NATIVE))
    rows = []
    try:
        names = ['Pi4_CP2','BUS_CP2','Monitor_CP2','PWM9685_CP2','PWM1608_CP2','AUX4092_CP2']
        names += [o.Name for o in d.Objects if o.Name.startswith('P0_') or 'Tray' in o.Name]
        for name in names:
            o = d.getObject(name)
            if o is None or 'Shape' not in o.PropertiesList or o.Shape.isNull():
                continue
            axes = []
            for i,face in enumerate(o.Shape.Faces):
                surface = face.Surface
                if isinstance(surface,Part.Cylinder) and surface.Radius < 6:
                    axes.append(dict(face=i+1,radius_mm=surface.Radius,
                        center_world_mm=list(surface.Center),axis_world=list(surface.Axis),
                        face_bounds_mm=bounds(face)))
            rows.append(dict(name=name,label=o.Label,shape_valid=o.Shape.isValid(),
                bounds_mm=bounds(o.Shape),placement_origin_mm=list(o.Placement.Base),
                cylindrical_faces=axes,read_only_saved_geometry=True))
    finally:
        A.closeDocument(d.Name)
    assert sha(NATIVE) == HASH
    result = dict(status='MOUNT_INTERFACE_INVENTORY_NOT_QUALIFIED',
        source=str(NATIVE.relative_to(ROOT)),source_sha256=HASH,
        script_sha256=sha(Path(__file__)),finished_utc=datetime.now(timezone.utc).isoformat(),
        worker_wall_seconds=round(time.monotonic()-tick,3),rows=rows,
        reference_rule='Invalid BUS compound is not an exact contact target; hole cylinders are datums only',
        no_recompute_or_save=True,physical_pass=False,stage_completed=False)
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':result['status'],'rows':[
        {'name':r['name'],'valid':r['shape_valid'],'cylinder_count':len(r['cylindrical_faces'])} for r in rows],
        'worker_wall_seconds':result['worker_wall_seconds']}),flush=True)


if __name__ == '__main__':
    main()
