"""Current USB-flat-ended carrier, not superseded fused carrier snapshots."""
import time,json
from pathlib import Path
import FreeCAD as A
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from receive_feline_pi_split_service_space import independent
from feline_solid_distance import distance,bbox_lower_bound
from feline_atomic_save import save_json


def certify(gap_at,stop=40.,minimum=0.,resolution=.025):
    """1-Lipschitz gap under translation; a failed bound is not a collision."""
    cache={};pending=[(0.,stop)];accepted=[];unresolved=[]
    def gap(z):
        if z not in cache:cache[z]=gap_at(z)
        return cache[z]
    while pending:
        lo,hi=pending.pop();a,b=gap(lo),gap(hi)
        bound=min(a,b)-(hi-lo)/2
        if bound>minimum+1e-6:accepted.append((lo,hi,bound));continue
        if min(a,b)<=minimum+1e-7 or hi-lo<=resolution:
            unresolved.append((lo,hi,a,b));continue
        mid=(lo+hi)/2;pending.extend(((lo,mid),(mid,hi)))
    return dict(continuous_clear=not unresolved,minimum_required_mm=minimum,
                certified_lower_bound_mm=min((r[2] for r in accepted),default=None),
                certified_intervals=accepted,unresolved_intervals=unresolved,
                sampled_gaps_mm=sorted(cache.items()))


def run(scene,usb_parts,cradle_parts):
    tick=time.monotonic()
    movers={'current_carrier':usb_parts['fixed_beam'],'collar':cradle_parts['collar']}
    fixed={n:s for n,s in scene.items() if n.startswith('PiGPIO:')}
    fixed['PiBudget:GPIO1992OccupiedHousing']=scene['PiBudget:GPIO1992OccupiedHousing']
    assert len(fixed)==6
    for s in [*movers.values(),*fixed.values()]:assert s.isValid() and s.Solids and not s.check(True)
    checks={}
    for name,original in movers.items():
        for target,b in fixed.items():
            def gap(z):
                a=independent(original);a.translate(A.Vector(0,0,z))
                lower=bbox_lower_bound(a.BoundBox,b.BoundBox)
                return lower if lower>2 else distance(a,b)
            # Own wire channels: certify no material intersection during release;
            # inherited nominal0.15mm jacket fit remains a delivery/print gate.
            minimum=0. if target.startswith('PiGPIO:') else 1.25
            checks[name+'|'+target]=certify(gap,minimum=minimum)
            print('CURRENT_RELEASE',name,target,checks[name+'|'+target]['continuous_clear'],flush=True)
    paths=[OUT/'n01-service-dependency-decision-20261023.json',OUT/'n01-Pi-open-cradle-joint.json',
           OUT/'W009-W069-harness-corridor/recovered-context.json',Path(__file__)]
    result=dict(status='CURRENT_CARRIER_GPIO_DIFFERENTIAL_RELEASE',checks=checks,
                continuous_changed_pairs_clear=all(r['continuous_clear'] for r in checks.values()),
                current_carrier_source='removable_USB_planning_witness.fixed_beam',
                source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in paths},
                removed_before_motion=['GPIO4/H1 ties','USB removable restraint','cradle lid'],
                scope='Only carrier+collar versus stationary5GPIO prefixes+housing; not whole robot',
                open=['Complete GPIO housing counterhold/access','W009/USB/power prerequisites',
                      'Full moving group and retained root/cradle combination','276 missing scene actors'],
                worker_seconds=round(time.monotonic()-tick,3),N01_complete=False,physical_pass=False)
    save_json(OUT/'n01-current-carrier-GPIO-release-20261024.json',result)
    return result


def receive_mounts(result,mount_checks,mount_seconds,contacts,pi_planes,counterhold,lower_access):
    assert len(mount_checks)==4 and all(r['continuous_clear'] for r in mount_checks.values())
    assert all(r['strict_valid'] and r['common_mm3']>1e-4 for r in contacts.values())
    exceptions={k:v for k,v in pi_planes.items() if v<1.25-1e-6}
    assert set(exceptions)=={
        'PiBudget:GPIO_header|PiBudget:GPIO1992OccupiedHousing',
        'PiBudget:UnlabelledTopComponentsBudget|PiBudget:GPIO1992OccupiedHousing'}
    result.update(retained_mount_continuous_checks=mount_checks,
                  printed_joint_intersection_checks=contacts,
                  pi_positive_axis_separation_mm=pi_planes,
                  pi_mating_reservation_exceptions=exceptions,
                  mount_worker_seconds=mount_seconds,
                  counterhold_upper_budget_probe=counterhold,
                  counterhold_lower_straight_entry_probe=lower_access,
                  counterhold_access_received=False,
                  source_script_extended_only_to_record_additional_checks=True)
    result['source_sha256'][Path(__file__).relative_to(ROOT).as_posix()]=sha(Path(__file__))
    result['open']=['Counterhold access: upper pad budget and straight Y entry not received',
                    'W009/USB/power prerequisites and whole moving-group integration',
                    'Full123portions/246ends and missing scene actors']
    result['next_strategy']='Before adding a permanent long counterhold bracket, evaluate Pi lift with GPIO mated and five full flexible signal leads; unplug only after access above the assembly. No assumption that an existing route length is spare cable.'
    save_json(OUT/'n01-current-carrier-GPIO-release-20261024.json',result)
    return result
