"""Actual planning material for ONLY the remaining24+2+1 kit interfaces.

Recipes are retained candidates, not their historical unsigned acceptance.
No old20station search or surface-cloud preprocessing is repeated here.
"""
import json
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
    assert len(groups)==27 and all(groups.values())
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in (path,opened,Path(__file__))}
    for name in ('n01-flat20-actual-clamp-kits.json','n01-coupled-clocked-joints.json','n01-bank-W027-open-saddle.json'):
        p=OUT/name;doc=json.loads(p.read_text());bundle=ROOT/doc['bundle']
        assert sha(bundle)==doc['bundle_sha256']
        pins.update({p.relative_to(ROOT).as_posix():sha(p),doc['bundle']:doc['bundle_sha256']})
    return groups,pins


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
