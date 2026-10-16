"""Overlay verified source parents on receiver parts, never print both revisions."""
import copy
import json
import time
from pathlib import Path
from plan_current_harness_interfaces import ROOT, OUT, SHA


def compose(prior, source):
    assert prior['status'] == 'CURRENT_BODY_RECEIVER_COMPONENT_NATIVE_SET_NOT_W5_SELECTION'
    assert source['status'] == 'THIRTEEN_SOURCE_LANDS_FIVE_NATIVE_PARENT_REPLACEMENTS_COMPLETE'
    rows = {r['identity']: copy.deepcopy(r) for r in prior['prints']}
    assert len(rows) == 12
    exports = {r['part']: r for r in source['exports']}
    replaced = []
    for p in source['parts']:
        name = 'UpperCarrier' if p['part'] == 'UpperCarrier001' else p['part']
        key = 'CP2:' + name
        old = rows.get(key)
        assert old is not None or name == 'LeftRiser'
        assert p['original_material_preserved'] and p['relocated_reopen']
        assert p['beam_Z_allowance_restore_mm'] == [0, .2, 0]
        r = copy.deepcopy(exports[p['part']])
        r.update(identity=key, native=p['native'], native_object=p['object'],
                 replaces=name, preserved_receiver_history=True)
        if old:
            r['superseded_export'] = old['path']
            replaced.append(key)
        rows[key] = r
    assert len(replaced) == 4 and len(rows) == 13
    assert sum(r['quantity'] for r in rows.values()) == 13
    assert sum(r['replaces'] is None for r in rows.values()) == 7
    return list(rows.values()), replaced


def run():
    tick = time.monotonic()
    inputs = [OUT/'current-body-receiver-native-set.json',
              OUT/'local-source-retention-native/manifest.json']
    prior, source = [json.loads(p.read_text()) for p in inputs]
    for n, h in source['source_sha256'].items():
        assert SHA(ROOT/n) == h, n
    for model in source['models']:
        assert SHA(ROOT/model['path']) == model['sha256']
    rows, replaced = compose(prior, source)
    for r in rows:
        assert SHA(ROOT/r['path']) == r['sha256'], r['path']
        assert r['printing']['fits_with_5mm_brim']
        x, y, z = r['printing']['size_mm']
        assert max(x+10, y+10, z) < 256
    result = dict(status='CURRENT_BODY_SOURCE_RECEIVER_NATIVE_SET_NOT_W5_SELECTION',
        prints=rows, replaced_prior_component_ids=replaced,
        replacement_Frame_quantity=4, replacement_UpperCarrier_quantity=1,
        replacement_LeftRiser_quantity=1, new_CAP_quantity=7,
        receiver_T18I_quantity=prior['receiver_T18I_quantity'],
        receiver_M2x14_quantity=prior['receiver_M2x14_quantity'],
        receiver_M2_nut_quantity=prior['receiver_M2_nut_quantity'],
        lacing_candidate_blanks=prior['feed_lacing_blanks']+source['source_lacing_blanks'],
        lacing_candidate_mm=prior['feed_lacing_candidate_mm']+source['source_lacing_project_mm'],
        scope='Four Frames, Upper, LeftRiser and seven caps. Replacements, not duplicated parents. '
              'Unchanged RightRiser and other robot parts stay in their existing packages.',
        open=['Remaining25 interfaces and current bank retention/M4 binding',
              'Whole assembled access/stock/current whole-model selection'],
        source_sha256={p.relative_to(ROOT).as_posix(): SHA(p) for p in inputs+[Path(__file__)]},
        worker_seconds=round(time.monotonic()-tick, 3), selected=False, stock_selected=False,
        W5_complete=False, M4_complete=False, physical_pass=False, print_ready=False)
    assert result['lacing_candidate_blanks'] == 31 and result['lacing_candidate_mm'] == 4650
    (OUT/'current-body-source-native-set.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(prints=13, replacements=6, new_caps=7,
                         worker_seconds=result['worker_seconds'])))


if __name__ == '__main__':
    run()
