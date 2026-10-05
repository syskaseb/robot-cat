"""Nominal articulation reserve for the12continuous factory looms.

Use current anchors/actual saved revolute axes and the received ±15deg
prototype screen. Do not convert a free-endpoint bound into cable collision
clearance, invent manufacturer cyclic bend ratings, or require physical PASS
for phase1. All trim marks remain provisional until unpowered phase2 fitting.
"""
from pathlib import Path
from datetime import datetime,timezone
import math,json
from servo_fuse_inputs_r1 import save,sha
from w5_motion_length_screen_r2 import rotate
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'hardware/electronics/full-cat'
OUT=BASE/'w5-loop-preparation-r1'

def main():
    start=datetime.now(timezone.utc);assert not (OUT/'preparation.json').exists()
    pins={}
    def read(rel):
        p=ROOT/rel;pins[rel]=sha(p);return json.loads(p.read_text(encoding='utf-8'))
    screen=read('hardware/electronics/full-cat/w5-motion-length-screen-r2/screen.json')
    movement=read('hardware/electronics/full-cat/w5-source-grip-motion-r1/checks.json')
    assert not movement['hits'] and not movement['errors']
    assert movement['screen_window_is_not_servo_or_operating_limit']
    axes={r['name']:r for r in read('hardware/simulation/p0/e6-leg-compatibility.json')['axes']}
    rows=[]
    for r in screen['looms']:
        points=[]
        # Kinematics compose outer first in placements; points are evaluated
        # through inner joint first, then its moving ancestor.
        for hip,knee in movement['samples_hip_knee_deg']:
            p=r['moving_grip_mm']
            for name in reversed(r['moving_ancestor_joints']):
                j=axes[name];angle=hip if j['stage']=='Hip' else knee
                p=rotate(p,j['pivot_mm'],j['axis'],math.radians(angle))
            points.append((hip,knee,p,math.dist(p,r['fixed_grip_mm'])))
        maximum=max(x[3] for x in points)
        #20mm extra over the sampled chord is a declared preparation margin,
        # NOT a proved curvature allowance or manufacturer's minimum radius.
        extra=math.ceil(max(0,maximum+20-r['current_rest_free_route_mm'])/10)*10
        planned=r['retained_common_blank_mm']+extra
        assert planned<=900,(r['loom'],planned)
        rows.append(dict(loom=r['loom'],factory_length_nominal_mm=900,
            moving_ancestor_joints=r['moving_ancestor_joints'],rest_free_route_mm=r['current_rest_free_route_mm'],
            maximum_sampled_endpoint_chord_mm=maximum,declared_preparation_margin_mm=20,
            added_moving_reserve_mm=extra,nominal_common_trial_blank_mm=planned,
            remaining_nominal_factory_margin_mm=900-planned,
            moving_anchor_samples=[dict(hip_deg=h,knee_deg=k,point_mm=p) for h,k,p,_ in points],
            bench_preparation='Keep900mm untrimmed. Mark the received body route and added reserve; trim all3cores only after unpowered fitting.',
            dressing='Retain the bundle only at the owned moving servo clip and fixed body frame. Keep the joint-spanning span free; never tie it across a hinge or to the horn.',
            fitting='With covers off and battery disconnected, move each joint gradually. Feed reserve into a broad outward bow; do not coil surplus into a narrow cage or let it cross a horn/screw.',
            acceptance_phase2='At the intended prototype travel there must be no tension, pinch, sharp kink or insulation rubbing. Shorten travel or redress/reprint the replaceable grip before powering.',
            numerical_screen_is_not_cable_clearance=True,delivered_usable_length_mm=None,
            cyclic_radius_or_torsion_rating_verified=False,continuous_cable_sweep_verified=False))
    assert len(rows)==12 and len({r['loom'] for r in rows})==12
    finish=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True)
    save(OUT/'preparation.json',dict(status='TWELVE_LOOM_NOMINAL_RESERVES_AND_UNPOWERED_FIT_RECIPE',
        looms=rows,prototype_screen_only_deg=15,full_operating_range_approved=False,
        no_P0_motion_limit_changed=True,no_new_connector_or_splice=True,
        nominal_factory_blanks_with_reserve_sum_mm=sum(r['nominal_common_trial_blank_mm'] for r in rows),
        maximum_trial_blank_mm=max(r['nominal_common_trial_blank_mm'] for r in rows),
        physical_phase2_checks_are_not_phase1_PASS=True,selected=False,W1_complete=False,W5_complete=False,physical_pass=False,
        source_sha256={**pins,Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__)),
            'tools/electronics/w5_motion_length_screen_r2.py':sha(ROOT/'tools/electronics/w5_motion_length_screen_r2.py')},
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds()))
    print(json.dumps(dict(looms=12,extra_reserve={r['loom']:r['added_moving_reserve_mm'] for r in rows},max_blank=max(r['nominal_common_trial_blank_mm'] for r in rows))))

if __name__=='__main__':main()
