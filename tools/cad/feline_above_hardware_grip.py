"""Place the whole AFTER grip ABOVE the actual complete rear hardware.

The former axial half-space was sufficient but needlessly put the entire
stock behind the furthest screw corner. A vertical half-space gives the same
1.25mm positive separation while respecting the bank's overhead corridor.
No offset grid, reduced stock, weakened margin or altered bought part.
"""
import math
import json
import numpy as np
import FreeCAD as A
import Part
from feline_compact_after_land import unit as original_unit
from feline_remaining_kits import candidates,materialise
from plan_feline_layout import OUT


def unit(st,choice):
    model=original_unit(st,choice);groups,_=candidates()
    reference=next(r for r in groups['Anchor:Rear'] if r['axis_X_mm']==72)
    hardware,_=materialise('Anchor:Rear',reference)
    highest=max(s.BoundBox.ZMax for s in hardware.values())
    stock={n:s for n,s in model['parts'].items() if n!='case' and not n.startswith('wire:')}
    axis=np.asarray(model['wires'][0]['grip_axis']);assert axis[2]>.1
    lowest=min(s.BoundBox.ZMin for s in stock.values())
    correction=(highest+1.25-lowest)/axis[2]
    guard=model['full_stock_guard_mm']+correction;assert guard>=0
    for s in stock.values():s.translate(A.Vector(*(correction*axis)))
    for w in model['wires']:
        q=np.asarray(w['point_mm']);d=np.asarray(w['departure_axis']);R=w['R_mm'];theta=math.radians(w['sweep_degrees']);b=np.array([0.,0.,1.]);a=q+w['first_mm']*d
        point=lambda t:a+R*math.sin(t)*d+R*(1-math.cos(t))*b
        end=point(theta);start=end+guard*axis;tip=start+9*axis
        path=Part.Wire([Part.makeLine(A.Vector(*q),A.Vector(*a)),Part.Arc(A.Vector(*a),A.Vector(*point(theta/2)),A.Vector(*end)).toShape(),Part.makeLine(A.Vector(*end),A.Vector(*tip))])
        s=path.makePipeShell([Part.Wire([Part.makeCircle(w['radius'],A.Vector(*q),A.Vector(*d))])],True,False)
        assert s.isValid() and len(s.Solids)==1
        model['parts']['wire:'+w['endpoint']]=s;w.update(grip_start_mm=start.tolist(),grip_end_mm=tip.tolist())
    assert min(s.BoundBox.ZMin for s in stock.values())>=highest+1.25-1e-6
    model.update(previous_axial_guard_mm=model['full_stock_guard_mm'],full_stock_guard_mm=guard,
        new_prefix_mm=model['new_prefix_mm']+correction,
        clearance_basis=dict(reference_rear_axis_mm=72,minimum_mm=1.25,actual_complete_hardware_top_mm=highest,
            lowest_full_stock_mm=min(s.BoundBox.ZMin for s in stock.values()),
            whole_stock_ABOVE_hardware_positive_separation=True,boxes_not_collision_verdict=True))
    assert model['new_prefix_mm']<=model['old_shortest_prefix_mm']
    return model


def receive_model(group,choice):
    """Explicit full-unit factory for the source-pinned shared receiver."""
    assert group=='D_FL'
    st=next(s for s in json.loads((OUT/'n01-flat-station-architecture.json').read_text())['stations'] if s['ref']==group)
    model=unit(st,choice)
    return model['parts'],{n:'proposal_wire' if k=='wire' else k for n,k in model['kinds'].items()}
