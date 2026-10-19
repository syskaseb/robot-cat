"""Actual planning material for ONLY the remaining24+2+1 kit interfaces.

Recipes are retained candidates, not their historical unsigned acceptance.
No old20station search or surface-cloud preprocessing is repeated here.
"""
import json
import ast
import hashlib
import subprocess
from functools import lru_cache
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from plan_feline_central_pi_wedge import packed
from receive_feline_flat_station_proposal import wire_shape
from receive_feline_global_case_candidates import placement


def candidates():
    path=OUT/'n01-whole51-joint-proposal.json';old=json.loads(path.read_text())
    groups={n:[dict(r) for r in rows] for n,rows in old['domains'].items()
            if n.startswith(('Bank:','Anchor:')) or n=='F_PWM_whole'}
    opened=OUT/'n01-bank-W027-open-saddle.json';packet=json.loads(opened.read_text())
    assert packet['domains'] and not packet.get('errors')
    groups['Bank:W027/single/end']=[dict(r,received_open_packet=True) for r in packet['domains']]
    extend_open_bank(groups,packet)
    assert len(groups)==27 and all(groups.values())
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in (path,opened,Path(__file__))}
    for name in ('n01-flat20-actual-clamp-kits.json','n01-coupled-clocked-joints.json','n01-bank-W027-open-saddle.json'):
        p=OUT/name;doc=json.loads(p.read_text());bundle=ROOT/doc['bundle']
        assert sha(bundle)==doc['bundle_sha256']
        pins.update({p.relative_to(ROOT).as_posix():sha(p),doc['bundle']:doc['bundle_sha256']})
    return groups,pins


def extend_open_bank(groups,packet):
    """Change the blocked BEND, not the two identical first9mm grips/heads."""
    key='Bank:W027/single/end';old=list(groups[key])
    for row in old:
        for degrees in (0,45,90,135,180,225,315):
            a=np.deg2rad(degrees)
            groups[key].append(dict(row,wire_bend_clock_degrees=degrees,
                bend_unit=[float(np.cos(a)),0.,float(np.sin(a))]))
    assert len(groups[key])==16
    assert all(row in groups[key] for row in old)


def prove_additive_extension(old_hash):
    """Old inputs have no new key, so every old material branch is identical."""
    rel='tools/cad/feline_remaining_kits.py'
    old=subprocess.run(['git','show','65e2b033:'+rel],cwd=ROOT,check=True,capture_output=True).stdout
    assert hashlib.sha256(old).hexdigest()==old_hash
    before=ast.parse(old);after=ast.parse(Path(__file__).read_text())
    class StripOnlyNewBranch(ast.NodeTransformer):
        def visit_If(self,node):
            if ast.unparse(node.test)=="'wire_bend_clock_degrees' in r":return None
            return self.generic_visit(node)
        def visit_Expr(self,node):
            if isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Name) and node.value.func.id=='extend_open_bank':return None
            return self.generic_visit(node)
    after=StripOnlyNewBranch().visit(after)
    for name in ('candidates','source_packet','sleeve','materialise'):
        get=lambda t:next(n for n in ast.walk(t) if isinstance(n,ast.FunctionDef) and n.name==name)
        assert ast.dump(get(before))==ast.dump(get(after)),name
    return dict(old_constructor_sha256=old_hash,old_recipe_geometry_AST_identical=True,
                added_only='14W027 alternative bend planes; same original2retained',
                old_mouths_first9_R_and_grip_heads_preserved=True)


@lru_cache(maxsize=3)
def source_packet(name):
    path=OUT/name;data,parts,rows=packed(path)
    return data,parts,rows


def sleeve(q,d,r,inner,outer,length):
    shape=Part.makeCylinder(outer,length,A.Vector(*q),A.Vector(*d)).cut(
          Part.makeCylinder(inner,length,A.Vector(*q),A.Vector(*d)))
    assert shape.isValid() and len(shape.Solids)==1
    return shape


def materialise(group,r):
    parts={};kinds={}
    if r.get('received_open_packet'):
        doc,source,rows=source_packet('n01-bank-W027-open-saddle.json')
        for row in r['parts']:
            parts[row['name']]=source[row['name']]
            kinds[row['name']]='proposal_wire' if row['kind']=='wire' else 'project_stock_reservation' if 'budget' in row['kind'] else 'proposal_material'
        if 'wire_bend_clock_degrees' in r:
            name=next(n for n in parts if kinds[n]=='proposal_wire')
            parts[name]=wire_shape(dict(r,radius=r['radius']))
        return parts,kinds
    if group.startswith('Bank:'):
        q=np.asarray(r['point_mm']);d=np.asarray(r['departure_axis']);radius=r['radius_mm']
        assert r['first_mm']==9 and r['cap_wall_mm']==2
        wire=wire_shape(dict(r,radius=radius));parts['wire:'+r['source_endpoint']]=wire
        # Full annular exterior includes both removable printed halves.
        # Its split/native fastening is NOT manufactured or accepted here.
        parts['split_cap_exterior']=sleeve(q,d,radius,radius+.15,radius+2,9)
        parts['band_budget']=sleeve(q+3.25*d,d,radius,radius+2,radius+3.2,2.5)
        angle=np.deg2rad(r['complete_band_head_degrees'])
        radial=np.array([np.cos(angle),0,np.sin(angle)])
        centre=q+4.5*d+(radius+6.2)*radial
        parts['head_budget']=Part.makeBox(6,6,6,A.Vector(*(centre-3)))
    elif group.startswith('Anchor:'):
        doc,source,rows=source_packet('n01-flat20-actual-clamp-kits.json')
        delta=A.Vector(r['axis_X_mm']-r['source_axis_X_mm'],0,0)
        for row in r['actual_parts']:
            s=source[row['name']].copy();s.translate(delta);parts[row['name']]=s
        assert len(parts)==12 and r['actual_parent_no_positive_overlap_verified']
    else:
        assert group=='F_PWM_whole' and r['source_selected_fuse']=='0242.100UAT1'
        doc,source,rows=source_packet('n01-coupled-clocked-joints.json')
        rot=np.asarray(r['rotation_rows']);c=np.asarray(r['source_centre_mm']);target=np.asarray(r['centre_mm'])
        pose=placement(rot,target-rot@c)
        for n,s in source.items():
            if rows[n]['group']!='F_PWM':continue
            p=s.copy();p.Placement=pose*p.Placement;parts[n]=p
        assert len(parts)==5
        for index,sign in enumerate((-1,1)):
            q=c+np.array([21*sign,0,0]);d=np.array([sign,0.,0.]);radius=1.55
            cap=sleeve(q,d,radius,radius+.15,radius+2,9)
            band=sleeve(q+3.25*d,d,radius,radius+2,radius+3.2,2.5)
            centre=q+4.5*d+np.array([0,0,(-1 if r['head_choices'][index]==0 else 1)*(radius+6.2)])
            head=Part.makeBox(6,6,6,A.Vector(*(centre-3)))
            for suffix,s in (('split_cap_exterior',cap),('band_budget',band),('head_budget',head)):
                s.Placement=pose*s.Placement;parts[f'End{index}:'+suffix]=s
    for n,s in parts.items():
        assert s.isValid() and s.Solids,(group,n)
        kinds[n]=('proposal_wire' if n.startswith('wire:') or group=='F_PWM_whole' and n!='F_PWM:case' and n.startswith('F_PWM:')
                  else 'project_stock_reservation' if 'budget' in n else 'proposal_material')
    return parts,kinds
