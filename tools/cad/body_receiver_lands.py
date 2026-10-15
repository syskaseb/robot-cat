"""Receiver restraint alternatives on unchanged already-qualified wire paths.

Use the original9mm terminal straight first. If a complete printed grip cannot
fit there, use a previous straight on THAT wire, within80mm along the wire.
No terminal or wire relocation and no assertion of a supplier bend/pull rating.
"""
import math


def candidates(row,route,maximum_terminal_run_mm=80):
    primary=(row['receiving_parts'][row['receiving_grip_part_index']]
             if 'receiving_parts' in row else row['receiving_land'])
    result=[];after=0
    for index,part in reversed(list(enumerate(route['parts']))):
        length=part['length_mm']
        if part['kind']=='line' and length>=9-1e-7:
            is_primary=part==primary
            margin=0 if is_primary else min(.5,(length-9)/2)
            end_fraction=(length-margin)/length;start_fraction=(length-margin-9)/length
            start=[a+(b-a)*start_fraction for a,b in zip(part['start'],part['end'])]
            end=[a+(b-a)*end_fraction for a,b in zip(part['start'],part['end'])]
            terminal_run=after+margin+4.5
            if terminal_run<=maximum_terminal_run_mm+1e-7:
                result.append(dict(id=row['wire']+'/Receiver',centre_world_mm=[(a+b)/2 for a,b in zip(start,end)],
                    start_world_mm=start,end_world_mm=end,axis=[(b-a)/9 for a,b in zip(start,end)],
                    length_mm=9,route_part_index=index,primary_terminal_land=is_primary,
                    terminal_run_to_grip_centre_mm=terminal_run,
                    fit_and_insulation_pull_sample_gate_open=True))
        after+=length
    assert any(r['primary_terminal_land'] for r in result),row['wire']
    return sorted(result,key=lambda r:(not r['primary_terminal_land'],r['terminal_run_to_grip_centre_mm']))
