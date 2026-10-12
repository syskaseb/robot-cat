"""Reuse a received continuous sweep, but never silently remove its obstruction.

Both BUS conductors belong to one real factory cable. The withdrawal itself
does not need a new372pair calculation after those obstacles are absent.
Access to remove that cable is a separate open prerequisite, NOT a free pass.
"""
import json,time
from pathlib import Path
import plan_u1_socket_carrier as U


def derive(receipt):
    assert not receipt['errors'],'An erroneous old sweep cannot be reused'
    hits=receipt['contacts']+receipt['reservation_resolutions']
    assert hits and {q['b'] for q in hits}=={'W003'},'Different obstacle requires new shared plan'
    return dict(status='CONDITIONAL_SOCKET_EXTRACTION_ONLY_BUS_RELEASE_ACCESS_OPEN',selected=False,
        E1_complete=False,W5_complete=False,physical_pass=False,
        prior_unplug_free_hypothesis_rejected=True,
        no_external_wire_disconnects_required_for_adapter=False,
        conditional_retainer_and_adapter_lift_mm=receipt['service_lift_mm'],
        reused_pairs=receipt['pairs'],removed_obstacle_contacts=len(receipt['contacts']),
        removed_obstacle_reservations=len(receipt['reservation_resolutions']),
        new_geometry_pairs=0,
        geometry_condition='Entire W002/W003 factory cable removed from the service volume BEFORE touching U1. This is not proof that cable can already be removed.',
        cable_ends={'W002':['BUS.H5.D','D_FL.1'],'W003':['BUS.H5.G','G2.4']},
        loose_cable_interfaces=3,shared_cable_bands_to_release=1,
        sequence=[
          'Disconnect and remove battery/USB; no live service. Label W002 DATA and W003 interface GND, neither is a servo power feed.',
          'Support the BUS cable; open exactly D_FL.1 and G2.4 and protect the two stripped ends separately.',
          'Release its ONE insulation band and unplug the single keyed H5 housing, without pulling wires or retaining a V contact/wire.',
          'Move the disconnected entire cable to an insulated bench tray OUTSIDE the robot, not an invented connected parking pose.',
          'Only after the cable is absent: cut the TWO U1-retainer ties, collect cuttings, lift keyed bar/foam12mm, then populated adapter12mm.',
          'Reassemble reverse order with new ties; verify socket orientation, cable labels and unpowered continuity before any phase2 power.'
        ],
        unresolved_prerequisites=[
          'Actual tool/lever access at current D_FL.1 and G2.4',
          'H5 housing withdrawal and whole cable passage through the current native carrier; no assumption that the housing fits a bare-core slot',
          'Independent external U1 grips and whole fixed-wire insulation/selection',
          'Unpowered delivered connector fit, extraction force and solder inspection'
        ],
        evidence_limit='Existing clear stationary geometry retained; conditional sweep does not close common BUS release, E1 or full W5.')


def run():
    tick=time.monotonic();f=U.OUT/'u1-socket-service-checks.json';r=json.loads(f.read_text())
    for name,digest in r['source_sha256'].items():assert U.sha(U.ROOT/name)==digest,name
    p=derive(r);p['source_sha256']={f.relative_to(U.ROOT).as_posix():U.sha(f),
        Path(__file__).relative_to(U.ROOT).as_posix():U.sha(Path(__file__))}
    p['worker_seconds']=round(time.monotonic()-tick,4)
    (U.OUT/'u1-socket-service-sequence.json').write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:p[k] for k in ('status','reused_pairs','new_geometry_pairs','loose_cable_interfaces','worker_seconds')}))


if __name__=='__main__':run()
