"""A single conditional 12-factory-cable/36-core termination recipe.

This independent W5 preparation does not select incomplete geometry, invent
delivered conductor data, duplicate fuse-local V stock, or qualify movement.
"""
from datetime import datetime,timezone
from pathlib import Path
import json,sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import save,sha
OUT=ROOT/'hardware/electronics/full-cat/w5-leg-end-preparation-r1'


def build(mapping,bank,process,cable):
    output_ends={row['id']:row for row in bank['ends'] if row['id'].endswith('.out')}
    looms=[];seen=set()
    for row in mapping['looms']:
        ends=[]
        for role in ('D','G','V'):
            end=row['electrical'][role]
            assert end['wire'] not in seen;seen.add(end['wire'])
            recipe=dict(wire=end['wire'],servo_contact=end['servo_end'],body_contact=end['body_end'],
                factory_contact_retained=True,colour_is_not_pin_identification=True,
                factory_plug_cavity_number=None,actual_cut_mm=None,far_end_cut_after_dry_fit=True)
            if role=='V':
                selected=output_ends[end['body_end']]
                assert selected['wire_id']==end['wire'] and end['body_end']=='F_'+row['loom']+'.out'
                recipe.update(body_terminal=selected['terminal'],
                    copper_range_mm2=process['catalog_part_copper_range_mm2'],
                    strip_nominal_mm=process['single_wire_strip_nominal_mm'],
                    strip_tolerance_mm=process['single_wire_strip_tolerance_mm'],
                    hand_tool=process['tool'],factory_core_actual_mm2=None,
                    max_insulation_guide_clearance_mm=process['max_insulation_guide_clearance_mm'],
                    insulation_guide_is_not_a_crimp_grip_rating=True,
                    existing_selected_bank_exit_mm=selected['local_exit_mm'],
                    local_bank_wire_is_part_of_this_same_core=True,
                    additional_local_wire_or_terminal_quantity=0)
            else:
                recipe.update(body_terminal='WAGO221-415',strip_nominal_mm=11,
                    copper_range_mm2=[.14,4],untinned=True,ferrule=False,
                    one_core_per_cage=True,factory_core_actual_mm2=None)
            ends.append(recipe)
        looms.append(dict(loom=row['loom'],physical_leg=row['physical_leg'],
            source_pcb=row['pcb'],one_factory_cable=True,factory_keyed_plugs_retained=1,
            far_factory_plugs_removed_after_fit=1,second_servo_socket='NC',
            nominal_factory_length_mm=cable['manufacturer_nominal_length_mm'],
            completed_full_length_and_restraints=False,ends=ends))
    assert len(looms)==12 and len(seen)==36
    return dict(status='COMPLETE_36_CORE_END_RECIPE_ROUTES_AND_DELIVERY_CONDITIONAL',
        looms=looms,continuous_cables=12,electrical_core_roles=36,logical_ends=72,
        body_connections=dict(WAGO221415=24,TE25201842=12),
        factory_cavity_assignment_known=False,new_splices=0,new_fuse_bypass_paths=0,
        candidate_purchase=dict(sku=cable['manufacturer_sku'],packs=2,cables_per_pack=6,
            cables=12,spare_cables=0,selected=False,
            no_double_count='Replace twelve incomplete leg loom roles, not twelve additional bank-local V cables; existing BUS34171 cable stock stays distinct.'),
        assembly=[
            'Unpowered: label physical leg and drive number; fit the single keyed factory plug, leave second socket NC.',
            'Route the intact three-core cable on the specified carriers, retaining service loops and insulated grip seats. Do not insert a splice at the virtual breakout.',
            'Dry-fit through the full designed joint range before cutting the far factory plug. Identify D/G/V by connector diagram and continuity, never by assumed colours.',
            'Separate only the body-side length needed for the three destinations; label each core wire ID and exact logical port at both ends.',
            'Cut D/G to the final unpowered fit and strip11mm for one untinned core per WAGO221415 cage. Keep live copper entirely inside the closed cage.',
            'Keep V continuous through its selected bank exit. Crimp one TE2-520184-2 using the listed supplier process only if actual Cu/insulation fit; strip7.14+/-0.38mm, no doubling, tinning or removed strands.',
            'Insulation-only restraints carry mechanical load, not the plug, bare core or terminal. Replace cut service ties with the same selected type.',
            'Phase2: inspect each crimp, continuity and absence of fuse bypass; validate movement and absence of pull/chafe before hardware power.'
        ],
        delivery_conditions=['Exact factory copper/insulation and applicable TE tooling row must be verified; catalogue mm2 labels are not a delivered measurement.',
            'Actual useful length, factory plug envelope and dynamic bend radius are unknown.900mm is nominal supplier length, not a complete moving-route approval.'],
        selected=False,motion_qualified=False,W5_complete=False,physical_pass=False)


def main():
    started=datetime.now(timezone.utc)
    assert not (OUT/'interface.json').exists(),'Preserve completed recipe'
    inputs={
        'mapping':ROOT/'hardware/electronics/full-cat/w5-leg-source-map-r1/interface.json',
        'bank':ROOT/'hardware/electronics/full-cat/servo-fuse-bank-electrical-r2/interface.json',
        'process':ROOT/'hardware/reference/leg-cable-2026-10-04/TE-output-process.json',
        'cable':ROOT/'hardware/reference/leg-cable-2026-10-04/facts.json',
    }
    value=build(**{key:json.loads(path.read_text(encoding='utf-8')) for key,path in inputs.items()})
    inputs['spec']=ROOT/'hardware/reference/servo-holder-p0-2026-09-24/114-2123-current-TE.pdf'
    inputs['script']=Path(__file__)
    finished=datetime.now(timezone.utc)
    value.update(source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in inputs.values()},
        started_utc=started.isoformat(),finished_utc=finished.isoformat(),
        worker_wall_seconds=(finished-started).total_seconds())
    OUT.mkdir(parents=True,exist_ok=True);save(OUT/'interface.json',value)
    print('LEG_END_RECIPE',value['continuous_cables'],value['electrical_core_roles'],value['body_connections'],flush=True)


if __name__=='__main__':main()
