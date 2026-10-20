"""Necessary escape bound for ANY 3D centreline with curvature <=1/R.

For s<=pi*R/2 its tangent turns by at most s/R. Thus axial travel is
at least R*sin(s/R), and transverse travel at most R*(1-cos(s/R)).
At first crossing of an axial plane L<R, all possible centres lie in a
disk of radius R-sqrt(R²-L²). Signed material distance is1-Lipschitz.
This can reject a fixed terminal/support layout, never prove a whole route.
"""
import math


def bound(R,L,signed_distance,wire_radius,required_gap=1.25):
    assert R>0 and wire_radius>0 and 0<L<R
    excursion=R-math.sqrt(R*R-L*L)
    centre_upper=signed_distance+excursion;gap_upper=centre_upper-wire_radius
    return dict(minimum_project_R_mm=R,axial_plane_distance_mm=L,
        maximum_arc_length_to_first_crossing_mm=R*math.asin(L/R),maximum_transverse_excursion_mm=excursion,
        signed_material_distance_at_axis_mm=signed_distance,maximum_possible_signed_centre_gap_mm=centre_upper,
        jacket_radius_mm=wire_radius,maximum_possible_jacket_gap_mm=gap_upper,required_gap_mm=required_gap,
        no_admissible_clearance_path=gap_upper<required_gap-1e-6,
        unavoidable_jacket_material_intersection=centre_upper<wire_radius-1e-6,
        any_3D_torsion_allowed=True,not_assuming_a_single_quarter_arc=True)
