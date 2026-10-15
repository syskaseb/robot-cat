"""Recover fixed interfaces from their selected receipts, never prior attempts.

Normalize only OPEN routes. Positive whole curves and their evidence remain
unchanged. Packing always starts from the original measured source fan.
"""
import copy
import json
from shared_body36_macro_routes import packed_front_prefixes


def selected_rows(selection_file, root):
    selection = json.loads(selection_file.read_text())
    options = json.loads((root / selection['domain_receipt']).read_text())['qualified_options']
    if selection['override_receipt']:
        options.update(json.loads((root / selection['override_receipt']).read_text())['replacement_options'])
    return {r['wire']: r for name, index in selection['selected_options'].items()
            for r in options[name][index]['rows']}


def normalize(parent, base, selected):
    original = {r['wire']: copy.deepcopy(r) for r in base['rows']}
    rows = copy.deepcopy(original)
    rows.update({r['wire']: copy.deepcopy(r) for r in parent['changed_rows']})
    packed = packed_front_prefixes(original)
    for name in parent['remaining_wire_ids']:
        row = rows[name]
        interface = selected[name]
        for key, value in interface.items():
            if key.startswith(('receiving_', 'receiver_')) or key == 'free_end':
                row[key] = copy.deepcopy(value)
        if name not in packed:
            continue
        source = original[name]['source_parts']
        after = original[name].get('source_after_jacket_first5_mm', source[1:])
        row['source_parts'] = copy.deepcopy(packed[name])
        row['source_after_jacket_first5_mm'] = copy.deepcopy(after + packed[name][len(source):])
        row['free_start'] = copy.deepcopy(packed[name][-1]['end'])
        row['source_free_axis'] = [0, 0, 1]
    return rows
