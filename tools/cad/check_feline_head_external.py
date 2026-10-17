"""Changed external head neighbours and floor; conservative nine-pose envelope.

Every head reference is checked at all9 pitch/yaw samples. This overbounds
fixed/yaw-only/pitch+yaw ownership, and cannot qualify internal head motion,
continuous movement, joint calibration or moving wiring. No hidden exclusions.
"""
import json,time
from pathlib import Path
import FreeCAD as A
from check_main_p0_placement import ROOT,SavedShapes,sha
from plan_feline_layout import OUT,STAGES
from check_feline_leg_body import placement


def main():
    tick=time.monotonic();reader=SavedShapes()
    proof=json.loads((OUT/'interior-native-checks.json').read_text())
    assert proof['status']=='COMMON_INTERIOR_ENDPOINTS_CLEAR_MOUNTS_WIRES_SKIN_OPEN'
    native=ROOT/proof['native'];assert sha(native)==proof['native_sha256']
    plan=json.loads((OUT/'module-layout.json').read_text())
    motion=json.loads((OUT/'motion-layout.json').read_text())
    head=next(g['objects'] for g in plan['groups'] if g['role']=='HeadMechanism')
    other=[n for g in plan['groups'] if g['role']!='HeadMechanism' for n in g['objects']]
    objects=reader.doc(native)
    retained=[n for n in objects if n.startswith(('Print_P0_','Print_CP2_TailRiser','Battery','Ref_Material_P0_','Ref_Material_tail_','BellyFoot','FrameHardwareNew'))]
    retained=[n for n in retained if n not in head and n not in other]
    # Read only actual BRep-bearing references, not organisational containers.
    scene={n:reader.shape(native,n) for n in other+retained}
    moving={n for g in motion['membership'].values() for ns in g.values() for n in ns}
    assert moving.issubset(scene),'All108 leg references must remain visible to external screen'
    fixed={n:s for n,s in scene.items() if n not in moving}
    fixed_bounds={n:s.BoundBox for n,s in fixed.items()}
    report=dict(status='HEAD_EXTERNAL_SCREEN_RUNNING',selected=False,physical_pass=False,
        contacts=[],errors=[],floor_contacts=[],pairs=0,poses=[],head_references=len(head),
        ownership='Conservative union: all73refs at all9combined samples. Fixed/yaw-only actual states are included at pitch0/yaw0; no internal ownership claim.',
        internal_head_motion_reused_not_rerun=True,continuous_motion=False,
        complete_moving_wiring=False,skin_included=False,
        source_sha256={native.relative_to(ROOT).as_posix():sha(native),
            (OUT/'module-layout.json').relative_to(ROOT).as_posix():sha(OUT/'module-layout.json'),
            (OUT/'motion-layout.json').relative_to(ROOT).as_posix():sha(OUT/'motion-layout.json'),
            Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))})
    dest=OUT/'head-external-motion.json'
    def save():
        report['worker_seconds']=round(time.monotonic()-tick,3);dest.write_text(json.dumps(report,indent=2)+'\n')
    def check(hn,h,bh,n,s,bs,pose,leg_pose=None):
        if not bh.intersect(bs):return
        report['pairs']+=1
        try:
            c=h.common(s)
            if not c.isNull() and not c.isValid():raise ValueError('Invalid intersection')
            if c.Volume>1e-5:report['contacts'].append(dict(head=hn,neighbour=n,pose=pose,leg_pose=leg_pose,volume_mm3=c.Volume,
                conservative_ownership_witness_requires_classification=True))
        except Exception as exc:report['errors'].append(dict(head=hn,neighbour=n,error=str(exc)))
    axes=json.loads((ROOT/'hardware/simulation/p0/e6-leg-compatibility.json').read_text())['axes']
    leg_scenes=[]
    for index,pose in enumerate(motion['poses'][:36]):
        current={}
        for code,g in motion['membership'].items():
            aa=[next(a for a in axes if a['code']==code and a['stage']==stage) for stage in STAGES]
            tf=placement(aa,pose['legs'][code]['angles_delta_degrees'])
            for stage,ns in g.items():
                for n in ns:
                    s=scene[n].copy();s.Placement=tf[stage]*s.Placement;current[n]=(s,s.BoundBox)
        leg_scenes.append(current)
    floor=motion['ground_rest_z_mm']+motion['poses'][35]['body_drop_mm']
    source={n:reader.shape(native,n) for n in head}
    for pitch in (-10,0,5):
        for yaw in (-15,0,15):
            posed={};pose=[pitch,yaw];start=report['pairs']
            for n,raw in source.items():
                s=raw.copy()
                if pitch:s.rotate(A.Vector(*plan['head_pitch_axis_mm']),A.Vector(0,1,0),pitch)
                if yaw:s.rotate(A.Vector(*plan['head_yaw_axis_mm']),A.Vector(0,0,1),yaw)
                b=s.BoundBox;posed[n]=(s,b)
                # Positive only requires an exact floor-volume witness.
                if b.ZMin<floor-.02:
                    import Part
                    c=s.common(Part.makeBox(2000,2000,1000,A.Vector(-1000,-1000,floor-1000)))
                    assert c.isNull() or c.isValid()
                    if c.Volume>1e-5:report['floor_contacts'].append(dict(head=n,pose=pose,volume_mm3=c.Volume))
                for fn,f in fixed.items():check(n,s,b,fn,f,fixed_bounds[fn],pose)
            for i,current in enumerate(leg_scenes):
                for hn,(h,bh) in posed.items():
                    for n,(s,bs) in current.items():check(hn,h,bh,n,s,bs,pose,i)
            report['poses'].append(dict(pitch=pitch,yaw=yaw,pairs=report['pairs']-start));save()
            print('Head external',pose,'contacts',len(report['contacts']),'errors',len(report['errors']),flush=True)
    report['source_sha256'].update(reader.hashes)
    report.update(status='HEAD_EXTERNAL_NINE_POSES_CLEAR_WIRING_SKIN_OPEN' if not any(report[k] for k in ('contacts','errors','floor_contacts')) else 'HEAD_EXTERNAL_WITNESSES_REQUIRE_REVIEW',
        leg_poses_checked=36,deepest_body_drop_mm=motion['poses'][35]['body_drop_mm'])
    save();print(json.dumps({k:report[k] for k in ('status','pairs','worker_seconds')}),flush=True)


if __name__=='__main__':main()
