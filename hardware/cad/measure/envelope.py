"""How much of the body can the skin occupy before a leg hits it?

Sweeps every pose the robot actually commands - walk at full speed, full
turn, stand, stretch, lie down - and reports how close a knee or a paw ever
gets to the centreline. That number is what licenses the cosmetic shell to
be a full-width solid form instead of something scalloped around the legs.

Run from the repo root:  python3 hardware/cad/measure/envelope.py
Re-run after any change to gait.py's defaults or to LegGeometry.
"""
import itertools, math, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'src' / 'robot_cat_gait'))
from robot_cat_gait.gait import GaitGenerator, GaitParams
from robot_cat_gait.leg_ik import LegGeometry

g = LegGeometry()
gen = GaitGenerator(geom=g, params=GaitParams())
p = gen.params
print(f'stance_height={p.stance_height} stance_width={p.stance_width} '
      f'swing_height={p.swing_height} max_stride={p.max_stride} '
      f'cycle_time={p.cycle_time} duty={p.duty_factor}')

def joints_of(pose):
    # pose is a flat list of 12: (hip, thigh, knee) x 4 legs
    return [tuple(pose[i*3:(i+1)*3]) for i in range(4)]

LEGS = [('FL', +1, +1), ('FR', +1, -1), ('RL', -1, +1), ('RR', -1, -1)]

def leg_points(qh, qt, qk, sx, sy):
    """Knee and paw in the BODY frame, metres."""
    xl = -g.thigh_length * math.sin(qt)
    zl = -g.thigh_length * math.cos(qt)
    xf = xl - g.calf_length * math.sin(qt + qk)
    zf = zl - g.calf_length * math.cos(qt + qk)
    d = sy * g.hip_offset
    out = []
    for a, b in ((xl, zl), (xf, zf)):
        # Rx(qh) applied to (a, d, b)
        y = d * math.cos(qh) - b * math.sin(qh)
        z = d * math.sin(qh) + b * math.cos(qh)
        out.append((sx * g.mount_x + a, sy * g.mount_y + y, z))
    return out

poses = []
for vx, wz in itertools.product((0.0, 0.05, 0.10, -0.05), (0.0, 0.6, -0.6)):
    gen.reset()
    for _ in range(400):                      # 4 s at 100 Hz
        poses.append(gen.step(0.01, vx, wz))
poses.append(gen.stand())
for a in (0.0, 0.25, 0.5, 0.75, 1.0):
    poses.append(gen.stretch_pose(a))
    poses.append(gen.lie_pose(a))
print(f'{len(poses)} poses sampled')

xs, ys, zs, hips = [], [], [], []
inner = None
for pose in poses:
    for (name, sx, sy), (qh, qt, qk) in zip(LEGS, joints_of(pose)):
        for part, (x, y, z) in zip(('knee', 'paw'),
                                   leg_points(qh, qt, qk, sx, sy)):
            if part == 'knee':
                xs.append(x)
                ys.append(abs(y))
                zs.append(z)
                hips.append(qh)
            if inner is None or abs(y) < inner[0]:
                inner = (abs(y), part, x, z, qh)

print()
print('KNEE, over every commanded pose (metres, body frame):')
print(f'  x: {min(xs):+.4f} .. {max(xs):+.4f}')
print(f'  |y| max: {max(ys):.4f}   (hip mount is at |y|=0.055)')
print(f'  z: {min(zs):+.4f} .. {max(zs):+.4f}   (hip joint is z=0)')
print(f'  hip roll: {math.degrees(min(hips)):+.1f} .. '
      f'{math.degrees(max(hips)):+.1f} deg')

BW, BH = 0.111, 0.141          # body box from cat.urdf.xacro
half = BW / 2
print()
print(f'Body box is {BW*1000:.0f} wide, {BH*1000:.0f} tall, '
      f'hips on its side face.')
print(f'  widest knee excursion outboard of the hip: '
      f'{(max(ys)-0.055)*1000:+.1f} mm')
print(f'  highest the knee ever rises: z = {max(zs)*1000:+.1f} mm')

print()
print('CLOSEST APPROACH TO THE CENTRELINE - this is the number that')
print('licenses a full-width cosmetic shell instead of one scalloped')
print('around the legs:')
print(f'  nearest part: {inner[1]} at |y| = {inner[0]*1000:.1f} mm  '
      f'(x = {inner[2]*1000:+.1f}, z = {inner[3]*1000:+.1f}, '
      f'hip roll {math.degrees(inner[4]):+.1f} deg)')
print(f'  body half-width: {half*1000:.1f} mm')
print(f'  CLEARANCE: {(inner[0]-half)*1000:+.1f} mm')
if inner[0] <= half:
    print('  -> a full-width shell WOULD be hit. Scallop it, or narrow')
    print('     the body, or reduce hip_range.')
    sys.exit(1)
