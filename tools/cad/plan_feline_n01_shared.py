"""N01 cause-changing layout preflight. No native build or source CAD writes.

One rear receiving bay relocation as a complete assembly; retained connector
types, both factory/custom exits, compulsory9mm lands and R12.4 factory paths.
Candidate rail foundation is screened separately, not called a finished mount.
"""
import copy
import json
import time
import sys
from datetime import datetime, timezone
from pathlib import Path

import FreeCAD as A
import Part
import numpy as np

from check_main_p0_placement import ROOT, SavedShapes, sha
from plan_feline_layout import OUT
from plan_feline_factory_links import routes

REV2 = '--shared-power-bay' in sys.argv
REV3 = '--flat-power-bay' in sys.argv
REV4 = '--flat-axial-power-bay' in sys.argv
REV5 = '--inboard-power-stack' in sys.argv
SUFFIX = '-r5' if REV5 else '-r4' if REV4 else '-r3' if REV3 else '-r2' if REV2 else ''
DEST = OUT / ('n01-shared-preflight'+SUFFIX+'.json')


def pipe(parts, radius):
    edges = []
    for e in parts:
        a, b = A.Vector(*e['start']), A.Vector(*e['end'])
        edges.append(Part.makeLine(a, b) if e['kind'] == 'line' else
                     Part.Arc(a, A.Vector(*e['mid']), b).toShape())
    w = Part.Wire(edges)
    p, t = w.Edges[0].valueAt(w.Edges[0].FirstParameter), w.Edges[0].tangentAt(w.Edges[0].FirstParameter)
    s = w.makePipeShell([Part.Wire([Part.makeCircle(radius, p, t)])], True, False)
    assert s.isValid() and len(s.Solids) == 1
    return s


def near(a, b, gap=0):
    a, b = a.BoundBox, b.BoundBox
    return sum(max(0, x-y, z-w)**2 for x,y,z,w in
               [(a.XMin,b.XMax,b.XMin,a.XMax), (a.YMin,b.YMax,b.YMin,a.YMax),
                (a.ZMin,b.ZMax,b.ZMin,a.ZMax)]) <= gap*gap


def main():
    tick = time.monotonic()
    reader = SavedShapes()
    source = OUT / 'motion-receivers-checks.json'
    receipt = json.loads(source.read_text())
    native = ROOT / receipt['native']
    assert sha(native) == receipt['native_sha256']
    planfile = ROOT / receipt['module_plan']
    plan = copy.deepcopy(json.loads(planfile.read_text()))
    groups = {g['role']: g for g in plan['groups']}
    deltas = {'W044_Joint': [20, 2, 0], 'W052_Joint': [20, -2, 0]}
    if REV2:
        # Change the entire receiving bay, not another local joint offset:
        # the vertically oriented rear power stations own the blocked space.
        # Raise both complete power stations above the factory feed layer.
        deltas.update({'WAGO:RL_P':[0,0,31], 'WAGO:RR_P':[0,0,31]})
    rotations={}
    if REV3:
        # Architecture change after two rejections: vertical power cases become
        # a flat outboard bed, below the frame, not an upward translation into it.
        rr=np.array([[0,0,1],[1,0,0],[0,1,0]],dtype=float)
        for role,sign in (('WAGO:RL_P',-1),('WAGO:RR_P',1)):
            oldcenter=np.mean(groups[role]['candidate_bounds_mm'],axis=0)
            newcenter=np.array([-12,sign*51,-27])
            deltas[role]=(newcenter-rr@oldcenter).tolist();rotations[role]=rr
    if REV4:
        # R3 changed case depth but directed its live9mm lands into the joint
        # bay. Orthogonal flat orientation keeps ALL power mouths axial+X.
        # Bounds are disjoint from joints/frame/U1 before the exact screen.
        rr=np.array([[1,0,0],[0,0,-1],[0,1,0]],dtype=float)
        for role,sign in (('WAGO:RL_P',-1),('WAGO:RR_P',1)):
            oldcenter=np.mean(groups[role]['candidate_bounds_mm'],axis=0)
            newcenter=np.array([-12,sign*56,-27])
            deltas[role]=(newcenter-rr@oldcenter).tolist();rotations[role]=rr
    if REV5:
        # R4 is static-clear but uses the established front-leg swept keepout.
        # Reserve it for motion; put the whole receiving stack INBOARD instead.
        # MTA top-26 ->9mm power bed[-24.25,-15.25] ->rail bottom-13.5.
        # Two large rails rise3mm together, remaining below frame bottom-2.
        rr=np.array([[1,0,0],[0,0,-1],[0,1,0]],dtype=float)
        for role,sign in (('WAGO:RL_P',-1),('WAGO:RR_P',1)):
            oldcenter=np.mean(groups[role]['candidate_bounds_mm'],axis=0)
            newcenter=np.array([-43,sign*15,-19.75])
            deltas[role]=(newcenter-rr@oldcenter).tolist();rotations[role]=rr
        deltas.update({'WAGO:P_SYS_new':[0,0,3], 'WAGO:P_REAR':[0,0,3]})
    for role, delta in deltas.items():
        g = groups[role]
        rr=rotations.get(role,np.eye(3))
        g['translation_mm'] = (rr@np.array(g['translation_mm']) + delta).tolist()
        g['rotation_rows']=(rr@np.array(g['rotation_rows'])).tolist()
        lo,hi=np.array(g['candidate_bounds_mm'])
        corners=np.array([[x,y,z] for x in (lo[0],hi[0]) for y in (lo[1],hi[1]) for z in (lo[2],hi[2])])@rr.T+delta
        g['candidate_bounds_mm']=[corners.min(axis=0).tolist(),corners.max(axis=0).tolist()]
    plan.update(status='N01_SHARED_CANDIDATE_NOT_SELECTED', selected=False,
                n01_relative_changes_mm=deltas, full_mounts_complete=False)
    planout = OUT / ('n01-module-plan'+SUFFIX+'.json')
    assert not planout.exists(), 'Receive existing N01 result, do not repeat'
    planout.write_text(json.dumps(plan, indent=2)+'\n')
    result = dict(status='RUNNING', selected=False, physical_pass=False,
        changed_complete_receiving_groups=deltas, connector_types_unchanged=True,
        relative_rotations={k:v.tolist() for k,v in rotations.items()},
        required_straight_mm=9, factory_bend_R_mm=12.4,
        factory_usable100_is_project_assumption=True,
        contacts=[], clearance_failures=[], errors=[], pairs=0,
        full_wiring_verified=False, full_motion_verified=False,
        support_plan_complete=False, native_built=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (source,native,planfile,Path(__file__))})
    def save():
        result['worker_seconds'] = round(time.monotonic()-tick,3)
        result['updated_utc'] = datetime.now(timezone.utc).isoformat()
        DEST.write_text(json.dumps(result,indent=2)+'\n')
    def gate():
        if time.monotonic()-tick > 180:
            result['status']='TIME_BOUNDED_PARTIAL'; save(); raise TimeoutError('180s preflight budget')
    save()
    scene, role_of = {}, {}
    for g in groups.values():
        for name in g['objects']:
            gate()
            s = reader.shape(native,name)
            if g['role'] in deltas:
                role=g['role']
                rot=(A.Rotation(A.Vector(1,0,0),90) if REV4 or REV5 else A.Rotation(A.Vector(1,1,1),120)) if role in rotations else A.Rotation()
                s.Placement=A.Placement(A.Vector(*deltas[role]),rot)*s.Placement
            scene[name],role_of[name] = s,g['role']
    inv = json.loads((OUT/'motion-layout.json').read_text())['inventory']
    for row in inv:
        name = row['object']
        if name not in scene and row['kind']=='surface' and (name.startswith(('Print_P0_','Ref_Material_P0_','Print_CP2_TailRiser','Battery')) or row['label'].startswith(('P0_','tail/'))):
            if not name.startswith('BatteryFrameHardware'): scene[name]=reader.shape(native,name)
    for i in range(1,5):scene[f'BellyFoot{i}']=reader.shape(native,f'BellyFoot{i}')
    def check(an,a,bn,b,scope,gap=0):
        gate()
        if not near(a,b,gap):return
        result['pairs']+=1
        try:
            assert a.isValid() and b.isValid(), 'Invalid target is not clearance'
            c=a.common(b)
            assert c.isNull() or c.isValid(), 'Invalid intersection'
            if c.Volume>1e-5:result['contacts'].append(dict(a=an,b=bn,scope=scope,volume_mm3=c.Volume))
            elif gap:
                distance=a.distToShape(b)[0]
                if distance<gap-1e-5:result['clearance_failures'].append(dict(a=an,b=bn,scope=scope,gap_mm=distance,required_mm=gap))
        except Exception as exc:result['errors'].append(dict(a=an,b=bn,scope=scope,error=str(exc)))
    changed = {n:s for n,s in scene.items() if role_of.get(n) in deltas}
    for n,s in changed.items():
        for bn,b in scene.items():
            if bn==n or role_of.get(bn)==role_of[n]:continue
            check(n,s,bn,b,'rear_joint_case')
    save();print('Rear cases',len(result['contacts']),len(result['errors']),flush=True)
    specifications=json.loads((OUT/'prefix-allocation.json').read_text())['specifications']
    lands={}
    result['lands']=[]
    for spec in specifications:
        if spec['role'] not in deltas:continue
        old_change=json.loads(planfile.read_text())['motion_receiving_changes'].get(spec['role'],
            {'rotation_rows':np.eye(3).tolist(),'translation_mm':[0,0,0]})
        p=np.array(old_change['rotation_rows'])@np.array(spec['point'])+old_change['translation_mm']+deltas[spec['role']]
        d=np.array(old_change['rotation_rows'])@np.array(spec['direction']);d/=np.linalg.norm(d)
        if spec['role'] in rotations:
            p=rotations[spec['role']]@(p-np.array(deltas[spec['role']]))+deltas[spec['role']]
            d=rotations[spec['role']]@d
        land=Part.makeCylinder(spec['radius'],9,A.Vector(*p),A.Vector(*d))
        lands[spec['id']]=land
        result['lands'].append(dict(id=spec['id'],start_mm=p.tolist(),end_mm=(p+9*d).tolist(),radius_mm=spec['radius']))
        for bn,b in scene.items():
            if role_of.get(bn)==spec['role']:continue
            check(spec['id'],land,bn,b,'required_complete9mm',gap=1.25)
    factory=routes(plan)
    result['factory_routes']=factory
    pipes={r['wire']:pipe(r['parts'],r['radius_mm']) for r in factory}
    for row in factory:
        wid=row['wire']
        if wid not in ('W044','W052'):continue
        trim=copy.deepcopy(row['parts'])
        for idx,first in ((0,True),(-1,False)):
            e=trim[idx];a,b=np.array(e['start']),np.array(e['end']);d=(b-a)/np.linalg.norm(b-a)
            if first:e['start']=(a+2.5*d).tolist()
            else:e['end']=(b-2.5*d).tolist()
        short=pipe(trim,row['radius_mm'])
        mates=set(groups[row['source_group']]['objects']+groups[row['joint_group']]['objects'])
        for bn,b in scene.items():check(wid,short if bn in mates else pipes[wid],bn,b,'rear_factory_path',gap=1.25)
        for bn,b in pipes.items():
            if wid!=bn:check(wid,pipes[wid],bn,b,'factory_mutual',gap=.2)
    result['source_sha256'].update(reader.hashes)
    result['status']='REAR_BAY_STATIC_LANDS_FACTORY_CLEAR_SHARED_PLAN_OPEN' if not any(result[k] for k in ('contacts','clearance_failures','errors')) else 'REAR_BAY_PREFLIGHT_REJECTED'
    save()
    print(json.dumps({k:result[k] for k in ('status','pairs','contacts','clearance_failures','errors','worker_seconds')}),flush=True)


if __name__=='__main__':main()
