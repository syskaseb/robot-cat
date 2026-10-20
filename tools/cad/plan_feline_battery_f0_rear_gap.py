"""Retain accepted low F0; use the ACTUAL rear-of-cell interior gap for POST.

Source atlas: batteryXmax80.25, rear-frameXmin107.5, sideinnerY27.
The upper transverse guess was occupied by rail stub/P0washer/20-station
foundations. Do not rerun it or build mounts on its failed assumptions.
"""
import itertools,math
from pathlib import Path
import numpy as np
import FreeCAD as A
from plan_feline_battery_f0_joint import path,pose
from plan_feline_n01_shared import pipe
from fit_feline_current_usb_space import biarc_join
from receive_feline_source_joint import receive


def construction(parts,ends):
    names={'F0':'Ref_Material_F0_CP2_0_0','XT60':'Ref_Material_XT60_CP2_0_0','POST':'Ref_Material_PostF0Splice_CP2_0_0'}
    actors={names['F0']:parts[names['F0']]};tf={}
    diagonal=A.Vector(2**-.5,2**-.5,0);cross=A.Vector(2**-.5,-2**-.5,0)
    inlet=A.Vector(*ends['W075/retained0/end']['point_mm']);outlet=A.Vector(*ends['W076/retained0/start']['point_mm'])
    plus=inlet-diagonal*20;centre=plus-diagonal*11.95+cross*3.5
    actors[names['XT60']],tf['XT60']=pose(parts[names['XT60']],[142.999996948242,0.000003051758,-35],
        A.Rotation(A.Vector(0,0,1),45)*A.Rotation(A.Vector(1,0,0),90),list(centre))
    post1=A.Vector(94.5,-5,15)
    actors[names['POST']],tf['POST']=pose(parts[names['POST']],[143.000000762939,-35,42],
        A.Rotation(A.Vector(0,1,0),-90)*A.Rotation(A.Vector(0,0,1),180),[96,-14.5,15])
    at=lambda group,id:tf[group].multVec(A.Vector(*ends[id]['point_mm']))
    actualplus=at('XT60','W075/retained0/start');ground=at('XT60','W001/retained0/start')
    assert (actualplus-plus).Length<1e-5
    assert (at('POST','W076/retained0/end')-post1).Length<1e-5
    post2=at('POST','W076/retained1/start')
    b=biarc_join(np.array(list(outlet)),np.array(list(diagonal)),np.array(list(post1)),np.array([0,-1,0]),2.,True)
    assert b and b['minimum_R_mm']>=12.4 and b['length_mm']+21<=89.5
    pieces=[]
    for a in b['arcs']:
        v=np.asarray(a['points_mm'][::-1] if a['reverse'] else a['points_mm'])
        pieces.append(dict(kind='arc',start=v[0].tolist(),mid=v[len(v)//2].tolist(),end=v[-1].tolist(),R_mm=a['R_mm']))
    recipes={'W075_factory':path(list(actualplus),list(diagonal),[('line',20)],12.4),
        'W076_factory':dict(parts=pieces,length_mm=b['length_mm'],minimum_R_mm=b['minimum_R_mm']),
        'W001_ground_prefix':path(list(ground),list(diagonal),[('turn',list(cross)),('line',9)],12.4),
        'W076_custom_prefix':path(list(post2),[0,1,0],[('turn',[0,0,1]),('line',9)],25.2)}
    for n,r in recipes.items():actors[n]=pipe(r['parts'],2.1 if n=='W076_custom_prefix' else 1.55)
    mouths={frozenset((names['F0'],n)) for n in ('W075_factory','W076_factory')}
    mouths.update(frozenset((names['XT60'],n)) for n in ('W075_factory','W001_ground_prefix'))
    mouths.update(frozenset((names['POST'],n)) for n in ('W076_factory','W076_custom_prefix'))
    own={}
    for a,b in itertools.combinations(actors,2):
        s,t=actors[a],actors[b];minimum=0. if frozenset((a,b)) in mouths else 1.25
        gap=s.distToShape(t)[0];c=s.common(t);assert c.isNull() or c.isValid()
        own[a+'|'+b]=dict(ok=gap>=minimum-1e-6 and c.Volume<1e-5,gap_mm=gap,minimum_mm=minimum,common_mm3=c.Volume,exact_own_mouth=frozenset((a,b)) in mouths)
    datums={k:list(v) for k,v in dict(BAT_plus=actualplus,BAT_minus=ground,F0_in=inlet,F0_out=outlet,POST1=post1,POST2=post2).items()}
    assert actors[names['F0']] is parts[names['F0']]
    return actors,recipes,own,names,datums,dict(unchanged_existing_body_names=[names['F0']],F0_pose_and_whole_body_NOT_changed=True,
        nominal_delivered_ports_not_supplier_verified=True,source_atlas_basis='Battery80.25/rearframe107.5/sideinner27; old transverse stubs and washer avoided',
        historical920_NOT_extra_BAT_wire=True)


if __name__=='__main__':receive(construction,Path(__file__),'n01-BAT-F0-rear-gap-joint.json')
