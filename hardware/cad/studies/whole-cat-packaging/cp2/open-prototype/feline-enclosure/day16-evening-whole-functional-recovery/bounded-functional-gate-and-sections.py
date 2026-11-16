import FreeCAD as A,FreeCADGui as G,Part,json
from pathlib import Path
D=A.ActiveDocument;V=A.Vector;P=Path(__file__).parent
root=D.getObject('TAIL_ROTATING_HOLLOW_REAL_ROOT').Shape
solids=root.Solids
report={'first_falsifier':{'named_risk':'Y-axis root torque path must join actual retained curved tail','valid_operand':root.isValid(),'separate_solids':len(solids),'pair_gap_mm':solids[0].distToShape(solids[1])[0] if len(solids)==2 else None,'common_mm3':solids[0].common(solids[1]).Volume if len(solids)==2 else None,'consequence':'WHOLE RECOVERY HOLD: rotation about Y is represented, but no continuous tail torque path. No installed mechanism/motion/print release. No second family attempted.'},'other_status':{'P07_support':'two solids; same functional root redesign remains unqualified','P11':'source roots remain, old power retention no longer matches 3 whole-unit poses; explicit functional replacement required','power_regions':'occupied routing and mouth binding not closed; no W043 length acceptance','head':'unchanged source, all prior OPEN retained'},'finite_power_gate':[]}
for a,b in [('PBAY_P_SYS','PBAY_F_PI'),('PBAY_P_SYS','PBAY_F_AUX'),('PBAY_P_REAR','PBAY_F_AUX')]:
 x=D.getObject(a).Shape;y=D.getObject(b).Shape
 report['finite_power_gate'].append(dict(a=a,b=b,distance_mm=x.distToShape(y)[0],common_mm3=x.common(y).Volume,scope='whole nominal cover pairs only; no all-neighbor acceptance'))
# Actual few-part sections, selected because they cross the two changed functional interfaces.
sections=[]
for name,axis,value,names in [('TAIL_AXIS_AND_LOAD','Y',0,['P07_open_tail_root_U','TAIL_ROTATING_HOLLOW_REAL_ROOT','TAIL_FIXED_BEARING_CARTRIDGE','MG92B_Tail','TAIL_HORN_ROOF_JOURNAL']),('POWER_FACING_END_LAYER','Z',65,['PBAY_F_PI','PBAY_P_SYS','PBAY_F_AUX','PBAY_P_REAR','P11_rear_gate','P19_BATTERY_MTA_SHARED_CARRIER'])]:
 if axis=='Y':pts=[V(x,value,z) for x,z in [(145,40),(255,40),(255,240),(145,240),(145,40)]]
 else:pts=[V(x,y,value) for x,y in [(35,-105),(200,-105),(200,105),(35,105),(35,-105)]]
 face=Part.Face(Part.makePolygon(pts));rows=[]
 for n in names:
  o=D.getObject(n)
  if not o or not hasattr(o,'Shape'):continue
  sec=o.Shape.section(face);edges=[]
  for e in sec.Edges:
   pts2=e.discretize(Deflection=0.2);edges.append([[q.x,q.z] if axis=='Y' else [q.x,q.y] for q in pts2])
  rows.append({'object':n,'edge_count':len(sec.Edges),'polylines_mm':edges})
 sections.append({'name':name,'normal_axis':axis,'coordinate':value,'objects':rows,'nonempty':any(r['edge_count'] for r in rows)})
(P/'first-whole-falsifier-and-finite-pairs.json').write_text(json.dumps(report,indent=2))
(P/'actual-functional-sections.json').write_text(json.dumps(sections,indent=2))
# Whole operating proposal, old unselected analytical aliases hidden; purchased protrusions stay visible.
for o in D.Objects:
 n=o.Name
 if n.startswith(('EV_','W043_ALLOCATED','CLOSED_HEAD_')) or n in ['Ola_ENVELOPE_not_print','Ola_tail_ENVELOPE']:
  o.ViewObject.Visibility=False
 if n.startswith('CLOSED_BODY_'):
  for parent in o.InList:
   if parent.TypeId=='App::DocumentObjectGroup':parent.ViewObject.Visibility=True
  o.ViewObject.Visibility=True;o.ViewObject.Transparency=0;o.ViewObject.ShapeColor=(0.18,0.2,0.23)
for n in ['OLA_REAL_FRONT_MASK','OLA_REAL_BACK_COVER']:
 o=D.getObject(n)
 if o:o.ViewObject.Visibility=True;o.ViewObject.Transparency=0
D.recompute();D.save();G.activeDocument().activeView().viewFront();G.activeDocument().activeView().fitAll();G.activeDocument().activeView().redraw()
print(json.dumps({'first_falsifier':report['first_falsifier'],'power_pairs':report['finite_power_gate'],'sections_nonempty':[s['nonempty'] for s in sections]}))
