"""Pin one complete local S0 prototype interface; R48 stays selected."""
from pathlib import Path
from datetime import datetime,timezone
import sys,json,copy
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import save,sha
OUT=ROOT/'hardware/electronics/full-cat/source-switch-interface-r1'
EVIDENCE=['source-switch-layout-r6','source-switch-restraints-r2','source-switch-mount-finish-r4','source-switch-assembly-finish-r3','source-switch-deck-native-r3']
SCRIPTS=['source_switch_layout_r6.py','source_switch_restraints_r2.py','source_switch_mount_finish_r4.py','source_switch_assembly_finish_r3.py','source_switch_deck_native_r3.py']

def verify_reports(root=ROOT):
    result=[];pins={}
    for folder,script in zip(EVIDENCE,SCRIPTS):
        p=root/'hardware/electronics/full-cat'/folder/'checks.json'
        m=json.loads(p.read_text(encoding='utf-8'))
        assert not m.get('hits') and not m.get('errors'),folder
        assert m['selected'] is False and m['physical_pass'] is False,folder
        assert sha(root/'tools/electronics'/script)==m['script_sha256'],script
        for rel,h in m['source_sha256'].items():
            assert sha(root/rel)==h,rel
            assert rel not in pins or pins[rel]==h,rel
            pins[rel]=h
        pins[p.relative_to(root).as_posix()]=sha(p)
        pins['tools/electronics/'+script]=m['script_sha256'];result.append(m)
    layout,rest,mount,assembly,native=result
    assert layout['lengths']['W076']['nominal_candidate_blank_mm']<=layout['lengths']['W076']['supplied_nominal_limit_mm']
    assert mount['deck_bolt_xy']==assembly['deck_bolt_xy']==native['deck_bolt_xy']==[[-79.5,92],[-29,92]]
    assert assembly['P_SYS_physical_labels_plus_X']==['.1','.2','.3','.4','.5']
    assert native['single_solid'] and native['closed_STL'] and native['relocated_reopen']
    assert rest['added_T18I']==assembly['extra_T18I']==2
    assert mount['M10_stack']['thread_projection_mm']>0 and mount['M6_stack']['thread_projection_mm']>0
    return result,pins

def main():
    start=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'interface.json').exists()
    result,pins=verify_reports();layout,rest,mount,assembly,native=result
    bodypath=ROOT/'hardware/electronics/full-cat/battery-feed-selected-r1/body-harness.json'
    pins[bodypath.relative_to(ROOT).as_posix()]=sha(bodypath)
    body=json.loads(bodypath.read_text(encoding='utf-8'))
    before={r['id']:(r['a'],r['b'],r['net']) for r in body['conductors']}
    candidate=copy.deepcopy(body)
    for row in candidate['conductors']:
        if row['id'] in assembly['nominal_wire_blanks_mm']:
            row.update(nominal_candidate_blank_mm=assembly['nominal_wire_blanks_mm'][row['id']],candidate_recipe=(OUT/'interface.json').relative_to(ROOT).as_posix())
    assert len(before)==80 and before=={r['id']:(r['a'],r['b'],r['net']) for r in candidate['conductors']}
    existing={r['id'] for r in body['conductors'] if r.get('nominal_selected_blank_mm') is not None}
    prospective=existing|set(assembly['nominal_wire_blanks_mm'])
    assert len(existing)==12 and len(prospective)==14
    interface=dict(status='COMPLETE_LOCAL_SOURCE_SWITCH_PROTOTYPE_AWAITING_BATCH_SELECTION',selected=False,
        current_selected_batch='one-batch-prototype-r48',W5_complete=False,E3_complete=False,physical_pass=False,
        native_deck=native['native'],native_mount=mount['native']['path'],
        STLs=['hardware/cad/studies/source-switch-deck-native-r3/Deck_x1.stl','hardware/cad/studies/source-switch-mount-finish-r4/Mount_x1.stl'],
        deck_bolt_xy=assembly['deck_bolt_xy'],nominal_wire_blanks_mm=assembly['nominal_wire_blanks_mm'],
        actual_cut_mm=None,selected_blanks_retained=12,prospective_blanks=14,total_body_blanks=80,
        W076_material='Intact original F0 FHAC0002ZXJ orange12AWG lead; not extra LAPP or a new splice.',
        W066_material='HELU23802 red4mm2, static radius25.2mm; nominal330mm replaces old unverified300mm planning reserve.',
        W043_material='Intact FHAC0001ZXJ16AWG factory lead;40mm retained with replaced route.',
        P_SYS_labels_plus_X=assembly['P_SYS_physical_labels_plus_X'],
        endpoints_preserved=True,assembly_order=assembly['assembly_order'],prototype_conditions=assembly['prototype_conditions'],
        new_quantities_to_allocate=dict(installed_PETG_mount=1,replace_Deck_STL=1,M2=assembly['added_M2'],M6_M10=assembly['extra_fasteners'],T18I=2,extra_ring_terminals=0),
        ring_allocation='Use two already-required TE130207 source rings; do not count them twice.',
        remaining=['Select one R49 batch with replacement Deck, added mount, synchronized W043 physical labels and exact SKU quantities.',
            'Allocate HELU330mm replacing legacy300mm and retain all other conductor budgets; no claim of final material census.',
            'Complete remaining66 unselected body blanks, twelve fuse holders/24 ends and leg/source restraints to close W5.',
            'E3/K2/K3/A2/A3 remain open. This local interface awards no phase1 points.'])
    save(OUT/'interface.json',interface);save(OUT/'body-harness-candidate.json',candidate)
    for f in interface['STLs']+[interface['native_deck'],interface['native_mount']]:pins[f]=sha(ROOT/f)
    for p in OUT.iterdir():
        if p.is_file() and p.name not in ('checks.json',):pins[p.relative_to(ROOT).as_posix()]=sha(p)
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='PINNED_LOCAL_SOURCE_INTERFACE_ONLY',source_sha256=pins,script_sha256=sha(Path(__file__)),
        selected=False,W5_complete=False,physical_pass=False,phase1_percent=70,prospective_blanks=14,
        started_utc=start.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-start).total_seconds()))
    print(json.dumps(dict(status=interface['status'],pins=len(pins),prospective_blanks=14,phase1_percent=70)),flush=True)

if __name__=='__main__':main()
