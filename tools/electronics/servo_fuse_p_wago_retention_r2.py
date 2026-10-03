"""One common strap placement clears the Pi/source leads with existing slots.

Shift band0.5mm within each4mm slot and put the head at the middle of the
upper band. Retain conservative lever conflicts as a sequence constraint:
all20ports operated before tightening body straps; cut strap before opening.
Do not call this in-situ lever qualification or conceal any wire contact.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_p_wago_retention_r1.py')
code=parent.read_text(encoding='utf-8').replace('servo-fuse-p-wago-retention-r1','servo-fuse-p-wago-retention-r2')
code=code.replace("sy=holes[ident]['slot_centers_xy_mm'][0][1]", "sy=holes[ident]['slot_centers_xy_mm'][0][1]+.5")
code=code.replace("[[x-16.5,sy],[x+16.5,sy]]", "[[x-16.5,sy-.5],[x+16.5,sy-.5]]")
code=code.replace("[x-18,sy-2.25,119.2,x-13.2,sy+2.25,122.7]", "[x-2.4,sy-2.25,119.2,x+2.4,sy+2.25,122.7]")
code=code.replace("    holes={r['id']:r for r in native['wago_ties']}", """    pins['tools/electronics/servo_fuse_p_wago_retention_r1.py']=sha(ROOT/'tools/electronics/servo_fuse_p_wago_retention_r1.py')
    prior=read('hardware/electronics/full-cat/servo-fuse-p-wago-retention-r1/checks.json')
    assert len(prior['hits'])==4 and not prior['errors']
    holes={r['id']:r for r in native['wago_ties']}""")
code=code.replace(" and not any(r['provisional_lever_to_new_strap_hits'] for r in rows)", "")
code=code.replace("native_grip_slots=8,", "native_grip_slots=8, strap_removal_required_before_any_lever_operation=True, lever_to_new_strap_conflicts_preserved=True,")
code=code.replace('Do not open levers through crossing installed wires.', 'Body band is a removable assembly restraint, not an in-situ lever-access fixture. Tighten only after closing all ports; cut this strap before lever opening. Do not open levers through crossing installed wires; release/dress the relevant wire before connector replacement. Delivered housing/lever/strap seating checked in phase2.')
exec(compile(code,str(Path(__file__).resolve()),'exec'))
