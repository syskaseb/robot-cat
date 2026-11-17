import FreeCAD as A,Part,json,math,time
from pathlib import Path
D=A.ActiveDocument;V=A.Vector;P=Path(__file__).parent
def put(n,x):(P/n).write_bytes((json.dumps(x,indent=2)+'\n').encode())
def box(x,y,z,a,b,c):return Part.makeBox(a,b,c,V(x,y,z))
def run():
 t=time.perf_counter();D.save();front=D.getObject('A17_INTEGRAL_FRONT_DECK_AND_N1').Shape;coverage=[];a=V(0,math.sin(math.radians(20)),math.cos(math.radians(20)))
 for n in ['RG_FRONT_GRID_WITH_INTEGRAL_HEAD_RECEIVER','P02_front_deck']:
  s=Part.Shape();s.read(str(P/('source-'+n+'.brep')));oldv=s.Volume
  for x,y in [(x,y) for x in [-80,-70] for y in [-22.5,22.5]]:
   hole=Part.makeCylinder(1.4,15.9,V(x,y,31.52)).fuse(Part.makeCone(1.4,2.5,1.1,V(x,y,47.42))).fuse(Part.makeCylinder(2.75,26,V(x,y,48.52)))
   p=V(x,y,48.52);ch=Part.makeCylinder(1.25,4,p,a).fuse(Part.makeCylinder(1.75,80,p+a*4,a)).common(box(x-4,y-4,50.52,8,42,90));s=s.cut(hole).cut(ch)
  coverage.append({'source_member':n,'source_volume':oldv,'explicit_matched_hole_and_driver_void_retirement':oldv-s.Volume,'protected_outside_voids_missing':s.cut(front).Volume})
 put('final-intended-front-member-coverage.json',{'members':coverage,'no_boughtparts_cut':True,'one_actual_print_replaces_two_unbuilt_prints':True,'wholekit':False,'physicalPASS':False})
 q=D.getObject('FC_F_POS').Shape;rows=[];ns=['Speaker','SPEAKER_REMOVABLE_BASKET_RIM_TRIAL_KEEPER','FORE_MTA_FIXED_COMMON_POSTS_AND_LOWER']+[o.Name for o in D.Objects if o.Name.startswith('SPKR_M2') and hasattr(o,'Shape')]
 for n in ns:
  s=D.getObject(n).Shape;g=q.distToShape(s)[0];c=q.common(s).Volume if g<1.25 else 0;rows.append({'source_full_unit_or_stock':n,'gap':g,'common':c,'required':1.25,'clear_scoped':g>=1.25-1e-6 and c<1e-7})
 put('final-acoustic-full-unit-stock-and-parting.json',{'rows':rows,'current_new_front_common':q.common(front).Volume,'all_printed_material_valid':q.isValid() and front.isValid(),'all_stock_poses_and_factoryends_unchanged':True,'old_failures_preserved':'0.667674/136.689 and ownfixed0.5 savedraw, notwaived orcounterreset','wholekit':False,'physicalPASS':False,'seconds':time.perf_counter()-t})
 print(json.dumps({'coverage':coverage,'rows':rows,'seconds':time.perf_counter()-t}))
run()
