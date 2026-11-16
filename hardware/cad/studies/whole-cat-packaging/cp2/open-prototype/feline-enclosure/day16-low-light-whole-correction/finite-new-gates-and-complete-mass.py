import FreeCAD as A,FreeCADGui as G,Part,json,math,time
from pathlib import Path
D=A.ActiveDocument;P=Path(__file__).parent;V=A.Vector;t=time.perf_counter()
def box(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
def bb(s):
 b=s.BoundBox;return[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
front=D.getObject('LOW_FRONT_LOAD_GRID').Shape;rear=D.getObject('LOW_REAR_LOAD_GRID').Shape
# Actualrear P01 step top41.52, not fullbbox45.52. Real4mm lands close thisknownsource interface.
for y in [-22.5,22.5]:rear=rear.fuse(box(108,y-3,41.52,18,6,4))
for x in [-80,-70,112,122]:
 for y in [-22.5,22.5]:
  cut=Part.makeCylinder(1.4,20,V(x,y,35)).fuse(Part.makeCone(1.25,2.35,1.1,V(x,y,52.42)))
  if x<30:front=front.cut(cut)
  else:rear=rear.cut(cut)
  n='LC_SOURCE_'+str(x)+'_'+str(y);o=D.getObject(n)
  if o:o.Shape=Part.makeCylinder(1.25,18.9,V(x,y,33.52)).fuse(Part.makeCone(1.25,2.35,1.1,V(x,y,52.42)))
D.getObject('LOW_FRONT_LOAD_GRID').Shape=front;D.getObject('LOW_REAR_LOAD_GRID').Shape=rear
# Oldframe standarddemands superseded by actualnewjointsets, not boughtS0metals.
retired=[]
for o in D.Objects:
 if o.Name.startswith(('H01_','H02_','H03_','H04_','H05_','H06_','H07_')):
  o.ViewObject.Visibility=False;retired.append(o.Name)
(P/'source-eight-root-complete-stack.json').write_bytes((json.dumps({'actual_source_axis':[-80,-70,112,122],'y':[-22.5,22.5],'front_P01_top':45.52,'rear_P01_steptop':41.52,'rear_grid_actual4mm_lands_added':True,'fastener':'8M2.5x20COUNTERSUNK nominal includeswholehead, unconfirmedstandarddemand','top':53.52,'tip':33.52,'frame_nominal_entry_belowP01_bottom38p52':5,'actual_source_thread':'physicalP00/source threadFIT, no framecut/drill','obsolete_unbuilt_hardware_demands_retired':retired},indent=2)+'\n').encode())
D.recompute();D.save()
checks=[]
def check(a,b,kind='foreign_nominal',clear=1.25):
 x=D.getObject(a).Shape;y=D.getObject(b).Shape;d=x.distToShape(y)[0]
 r={'a':a,'b':b,'kind':kind,'gap_mm':d,'threshold':clear,'pass_for_scope':d>=clear-1e-6}
 if d<1e-6 and kind=='separate_prints':
  c=x.common(y);r['common_mm3']=c.Volume;r['valid']=c.isValid();r['pass_for_scope']=c.isValid() and abs(c.Volume)<1e-6
 checks.append(r);(P/'bounded-current-whole-gates.json').write_bytes((json.dumps({'checks':checks,'status':'CURRENT_LOCAL_CHECKS_ONLY_NOT_WHOLEPASS','cursor':len(checks)},indent=2)+'\n').encode())
for a,b in [('Speaker','Pi_GPIO1992_factory_female'),('MAIN_UNSHRUNK_FAMILY_SCOPE','S1_NKK_S821_installed'),('AUX_FULL9p5_POPULATED_SCOPE','S1_NKK_S821_installed'),('PBAY_P_SYS','LOW_COMMON_LOGIC_SHELF'),('PBAY_P_REAR','LOW_COMMON_LOGIC_SHELF'),('Monitor_MOD05015','MG92B_Tail'),('LC_LOGIC_R_fullscrew','AUX_FULL9p5_POPULATED_SCOPE')]:check(a,b)
check('LOW_FRONT_LOAD_GRID','LOW_REAR_LOAD_GRID','separate_prints',0)
check('LC_CURVED_BODY_F_NEG','OLA_REAL_BACK_COVER')
check('LC_CSI200_NEUTRAL_OCCUPIED_FLAT','HEAD_MOVING_SENSOR_FRAME_AND_COVER_SPINE','nominal_named_neckpinch')
# Finite contact viaactual coplanar faces, no invented100strengthgate.
def faces_at(s,z):return [f for f in s.Faces if abs(f.BoundBox.ZMin-z)<1e-5 and abs(f.BoundBox.ZMax-z)<1e-5]
contacts=[]
for n,plane,partner in [('LOW_HEAD_SOURCE_BRIDGE',48.52,'LOW_FRONT_LOAD_GRID'),('LOW_TAIL_COMMON_SOURCE_ROOT',48.52,'LOW_REAR_LOAD_GRID'),('LOW_PI_COMMON_TRAY',48.52,'LOW_FRONT_LOAD_GRID')]:
 aa=faces_at(D.getObject(n).Shape,plane);b=faces_at(D.getObject(partner).Shape,plane);area=Part.makeCompound(aa).common(Part.makeCompound(b)).Area if aa and b else 0
 contacts.append({'a':n,'b':partner,'contact_planeZ':plane,'actual_face_common_area_mm2':area,'strengthPASS':False})
(P/'actual-useful-separate-bearing-contacts.json').write_bytes((json.dumps(contacts,indent=2)+'\n').encode())
# Effective print membership exactly declared; no masscreditfor vanishedreartechnicalfailure.
base=json.loads((P.parent/'day16-low-light-whole-concept/whole-low-layout-effectivity.json').read_text());iface=json.loads((P/'whole-interface-realization.json').read_text())
selected=set(base['retained_print_names']+base['new_prints']+iface['new_prints'])
selected-=set(n for n in selected if n.startswith('LOW_THIN_BODY_') or n in ['OLA_REAL_FRONT_MASK','LOW_WAGO_NEG_OPEN_COMMON_RAIL','LOW_WAGO_POS_OPEN_COMMON_RAIL'])
selected.update(['LC_CURVED_BODY_'+q for q in ['F_NEG','F_POS','R_NEG','R_POS']]);selected.add('LC_ORBIT_CHEEK_FRONT_MASK')
rows=[]
for n in sorted(selected):
 s=D.getObject(n).Shape;vol=s.Volume;c=sum((q.CenterOfMass*q.Volume for q in s.Solids),V())/vol if vol else V();rows.append({'name':n,'volume_mm3':vol,'PETG_full_g':vol*.00127,'COM_mm':list(c),'bounds_mm':bb(s),'solids':len(s.Solids)})
steel=[o for o in D.Objects if o.Name.startswith('LC_') and hasattr(o,'CorrectionScope') and o.CorrectionScope=='steel'];steelg=sum(o.Shape.Volume for o in steel)*.00785
m={'same_PETG_density_g_cm3':1.27,'baseline70prints_g':1778.501,'firstconcept51_g':1114.852143,'current_selected_prints_g':sum(q['PETG_full_g'] for q in rows),'modeled_print_delta_g':1778.501-sum(q['PETG_full_g'] for q in rows),'current_new_steel_demand_g_at7p85':steelg,'steel_current_count':len(steel),'net_whole_mass_delta':'UNKNOWN: oldhardware demand mass notfrozen; missingremainingretention/skinfasteners/clothdelivery/allwiremass','future_mounting_material_allowance':'not bounded; do notcash664g','rows':rows,'physicalPASS':False}
(P/'same-density-complete-correction-mass.json').write_bytes((json.dumps(m,indent=2)+'\n').encode())
print(json.dumps({'checks':checks,'contacts':contacts,'printmass':m['current_selected_prints_g'],'printdelta':m['modeled_print_delta_g'],'steelg':steelg,'seconds':time.perf_counter()-t}))
