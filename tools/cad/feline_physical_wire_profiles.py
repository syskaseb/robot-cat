"""Separate nominal K1474 jacket from the legacy conservative capacity budget.

All other materials, especially HELU23802, retain the selected contract.
OD2.1 is an explicit PROJECT assumption, never a manufacturer guarantee.
"""
import ast
from check_main_p0_placement import ROOT,sha
from feline_selected_material_contract import load as parent


def load():
    result,source,delta=parent();f=ROOT/'tools/cad/plan_current_main_neck_insulation.py'
    values=[ast.literal_eval(n.value) for n in ast.walk(ast.parse(f.read_text())) if isinstance(n,ast.keyword) and n.arg=='project_jacket_OD_mm']
    assert values==[2.1];radius=values[0]/2
    for w in ('W060','W078','W079','W080'):
        r=result['portions'][w+'/retained0'];assert 'K1474' in r['selected_material']
        r.update(legacy_capacity_radius_mm=r['project_radius_mm'],project_radius_mm=radius,
            physical_OD_basis='Explicit selected MAIN neck project assumption, not generic max-cap capacity',
            physical_OD_source_sha256=sha(f),nominal_physical_profile_not_supplier_guarantee=True,
            larger_Pi_source_BRep_is_capacity_enclosing_nominal_wire=True)
    return result,source,delta
