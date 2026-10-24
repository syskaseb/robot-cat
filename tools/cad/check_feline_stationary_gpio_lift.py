"""Differential test: Pi rises, existing GPIO housing/wires stay stationary.

No layout edits, no replacement of prior external-carrier checks. Generic
component reservations and intended pin engagement are reported separately.
"""
import json,time
import FreeCAD as A
from plan_feline_layout import OUT
from check_main_p0_placement import sha
from receive_feline_pi_split_service_space import independent
from feline_solid_distance import bbox_lower_bound,distance
from feline_atomic_save import save_json
from pathlib import Path


def run(scene,metadata,split,split_doc):
    tick=time.monotonic()
    for name in ('ReferenceOriginalCarrier','PiCarrierRemovable','PiCarrierLift40Sweep'):
        assert not split[name].check(True), 'Strict BRep failure: '+name
    fixed={n:s for n,s in scene.items() if n.startswith(('PiGPIO:', 'PiGrip:GPIO4:', 'PiGrip:H1:'))}
    fixed['PiBudget:GPIO1992OccupiedHousing']=scene['PiBudget:GPIO1992OccupiedHousing']
    names={k.split('|')[0] for k in split_doc['pi_external_lift_checks']}
    names-=set(fixed)|{'PiBudget:RetainedK1474Boot'} # already unplugged at existing adapter
    movers={n:scene[n] for n in sorted(names)}
    movers['PiCarrierRemovable']=split['PiCarrierRemovable']
    checks={};exceptions={};errors={}
    for name,base in movers.items():
        for target,b in fixed.items():
            key=name+'|'+target
            samples=[]
            try:
                assert base.isValid() and b.isValid() and base.Solids and b.Solids
                for z in range(11):
                    a=independent(base);a.translate(A.Vector(0,0,z))
                    lower=bbox_lower_bound(a.BoundBox,b.BoundBox)
                    gap=lower if lower>=1.75 else distance(a,b)
                    row={'z_mm':z,'gap_mm':gap,'method':'separated_bounds_lower_bound' if lower>=1.75 else 'solid_distance'}
                    if gap<1e-7:
                        overlap=a.common(independent(b));assert overlap.isValid()
                        row['common_mm3']=overlap.Volume
                    samples.append(row)
                bound=min(r['gap_mm'] for r in samples)-.5
                value=dict(samples=samples,continuous_gap_lower_bound_mm=bound,
                           minimum_mm=1.25,clear=bound>=1.25-1e-6)
                if target=='PiBudget:GPIO1992OccupiedHousing' and name in (
                    'PiBudget:GPIO_header','PiBudget:UnlabelledTopComponentsBudget'):
                    value['reason']='Intended pin engagement or generic occupied component reservation; not real material contact proof'
                    exceptions[key]=value
                else:checks[key]=value
            except Exception as exc:errors[key]=str(exc)
        print('CHECKED',name,flush=True)
    result=dict(status='DIFFERENTIAL_STATIONARY_GPIO_LIFT_ONLY',
        moving=list(movers),stationary=list(fixed),translation_mm=[0,0,10],
        checks=checks,mating_or_generic_reservations=exceptions,errors=errors,
        failures=[k for k,r in checks.items() if not r['clear']],
        continuous_bound_method='1mm spaced samples; subtract0.5mm nearest-sample translation distance',
        source_sha256={},
        script_sha256=sha(Path(__file__)),worker_seconds=round(time.monotonic()-tick,3),
        open=['Housing needs counterhold/support during withdrawal',
              'Reuse prior external lift proof only for unchanged movers and fixed actors',
              'USB whole flex and W009 parking still required; this is not whole service approval'],
        N01_complete=False,selected_geometry_changed=False,physical_pass=False)
    for filename in ('n01-Pi-split-service-space.json','W009-W069-harness-corridor/recovered-context.json'):
        result['source_sha256'][filename]=sha(OUT/filename)
    save_json(OUT/'n01-stationary-GPIO-Pi-lift-20261024.json',result)
    print('RESULT',result['worker_seconds'],result['failures'],errors,flush=True)
    return result


def board_only(scene,split,previous):
    """Rejection-only probe after removing Pi fasteners; carrier does not rise."""
    tick=time.monotonic();checks={};errors={}
    names=[n for n in previous['moving'] if n.startswith('PiBudget:') or n=='Ref_Material_Pi4NominalPCB_0_0']
    carrier=split['ReferenceOriginalCarrier']
    assert not carrier.check(True), 'Strict BRep failure: original carrier'
    for name in names:
        samples=[]
        try:
            for z in (0,.5,1,2,5,7,10,40):
                a=independent(scene[name]);a.translate(A.Vector(0,0,z))
                gap=distance(a,carrier)
                row=dict(z_mm=z,gap_mm=gap)
                if gap<1e-7:
                    c=a.common(independent(carrier));assert c.isValid()
                    row['common_mm3']=c.Volume
                samples.append(row)
            checks[name]=samples
        except Exception as exc:errors[name]=str(exc)
        print('BOARD_ONLY',name,flush=True)
    result=dict(status='BOARD_ONLY_LIFT_SAMPLED_REJECTION_PROBE',checks=checks,errors=errors,
        inherited_GPIO_checks={k:v for k,v in previous['checks'].items() if k.split('|')[0] in names},
        inherited_GPIO_reservations=previous['mating_or_generic_reservations'],
        assumptions=['Pi mounting screws removed before lift; access needs constructive verification',
                     'Original complete carrier and GPIO grips remain fixed',
                     'Power K1474 unplugged at adapter; USB flex remains conditional'],
        source_sha256={'n01-stationary-GPIO-Pi-lift-20261024.json':sha(OUT/'n01-stationary-GPIO-Pi-lift-20261024.json')},
        script_sha256=sha(Path(__file__)),worker_seconds=round(time.monotonic()-tick,3),
        continuous_path_qualified=False,N01_complete=False,physical_pass=False)
    save_json(OUT/'n01-board-only-GPIO-lift-20261024.json',result)
    print('BOARD_RESULT',result['worker_seconds'],errors,flush=True)
    return result


def invalidate_probes(split):
    """Keep numerical diagnostics, but revoke eligibility when strict BRep fails."""
    validation={}
    for name in ('ReferenceOriginalCarrier','PiCarrierRemovable','PiCarrierLift40Sweep'):
        try:
            issues=split[name].check(True)
            validation[name]=dict(strict_valid=not issues,issues=str(issues))
        except Exception as exc:
            validation[name]=dict(strict_valid=False,issues=str(exc))
    assert not all(v['strict_valid'] for v in validation.values())
    for filename in ('n01-stationary-GPIO-Pi-lift-20261024.json','n01-board-only-GPIO-lift-20261024.json'):
        path=OUT/filename;result=json.loads(path.read_text())
        result['original_status']=result['status']
        result['status']='DIAGNOSTIC_ONLY_STRICT_CARRIER_BREP_HOLD'
        result['strict_source_validation']=validation
        result['numerical_gaps_and_overlaps_are_not_qualified_geometry_evidence']=True
        result['whole_service_approved']=False
        result['source_validation_script_sha256']=sha(Path(__file__))
        if 'n01-stationary-GPIO-Pi-lift-20261024.json' in result.get('source_sha256',{}):
            result['source_sha256']['n01-stationary-GPIO-Pi-lift-20261024.json']=sha(OUT/'n01-stationary-GPIO-Pi-lift-20261024.json')
        save_json(path,result)
    return validation


def receive_released_ties(scene,split,previous,sweep_checks,sweep_seconds):
    """Receive only changed GPIO interface, reusing the saved continuous sweep."""
    from check_main_p0_placement import ROOT
    expected={n for n in previous['stationary'] if not n.startswith('PiGrip:')}
    assert set(sweep_checks)==expected and len(expected)==6
    assert not split['PiCarrierLift40Sweep'].check(True)
    assert all(r['gap_mm']>=.15-1e-6 for r in sweep_checks.values())
    extension={};near_nuts={}
    for name in previous['moving']:
        if name=='PiCarrierRemovable':continue
        a=scene[name].BoundBox
        for target in expected:
            b=scene[target].BoundBox
            xy=max(0,a.XMin-b.XMax,b.XMin-a.XMax,a.YMin-b.YMax,b.YMin-a.YMax)
            extension[name+'|'+target]=max(xy,a.ZMin+10-b.ZMax)
            assert extension[name+'|'+target]>=1.25-1e-6
            key=name+'|'+target
            if key in previous['checks'] and not previous['checks'][key]['clear']:
                assert 'Nut_' in name and xy>=1.25-1e-6
                near_nuts[key]=dict(continuous_XY_separation_mm=xy)
    files=['n01-stationary-GPIO-Pi-lift-20261024.json',
           'n01-board-only-GPIO-lift-20261024.json','n01-Pi-split-service-space.json']
    result=dict(status='GPIO_RELEASED_TIES_NECESSARY_NOMINAL_SPACE_RECEIVED',
        sequence=['Isolate source; open access and support Pi/carrier',
                  'Release and remove GPIO4/H1 ties completely; retain all wire identities',
                  'Counterhold complete GPIO housing, never pull individual wires',
                  'After power/USB/W009 prerequisites and cradle lid release, raise Pi+carrier7mm off GPIO pins',
                  'Keep all five wire paths stationary while carrier proceeds to40mm'],
        continuous_carrier_sweep_checks=sweep_checks,
        inherited_own_channel_clearance_mm=.15,clearance_basis='Existing feline_shared_pi_carrier.saddle nominal fit, not newly relaxed spacing',
        full_lift_extension_lower_bounds_mm=extension,nut_XY_separation=near_nuts,
        first10mm_source=files[0],mating_pin_exception=previous['mating_or_generic_reservations'],
        source_sha256={f:sha(OUT/f) for f in files},script_sha256=sha(Path(__file__)),
        channel_source_sha256=sha(ROOT/'tools/cad/feline_shared_pi_carrier.py'),
        changed_interface_sweep_seconds=sweep_seconds,
        open=['Constructive counterhold and tie cutting/removal access',
              'Complete W009 parking, USB flex and power parking prerequisites',
              '276 missing scene actors and whole N01 reconciliation',
              'Delivered jacket size/print fit at nominal0.15mm channel gap'],
        normal_poses_changed=False,wire_paths_changed=False,selected_geometry_changed=False,
        whole_service_approved=False,N01_complete=False,physical_pass=False)
    save_json(OUT/'n01-GPIO-release-order-20261024.json',result)
    return result
