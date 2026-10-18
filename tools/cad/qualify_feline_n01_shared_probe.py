"""Changed immutable world material only: true torso and adopted 36 leg poses.

No native build, whole-harness qualification, continuous sweep or physical PASS.
BUS reuses its separate unchanged scoped receipt; do not reinterpret bad BRep.
"""
import hashlib
import json
from pathlib import Path
import sys
import time
import zipfile

import FreeCAD as A
import Part
from check_main_p0_placement import ROOT, SavedShapes, sha
from plan_feline_layout import OUT, MODEL, STAGES
from check_feline_leg_body import placement


def main():
    tick=time.monotonic()
    dest=OUT/'n01-shared-probe-motion-envelope.json'
    assert not dest.exists(), 'Receive existing immutable result before rerun'
    src=OUT/'n01-shared-probe.json'
    data=json.loads(src.read_text())
    report=dict(status='RUNNING_CHANGED_SHARED_SCOPE',N01_complete=False,
        selected=False,physical_pass=False,native_changed=False,poses=[],
        envelope_outside=[],wall_budget_failures=[],contacts=[],
        reservation_contacts=[],errors=[],pairs=0,wall_gap_required_mm=3.65,
        continuous_motion_verified=False,full_harness_verified=False,
        BUS_scope='Separate unchanged envelope/36pose receipt reused; supplier rotation validity unresolved',
        source_sha256={src.relative_to(ROOT).as_posix():sha(src)})
    def save():
        report['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    def gate():
        if time.monotonic()-tick>240:raise TimeoutError('240s scoped worker cap; retain partial receipt')
    reader=SavedShapes()
    try:
        for n,h in data['source_sha256'].items():
            gate();assert sha(ROOT/n)==h,n
        bundle=ROOT/data['shared_probe']
        assert sha(bundle)==data['shared_probe_sha256']
        parts={};kinds={}
        with zipfile.ZipFile(bundle) as z:
            for row in data['parts']:
                b=z.read(row['entry']);assert hashlib.sha256(b).hexdigest()==row['sha256']
                s=Part.Shape();s.importBrepFromString(b.decode('utf-8'))
                assert s.isValid() and s.Solids,row['name']
                assert abs(s.Volume-row['volume_mm3'])<1e-5,row['name']
                parts[row['name']]=s;kinds[row['name']]=row['kind']
        outer=reader.shape(OUT/'FelineLayoutEnvelope.FCStd','TorsoEnvelope')
        assert outer.isValid() and len(outer.Solids)==1
        surface=Part.makeCompound(outer.Shells)
        report['parts']=len(parts);save()
        for n,s in parts.items():
            gate()
            diff=s.cut(outer)
            assert diff.isNull() or diff.isValid(),n
            if diff.Volume>1e-5:
                report['envelope_outside'].append(dict(object=n,outside_mm3=diff.Volume))
            else:
                gap=s.distToShape(surface)[0]
                if gap<3.65-1e-5:report['wall_budget_failures'].append(dict(object=n,gap_mm=gap))
            save()
        motionpath=OUT/'motion-layout.json'
        motion=json.loads(motionpath.read_text())
        axispath=ROOT/'hardware/simulation/p0/e6-leg-compatibility.json'
        axes=json.loads(axispath.read_text())['axes']
        report['source_sha256'].update({p.relative_to(ROOT).as_posix():sha(p) for p in (motionpath,axispath)})
        moving={n:reader.shape(MODEL,n) for group in motion['membership'].values() for ns in group.values() for n in ns}
        assert len(moving)==108
        corners={n:[A.Vector(x,y,z) for x in (s.BoundBox.XMin,s.BoundBox.XMax)
            for y in (s.BoundBox.YMin,s.BoundBox.YMax) for z in (s.BoundBox.ZMin,s.BoundBox.ZMax)] for n,s in moving.items()}
        pb={n:s.BoundBox for n,s in parts.items()}
        for index in range(36):
            sample=motion['poses'][index];pairs_before=report['pairs']
            floor=motion['ground_rest_z_mm']+sample['body_drop_mm']
            for code,group in motion['membership'].items():
                aa=[next(a for a in axes if a['code']==code and a['stage']==st) for st in STAGES]
                transforms=placement(aa,sample['legs'][code]['angles_delta_degrees'])
                for st,names in group.items():
                    for n in names:
                        gate();B=A.BoundBox()
                        for v in corners[n]:B.add(transforms[st].multVec(v))
                        near=[pn for pn,b in pb.items() if B.intersect(b)]
                        if not near:continue
                        s=moving[n].copy();s.Placement=transforms[st]*s.Placement
                        assert s.isValid(),n
                        for pn in near:
                            gate();report['pairs']+=1
                            common=s.common(parts[pn]);assert common.isNull() or common.isValid(),(n,pn)
                            if common.Volume>1e-5:
                                row=dict(leg=n,object=pn,pose=index,volume_mm3=common.Volume)
                                report['reservation_contacts' if 'reservation' in kinds[pn] else 'contacts'].append(row)
            below=[n for n,b in pb.items() if b.ZMin<floor-1e-5]
            report['poses'].append(dict(index=index,pairs=report['pairs']-pairs_before,floor_z_mm=floor,parts_below_floor=below))
            save();print('pose',index,'pairs',report['pairs'],'contacts',len(report['contacts']),flush=True)
        failed=any(report[k] for k in ('errors','envelope_outside','wall_budget_failures','contacts','reservation_contacts')) or any(p['parts_below_floor'] for p in report['poses'])
        report['status']='CHANGED_SHARED_SCOPE_REJECTED' if failed else 'CHANGED_SHARED_TRUE_OUTER_AND_ADOPTED36_CLEAR_RESTRAINTS_ASSEMBLY_HARNESS_OPEN'
    except Exception as exc:
        report['errors'].append(dict(error=repr(exc)))
        report['status']='CHANGED_SHARED_SCOPE_INCOMPLETE_ERROR'
    report['source_sha256'].update(reader.hashes)
    report['source_sha256'][Path(__file__).relative_to(ROOT).as_posix()]=sha(Path(__file__))
    save()
    print(json.dumps({k:report[k] for k in ('status','pairs','worker_seconds','errors','envelope_outside','wall_budget_failures','contacts','reservation_contacts')}),flush=True)


def finalize_received():
    """Recover final-save bookkeeping only, never rerun completed CAD work."""
    dest=OUT/'n01-shared-probe-motion-envelope.json';report=json.loads(dest.read_text())
    assert report['status']=='RUNNING_CHANGED_SHARED_SCOPE'
    assert [p['index'] for p in report['poses']]==list(range(36))
    assert report['parts']==64 and report['pairs']==1040
    src=OUT/'n01-shared-probe.json';data=json.loads(src.read_text())
    for n,h in data['source_sha256'].items():assert sha(ROOT/n)==h,n
    assert sha(ROOT/data['shared_probe'])==data['shared_probe_sha256']
    report['source_sha256'].update({p.relative_to(ROOT).as_posix():sha(p) for p in
        (src,MODEL,OUT/'FelineLayoutEnvelope.FCStd',OUT/'motion-layout.json',
         ROOT/'hardware/simulation/p0/e6-leg-compatibility.json',Path(__file__))})
    report['status']='CHANGED_SHARED_SCOPE_REJECTED'
    report['final_save_recovery']='All36poses saved; original finalizer used str instead of Path in sha. Corrected bookkeeping only, no geometry rerun.'
    report['geometry_computation_seconds']=report['worker_seconds']
    dest.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(report['status'],report['geometry_computation_seconds'],flush=True)


if __name__=='__main__':
    if '--finalize-received' in sys.argv:finalize_received()
    else:main()
