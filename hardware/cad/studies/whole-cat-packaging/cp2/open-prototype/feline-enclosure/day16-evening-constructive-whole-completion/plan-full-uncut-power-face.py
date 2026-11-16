import FreeCAD as A,FreeCADGui as G,Part,json,math
from pathlib import Path
D=A.ActiveDocument;P=Path(__file__).parent;V=A.Vector
# Full same WAGO cover. Face-normal reversal and offset branch order are derived jointly from full uncut pigtail storage.
o=D.getObject('PBAY_P_SYS');b=o.Shape.BoundBox;o.Placement.Base+=V(114,25.5,59.625)-V(b.XMin,b.YMin,b.ZMin)
o.Label='P_SYS all5 entries +X; lever+Z; W043 return lane separated from outgoing lane'
R=12.4;raw=[84.5,94.5];termination=14.0;start=V(106,67,65.125);end=V(136,42.2,65.125)
# Raw factory blank includes bare end. No cutoff. L=two tangent legs + piR + same-unit insertion14.
a0=(raw[0]-termination+start.x+end.x-math.pi*R)/2
a1=(raw[1]-termination+start.x+end.x-math.pi*R)/2
assert a0>=end.x
v0=V(a0,67,65.125);vm=V(a0+R,54.6,65.125);v1=V(a0,42.2,65.125)
wire=Part.Wire([Part.makeLine(start,v0),Part.Arc(v0,vm,v1).toShape(),Part.makeLine(v1,end)])
prof=Part.Wire(Part.makeCircle(1.95,start,V(1,0,0)))
base=wire.makePipeShell([prof],True,False)
# Continuous family cover, not a grid: same full profiles swept by tangent translation a0..a1.
arc=Part.Wire([Part.Arc(v0,vm,v1).toShape()]);pc=Part.Wire(Part.makeCircle(1.95,v0,V(1,0,0)));arcshape=arc.makePipeShell([pc],True,False)
# Extrusion of every face plus endpoint solid covers all X translations continuously; classify only material of profile.
parts=[base]
for face in arcshape.Faces:
 if face.Area>1e-8:
  try:parts.append(face.extrude(V(a1-a0,0,0)))
  except Exception:pass
parts.append(arcshape.translated(V(a1-a0,0,0)))
# Shared straight-lane cover extends to maximum tangent; two 3.9 diameter tubes, no whole outer-BBox air.
parts +=[Part.makeCylinder(1.95,a1-start.x,start,V(1,0,0)),Part.makeCylinder(1.95,a1-end.x,end,V(1,0,0))]
cover=Part.makeCompound(parts)
ref=D.addObject('PartDesign::Feature','W043_FULL_UNCUT_ADAPTIVE_HANDLAY_COVER');ref.Shape=cover;ref.ViewObject.ShapeColor=(0.9,0.2,0.1);ref.ViewObject.Transparency=55
# One live nominal core path for inspection, never a printed part; adaptive cover retains full unit, not cut29.
nom=D.addObject('PartDesign::Feature','W043_MIN84p5_NOMINAL_OCCUPIED_PROFILE');nom.Shape=base;nom.ViewObject.ShapeColor=(0.9,0.15,0.05)
# source P11 actual retained anchor witnesses, before any detailed keeper/plate material design
anchor=Part.makeBox(7,4,2,V(100,79,57.625));realanchor=D.getObject('P11_rear_gate').Shape.common(anchor)
report={'raw_factory_budget_mm':raw,'same_unit_termination_mm':termination,'factory_bare_included':True,'electrical_cut':None,'exterior_path_mm':[raw[0]-termination,raw[1]-termination],'project_R_center':R,'project_OD':3.1,'profile_radius_including_margin':1.95,'working_tangent_interval_X':[a0,a1],'whole_entry_orientation':{'P_SYS_normal_out':[1,0,0],'entry_face_X':136,'cover_bounds':[114,25.5,59.625,136,62.5,70.625],'lever_access':[0,0,1]},'source_exit_assumption':[106,67,65.125],'receiver_entry_assumption':[136,42.2,65.125],'profile_spacing':24.8,'uncut_surplus':'stored in same-unit U return, not discarded and not additional branch; full84.5..94.5','continuous_cover_method':'analytic semicircle+tangent construction; full circular profile and continuous 5mm arc translation; compound may self-overlap, not printed hardware','primary_mouths':'whole same-face known; individual mouth/height/strip stop UNKNOWN, bounded prototype FIT datum; conditional planned route not delivered fit','qualified_source_planning_only':True,'planned_end_registration':{'FHAC_face_region':[106,56,55,106,78,75.25],'WAGO_face_region':[136,25.5,59.625,136,62.5,70.625],'condition':'actual exit and one occupied chamber must fit phase2 aligned lines without violating all profiles and this raw-unit budget'},'P11_root_witness_mm3':realanchor.Volume,'P11_future_load_route':'actual POSbase root X100..107 Y79..83 -> outside battery Lwing -> common P_SYS/REAR/FHAC shelves; root35/49, cap/nutfeeds and bank lowerdogleg stay protected. Keeper design follows whole-region acceptance, not automatic current print release.'}
(P/'power-face-full-uncut-stock-plan.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())
D.recompute();D.save()
# Named local whole unit risk: does storing full selected length hit actual F_AUX or other bought/module supports? No old field scans.
checks=[]
for n in ['PBAY_F_AUX','PBAY_P_REAR','PBAY_F_PI','PBAY_P_SYS','P11_rear_gate','P06_S0_shared_panel','P19_BATTERY_MTA_SHARED_CARRIER']:
 o=D.getObject(n)
 if not o:continue
 s=o.Shape
 if not cover.BoundBox.intersect(s.BoundBox):
  checks.append(dict(object=n,bounds_separate=True,scope='numeric whole cover cull'));continue
 # Own source/receiver entry contains the proper terminal region; do not grant blanket Own to unrelated material.
 if n in ['PBAY_F_PI','PBAY_P_SYS']:
  checks.append(dict(object=n,scope='endpoint region requires actual mouth registration FIT; not foreign-material PASS'));continue
 checks.append(dict(object=n,allocated_profile_common_mm3=cover.common(s).Volume,min_distance=cover.distToShape(s)[0],operands_valid=[cover.isValid(),s.isValid()]))
(P/'power-full-uncut-local-gates.json').write_bytes((json.dumps(checks,indent=2)+'\n').encode())
print(json.dumps({'tangent_interval':[a0,a1],'raw':raw,'exterior':[raw[0]-termination,raw[1]-termination],'actual_root_witness':realanchor.Volume,'checks':checks}))
