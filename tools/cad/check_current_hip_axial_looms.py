"""Qualify actual Hip material before rerouting its OPEN fixed neighbours.

The prior cheap wire rejection remains valid. This read-only gate separates
those known conflicts from actual frame/motor interference; it never selects
the layout, suppresses a contact, or reruns the eight unchanged Knee proof.
"""
import itertools
import json
import time
import zipfile
from pathlib import Path
from plan_current_main_sources import ROOT, OUT, SHA
from plan_current_moving_looms import add, sub, mul, rotation
from plan_current_hip_axial_looms import s_offset
from plan_current_mta_interfaces import line


def parts(row, angle):
    pose = next(p for p in row['poses'] if p['angle'] == angle)
    pivot, axis = row['pivot_mm'], row['joint_axis']
    tangent = row['axial_tangent']
    fixed = row['fixed_anchor_world_mm']
    end = add(pivot, rotation(sub(row['moving_anchor_rest_world_mm'], pivot), axis, angle))
    first, last = add(fixed, mul(tangent, 9)), sub(end, mul(tangent, 9))
    mid = add(mul(add(first, last), .5), [0, row['side'] * pose['bulge_mm'], 0])
    return [line(fixed, first)] + s_offset(first, mid, tangent) + s_offset(mid, last, tangent) + [line(last, end)]


def run():
    tick = time.monotonic()
    source = OUT / 'hip-axial-loom-plan.json'
    plan = json.loads(source.read_text())
    assert plan['status'] == 'REJECTED_AXIAL_HIP_SHARED_WIRES'
    for n, h in plan['source_sha256'].items():
        assert SHA(ROOT / n) == h, n
    from current_complete_harness_context import context, W, Part
    reader, pins, targets, old = context()
    archive = ROOT / 'hardware/simulation/v35/inputs.zip'
    af = ROOT / 'hardware/simulation/p0/e6-leg-compatibility.json'
    pins.update((source, Path(__file__), archive, af, ROOT / 'tools/cad/plan_current_hip_axial_looms.py'))
    axes = json.loads(af.read_text())['axes']
    with zipfile.ZipFile(archive) as z:
        components = json.loads(z.read('geometry.json'))['components']
    stages = {q['name']: q['stage'].split('_')[1:] for q in components if q['stage'].startswith('Motion_')}
    rows = {r['section']: r for r in plan['loops']}
    def shape(row, angle):
        q = W.makewire(parts(row, angle))
        assert q.isValid() and abs(sum(e.Length for e in q.Edges) - row['guide_mm']) < .001
        return q
    nominal = {n: shape(r, 0) for n, r in rows.items()}
    result = dict(status='PENDING', pairs=0, material_contacts=[], fixed_wire_contacts=[], mutual_contacts=[],
                  errors=[], tested_poses=[], selected=False, W5_complete=False, physical_pass=False,
                  native_changed=False, support_feet_qualified=False, continuous_motion_verified=False,
                  scope='12 axial Hip sections only. Known fixed-wire rejection is NOT waived. Knee proof is unchanged.')
    tested = set()
    def pair(n, c, m, t, rr, category, pose):
        if not W.near(c, t, 3 + rr):
            return
        result['pairs'] += 1
        try:
            assert c.isValid() and t.isValid()
            d, points, _ = c.distToShape(t)
            if d < 3 + rr - 1e-4:
                hit = dict(a=n, b=m, distance_mm=d, required_mm=3+rr, pose=pose,
                           witness_mm=[list(v) for v in points[0]] if points else None)
                result[category].append(hit)
                print(category, json.dumps(hit), flush=True)
        except Exception as e:
            result['errors'].append(dict(a=n, b=m, cause=repr(e)))
    def case(code, angles):
        hip, knee, ankle = angles
        pose = dict(code=code, hip=hip, knee=knee, ankle=ankle)
        ts = {}; T = W.A.Placement()
        if code:
            for stage, angle in zip(('Hip','Knee','Ankle'), angles):
                a = next(v for v in axes if v['code']==code and v['stage']==stage)
                pv = W.A.Vector(*a['pivot_mm']); rot = W.A.Rotation(W.A.Vector(*a['axis']), angle)
                T = T * W.A.Placement(pv - rot.multVec(pv), rot); ts[stage] = T
        changing = {n for n,r in rows.items() if code is None or r['cad_code']==code}
        curves = {n: shape(rows[n],hip) if code and n in changing else c for n,c in nominal.items()}
        for n in sorted(changing):
            c = curves[n]
            for m,t in targets.items():
                if not t.Solids: continue
                member = stages.get(m.removeprefix('P0_'))
                stage = member[1] if member and member[0]==code else None
                ma = () if not stage else angles[:('Hip','Knee','Ankle').index(stage)+1]
                key = (n,hip,m,ma)
                if key in tested: continue
                tested.add(key)
                if stage:
                    t=t.copy(); t.Placement=ts[stage]*t.Placement
                pair(n,c,m,t,0,'material_contacts',pose)
            for m,(t,rr) in old.items():
                key=(n,hip,m)
                if key not in tested:
                    tested.add(key); pair(n,c,m,t,rr,'fixed_wire_contacts',pose)
            for m,t in curves.items():
                if m==n or m in changing and m<n: continue
                ma=hip if m in changing else 0
                key=('mutual',tuple(sorted(((n,hip),(m,ma)))))
                if key not in tested:
                    tested.add(key); pair(n,c,m,t,3,'mutual_contacts',pose)
        result['tested_poses'].append(pose)
        print('Hip axial material pose',code,angles,'pairs',result['pairs'],flush=True)
    case(None,(0,0,0))
    if not result['material_contacts'] and not result['mutual_contacts'] and not result['errors']:
        for code in dict.fromkeys(r['cad_code'] for r in rows.values()):
            for angles in itertools.product((-15,0,15),repeat=3):
                if angles==(0,0,0): continue
                case(code,angles)
                if result['material_contacts'] or result['mutual_contacts'] or result['errors']: break
            if result['material_contacts'] or result['mutual_contacts'] or result['errors']: break
    result.update(status='REJECTED_AXIAL_HIP_ACTUAL_MATERIAL' if result['material_contacts'] or result['mutual_contacts'] or result['errors'] else 'AXIAL_HIP_MATERIAL_SAMPLED_ONLY_FIXED_WIRES_AND_SUPPORTS_OPEN',
                  worker_seconds=round(time.monotonic()-tick,3),
                  source_sha256={**reader.hashes,**{p.relative_to(ROOT).as_posix():SHA(p) for p in pins}})
    (OUT/'hip-axial-loom-material.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:result[k] for k in ('status','pairs','worker_seconds')}),flush=True)
    return result


if __name__=='__main__':
    run()
