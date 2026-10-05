"""Measure all four fixed loom-bracket landings before native construction.

An exact vertical line/material intersection establishes each proposed screw
stack. Bounding boxes allocate print space, not material or collision proof.
Existing P0 parts, received paths and bank are immutable inputs.
"""
from pathlib import Path
from datetime import datetime, timezone
import json
from servo_fuse_inputs_r1 import save, sha
from w5_whole_connection_plan import ROOT, BASE, OUT as CONNECTION, read

OUT = BASE/'w5-loom-attachment-plan-r1'
DECK = ROOT/'hardware/cad/studies/w5-central-retention-native-r1/CentralRetentionDeck_CANDIDATE_WORLD.brep'
CORRIDORS = BASE/'w5-leg-corridors-r3/intent.json'
SOURCE_MAP = BASE/'w5-leg-source-map-r1/interface.json'


def main():
    import FreeCAD as A, Part
    start=datetime.now(timezone.utc)
    assert not (OUT/'plan.json').exists()
    connection=read(CONNECTION/'plan.json')
    assert connection['discontinuous_core_joins']==0
    deck=Part.read(str(DECK)); assert deck.isValid() and len(deck.Solids)==1
    corridors=read(CORRIDORS)['routes']; sources={r['loom']:r for r in read(SOURCE_MAP)['looms']}
    groups=[]; pins=[Path(__file__),CONNECTION/'plan.json',DECK,CORRIDORS,SOURCE_MAP]
    OUT.mkdir(parents=True,exist_ok=True)
    for leg in ('FL','FR','RL','RR'):
        side=1 if leg.endswith('L') else -1
        root_x=-92 if leg.startswith('F') else 130
        root_y=side*85
        rays=[]
        for dx in (-7,7):
            x,y=root_x+dx,root_y
            line=Part.makeLine(A.Vector(x,y,0),A.Vector(x,y,200))
            common=line.common(deck)
            intervals=sorted([[min(e.valueAt(e.FirstParameter).z,e.valueAt(e.LastParameter).z),
                               max(e.valueAt(e.FirstParameter).z,e.valueAt(e.LastParameter).z)]
                              for e in common.Edges])
            rays.append(dict(axis_xy_mm=[x,y],actual_Deck_material_intervals_z_mm=intervals,
                upper_material_plane_mm=max((p[1] for p in intervals),default=None)))
            print('LOOM_LANDING',leg,dx,intervals,flush=True)
            save(OUT/'progress.json',dict(leg=leg,rays=rays,
                updated_utc=datetime.now(timezone.utc).isoformat()))
        all_present=all(r['actual_Deck_material_intervals_z_mm'] for r in rays)
        tops=[r['upper_material_plane_mm'] for r in rays if r['upper_material_plane_mm'] is not None]
        same_plane=all_present and max(tops)-min(tops)<1e-5
        # Four independent fixed printed frames: a whole-robot one-piece rail
        # would exceed256mm. Do not move P0 or force it into the print volume.
        split=[r for r in corridors if r['loom'].startswith(leg)]
        points=[r['fixed_breakout_provisional_mm'] for r in split]
        footprint=[min([root_x-13]+[p[0]-6 for p in points]),
                   min([root_y-9]+[p[1]-7 for p in points]),
                   min([75]+[p[2]-5 for p in points]),
                   max([root_x+13]+[p[0]+6 for p in points]),
                   max([root_y+9]+[p[1]+7 for p in points]),
                   max([max(tops)+8 if tops else 117]+[p[2]+5 for p in points])]
        size=[footprint[i+3]-footprint[i] for i in range(3)]
        assert all(v+6<=256 for v in size)
        groups.append(dict(leg=leg,owner='NEW_FIXED_SPLIT_FRAME_'+leg,
            supported_looms=[r['loom'] for r in split],fixed_split_axes_mm=points,
            proposed_root_centre_xy_mm=[root_x,root_y],screw_stack_material=rays,
            identical_root_bearing_plane=same_plane,
            candidate_footprint_mm=footprint,candidate_dimensions_mm=size,
            allocation_fit_with6mm_allowance=True,not_slicer_or_collision_proof=True,
            fixed_split_grips=3,nominal_bundle_diameter_mm=5.5,
            proposed_body_attachment=dict(fastener_count=2,diameter_mm=3,
                selected_length_mm=None,new_Deck_holes_and_nut_access_pending=True),
            existing_moving_carriers=[dict(loom=r['loom'],
                carriers=r['carriers'],pcb=sources[r['loom']]['pcb'],
                housing=sources[r['loom']]['housing'],
                port_datums_mm=sources[r['loom']]['connector_reservation_world_mm'],
                cable_exit_axis=sources[r['loom']]['cable_exit_world_axis'],
                moving_grip_mount_pending=True) for r in split]))
    finish=datetime.now(timezone.utc)
    save(OUT/'plan.json',dict(status='ONE_TWELVE_LOOM_FIXED_AND_MOVING_ATTACHMENT_PLAN',
        groups=groups,fixed_split_frames=4,fixed_split_grips=12,moving_source_grips=12,
        candidate_new_M3_attachment_count=8,selected_new_fasteners=0,
        exact_root_axes_in_material=sum(bool(r['actual_Deck_material_intervals_z_mm']) for g in groups for r in g['screw_stack_material']),
        all_four_root_planes_match=all(g['identical_root_bearing_plane'] for g in groups),
        frozen_37_body_paths_unchanged=True,P0_unchanged=True,
        construction_order=[
            'Receive measured landing stacks; reject unsupported axes before constructing a native frame.',
            'Model one fixed frame per leg with three insulation-only grips and two actual Deck attachments; include bolt/nut/tool envelopes in the common layout.',
            'Model twelve moving source grips on the existing rigid servo carriers; never use PCB solder joints or the cable plug as structural anchors.',
            'Keep the three continuous cores at each matched split. No splice, connector or separate wire purchase at that virtual interface.',
            'Check all4frames/24grips together against49fixed paths and actual fixed/moving owners, then qualify defined joint ranges and service removal.',
            'Only after material/mounting/access checks integrate native holes/linked frames and choose exact fastener lengths/stock.'],
        nominal_clearance_and_section_assumptions=dict(bundle_mm=5.5,groove_allowance_mm=.2,
            rail_section_mm=[8,6],footprint_margin_mm=6,
            PETG_strength_and_cable_pullout_not_certified=True),
        native_geometry_complete=False,physical_attachments_complete=False,
        moving_range_complete=False,stock_selected=False,
        selected=False,W1_complete=False,W5_complete=False,physical_pass=False,
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),
        worker_wall_seconds=(finish-start).total_seconds(),
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in pins}))
    print('LOOM_ATTACHMENT_PLAN',sum(g['identical_root_bearing_plane'] for g in groups),'OF4_ROOTS',flush=True)


if __name__=='__main__':main()
