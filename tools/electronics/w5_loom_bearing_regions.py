"""Derive a common front attachment region from actual Deck bearing faces.

R2 received both rear roots. Front point guesses are not repeated: intersect
the complete intended foot-width strips with the actual109mm planar faces,
then prove one entire foot footprint in that shared region before native CAD.
"""
from pathlib import Path
from datetime import datetime, timezone
import json
import math
from servo_fuse_inputs_r1 import save,sha
from w5_loom_attachment_plan import ROOT,BASE,DECK,read

OUT=BASE/'w5-loom-bearing-regions-r1'
PRIOR=BASE/'w5-loom-attachment-plan-r2/plan.json'


def overlap(a,b):
    return [[max(x[0],y[0]),min(x[1],y[1])] for x in a for y in b
            if min(x[1],y[1])-max(x[0],y[0])>1e-5]


def main():
    import FreeCAD as A, Part
    start=datetime.now(timezone.utc);assert not (OUT/'plan.json').exists()
    prior=read(PRIOR);assert prior['received_exact8ray_method']
    assert all(g['identical_root_bearing_plane'] for g in prior['groups'] if g['leg'].startswith('R'))
    deck=Part.read(str(DECK));OUT.mkdir(parents=True,exist_ok=True)
    faces=[f for f in deck.Faces if isinstance(f.Surface,Part.Plane)
           and abs(f.BoundBox.ZMin-109)<1e-5 and abs(f.BoundBox.ZMax-109)<1e-5
           and f.normalAt(0,0).z>.9]
    assert faces
    strips=[];shared=[[-120,-20]]
    for side in (-1,1):
        for y in (side*76,side*85,side*94):
            line=Part.makeLine(A.Vector(-120,y,109),A.Vector(-20,y,109))
            spans=[]
            for face in faces:
                b=face.BoundBox
                if not b.YMin-1e-6<=y<=b.YMax+1e-6 or b.XMax<-120 or b.XMin>-20:continue
                common=line.common(face)
                spans.extend([[e.BoundBox.XMin,e.BoundBox.XMax] for e in common.Edges if e.Length>1e-5])
            spans.sort();merged=[]
            for lo,hi in spans:
                if merged and lo<=merged[-1][1]+1e-5:merged[-1][1]=max(merged[-1][1],hi)
                else:merged.append([lo,hi])
            strips.append(dict(y_mm=y,actual_bearing_spans_x_mm=merged))
            shared=overlap(shared,merged)
            print('FRONT_BEARING_STRIP',y,merged,flush=True)
            save(OUT/'progress.json',dict(strips=strips,shared=shared))
    # Root footprint26x18, half-width13, extra0.5mm to the material boundary.
    choices=[(math.ceil((lo+13.5)*4)/4,hi-13.5) for lo,hi in shared if hi-lo>=27]
    centres=[lo for lo,hi in choices if lo<=hi]
    root_x=min(centres) if centres else None
    footprint_receipts=[]
    if root_x is not None:
        for side in (-1,1):
            cy=side*85
            points=[A.Vector(x,y,109) for x,y in
                    ((root_x-13,cy-9),(root_x+13,cy-9),(root_x+13,cy+9),(root_x-13,cy+9))]
            foot=Part.Face(Part.makePolygon(points+[points[0]]))
            area=sum(foot.common(face).Area for face in faces
                     if foot.BoundBox.intersect(face.BoundBox))
            footprint_receipts.append(dict(leg='FL' if side>0 else 'FR',root_x_mm=root_x,
                root_y_mm=cy,footprint_area_mm2=foot.Area,actual_bearing_area_mm2=area,
                entire_flat_foot_supported=abs(area-foot.Area)<1e-5,
                planned_screw_axes_xy_mm=[[root_x-5,cy],[root_x+5,cy]],
                bearing_plane_mm=109))
            print('FRONT_FULL_FOOT',side,root_x,area,foot.Area,flush=True)
    finish=datetime.now(timezone.utc)
    save(OUT/'plan.json',dict(status='ACTUAL_SHARED_FRONT_BEARING_REGION_PLAN',
        source_front_points_rejected=True,prior_rear_roots_preserved=True,
        actual_planar_faces=len(faces),foot_width_mm=26,foot_depth_mm=18,
        strips=strips,shared_actual_x_regions_mm=shared,planned_root_x_mm=root_x,
        footprints=footprint_receipts,
        whole_front_bearing_supported=len(footprint_receipts)==2 and all(r['entire_flat_foot_supported'] for r in footprint_receipts),
        fixed_frame_native_pending=True,fastener_and_foreign_contact_checks_pending=True,
        selected=False,W1_complete=False,W5_complete=False,physical_pass=False,
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds(),
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in [Path(__file__),PRIOR,DECK]}))


if __name__=='__main__':main()
