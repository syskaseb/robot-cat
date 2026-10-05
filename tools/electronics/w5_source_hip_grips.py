"""Four hip grips planned from case/carrier ownership, not the body cover.

Keep all received source saddles. A positive-X strap captures the existing
case/WConnector fixed group; the separate body cover stays outside that lane.
The offset source bridge clears the maximum cover height of BOTH rear hips.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,math
import w5_source_grip_common as M
from servo_fuse_inputs_r1 import save,sha
from check_main_p0_placement import SavedShapes
from w5_leg_corridors_r1 import components
ROOT=M.ROOT;BASE=M.BASE;OUT=BASE/'w5-source-hip-grips-r1'
FULL=BASE/'w5-source-mount-full-profile-r1/plan.json'
OWNERSHIP=BASE/'w5-hip-source-mount-plan-r1/plan.json'
LONG=ROOT/'hardware/reference/hellermann-11102189-2026-10-05/dimensions.json'
OLD_PLAN=M.PLAN;OLD_TIE=M.TIE;OLD_PROPOSED=M.proposed


def proposed(A,Part):
    parts,old=OLD_PROPOSED(A,Part)
    def box(b):return Part.makeBox(*(b[i+3]-b[i] for i in range(3)),A.Vector(*b[:3]))
    zi=14.85+.2;zo=zi+1.5;yf=-29.9;yb=10.12
    boxes=dict(TopJaw=[-7.5,yf,zi,4,yb,zo],BottomJaw=[-7.5,yf,-zo,4,yb,-zi],
        BackJaw=[-7.5,8.62,-zo,4,yb,zo],
        BridgeRiser=[-8,-26.8,zi,-5,-25,22.5],
        CoverBridge=[-8,-50.5,19.5,-5,-25,22.5],
        SourcePost=[-8,-53.5,-7,-5,-47.5,22.5],
        SaddleBeam=[-15.55,-53.5,-7,-5,-47.5,1])
    roots=[box(b) for b in boxes.values()]
    cx,cy,cz=old['source_saddle_center_in_PCB_frame_mm']
    roots.append(Part.makeCylinder(5.5,6,A.Vector(cx,cy-3,cz),A.Vector(0,1,0)))
    def half_channel(ri,ro,upper):
        ann=Part.makeCylinder(ro,3,A.Vector(cx,cy-1.5,cz),A.Vector(0,1,0)).cut(
            Part.makeCylinder(ri,3.2,A.Vector(cx,cy-1.6,cz),A.Vector(0,1,0)))
        return ann.common(box([cx-ro-.1,cy-1.6,cz if upper else cz-ro-.1,
            cx+ro+.1,cy+1.6,cz+ro+.1 if upper else cz]))
    rear_window=[.15,8.52,-zo-.1,3.05,9.92,zo+.1]
    cutters=[Part.makeCylinder(3.05,8,A.Vector(cx,cy-4,cz),A.Vector(0,1,0)),
        box([cx-6,cy-4,cz,cx+6,cy+4,cz+7]),
        half_channel(5.25,6.95,False),half_channel(2.5,4.2,True),
        *[box(b) for b in old['tie_corner_slots_mm']],box(rear_window)]
    clip=roots[0].multiFuse(roots[1:]).cut(Part.makeCompound(cutters))
    assert clip.isValid() and len(clip.Solids)==1
    bands=[[.35,yf,zo,2.85,yb,zo+1.2],[.35,yf,-zo-1.2,2.85,yb,-zo],
        [.35,yf-1.2,-zo,2.85,yf,zo],[.35,8.62,-zo,2.85,9.82,zo]]
    head=[-.65,-12.4,zo+.6,3.85,-7.6,zo+4.5]
    parts.update(Clip=clip,BodyBand=Part.makeCompound([box(b) for b in bands]),BodyHead=box(head))
    spec=dict(old,root_boxes_mm=boxes,body_band_boxes_mm=bands,body_head_box_mm=head,
        rear_band_window_mm=rear_window,root_case_gap_mm=.2,root_wall_mm=1.5,
        body_aperture_diagonal_mm=math.hypot(yb-yf,2*zo),
        nominal_rectangular_body_band_perimeter_mm=2*(yb-yf+2*zo),
        body_tie_SKU='111-02189',cable_tie_SKU='111-02370',
        bridge_floor_mm=19.5,root_capture='Existing servo and its own fixed WConnector, NEVER the separate body cover.',
        assembly='Before fitting the hip into the body, slide this root around its case/WConnector group and fit T18L. Keep the body cover independent. Plug the unchanged source lead and strap its insulation in the unchanged saddle with T18I. Shared assembly and full joint motion remain pending.',
        strength_pullout_and_actual_tightening_unknown=True)
    return parts,spec


def main():
    start=datetime.now(timezone.utc);assert not (OUT/'checks.json').exists()
    plan=json.loads(OLD_PLAN.read_text(encoding='utf-8'))
    full=json.loads(FULL.read_text(encoding='utf-8'));own=json.loads(OWNERSHIP.read_text(encoding='utf-8'))
    reader=SavedShapes();objects=reader.doc(M.ENTRY);groups=components(objects)
    looms=[r for r in plan['looms'] if r['loom'].endswith('1')];assert len(looms)==4
    captures=[]
    for row in looms:
        f=next(p for p in full['rows'] if p['loom']==row['loom'])
        carrier=next(p for p in f['carrier_and_PCB'] if p['label'].startswith('WConnector'))
        assert groups('Rigid_'+carrier['name'])==groups('Rigid_'+row['case'])
        c=next(p for p in own['rows'] if p['loom']==row['loom'])
        for cover in c['cover_sections']:
            assert not cover['same_rigid_component']
            assert cover['full_bounds_PCB_mm'][3]<.35
            assert cover['full_bounds_PCB_mm'][5]<19.5
        captures.append(dict(loom=row['loom'],carrier=carrier['name'],same_fixed_component=True,
            body_cover_not_captured=True))
    OUT.mkdir(parents=True,exist_ok=True);intent=OUT/'intent.json'
    save(intent,dict(looms=looms,source_sha256={**plan['source_sha256'],
        OLD_PLAN.relative_to(ROOT).as_posix():sha(OLD_PLAN),FULL.relative_to(ROOT).as_posix():sha(FULL),
        OWNERSHIP.relative_to(ROOT).as_posix():sha(OWNERSHIP)},captures=captures,
        proposed_print_quantity=4,selected=False,physical_pass=False))
    M.OUT=OUT;M.PLAN=intent;M.TIE=LONG;M.proposed=proposed;M.main()
    bp=OUT/'blueprint.json';p=OUT/'checks.json'
    blueprint=json.loads(bp.read_text(encoding='utf-8'))
    blueprint.update(new_print_identity='SourceClipHip',print_quantity=4,T18L_installed=4,T18I_installed=4,
        fixed_component_capture=captures,bridge_basis=OWNERSHIP.relative_to(ROOT).as_posix())
    save(bp,blueprint)
    proof=json.loads(p.read_text(encoding='utf-8'));finish=datetime.now(timezone.utc)
    proof.update(status='FOUR_HIP_SOURCE_GRIPS_REJECTED' if proof['hits'] or proof['errors'] else 'FOUR_HIP_SOURCE_GRIPS_P0_CLEAR_HARNESS_PENDING',
        fixed_component_capture=captures,print_quantity=4,T18L_installed=4,T18I_installed=4,
        selected=False,W1_complete=False,W5_complete=False,physical_pass=False,
        wrapper_started_utc=start.isoformat(),wrapper_finished_utc=finish.isoformat(),
        wrapper_wall_seconds=(finish-start).total_seconds())
    for path in (Path(__file__),FULL,OWNERSHIP,OLD_PLAN,OLD_TIE,LONG):
        proof['source_sha256'][path.relative_to(ROOT).as_posix()]=sha(path)
    proof['files'][bp.relative_to(ROOT).as_posix()]=sha(bp);save(p,proof)
    print('HIP_GRIPS_RECEIVED',proof['pairs'],len(proof['hits']),len(proof['errors']),flush=True)


if __name__=='__main__':main()
