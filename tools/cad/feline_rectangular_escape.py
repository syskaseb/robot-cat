"""Sharper necessary escape test at an actual rectangular obstacle face.

The reachable cross-section lies in radiusD from the existing curvature
bound. A radiusm disk contained in the face gives distance-to-face <=
max(0,D-m) everywhere in that reachable disk. No bbox contact inference.
"""
from feline_terminal_escape import bound


def certificate(R,L,inscribed_face_radius,wire_radius,required_gap=1.25):
    assert inscribed_face_radius>=0
    base=bound(R,L,0.,wire_radius,required_gap)
    distance=max(0.,base['maximum_transverse_excursion_mm']-inscribed_face_radius)
    return dict(base,inscribed_face_disk_radius_mm=inscribed_face_radius,
        maximum_possible_distance_to_actual_face_mm=distance,
        maximum_possible_jacket_gap_mm=distance-wire_radius,
        no_admissible_clearance_path=distance<wire_radius+required_gap-1e-6,
        unavoidable_jacket_material_intersection=distance<wire_radius-1e-6,
        face_disk_containment_must_be_verified=True)
