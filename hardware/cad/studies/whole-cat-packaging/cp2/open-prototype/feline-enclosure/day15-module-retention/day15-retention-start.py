import FreeCAD as A,FreeCADGui as G,Part,json,math
from pathlib import Path
from datetime import datetime,timezone
V=A.Vector;S=A.getDocument('DAY15_POWER_CAPACITY');P=Path(S.FileName).parent.parent/'day15-module-retention';D=A.newDocument('DAY15_MODULE_RETENTION');groups={}
for o in S.Objects:
 if o.TypeId=='App::DocumentObjectGroup':groups[o.Name]=D.addObject('App::DocumentObjectGroup',o.Name)
for o in S.Objects:
 if not hasattr(o,'Shape') or not hasattr(o.ViewObject,'ShapeColor'):continue
 q=D.addObject('PartDesign::Feature',o.Name);q.Shape=o.Shape;q.Label=o.Label;q.ViewObject.ShapeColor=o.ViewObject.ShapeColor;q.ViewObject.Transparency=o.ViewObject.Transparency;q.ViewObject.Visibility=o.ViewObject.Visibility
 for prop in ['AssemblyNote','Status','OriginalSource']:
  if hasattr(o,prop):q.addProperty('App::PropertyString',prop);setattr(q,prop,str(getattr(o,prop)))
 for g in S.Objects:
  if g.TypeId=='App::DocumentObjectGroup' and o in g.Group:groups[g.Name].addObject(q)
grp=D.addObject('App::DocumentObjectGroup','RETENTION_INTERFACES_PLANNING_NOT_PRINTS')
# One local capacity section selected from the ACTUAL upper beam bottom132.5, not a new wirecurve.
# Available verticalinterval in existingbox:121..(132.5-1.25)=131.25. FullOD6+.4 =>centre124.4..127.85, choosemid126.125.
z=(124.4+127.85)/2;s=Part.makeCylinder(3.4,10,V(-106,52,z),V(1,0,0));o=D.addObject('PartDesign::Feature','F0_SINGLE_OD6_MARGIN04_LOCAL_CAPACITY');o.Shape=s;o.ViewObject.ShapeColor=(.9,.5,.1);o.ViewObject.Transparency=35;grp.addObject(o)
D.Label='DAY15 whole module retention PLAN — F0 mouth FIT2';D.recompute();D.saveAs(str(P/'module-retention.FCStd'))
gap=s.distToShape(D.getObject('P10_front_gate').Shape)[0];common=s.common(D.getObject('P10_front_gate').Shape);r=dict(status='LOCAL_STRAIGHT_CAPACITY_CLEAR_MOUTH_AND_W075_REACH_UNQUALIFIED' if gap>=1.25 else 'LOCAL_CAPACITY_HOLD',gap=gap,common_mm3=common.Volume,valid=common.isValid(),declared_OD=6,margin=.4,R='straight local section: infinity, no bend manufactured/claimed',full_span_X=[-106,-96],section_YZ_centre=[52,z],actual_P10_local_bottomZ=132.5,available_centreZ_interval=[124.4,127.85],whole_F0_link='FIT2_UNQUALIFIED: no true deliveredmouth or connectingbend/length proof',W075_design_max_mm=50,manufacturer_lead_nominal89p5_not_design_limit=True,strip6p35_included_not_extra=True,actual_cut_slack=None,raw_rectangular_common180_preserved=True,new_material=False)
(P/'F0-local-disposition.json').write_bytes((json.dumps(r,indent=2)+'\n').encode());print(json.dumps(r))
