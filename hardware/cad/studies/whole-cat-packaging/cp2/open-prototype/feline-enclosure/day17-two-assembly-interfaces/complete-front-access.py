import FreeCAD as A,Part,json,time,math
from pathlib import Path
D=A.ActiveDocument;V=A.Vector;P=Path(__file__).parent
def put(n,x):(P/n).write_bytes((json.dumps(x,indent=2,ensure_ascii=False)+'\n').encode())
def box(x,y,z,a,b,c):return Part.makeBox(a,b,c,V(x,y,z))
def capsule(x,y0,y1,z,r,h):
 q=Part.makeCylinder(r,h,V(x,y0,z)).fuse(Part.makeCylinder(r,h,V(x,y1,z)))
 return q.fuse(box(x-r,min(y0,y1),z,2*r,abs(y1-y0),h))
def run():
 t=time.perf_counter();D.save();o=D.getObject('A17_INTEGRAL_FRONT_DECK_AND_N1');q=o.Shape.copy();before=q.copy()
 for x in [-80,-70]:
  for y in [-22.5,22.5]:q=q.cut(Part.makeCylinder(2.75,26,V(x,y,48.52)))
 q=q.removeSplitter();o.Shape=q
 # ExistingactualH01sourceactors enabled, notduplicatephysicalimports/newsteelcounts.
 for i in range(8):D.getObject('H01_source_M2p5x16_flat_'+str(i)).ViewObject.Visibility=True
 D.recompute();D.save();rows=[]
 for i,(x,y) in enumerate([(x,y) for x in [-80,-70] for y in [-22.5,22.5]]):
  bolt=D.getObject('H01_source_M2p5x16_flat_'+str(i)).Shape;b=bolt.BoundBox;assert abs(b.ZMax-48.52)<1e-5
  sy=1 if y>0 else -1;yentry=sy*31
  lateral=capsule(x,y,yentry,56.5,1.25,14.75).fuse(capsule(x,y,yentry,71.25,2.5,1.25))
  vertical=bolt.fuse(Part.makeCylinder(1.25,40,V(x,y,32.52))).fuse(Part.makeCylinder(2.5,23.98,V(x,y,48.52)))
  p=V(x,y,48.52);a=V(0,sy*math.sin(math.radians(20)),math.cos(math.radians(20)))
  driver=Part.makeCylinder(1,4,p,a).fuse(Part.makeCylinder(1.5,80,p+a*4,a))
  rr={'axis':[x,y],'actual_sourcebolt':D.getObject('H01_source_M2p5x16_flat_'+str(i)).Name,'sourcebolt_bounds':str(b),'final_bolt_print_common':q.common(bolt).Volume,'whole_bolt_lateral_stock_common':q.common(lateral).Volume,'whole_bolt_vertical_insertion_common':q.common(vertical).Volume,'outboard20deg_driver_common':q.common(driver).Volume,'order':'Barefrontfirst. Stagewhole16mmbolt atheadtop72.5 throughoutboardY31..22.5, THENlowerZ24 tooriginalseat. Tightenfromoutboard20deg socketballtool BEFOREboards/banks. Actualdrive/revision/threadFIT1.'}
  rows.append(rr);put('front-full-fastener-and-access.json',{'rows':rows,'cursor':len(rows),'all':4,'wholePASS':False})
 # Finite matched structuralparting, no oldglobalproofreplay.
 parting=[]
 for n in ['P01_load_rail','P01_load_rail_instance2','P03_rear_deck_integrated_load_yoke','P04_deck_splice','P04_deck_splice_instance2']:
  other=D.getObject(n)
  if other:
   c=q.common(other.Shape);parting.append({'part':n,'common':c.Volume,'valid':c.isValid(),'nominal_contact_or_original_parting':'OriginalP01bearing/P03split/P04splices. No separateprintfusion.'})
 put('front-access-completion.json',{'rows':rows,'parting':parting,'new_sourceheadwell_top':74.52,'original16mmfastener_sourcegeometry_unchanged':True,'whole_source_hardware_not_inventoryproof':True,'source_boughtframe_nevercut':True,'additional_PRINT_ONLY_void_volume':before.Volume-q.Volume,'remaining_sourcefloor_annularweb_nominal':1.9,'nominalheadwellradialclearance_min':.25,'driver':'Oneplanned1.5mmhexballsocket-compatibletype/full3mmshank, sourceheadactualdrive stillFIT1/no purchasedSKUclaim','frontloadroute':'ONEintegralN1+P02 ->4originalfrontH01countersunksets ->P01 ->sourceWAVEGOaxes. Front2legacydeckedgejawprints no longerneededforN1/P02retention; physicaloldhardwarekept/notdiscarded, no purchase. Rearseparateinterface unchanged/unqualifiedunlesspriorreceived.','retired_UNBUILT_frontclamp_roles':['P16_front_lower_jaw','CL_Fp_lower','front2oldM3clampsonlyasneeded_by_old_separateframe'], 'protected_material_except_originalsourcewell_tools':True,'wholekit':False,'physicalPASS':False,'seconds':time.perf_counter()-t})
 q.exportBrep(str(P/'A17_integral_front_world.brep'));D.save();print(json.dumps({'rows':rows,'parting':parting,'seconds':time.perf_counter()-t}))
run()
