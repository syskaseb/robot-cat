"""One functional bank receiving plan around ALL known occupied corridors.

Left positive-X receiving gallery is ABOVE P_SYS/D_FL, below the PCBs.
Fore left stays below S0 key. Right fore OUT and rear IN use a shared
diagonal-X/down gallery, away from the opposite receiving stock and key/BUS.
Full9 AFTER grips, retainedR, unaltered stock volumes and bought mouths.
Project entry/sweep values are not manufacturer specifications.
"""
import copy
import math
import numpy as np
import FreeCAD as A
import Part
from feline_bank_receiving_grips import both_after_candidates,both_after_materialise
from feline_remaining_kits import materialise as original_material


def zone(group,r):
    q=r['point_mm']
    if group=='Bank:W020/body/end':return 'FORE_LEFT_SPLIT_BELOW_S0_KEY'
    if q[1]>0 and (q[0]>0 or group=='Bank:W029/single/end'):return 'UPPER_LEFT_ABOVE_PSYS_DFL'
    if q[1]<0 and '_OUT_' in r.get('terminal_name',''):return 'RIGHT_OUT_RETURN180_BELOW_BANK'
    if group=='Bank:W058/single/end':return 'REAR_IN_RETURN_MINUS_X_AWAY_BUS'
    return None


def candidates(groups):
    result={}
    for group,rows in both_after_candidates(groups).items():
        role=zone(group,rows[0]['base_recipe'])
        if role is not None:result[group]=[dict(copy.deepcopy(r),receiving_zone=role) for r in rows]
        if role=='FORE_LEFT_SPLIT_BELOW_S0_KEY':
            result[group].extend(dict(copy.deepcopy(r),receiving_zone='FORE_LEFT_DOWN_TO_RECEIVING_LEVEL') for r in rows)
        if role=='RIGHT_OUT_RETURN180_BELOW_BANK':
            for r in result[group]:r.update(current_prefix_sweep_degrees=180,current_prefix_entry_mm=0,template_turn60_is_not_current_profile=True)
            if group=='Bank:W031/body/end':
                result[group].extend(dict(copy.deepcopy(r),receiving_zone='FORE_RIGHT_RETURN120_BELOW_ALL_LEFT',current_prefix_sweep_degrees=120,template_turn60_is_not_current_profile=True) for r in rows)
                result[group].extend(dict(copy.deepcopy(r),receiving_zone='FORE_RIGHT_VERTICAL_BELOW_LEFT_GALLERY',current_prefix_sweep_degrees=90,template_turn60_is_not_current_profile=True) for r in rows)
                result[group].extend(dict(copy.deepcopy(r),receiving_zone='FORE_RIGHT_BELOW_S0_KEY') for r in rows)
            else:result[group].extend(copy.deepcopy(r) for r in rows)
    assert len(result)==16,(len(result),sorted(result))
    return result


def profile(group,recipe):
    r=recipe['base_recipe'];q=np.asarray(r['point_mm']);d=np.asarray(r['departure_axis']);role=recipe.get('receiving_zone',zone(group,r))
    assert role is not None
    entry=3.;degrees=60.
    if role=='UPPER_LEFT_ABOVE_PSYS_DFL':b=np.array([0.,0.,1.]);degrees=45.
    elif role=='FORE_LEFT_SPLIT_BELOW_S0_KEY':b=np.array([1.,0.,-1.])/math.sqrt(2)
    elif role=='FORE_RIGHT_VERTICAL_BELOW_LEFT_GALLERY':b=np.array([0.,0.,-1.]);degrees=90.
    elif role=='FORE_LEFT_DOWN_TO_RECEIVING_LEVEL':b=np.array([0.,0.,-1.])
    elif role=='FORE_RIGHT_RETURN120_BELOW_ALL_LEFT':b=np.array([0.,0.,-1.]);degrees=120.
    elif role=='RIGHT_OUT_RETURN180_BELOW_BANK':b=np.array([0.,0.,-1.]);degrees=180.;entry=0.
    else:b=np.array([-1.,0.,-1.])/math.sqrt(2)
    theta=math.radians(degrees);start=q+(entry+r['R_mm']*math.sin(theta))*d+r['R_mm']*(1-math.cos(theta))*b
    axis=math.cos(theta)*d+math.sin(theta)*b
    return dict(start=start,axis=axis,tip=start+9*axis,bend=b,entry=entry,degrees=degrees,role=role)


def materialise(group,recipe):
    if not recipe.get('receiving_zone'):return both_after_materialise(group,recipe)
    r=recipe['base_recipe'];p=profile(group,recipe);parts,kinds=original_material(group,r)
    q=np.asarray(r['point_mm']);d=np.asarray(r['departure_axis']);R=r['R_mm'];theta=math.radians(p['degrees']);a=q+p['entry']*d
    point=lambda t:a+R*math.sin(t)*d+R*(1-math.cos(t))*p['bend']
    edges=([Part.makeLine(A.Vector(*q),A.Vector(*a))] if p['entry']>1e-8 else [])
    path=Part.Wire(edges+[Part.Arc(A.Vector(*a),A.Vector(*point(theta/2)),A.Vector(*p['start'])).toShape(),Part.makeLine(A.Vector(*p['start']),A.Vector(*p['tip']))])
    radius=r.get('radius_mm',r.get('radius'));wire=path.makePipeShell([Part.Wire([Part.makeCircle(radius,A.Vector(*q),A.Vector(*d))])],True,False)
    assert wire.isValid() and len(wire.Solids)==1
    rotation=A.Rotation(A.Vector(*d),A.Vector(*p['axis']));pose=A.Placement(A.Vector(*p['start'])-rotation.multVec(A.Vector(*q)),rotation)
    for n,s in list(parts.items()):
        if kinds[n]=='proposal_wire':parts[n]=wire
        else:
            v=s.copy();v.Placement=pose*v.Placement;parts[n]=v
            assert v.isValid() and v.Solids
    return parts,kinds
