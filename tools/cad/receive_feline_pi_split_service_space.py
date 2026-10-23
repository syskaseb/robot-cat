"""Necessary detachable-Pi service space; cable parking/retention still OPEN.

This is NOT a native mount or a completed N01. The solid cylindrical coupler
is a reservation for a split saddle, not filled printable material around a rod.
"""
import hashlib,json,time,zipfile
import Part
from pathlib import Path
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json

DEST=OUT/'n01-Pi-split-service-space.json'

def independent(shape):
    # OCC Boolean/prism operations can alter shared child topology even when
    # the Python wrapper looks distinct. Roundtrip isolates ownership.
    result=Part.Shape();result.importBrepFromString(shape.exportBrepToString())
    assert result.isValid()
    return result

def receive(original,fixed,mobile,mobile_sweep,budgets,static,heads,motion,
            pi_lift,mobile_lift,fixed_lift,key_after_lift,key_sweep,recipe,rejected):
    tick=time.monotonic();assert not DEST.exists()
    assert len(fixed.Solids)==len(mobile.Solids)==1 and fixed.isValid() and mobile.isValid()
    assert independent(fixed).cut(independent(original)).Volume+independent(mobile).cut(independent(original)).Volume<1e-5
    assert independent(fixed).common(independent(mobile)).Volume<1e-7
    removed_shape=independent(original).cut(Part.makeCompound([independent(fixed),independent(mobile)]))
    assert removed_shape.isValid()
    removed=removed_shape.Volume
    assert abs(removed-3.141592653589793*1.5**2*.25)<1e-5
    checks={k:v for k,v in static['checks'].items() if ':head' not in k}
    checks.update(heads['checks'])
    assert not static['errors'] and not heads['errors'] and all(v['ok'] for v in checks.values())
    assert motion['status']=='SOURCE_UNIT_SAMPLE36_MOTION_RECEIVED'
    assert set(motion['completed'])==set(budgets) and all(v['ok'] for v in motion['checks'].values())
    # Pi and the upper carrier are one moving group. Old internal pairs are
    # replaced by every moving Pi part vs the actually retained lower root.
    external_pi={k:v for k,v in pi_lift['checks'].items() if not k.endswith('|SharedPi:Carrier')}
    assert not pi_lift['errors'] and all(v['ok'] for v in external_pi.values())
    assert not fixed_lift['errors'] and not fixed_lift['failures']
    assert not key_after_lift['errors'] and not key_after_lift['failures']
    upper=dict(mobile_lift['checks']);mate=upper.pop('PiCarrierLift40|PiRootRetained')
    assert not mobile_lift['errors'] and all(v['ok'] for v in upper.values())
    assert mate['gap_mm']>=.25-1e-6 and independent(mobile_sweep).common(independent(fixed)).Volume<1e-7
    assert independent(key_sweep).common(independent(fixed)).Volume<1e-7 and key_sweep.distToShape(fixed)[0]>=.5
    payload={'ReferenceOriginalCarrier':original,'PiRootRetained':fixed,'PiCarrierRemovable':mobile,
             'PiCarrierLift40Sweep':mobile_sweep,**budgets}
    archive=DEST.with_suffix('.breps.zip');geometry=[]
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
        for name,s in payload.items():
            assert s.isValid() and s.Solids
            data=s.exportBrepToString().encode();entry=str(len(geometry))+'.brep';z.writestr(entry,data)
            geometry.append(dict(name=name,entry=entry,sha256=hashlib.sha256(data).hexdigest(),
                kind='planning_reservation' if name.startswith('PiSplit:') else 'planning_material_or_sweep'))
    paths=[Path(__file__),OUT/'n01-W049-joint-corridor-received.json',OUT/'n01-Pi-root-access-plan.json',
           OUT/'n01-Pi-split-coupler-sampled36.json',OUT/'n01-shared-Pi-carrier-r3-core-received.json',
           ROOT/'hardware/reference/cable-ties/t18i-111-02370/head-envelope.json']
    result=dict(status='DETACHABLE_PI_NECESSARY_SERVICE_GEOMETRY_NOT_CABLE_PARKING',
        recipe=recipe,static_budget_checks=checks,pi_external_lift_checks=external_pi,
        upper_carrier_external_checks=upper,retained_root_checks=fixed_lift['checks'],
        key_vs_lifted_unit=key_after_lift['checks'],intended_split_initial_gap_mm=mate['gap_mm'],
        split_sweep_common_mm3=0,removed_rod_mm3=removed,
        global_volume_subtraction_mm3=original.Volume-fixed.Volume-mobile.Volume,
        key_sweep_retained_root_gap_mm=key_sweep.distToShape(fixed)[0],
        excluded_cables_requiring_explicit_release_and_parking=pi_lift['removal_hypotheses'],
        fixed_P0_PWM_and_normal_PCB_poses_unchanged=True,selected=False,
        complete_service_received=False,N01_complete=False,physical_pass=False,
        open=['Constructive split-saddle retention and installed release/tool access; space is not clamp strength',
              'Pi GPIO/power/USB full-length release and parking with remote ends included',
              'Five F_PI top-access wire groups W027/W020/W031/W033/W035 release and parking',
              'S0 actual key mechanism/off-position and delivered F_PI cap fit',
              'Native module/mount manufacture and physical load/fit tests belong to later gates'],
        rejected_topologies=rejected,geometry=geometry,bundle=archive.relative_to(ROOT).as_posix(),
        bundle_sha256=sha(archive),source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in paths},
        measured_seconds=dict(static_nominal=static['worker_seconds'],conservative_heads=heads['worker_seconds'],
            sampled36=motion['worker_seconds'],Pi_lift=pi_lift['worker_seconds'],carrier_lift_queries=mobile_lift['worker_seconds'],
            retained_root=fixed_lift['worker_seconds'],key_after_lift=key_after_lift['worker_seconds']),
        worker_seconds=round(time.monotonic()-tick,3))
    save_json(DEST,result);return result
