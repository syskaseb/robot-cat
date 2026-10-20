"""Selected SKU governs also composite labels such as factory+HELU extension.

Do not identify material by the first word of a human-readable CSV label.
The immutable previous delta and received W066 correction stay pinned.
"""
import json
from check_main_p0_placement import ROOT,sha
from feline_current_wire_contract import load as parent


def load():
    result,source,delta=parent()
    facts=ROOT/'hardware/reference/parent-fuse-extensions-2026-10-03/facts.json'
    material=json.loads(facts.read_text())['HELU23802']
    roles=ROOT/'hardware/electronics/full-cat/servo-fuse-main-feeds-materials-r1/materials.json'
    extensions={r['id'].removesuffix('_extension')+'/custom' for r in json.loads(roles.read_text())['HELU23802']['extensions']}
    for name,row in result['portions'].items():
        if 'project_radius_mm' not in row:continue
        if name in extensions or 'HELU23802' in (row.get('selected_material') or ''):
            row['project_radius_mm']=max(row['project_radius_mm'],material['routing_OD_mm']/2)
            row['minimum_project_R_mm']=max(row['minimum_project_R_mm'],material['routing_radius_mm'])
            row['typed_bend_basis']='Retained HELU SKU also in composite factory+extension material role'
            if name in extensions:row['extension_material_role']='HELU23802 extension; original whole-net CSV describes factory tail, not this custom portion'
    result['selected_material_rule_sha256']=sha(ROOT/'tools/cad/feline_selected_material_contract.py')
    result['selected_extension_role_source_sha256']=sha(roles)
    return result,source,delta
