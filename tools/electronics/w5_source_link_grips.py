"""One complete-case root for the eight link-stage source leads.

Preserve the rejected source and its exact contact record. Reuse its joint
neighbor-check engine, not its incomplete casing root. Four hip mounts have
different cover constraints and are explicitly outside this family.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, math
import w5_source_grip_common as M
from servo_fuse_inputs_r1 import save, sha
ROOT=M.ROOT;BASE=M.BASE
OUT=BASE/'w5-source-link-grips-r1'
FULL=BASE/'w5-source-mount-full-profile-r1/plan.json'
LONG=ROOT/'hardware/reference/hellermann-11102189-2026-10-05/dimensions.json'
OLD_PLAN=M.PLAN;OLD_TIE=M.TIE;old_proposed=M.proposed


def proposed(A,Part):
    parts, original=old_proposed(A,Part)
    def box(b):
        return Part.makeBox(*(b[i+3]-b[i] for i in range(3)),A.Vector(*b[:3]))
    xmin,xmax=-4.7,-1.7
    ymin,ymax=-29.9,9.32602791928
    zi=12.388596968413133+.2;zo=zi+1.5
    boxes=dict(TopJaw=[xmin,ymin,zi,xmax,ymax,zo],
        BottomJaw=[xmin,ymin,-zo,xmax,ymax,-zi],
        BackJaw=[xmin,7.82602791928,-zo,xmax,ymax,zo],
        FrontFoot=[-8,ymin,-zo,xmax,-28.4,-zi],
        RootStem=[-8,-31.9,-zo,-5,-28.4,-1],
        SourceArm=[-8,-50.5,-7,-5,-31,-1],
        SaddleBeam=[-15.55,-53.5,-7,-5,-47.5,1])
    roots=[box(b) for b in boxes.values()]
    cx,cy,cz=original['source_saddle_center_in_PCB_frame_mm']
    roots.append(Part.makeCylinder(5.5,6,A.Vector(cx,cy-3,cz),A.Vector(0,1,0)))
    tools=[Part.makeCylinder(3.05,8,A.Vector(cx,cy-4,cz),A.Vector(0,1,0)),
           box([cx-6,cy-4,cz,cx+6,cy+4,cz+7])]
    # Preserve the already checked cable strap slots and open saddle; only
    # their supporting beam/root changes, never the source wire datum.
    def half_channel(ri,ro,upper):
        ann=Part.makeCylinder(ro,3,A.Vector(cx,cy-1.5,cz),A.Vector(0,1,0)).cut(
            Part.makeCylinder(ri,3.2,A.Vector(cx,cy-1.6,cz),A.Vector(0,1,0)))
        return ann.common(box([cx-ro-.1,cy-1.6,cz if upper else cz-ro-.1,
            cx+ro+.1,cy+1.6,cz+ro+.1 if upper else cz]))
    tools += [half_channel(5.25,6.95,False),half_channel(2.5,4.2,True)]
    tools += [box(b) for b in original['tie_corner_slots_mm']]
    clip=roots[0].multiFuse(roots[1:]).cut(Part.makeCompound(tools))
    assert clip.isValid() and len(clip.Solids)==1
    body_boxes=[[-4.65,ymin,zo,-2.15,ymax,zo+1.2],
        [-4.65,ymin,-zo-1.2,-2.15,ymax,-zo],
        [-4.65,ymin-1.2,-zo,-2.15,ymin,zo],
        [-4.65,ymax,-zo,-2.15,ymax+1.2,zo]]
    body_head=[-6,-12.4,zo+.6,-1.5,-7.6,zo+4.5]
    parts.update(Clip=clip,BodyBand=Part.makeCompound([box(b) for b in body_boxes]),BodyHead=box(body_head))
    spec=dict(original,root_boxes_mm=boxes,body_band_boxes_mm=body_boxes,body_head_box_mm=body_head,
        complete_servo_case_profile_basis=FULL.relative_to(ROOT).as_posix(),
        root_case_gap_mm=.2,root_wall_mm=1.5,
        body_aperture_diagonal_mm=math.hypot(ymax-ymin,2*zo),
        nominal_rectangular_body_band_perimeter_mm=2*(ymax-ymin+2*zo),
        body_tie_SKU='111-02189',cable_tie_SKU='111-02370',
        root_connection='FrontFoot joins the lower jaw behind the body band; offset stem and source arm lie outside its strap lane. No added P0 screw stack.',
        assembly='Fit the removable complete-case root before assembling the link stage. Fit one T18L around case/root, plug the unchanged lead, seat its insulation in the open saddle and fit one T18I. Verify tightening, pull relief and actual case/PCB clearance in phase2.',
        source_factory_looms_and_body_wiring_pending=True)
    return parts,spec


def main():
    start=datetime.now(timezone.utc)
    assert not (OUT/'checks.json').exists()
    original=json.loads(OLD_PLAN.read_text(encoding='utf-8'))
    full=json.loads(FULL.read_text(encoding='utf-8'))
    assert full['source_clip_R1_rejected'] and len(full['rows'])==12
    looms=[r for r in original['looms'] if r['loom'][-1] in ('2','3')]
    assert len(looms)==8
    OUT.mkdir(parents=True,exist_ok=True)
    intent=OUT/'intent.json'
    save(intent,dict(looms=looms,source_sha256={**original['source_sha256'],
        OLD_PLAN.relative_to(ROOT).as_posix():sha(OLD_PLAN),FULL.relative_to(ROOT).as_posix():sha(FULL)},
        proposed_print_quantity=8,body_ties='8xT18L111-02189',cable_ties='8xT18I111-02370',
        four_hip_grips_pending=True,selected=False,physical_pass=False))
    M.OUT=OUT;M.PLAN=intent;M.TIE=LONG;M.proposed=proposed
    M.main()
    blueprint_path=OUT/'blueprint.json';proof_path=OUT/'checks.json'
    blueprint=json.loads(blueprint_path.read_text(encoding='utf-8'))
    blueprint.update(new_print_identity='SourceClipLink',print_quantity=8,T18I_installed=8,T18L_installed=8,
        four_hip_grips_pending=True)
    save(blueprint_path,blueprint)
    proof=json.loads(proof_path.read_text(encoding='utf-8'))
    proof.update(status='EIGHT_LINK_SOURCE_GRIPS_REJECTED' if proof['hits'] or proof['errors'] else 'EIGHT_LINK_SOURCE_GRIPS_P0_CLEAR_COMPLETE_HARNESS_PENDING',
        scope='Eight link-stage clips/straps vs received P0 and each other. Whole source/body paths, joint motion and mounting sequence remain open.',
        print_quantity=8,T18L_installed=8,T18I_installed=8,four_hip_grips_pending=True,
        selected=False,W1_complete=False,W5_complete=False,physical_pass=False)
    for p in (Path(__file__),FULL,OLD_PLAN,OLD_TIE,LONG):
        proof['source_sha256'][p.relative_to(ROOT).as_posix()]=sha(p)
    proof['files'][blueprint_path.relative_to(ROOT).as_posix()]=sha(blueprint_path)
    finish=datetime.now(timezone.utc)
    proof.update(wrapper_started_utc=start.isoformat(),wrapper_finished_utc=finish.isoformat(),
        wrapper_wall_seconds=(finish-start).total_seconds())
    save(proof_path,proof)
    print('LINK_GRIPS_RECEIVED',len(proof['hits']),len(proof['errors']),flush=True)


if __name__=='__main__':
    main()
