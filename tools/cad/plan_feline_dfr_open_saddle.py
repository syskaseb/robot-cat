"""D_FR planning candidate: open existing seats, retain the selected nylon tie.

No native selection or physical retention qualification. Nominal five equal
wire crowns meet the lowered tie; groove fit and pull retention need fitting.
This removes a removable PETG cap, not any purchased connector or wire.
"""


def build(scene):
    import FreeCAD as A
    import Part

    parent = scene['Station:D_FR:split_common_comb'].copy()
    base = parent.common(Part.makeBox(30, 12, 20, A.Vector(1, -45.5, 25.26)))
    band = Part.makeBox(28.5, 2.5, 7.5, A.Vector(1.375, -41, 40.51)).cut(
        Part.makeBox(26.1, 4, 5.1, A.Vector(2.575, -41.75, 41.71)))
    head = scene['Station:D_FR:head_budget'].copy()
    for shape in (base, band, head):
        shape.check(True)
        assert shape.isValid() and len(shape.Solids) == 1
    return {'base': base, 'band': band, 'head': head}, {
        'status': 'PLANNING_CANDIDATE_NOT_SELECTED',
        'wire_centres_and_purchased_parts_changed': False,
        'seat_length_mm': 9, 'nominal_radial_groove_gap_mm': .15,
        'tie_crown_Z_mm': 46.81,
        'cap_removed': True,
        'service_intent': 'Support five wires, cut nylon, release chosen wire; no PETG cap extraction.',
        'open': ['Tie cutting/support access', 'Whole W009 parking',
                 'Native integration', 'Individual pull retention after physical fitting'],
        'N01_complete': False, 'physical_pass': False,
    }
