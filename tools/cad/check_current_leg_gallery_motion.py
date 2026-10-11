"""Changed receiving gallery vs articulated saved leg material, read only.

The +/-15deg grid is a PROJECT packaging allowance, NOT approved mechanical
travel, calibrated limits, a swept-volume proof or a physical walking result.
Uses archived leg membership and current saved world solids; no native solver.
"""
import hashlib,itertools,json,time,zipfile
from pathlib import Path
from current_leg_harness_context import context,W,Part,ROOT,OUT

STAGES=('Hip','Knee','Ankle')

def run():
    tick=time.monotonic();reader,pins,targets,retained=context()
    fp=OUT/'leg-stations-plan.json';bp=OUT/'bank-input-plan.json'
    af=ROOT/'hardware/simulation/p0/e6-leg-compatibility.json'
    archive=ROOT/'hardware/simulation/v35/inputs.zip'
    axes=json.loads(af.read_text());plan=json.loads(fp.read_text());bank=json.loads(bp.read_text())
    pins.update((Path(__file__),af,archive,fp,bp))
    assert axes['saved_leg_axes_and_foot_proxies_compatible'] and not axes['errors']
    # Historical current-assembly pointer is intentionally superseded by CP2.
    # Pin the immutable E6/archived leg sources, not that unrelated live pointer.
    for n in ('hardware/cad/assembly/RobotCatNarrowRimEars.FCStd',
              'hardware/simulation/v35/inputs.zip',
              'hardware/skorupa/v35/Kot_v35_ZASILANIE_AUX.FCStd'):
        assert W.sha(ROOT/n)==axes['source_files_sha256'][n],n
        pins.add(ROOT/n)
    with zipfile.ZipFile(archive) as z:geometry=json.loads(z.read('geometry.json'))
    membership={c:{s:[] for s in STAGES} for c in ('FL','FR','RL','RR')}
    for row in geometry['components']:
        if row['stage'].startswith('Motion_'):
            _,code,stage=row['stage'].split('_')
            name='P0_'+row['name']
            assert name in targets,(name,'Missing current leg member')
            assert targets[name].isValid() and targets[name].Solids,name
            membership[code][stage].append(name)
    assert all([len(m[s]) for s in STAGES]==[9,14,4] for m in membership.values())
    solids={n:targets[n] for n in plan['stations']}
    curves={n:(W.makewire(r['parts']),r['radius_mm']) for n,r in
            {**plan['routes'],**bank['routes']}.items()}
    report=dict(status='PENDING',selected=False,W5_complete=False,physical_pass=False,
      angle_grid_degrees=[-15,0,15],approved_motion_limits=False,
      continuous_sweep_verified=False,poses=0,pairs=0,contacts=[],errors=[],
      native_parts_changed=0,
      scope='All12candidate receiving cases and4output/12input guides vs current saved27leg solids per leg. Project sampled packaging allowance only; no factory loom flexibility or retained robot self-motion qualification.')
    for code,groups in membership.items():
        axis={r['stage']:r for r in axes['axes'] if r['code']==code}
        for angles in itertools.product(report['angle_grid_degrees'],repeat=3):
            transform=W.A.Placement();report['poses']+=1
            for stage,angle in zip(STAGES,angles):
                a=axis[stage];p=W.A.Vector(*a['pivot_mm']);rot=W.A.Rotation(W.A.Vector(*a['axis']),angle)
                transform=transform*W.A.Placement(p-rot.multVec(p),rot)
                for name in groups[stage]:
                    shape=targets[name].copy();shape.Placement=transform*shape.Placement
                    assert shape.isValid(),name
                    for n,s in solids.items():
                        if not W.near(s,shape,0):continue
                        report['pairs']+=1;v=s.common(shape).Volume
                        if v>1e-5:report['contacts'].append(dict(a=n,b=name,leg=code,angles=angles,volume_mm3=v))
                    for n,(c,rr) in curves.items():
                        if not W.near(c,shape,rr):continue
                        report['pairs']+=1;d,pts,_=c.distToShape(shape)
                        if d<rr-1e-4:report['contacts'].append(dict(a=n,b=name,leg=code,angles=angles,
                          distance_mm=d,required_mm=rr,witness_mm=[list(v) for v in pts[0]] if pts else None))
            print('Leg gallery',code,angles,'contacts',len(report['contacts']),flush=True)
    report.update(status='SAMPLED_PROJECT_LEG_GALLERY_CLEAR_NOT_APPROVED_SWEEP' if not report['contacts'] else 'REJECTED_PROJECT_LEG_GALLERY_MOTION',
      worker_seconds=round(time.monotonic()-tick,3),membership=membership,
      source_sha256={**reader.hashes,**{p.relative_to(ROOT).as_posix():W.sha(p) for p in pins}})
    (OUT/'leg-gallery-motion-checks.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:report[k] for k in ('status','poses','pairs','worker_seconds')}),flush=True)

if __name__=='__main__':run()
