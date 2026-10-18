"""Typed source radii for ALL occupied WAGO ports; no new component selection.

Keep inherited nominal/default recipes visibly provisional. An unidentified
radius retains the old conservative budget, never a guessed smaller value.
Logical endpoint and wire identity must BOTH agree before importing a recipe.
"""
import hashlib
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype'
OUT = BASE / 'feline-enclosure'


def wire_identity(value):
    # Only the two explicitly documented accounting suffixes are normalized.
    return value.removesuffix('/custom').removesuffix('.source')


def compose():
    tick = time.monotonic()
    files = dict(ports=OUT/'n01-twenty-wago-port-contract.json',
        packet=OUT/'n01-current-endpoint-packet-r3.json',
        lands=OUT/'n01-all-current-first-lands.json',
        specifications=OUT/'prefix-allocation.json',
        common=BASE/'body-harness-checkpoint/u1-common-wiring-plan.json',
        aux=BASE/'aux-wiring-checkpoint/whole-layout-plan.json',
        tail=BASE/'tail-wiring-checkpoint/selection.json',
        pwm=BASE/'pwm-branch-checkpoint/selection.json')
    data = {k:json.loads(p.read_text()) for k,p in files.items()}
    lands = {r['id']:r for r in data['lands']['land_recipes']}
    specs = {r['id']:r for r in data['specifications']['specifications']}
    ports = []
    for station in data['ports']['stations']:
        for port in station['occupied_ports']:
            wire = wire_identity(port['wire'])
            matches = [e for e in data['packet']['endpoints']
                if e['role']==port['endpoint'] and e['wire']==wire]
            assert len(matches)<=1, (port['endpoint'], matches)
            radius = None; basis = None; source_id = None; bend_radius = 12.4
            inherited_default = False
            if matches and matches[0]['id'] in lands:
                source_id = matches[0]['id']; radius = lands[source_id]['radius_mm']
                basis = 'lands'; inherited_default = source_id not in specs
            elif wire in data['common']['routes']:
                recipe = data['common']['routes'][wire]
                ends = [e for e in recipe['ends'].values()
                    if e['physical_terminal']==port['endpoint']]
                assert len(ends)==1, (wire,port['endpoint'])
                radius = ends[0]['radius']; basis = 'common'; source_id = wire
                bend_radius = max(12.4, recipe['source']['project_radius_mm'])
            elif wire in data['aux']['routes']:
                radius=data['aux']['routes'][wire]['radius']; basis='aux'; source_id=wire
            elif wire=='XA01':
                radius=data['aux']['routes']['XA01_factory']['radius']; basis='aux'; source_id='XA01_factory'
            elif wire in data['tail']['routes']:
                radius=data['tail']['routes'][wire]['radius']; basis='tail'; source_id=wire
            elif port['wire']=='XP03.source':
                radius=data['pwm']['routes']['XP03_source']['radius']; basis='pwm'; source_id='XP03_source'
            elif wire in data['pwm']['routes']:
                radius=data['pwm']['routes'][wire]['radius']; basis='pwm'; source_id=wire
            known = radius is not None
            ports.append(dict(endpoint=port['endpoint'], wire=port['wire'],
                station=station['ref'], group=station['current_group'],
                physical_port=port['physical_port'], schematic_port=port['schematic_port'],
                nominal_project_radius_mm=radius,
                query_radius_mm=radius if known else 2.1,
                prior_uniform_reservation_radius_mm=2.1,
                source_file=files[basis].relative_to(ROOT).as_posix() if known else None,
                source_recipe_id=source_id,
                inherited_nominal_recipe_not_guaranteed_OD=inherited_default,
                unknown_retains_conservative_budget=not known,
                bend_radius_mm=bend_radius,
                supplier_datum_or_OD_guaranteed=False,
                current_route_grip_or_port_fit_qualified=False))
    assert len(ports)==86 and len({r['endpoint'] for r in ports})==86
    return dict(status='ALL86_TYPED_PROJECT_RADII_NOT_GEOMETRY_ACCEPTANCE',
        selected=False,N01_complete=False,physical_pass=False,
        current_parts_or_ECAD_changed=False,
        ports=ports,unknown_endpoints=[r['endpoint'] for r in ports if r['unknown_retains_conservative_budget']],
        nominal_source_ports=sum(r['nominal_project_radius_mm'] is not None for r in ports),
        inherited_default_recipe_ports=sum(r['inherited_nominal_recipe_not_guaranteed_OD'] for r in ports),
        source_sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (*files.values(),Path(__file__))},
        worker_seconds=round(time.monotonic()-tick,4))


if __name__=='__main__':
    result=compose()
    (OUT/'n01-station-profile-contract.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:result[k] for k in ('nominal_source_ports','unknown_endpoints','inherited_default_recipe_ports','worker_seconds')}))
