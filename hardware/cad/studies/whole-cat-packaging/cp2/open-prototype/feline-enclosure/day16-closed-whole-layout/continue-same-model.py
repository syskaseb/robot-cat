import FreeCAD as A,FreeCADGui as G,Part,json,math,time
from pathlib import Path
from datetime import datetime,timezone
V=A.Vector;P=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day16-closed-whole-layout')
def box(x,y,z,a,b,c):return Part.makeBox(a,b,c,V(x,y,z))
def cyl(x,y,z,r,h,axis=None):return Part.makeCylinder(r,h,V(x,y,z),axis or V(0,0,1))
def run():
 D=A.getDocument('DAY16_CLOSED_WHOLE_PROPOSAL');S=A.getDocument('DAY15_WHOLE_REAR_LAYER');T=time.perf_counter()
 # Technical representation repair: source cosmetic nose may already be NULL after opticalopening. No physical part changed.
 null=[]
 for o in D.Objects:
  if o.Name.startswith('Ola_') and hasattr(o,'Shape') and o.Shape.isNull():o.ViewObject.Visibility=False;null.append(o.Name)
 D.Label='DAY16 CLOSED WHOLE / SAVED SAME GEOMETRY AFTER NULL COSMETIC';D.recompute();D.saveAs(str(P/'closed-whole-layout.FCStd'))
 lower=D.getObject('P11_rear_gate').Shape;upper=D.getObject('P11_REMOVABLE_UPPER_CROSSMEMBER').Shape;old=S.getObject('P11_rear_gate').Shape
 bore=cyl(90,-83,130,1.7,23,V(1,0,0)).fuse(cyl(90,83,130,1.7,23,V(1,0,0)));expected=old.cut(bore);combined=lower.fuse(upper)
 r=dict(utc=datetime.now(timezone.utc).isoformat(),technical_only_null_cosmetic_hidden=null,no_geometry_family_rerun=True,P11_material=dict(source_expected_missing=expected.cut(combined).Volume,unexpected_added=combined.cut(expected).Volume,part_common=lower.common(upper).Volume,lower_solids=len(lower.Solids),upper_solids=len(upper.Solids)),gate=[],first_falsifier=None)
 arms=[box(-141,y,132.5,43,6,5.5) for y in [-76,70]];r['headroot']=dict(actual_root_arm_common=[s.common(S.getObject('P10_front_gate').Shape).Volume for s in arms],source_P10_missing=S.getObject('P10_front_gate').Shape.cut(D.getObject('P10_front_gate').Shape).Volume,new_P10_solids=len(D.getObject('P10_front_gate').Shape.Solids),MG_horn_and_mountingdatums_physicalFIT3=True,independent8mm_bearing_pin_NOTservooutput=True,retainer_and_movingfork_fulljoint_detail_OPEN=True)
 for n,s in [('root0',cyl(103,35,115,4.25,35)),('root1',cyl(103,49,115,4.25,35)),('M2_MAIN',cyl(89.321,24.159,122.8748,2.2,25)),('M2_AUX',cyl(101.159,70.241,122.87,2.2,25))]:
  c=s.common(lower);row=dict(name=n,target='ACTUAL_NEW_LOWER_P11_CAP_ABSENT',common=c.Volume,valid=c.isValid());r['gate'].append(row)
  if c.Volume>1e-5 or not c.isValid():r['first_falsifier']=row;break
 if not r['first_falsifier']:
  for n in ['AUX_FULL9p5_POPULATED_SCOPE','MAIN_UNSHRUNK_FAMILY_SCOPE','AUX_all_terminal_field_FIT2','MAIN_all_terminal_field_FIT2']:
   s=D.getObject(n).Shape;b=s.BoundBox;c=upper.common(box(b.XMin,b.YMin,0,b.XLength,b.YLength,200));empty=c.isNull() or c.Volume<1e-5;gap=None if empty else c.BoundBox.ZMin-b.ZMax;row=dict(name='CAP_CONTINUOUS_PLUS_Z_CLOSING',other=n,emptyXYcolumn=empty,min_gap=gap,valid=c.isValid(),clear=empty or gap>=1.25-1e-6);r['gate'].append(row)
   if not row['clear']:r['first_falsifier']=row;break
 if not r['first_falsifier'] and not all(x>1e-5 for x in r['headroot']['actual_root_arm_common']):r['first_falsifier']=dict(name='HEAD_NEW_LOAD_BRIDGE_NO_ACTUAL_P10_ROOT',values=r['headroot']['actual_root_arm_common'])
 r['print_plan']=[]
 for o in D.Objects:
  if not o.Name.startswith(('CLOSED_BODY_','CLOSED_HEAD_')):continue
  b=o.Shape.BoundBox;dims=[b.XLength,b.YLength,b.ZLength];isbody=o.Name.startswith('CLOSED_BODY_');xy=[dims[0],dims[2]] if isbody else dims[:2];h=dims[1] if isbody else dims[2]
  r['print_plan'].append(dict(part=o.Name,geometry=dims,solids=len(o.Shape.Solids),orientation='Y seam down' if isbody else 'Z140 seam down',brim_per_side6=True,vertical_removable_support_projection='Inside fullpart XY projection; explicit setupoccupiedregion includes6mmbrim. Open seam permits supportremoval. No slicer/printPASS.',occupiedXYZ=[xy[0]+12,xy[1]+12,h],under256=max(xy[0]+12,xy[1]+12,h)<256,print_release=False))
 r['status']='WHOLE_PROPOSAL_FIRST_FALSIFIER_HOLD_NO_SECOND_FAMILY' if r['first_falsifier'] else 'NEW_REAL_PARTING_INITIAL_TOOL_AND_CAP_CLOSURE_CLEAR_SCOPED_WHOLE_STILL_UNQUALIFIED'
 r['whole_feasible']=False;r['physical_pass']=False;r['actual_fit_cut_slack']=None;r['seconds']=time.perf_counter()-T
 (P/'first-whole-falsifier-and-source-proof.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
 rows=[]
 for z in [130,150]:
  for n in ['P11_rear_gate','P11_REMOVABLE_UPPER_CROSSMEMBER']+[o.Name for o in D.Objects if o.Name.startswith(('CLOSED_BODY_','CLOSED_HEAD_'))]+['AUX_FULL9p5_POPULATED_SCOPE','MAIN_Pololu4853']:
   s=D.getObject(n).Shape
   if s.BoundBox.ZMin>z or s.BoundBox.ZMax<z:continue
   sec=s.section(Part.makePlane(500,250,V(-270,-120,z)));rows.append(dict(z=z,name=n,lines=[[[v.x,v.y] for v in e.discretize(Deflection=.2)] for e in sec.Edges]))
 (P/'whole-assembly-sections.json').write_text(json.dumps(rows)+'\n',encoding='utf-8')
 for o in D.Objects:
  if hasattr(o.ViewObject,'ShapeColor') and (o.Name.startswith(('FEED_','KEY_','CAPTURE_','DIRECT_','VIEW_','AL_','CF_','P12_FULL_OD6','P12_UNCHANGED_R24')) or 'section' in o.Name.lower()):o.ViewObject.Visibility=False
 D.Label='DAY16 CLOSED WHOLE / '+r['status'];D.recompute();D.save();A.setActiveDocument(D.Name)
 print(json.dumps(dict(status=r['status'],objects=len(D.Objects),material=r['P11_material'],headroot=r['headroot'],first=r['first_falsifier'],printplan=r['print_plan'],seconds=r['seconds'])))
run()
