"""One shared planning scene: selected saved geometry, lying path and shell.

Does not save/recompute the released robot. Sampled mesh floor screening and
numerical IK are planning evidence; native clearance/mounts remain separate.
"""
import argparse
import json
import math
import pickle
import time
import zipfile
from pathlib import Path

import FreeCAD as A
import numpy as np
from check_main_p0_placement import ROOT, SavedShapes, prop, sha

BASE = ROOT / 'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype'
OUT = BASE / 'feline-enclosure'
MODEL = BASE / 'phase1-whole-assembly/RobotCatPhase1Current.FCStd'
REFERENCE = ROOT / 'hardware/reference/appearance/ola-cat-reference.jpg'
STAGES = ('Hip', 'Knee', 'Ankle')


def rotation(axis, degrees):
    a = np.asarray(axis, dtype=float)
    a /= np.linalg.norm(a)
    x, y, z = a
    skew = np.array([[0, -z, y], [z, 0, -x], [-y, x, 0]])
    angle = math.radians(degrees)
    return np.eye(3) + math.sin(angle)*skew + (1-math.cos(angle))*(skew@skew)


def transforms(axes, angles):
    result = []
    r, t = np.eye(3), np.zeros(3)
    for axis, angle in zip(axes, angles):
        q = rotation(axis['axis'], angle)
        p = np.array(axis['pivot_mm'])
        t = r@(p-q@p)+t
        r = r@q
        result.append((r.copy(), t.copy()))
    return result


def apply(points, transform):
    r, t = transform
    return points@r.T+t


def solve(axes, foot_point, foot_vertices, target, initial):
    """Keep proxy XY and lowest tessellated foot Z, with free foot orientation."""
    def function(q):
        tf = transforms(axes, q)[-1]
        p = apply(foot_point, tf)
        return np.array([p[0], p[1], apply(foot_vertices, tf)[:, 2].min()])
    q = np.array(initial, dtype=float)
    for iteration in range(90):
        value = function(q)
        residual = target-value
        if np.linalg.norm(residual) < .02:
            return q, float(np.linalg.norm(residual)), iteration
        jacobian = np.column_stack([(function(q+np.eye(3)[i]*.01)-value)/.01 for i in range(3)])
        step = np.linalg.solve(jacobian.T@jacobian + np.eye(3)*.0001, jacobian.T@residual)
        step *= min(1, 6/max(np.abs(step).max(),1e-9))
        choices = [q+step*f for f in (1,.5,.25,.125,.0625)]
        improved = min(choices,key=lambda v:np.linalg.norm(target-function(v)))
        if np.linalg.norm(target-function(improved)) >= np.linalg.norm(residual)-1e-8:
            break
        q = improved
        if np.abs(q).max() > 150:
            break
    return q, float(np.linalg.norm(target-function(q))), iteration+1


def load():
    selected = json.loads((BASE/'phase1-whole-assembly/selection.json').read_text())
    assert sha(MODEL) == selected['native_sha256']
    reader = SavedShapes()
    objects = reader.doc(MODEL)
    labels = {n:prop(o, 'Label')[0].get('value') for n,o in objects.items()}
    cache = BASE/'phase1-prototype-final/preview/triangulation-cache.pkl'
    meshes = {}
    with cache.open('rb') as f:
        header = pickle.load(f)
        assert header['model_sha256'] == sha(MODEL)
        assert all(sha(ROOT/n) == h for n,h in header['native_pins'].items())
        while True:
            try:
                name, mesh = pickle.load(f)
            except EOFError:
                break
            meshes[name] = mesh
    archive = ROOT/'hardware/simulation/v35/inputs.zip'
    with zipfile.ZipFile(archive) as z:
        geometry = json.loads(z.read('geometry.json'))
    axis_path = ROOT/'hardware/simulation/p0/e6-leg-compatibility.json'
    axis_data = json.loads(axis_path.read_text())
    membership = {code:{stage:[] for stage in STAGES} for code in ('FL','FR','RL','RR')}
    for row in geometry['components']:
        if not row['stage'].startswith('Motion_'):
            continue
        _,code,stage = row['stage'].split('_')
        prefix = 'P0_'+row['name']+'/'
        names = [n for n in meshes if labels[n].startswith(prefix)]
        assert len(names) == 1, (row['name'],names)
        membership[code][stage].append(names[0])
    assert all([len(groups[s]) for s in STAGES] == [9,14,4] for groups in membership.values())
    # Re-establish all actual current horn datums rather than trusting names.
    datum_checks = []
    import Part
    for axis in axis_data['axes']:
        prefix = 'P0_'+axis['horn']+'/'
        names = [n for n in meshes if labels[n].startswith(prefix)]
        assert len(names) == 1
        shape = reader.shape(MODEL, names[0])
        cylinders = [f.Surface for f in shape.Faces if isinstance(f.Surface,Part.Cylinder)
                     and abs(f.Surface.Radius-9.6)<1e-5]
        assert len(cylinders) == 1
        cylinder = cylinders[0]
        delta = np.linalg.norm(np.array(list(cylinder.Center))-axis['pivot_mm'])
        direction = abs(np.dot(np.array(list(cylinder.Axis)),axis['axis']))
        assert delta < 1e-5 and abs(direction-1) < 1e-8, axis['name']
        datum_checks.append(dict(joint=axis['name'],current_object=names[0],pivot_error_mm=float(delta)))
    pins = {**reader.hashes, **header['native_pins']}
    for path in (REFERENCE, archive, axis_path, Path(__file__)):
        pins[path.relative_to(ROOT).as_posix()] = sha(path)
    return meshes, labels, membership, axis_data, pins, datum_checks


def screen(max_drop, foot_shift):
    tick = time.monotonic()
    OUT.mkdir(exist_ok=True)
    meshes, labels, membership, data, pins, datums = load()
    mesh_vertices = {n:np.unique(m[0].reshape(-1,3),axis=0) for n,m in meshes.items() if m[2]=='surface'}
    path = []
    previous = {code:np.zeros(3) for code in membership}
    min_rest_z = min(mesh_vertices[n][:,2].min() for g in membership.values() for n in g['Ankle'])
    for drop in np.linspace(0,max_drop,49):
        legs = {}
        for code,groups in membership.items():
            axes = [next(a for a in data['axes'] if a['code']==code and a['stage']==s) for s in STAGES]
            f = next(f for f in data['feet'] if f['code']==code)
            foot_name = next(n for n in groups['Ankle'] if labels[n].startswith('P0_'+f['part']+'/'))
            foot = mesh_vertices[foot_name]
            point = np.array([21-f['proxy_m'][0]*1000,-f['proxy_m'][1]*1000,18.51+f['proxy_m'][2]*1000])
            assert abs(foot[:,2].min()-point[2]) < .8
            fraction=drop/max_drop if max_drop else 0
            target = np.array([point[0]+foot_shift*fraction,point[1],min_rest_z+drop])
            q,error,iterations = solve(axes,point,foot,target,previous[code])
            previous[code] = q
            tf = transforms(axes,q)
            below = []
            lowest = (None,float('inf'))
            for stage,pose in zip(STAGES,tf):
                for n in groups[stage]:
                    z = float(apply(mesh_vertices[n],pose)[:,2].min()-drop)
                    if z<lowest[1]: lowest=(n,z)
                    if z < min_rest_z-.8: below.append(dict(object=n,penetration_mm=round(min_rest_z-z,4)))
            legs[code] = dict(physical_leg=axes[0]['physical_leg'],angles_delta_degrees=q.tolist(),
                foot_fit_error_mm=error,iterations=iterations,lowest_object=lowest[0],
                floor_mesh_gap_mm=lowest[1]-min_rest_z,mesh_floor_intrusions=below)
        path.append(dict(body_drop_mm=float(drop),legs=legs))
    inventory = []
    for name,(triangles,color,kind) in meshes.items():
        pts=triangles.reshape(-1,3);lo=pts.min(0);hi=pts.max(0)
        inventory.append(dict(object=name,label=labels[name],kind=kind,bounds_mm=[lo.tolist(),hi.tolist()],
            torso_box_exceeded=bool(lo[0]<-141.5 or hi[0]>183.5 or lo[1]<-100 or hi[1]>100 or lo[2]<-20 or hi[2]>140)))
    report=dict(status='CURRENT_DATUM_LIE_PATH_PLANNING_ONLY',selected=False,physical_pass=False,
        current_horn_datums_verified=datums,membership=membership,ground_rest_z_mm=float(min_rest_z),
        body_drop_target_mm=max_drop,foot_shift_x_target_mm=foot_shift,poses=path,inventory=inventory,source_sha256=pins,
        solver='Numerical FK from verified current12horn datums; keep foot proxyXY and tessellated bottomZ. Free foot orientation, independent legs.',
        open=['Mechanical joint limits and native joints','Leg-to-leg/body/support collisions',
              'Cable bending/tension with full motion','Load/COM/torque estimates','Pad load path and actual contact','Shell containment and mounting'],
        worker_seconds=round(time.monotonic()-tick,3))
    (OUT/'motion-layout.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=report['status'],seconds=report['worker_seconds'],datums=len(datums),poses=len(path),
        worst_foot_error_mm=max(l['foot_fit_error_mm'] for p in path for l in p['legs'].values()),
        poses_with_floor_intrusions=sum(any(l['mesh_floor_intrusions'] for l in p['legs'].values()) for p in path))),flush=True)


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--drop',type=float,default=120)
    parser.add_argument('--foot-shift',type=float,default=0)
    args=parser.parse_args()
    screen(args.drop,args.foot_shift)
