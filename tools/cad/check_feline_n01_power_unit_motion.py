"""One received power-unit pose vs adopted36leg samples and true envelope.

Does not recompute native CAD or repeat the static scene. Old torso is tested
as actual saved outer volume, not its box. All contacts/failures are retained.
"""
import json
import time
from pathlib import Path
import FreeCAD as A
import Part
import numpy as np
from check_main_p0_placement import ROOT,SavedShapes,sha
from plan_feline_layout import OUT,BASE,MODEL,STAGES
from plan_feline_n01_shared import pipe
from check_feline_leg_body import placement

def pose(r,t):
    m=A.Matrix()
    for i in range(3):
        for j in range(3):setattr(m,f'A{i+1}{j+1}',r[i][j])
    return A.Placement(A.Vector(*t),A.Rotation(m))

def main():
    tick=time.monotonic();reader=SavedShapes();dest=OUT/'n01-power-unit-motion-envelope.json'
    assert not dest.exists(),'Receive previous result; no unchanged rerun'
    files=[OUT/'n01-coupled-pi-bus-plan-r3.json',OUT/'n01-coupled-pi-bus-checks-spatial.json',
        OUT/'n01-module-plan-r5.json',OUT/'motion-layout.json',ROOT/'hardware/simulation/p0/e6-leg-compatibility.json']
    plan,screen,groups,motion,axisdata=[json.loads(p.read_text()) for p in files]
    assert screen['status']=='CHANGED_STATIC_INTERFACES_CLEAR_FULL_PLAN_OPEN' and not screen['contacts'] and not screen['errors']
    for p,h in screen['source_sha256'].items():assert sha(ROOT/p)==h,p
    choice=screen['whole_unit_search']['chosen_one'];T=pose(choice['R'],choice['translation_mm'])
    native=OUT/'FelineInteriorMotion.FCStd';parts={}
    for g in groups['groups']:
        role=g['role']
        if role not in plan['unit_template_groups']:continue
        if role=='F_PI':
            f=plan['F_PI'];R=np.array(f['rotation_relative_current'])
            P=pose(R.tolist(),(np.array(f['centre_mm'])-R@np.array(f['old_centre_mm'])).tolist())
        else:
            r=plan['relative_poses'][role];P=pose(r['rotation_rows'],r['translation_mm'])
        for n in g['objects']:
            s=reader.shape(native,n);s.Placement=T*P*s.Placement;parts[n]=s
    for name,segments in screen['current_full_route_parts'].items():
        row=next(r for r in plan['routes'] if r['wire']==name);parts[name]=pipe(segments,row['radius_mm'])
    # Orthogonal whole-template transform leaves these solid boxes exact
    # reservations; they are not manufactured clips or native support approval.
    reservations=set()
    for n,(lo,hi) in screen['unit_reservations_world_bounds_mm'].items():
        parts[n]=Part.makeBox(*(np.array(hi)-lo),A.Vector(*lo));reservations.add(n)
    report=dict(status='RUNNING',selected=False,N01_complete=False,physical_pass=False,native_changed=False,
        contacts=[],reservation_contacts=[],errors=[],poses=[],pairs=0,envelope_outside=[],
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in files+[Path(__file__)]},
        scope='Only received complete Pi unit/new wire/complete relief reservations against108articulated leg parts at accepted0..35. Old torso outer volume is actual containment, not box. No full other nets, supports, tools or continuous sweep.')
    def save():
        report.update(worker_seconds=round(time.monotonic()-tick,3),updated_utc=__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat())
        dest.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    def gate():
        if time.monotonic()-tick>180:
            report['status']='TIME_BOUNDED_PARTIAL_NOT_SELECTED';save();raise TimeoutError('180s cap')
    outerfile=OUT/'FelineLayoutEnvelope.FCStd';outer=reader.shape(outerfile,'TorsoEnvelope')
    assert outer.isValid() and len(outer.Solids)==1
    for n,s in parts.items():
        gate()
        try:
            assert s.isValid() and len(s.Solids)>0
            outside=s.cut(outer);assert outside.isNull() or outside.isValid()
            if outside.Volume>1e-5:
                b=outside.BoundBox
                report['envelope_outside'].append(dict(object=n,reservation=n in reservations,
                    outside_volume_mm3=outside.Volume,bounds_mm=[[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]]))
        except Exception as exc:report['errors'].append(dict(object=n,scope='true_saved_outer_envelope',error=str(exc)))
    report['outer_volume_is_not_2p4mm_wall_or_accepted_new_skin']=True
    save();print('True envelope outside',len(report['envelope_outside']),flush=True)
    moving={n:reader.shape(MODEL,n) for group in motion['membership'].values() for ns in group.values() for n in ns}
    fixedbounds={n:s.BoundBox for n,s in parts.items()};axes=axisdata['axes']
    valid={}
    for index in range(36):
        p=motion['poses'][index]
        for code,group in motion['membership'].items():
            a=[next(a for a in axes if a['code']==code and a['stage']==st) for st in STAGES]
            transforms=placement(a,p['legs'][code]['angles_delta_degrees'])
            for st,names in group.items():
                for n in names:
                    gate();s=moving[n].copy();s.Placement=transforms[st]*s.Placement;b=s.BoundBox
                    for un,u in parts.items():
                        if not b.intersect(fixedbounds[un]):continue
                        report['pairs']+=1
                        try:
                            if n not in valid:valid[n]=s.isValid() and bool(s.Solids)
                            assert valid[n],'Invalid leg material'
                            c=s.common(u);assert c.isNull() or c.isValid()
                            if c.Volume>1e-5:
                                report['reservation_contacts' if un in reservations else 'contacts'].append(
                                    dict(pose=index,leg=n,unit=un,volume_mm3=c.Volume))
                        except Exception as exc:report['errors'].append(dict(pose=index,a=n,b=un,error=str(exc)))
        report['poses'].append(index);save()
    report.update(source_sha256={**report['source_sha256'],**reader.hashes},
        status='ADOPTED_MOTION_CLEAR_OLD_ENVELOPE_REJECTED' if report['envelope_outside'] and not(report['contacts'] or report['reservation_contacts'] or report['errors'])
        else 'ADOPTED_UNIT_MOTION_REJECTED' if report['contacts'] or report['reservation_contacts'] or report['errors'] else 'ADOPTED_UNIT_MOTION_AND_OUTER_CONTAINMENT_CLEAR_WALLS_MOUNTS_TOOLS_OPEN')
    save();print(json.dumps(dict(status=report['status'],poses=len(report['poses']),pairs=report['pairs'],contacts=len(report['contacts']),reservation_contacts=len(report['reservation_contacts']),outside=len(report['envelope_outside']),errors=len(report['errors']),seconds=report['worker_seconds'])),flush=True)

if __name__=='__main__':main()
