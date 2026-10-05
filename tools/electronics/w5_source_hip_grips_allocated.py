"""Reconstruct one four-copy hip grip from the received common free lane.

The root captures the hip's existing WConnector, already fixed to its case.
Neither PCB nor separately body-fixed cover bears the cable load. The new
upper cross-bridge avoids the frame rather than cutting or moving P0.
"""
import json
from pathlib import Path
import w5_source_hip_grips as H
from servo_fuse_inputs_r1 import save,sha
ROOT=H.ROOT;BASE=H.BASE;OUT=BASE/'w5-source-hip-grips-r2'
LANE=BASE/'w5-hip-band-lane-plan-r1/plan.json'
SECTION=BASE/'w5-hip-root-section-allocation-r1/plan.json'
ORIGINAL=H.proposed


def proposed(A,Part):
    parts,spec=ORIGINAL(A,Part)
    lane=json.loads(LANE.read_text(encoding='utf-8'));axis=lane['selected_axis_x_PCB_mm'];assert axis is not None
    xmin,xmax=axis-2.7,axis+2.7
    assert xmin>max(h['conservative_contact_projection_mm'][1] for h in lane['actual_witnesses'])+.08
    zi=15.05;zo=16.55;yf=-29.9;yb=10.12
    def box(b):return Part.makeBox(*(b[i+3]-b[i] for i in range(3)),A.Vector(*b[:3]))
    boxes=dict(TopJaw=[xmin,yf,zi,xmax,yb,zo],BottomJaw=[xmin,yf,-zo,xmax,yb,-zi],
        BackJaw=[xmin,8.62,-zo,xmax,yb,zo],
        BridgeRiser=[axis-1.5,-26.8,zi,axis+1.5,-25,22.5],
        CoverBridge=[-9,-26.8,19.5,xmax,-25,22.5],
        LongCoverBridge=[-9,-50.5,19.5,-6,-25,22.5],
        SourcePost=[-9,-53.5,-7,-6,-47.5,22.5],
        SaddleBeam=[-15.55,-53.5,-7,-5,-47.5,1])
    cx,cy,cz=spec['source_saddle_center_in_PCB_frame_mm']
    roots=[box(b) for b in boxes.values()]+[Part.makeCylinder(5.5,6,A.Vector(cx,cy-3,cz),A.Vector(0,1,0))]
    def channel(ri,ro,upper):
        ann=Part.makeCylinder(ro,3,A.Vector(cx,cy-1.5,cz),A.Vector(0,1,0)).cut(
            Part.makeCylinder(ri,3.2,A.Vector(cx,cy-1.6,cz),A.Vector(0,1,0)))
        return ann.common(box([cx-ro-.1,cy-1.6,cz if upper else cz-ro-.1,cx+ro+.1,cy+1.6,cz+ro+.1 if upper else cz]))
    window=[axis-1.45,8.52,-zo-.1,axis+1.45,9.92,zo+.1]
    tools=[Part.makeCylinder(3.05,8,A.Vector(cx,cy-4,cz),A.Vector(0,1,0)),
        box([cx-3.05,cy-4,cz,cx+3.05,cy+4,cz+7]),channel(5.25,6.95,False),channel(2.5,4.2,True),
        *[box(b) for b in spec['tie_corner_slots_mm']],box(window)]
    union=roots[0].multiFuse(roots[1:])
    print('HIP_ROOT_UNION',union.isValid(),len(union.Solids),union.check(True),flush=True)
    clip=union.cut(Part.makeCompound(tools))
    assert clip.isValid() and len(clip.Solids)==1, ('HIP_ROOT_CUT',clip.isValid(),len(clip.Solids),clip.check(True))
    bands=[[axis-1.25,yf,zo,axis+1.25,yb,zo+1.2],[axis-1.25,yf,-zo-1.2,axis+1.25,yb,-zo],
        [axis-1.25,yf-1.2,-zo,axis+1.25,yf,zo],[axis-1.25,8.62,-zo,axis+1.25,9.82,zo]]
    head=[axis-2.25,-12.4,zo+.6,axis+2.25,-7.6,zo+4.5]
    parts.update(Clip=clip,BodyBand=Part.makeCompound([box(b) for b in bands]),BodyHead=box(head))
    spec.update(root_boxes_mm=boxes,body_band_boxes_mm=bands,body_head_box_mm=head,rear_band_window_mm=window,
        common_allocated_band_axis_x_PCB_mm=axis,rear_side_web_mm=1.25,
        root_capture='Own WConnector rigidly fixed to hip servo; PCB and separate body cover untouched.',
        rear_lane_allocation=LANE.relative_to(ROOT).as_posix(),source_post_head_gap_mm=.25,
        open_cable_entry_width_mm=6.1,
        geometry_repair='Previous12mm entry severed the offset SourcePost (two solids). Use the6.1mm cable mouth, matching the existing6.1mm bore and preserving the side post. No route/station change.',
        assembly='Fit the root to the hip WConnector before its final body installation, then fit T18L through the rear root window. Keep FrontRearCover separate. Seat the unchanged factory source lead at the unchanged saddle and fit T18I. Full joint motion and shared mounting still pending.')
    return parts,spec


def main():
    H.OUT=OUT;H.proposed=proposed;H.main()
    path=OUT/'checks.json';proof=json.loads(path.read_text(encoding='utf-8'))
    for p in (Path(__file__),LANE,SECTION):proof['source_sha256'][p.relative_to(ROOT).as_posix()]=sha(p)
    save(path,proof)


if __name__=='__main__':main()
