"""Receive the exact manufacturer's STEP; never infer delivered/crimped fit."""
from pathlib import Path
from datetime import datetime, timezone
import json, sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import save, sha
OUT = ROOT/'hardware/reference/source-terminal-2026-10-04'

def main():
    import FreeCAD as A
    import Part
    start = datetime.now(timezone.utc)
    step = OUT/'te130171/c-130171-l-3d.stp'
    assert not (OUT/'received.json').exists()
    shape = Part.Shape(); shape.read(str(step))
    def bounds(s):
        return [getattr(s.BoundBox, k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]
    faces = []
    for i, f in enumerate(shape.Faces):
        surf = f.Surface
        row = dict(index=i, type=type(surf).__name__, bounds_mm=bounds(f), area_mm2=f.Area)
        if hasattr(surf, 'Radius'):
            row.update(radius_mm=surf.Radius, axis=list(surf.Axis), centre=list(surf.Center))
        if hasattr(surf, 'Position'): row['position'] = list(surf.Position)
        faces.append(row)
    target = OUT/'TE130171_LOCAL.brep'; shape.exportBrep(str(target))
    finish = datetime.now(timezone.utc)
    record = dict(status='MANUFACTURER_REFERENCE_UNCRIMPED_NOT_PHYSICAL_FIT',
        manufacturer_product='https://www.te.com/en/product-130171.html',
        observed_download_label='ENG_CVM_CVM_130171_L.3d_stp.zip', revision='L',
        download_method='Observed STEP link in manufacturer page, browser download; shell request returned403.',
        valid=shape.isValid(), solids=len(shape.Solids), bounds_mm=bounds(shape), faces=faces,
        nominal_drawing=dict(length_max_mm=27.686, width_mm=9.525, hole_diameter_mm=5.258,
            drawing_material_mm=.991, webpage_tongue_mm=.79,
            wire_insulation_range_mm=[3.81,6.35], wire_range_is_not_terminal_outer_diameter=True),
        assumptions=['Uncrimped CAD is not a delivered/crimped dimension.',
            'Model revisionL versus drawingB4 and webpage tongue thickness require explicit comparison.',
            'Use drawing for tolerances; STEP for nominal shape only.'],
        selected=False, physical_pass=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in [Path(__file__), step,
            OUT/'ENG_CVM_CVM_130171_L.3d_stp.zip',
            ROOT/'hardware/electronics/power-platform/switch-terminations-p0.json']},
        files={target.relative_to(ROOT).as_posix():sha(target)},
        started_utc=start.isoformat(), finished_utc=finish.isoformat(),
        worker_wall_seconds=(finish-start).total_seconds())
    save(OUT/'received.json', record)
    print(json.dumps(record), flush=True)

if __name__ == '__main__': main()
