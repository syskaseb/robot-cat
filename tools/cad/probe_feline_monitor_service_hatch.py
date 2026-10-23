"""N01 necessary hatch topology test; not production geometry or approval."""
import time
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT, sha
from plan_feline_layout import OUT
from feline_source_restraint_plan import box
from feline_solid_distance import bbox_lower_bound
from feline_fore_power_pair import SolidQueries
from plan_feline_pi_root_access import profile_gap
from feline_atomic_save import save_json


def probe(scene, metadata, pins):
    tick = time.monotonic()
    plate = scene['Print_P0_BATTERY_PLATE_R4']
    window = box([-71.75,-23.75,-2],[-40.25,23.75,1])
    fixed = plate.cut(window).removeSplitter()
    hatch = box([-78,-25.5,-4.5],[-34,25.5,-1.5])
    tray = scene['MonitorTray:rooted_pocket']
    for y in [-22.5,22.5]:
        hatch = hatch.fuse(box([-62,y-1,-1.5],[-60,y+1,0]))
    hatch = hatch.fuse(tray).removeSplitter()
    for x in [-75,-37]:
        hole = Part.makeCylinder(1.7,8,A.Vector(x,0,-5))
        fixed = fixed.cut(hole)
        hatch = hatch.cut(hole)
    candidates = {'hatch_closed':hatch}
    # Continuous downward necessary sweep represented conservatively by its
    # full rectangular section, not by samples. Header unplugged first.
    candidates['withdrawal_budget'] = box([-78,-25.5,-44.5],[-34,25.5,23.5])
    candidates['driver_front'] = Part.makeCylinder(4,35,A.Vector(-75,0,-39.5))
    candidates['driver_rear'] = Part.makeCylinder(4,35,A.Vector(-37,0,-39.5))
    excluded = {'Print_P0_BATTERY_PLATE_R4','MonitorTray:rooted_pocket',
                'Station:Monitor:case','MonitorTray:full_header_access'}
    query = SolidQueries(); checks = {}; errors = {}
    for label, shape in candidates.items():
        for name,target in scene.items():
            if name in excluded: continue
            if bbox_lower_bound(shape.BoundBox,target.BoundBox) >= .5+1e-6: continue
            try:
                if target.Solids:
                    gap=query.distance(shape,target)
                    r=dict(ok=gap>=.5-1e-6,gap_mm=gap,minimum_mm=.5)
                else:
                    radius=metadata.get(name,{}).get('nominal_profile_radius_mm') or metadata.get(name,{}).get('radius_mm')
                    assert radius is not None, 'missing profile radius'
                    r=profile_gap(shape,target,radius,.5)
                checks[label+'|'+name]=r
            except Exception as exc: errors[label+'|'+name]=str(exc)
    # Actual material, not bounding-box contact. A disconnected plate is a
    # rejected topology, not a cosmetic fault that may be ignored.
    geometry=dict(fixed_valid=fixed.isValid(),fixed_solids=len(fixed.Solids),
                  hatch_valid=hatch.isValid(),hatch_solids=len(hatch.Solids),
                  closed_overlap_mm3=fixed.common(hatch).Volume)
    result=dict(status='NECESSARY_TOPOLOGY_SCREEN_ONLY',geometry=geometry,
        checks=checks,errors=errors,failures=[k for k,v in checks.items() if not v['ok']],
        excluded=sorted(excluded),selected=False,N01_complete=False,physical_pass=False,
        open=['plate strength/load path','actual fastener stack','header unplug access',
              'changed36pose motion','F_PI lid orientation fit','new plate vs retained parts'],
        source_sha256={**pins,Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
        worker_seconds=round(time.monotonic()-tick,3))
    save_json(OUT/'n01-Monitor-service-hatch-proposal.json',result)
    print(geometry,result['failures'],errors,result['worker_seconds'],flush=True)
    return result,fixed,hatch
