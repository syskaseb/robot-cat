"""Complete replacement ownership and structural extents; no geometry PASS.

Read the original four-channel constructor, not only its first failed part.
Every retired physical/reservation function has an explicit successor or hold.
"""
import hashlib
import json
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure'
PSYS_OWNED={'P_SYS_CommonRelief':('frame_reservation','UpperFrame'),
            'PSYSTie':('tie_reservation','PSYSTie'),
            'PSYSTieHead':('tie_reservation','PSYSTie')}


def own_reservation(name,meta):
    if name not in PSYS_OWNED:return False
    assert (meta.get('kind'),meta.get('owner'))==PSYS_OWNED[name],(name,meta)
    return True


def main():
    tick=time.monotonic()
    files=[OUT/n for n in ('n01-common-restraint-world-probe.json',
        'n01-common-restraint-material-r2.json','n01-flat-station-architecture.json',
        'n01-whole-constraint-map.json','n01-central-spine-power-plan-r4.json')]
    old,retention,flat,world,power=[json.loads(p.read_text()) for p in files]
    rows={r['name']:r for r in old['parts']}
    assert set(n for n in rows if 'psys' in n.lower() or 'p_sys' in n.lower())==set(PSYS_OWNED)
    assert all(own_reservation(n,rows[n]) for n in PSYS_OWNED)
    station=next(s for s in flat['stations'] if s['ref']=='P_SYS')
    ports={p['wire']:p['endpoint'] for p in station['ports']}
    assert set(ports)=={'W043','W066','W067','W068'}
    route=next(r for r in power['routes'] if r['wire']=='W043')
    assert route['radius_mm']==1.7 and route['parts'][-1]['length_mm']>=9
    sides=[r for r in world['parts'] if r['name'] in
        ('Ref_Material_P0_SideLeft22_0_0','Ref_Material_P0_SideRight22_0_0')]
    assert len(sides)==2
    end=min(r['world_bounds_mm'][1][0] for r in sides)
    assert abs(end-127)<1e-5
    result=dict(status='COMPLETE_OWNER_CONTRACT_FRAME_ROOTS_OPEN',selected=False,
        N01_complete=False,physical_pass=False,
        source_sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in files+[Path(__file__),ROOT/'tools/cad/plan_feline_common_restraints.py']},
        complete_P_SYS_retired_set=[rows[n] for n in sorted(PSYS_OWNED)],
        successor=dict(cap='One four-channel removable cap',band='One complete new band',
            head='One full side head',support='Whole case floor and independent clamp stem',
            occupied_jackets=ports,protected_W043=dict(radius_mm=1.7,grip_mm=9,
                last_straight_mm=route['parts'][-1]['length_mm'],whole_route_unchanged=True)),
        other19_station_case_and_REV3_prefixes_replaced_together=True,
        other_station_common_comb_tie_heads_in_original_constructor=[],
        retained_function_groups=['MAIN comb/tie/head','4 nine-wire cuffs/ties/heads',
            '8 inline joint retainers','24 factory/custom seats and ties',
            '4MTA source body bands','all purchased cases and bank source identities'],
        retained_root_dependencies=retention['root_unions'],
        root_dependency_policy='Retained cuff/MAIN functions require replacement shared roots; retirement of a scaffold does not approve floating retained children.',
        carrier_extent_basis=dict(retained_P0_side_records=sides,
            rear_X_mm=end,fore_X_mm=-126,root_pier_must_overlap_finite_rail=True,
            tail_cosmetic_section_X158_is_not_structural_anchor=True,
            print_split_required=True,split_X_mm=45,
            print_segment_X_lengths_mm=[171,82],margin_to256_without_joint_mm=[85,174]),
        frame_root_holds=['Actual four clamp seats and bolt stacks must be retained/reconnected',
            'Cross-ties to outboard rails plus driver access not yet received',
            'All retained cuff/MAIN/bank dependencies must have positive complete load paths',
            'Split joint fasteners and PETG stiffness/creep remain unqualified'],
        previous_R2_receipt='5f2be86c: full four-core cap mate received; old own PSYSTie remained; rails at cosmetic tail taper fail actual wall gap2.8607/3.25',
        worker_seconds=round(time.monotonic()-tick,6))
    dest=OUT/'n01-flat20-owner-contract.json'
    assert not dest.exists(),'Receive existing contract rather than duplicate it'
    dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=result['status'],retired=list(PSYS_OWNED),ports=len(ports),seconds=result['worker_seconds'])))


if __name__=='__main__':main()
