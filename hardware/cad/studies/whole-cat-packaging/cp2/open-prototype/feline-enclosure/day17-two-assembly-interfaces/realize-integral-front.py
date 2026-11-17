import FreeCAD as A,Part,json,time
from pathlib import Path
D=A.ActiveDocument;V=A.Vector;P=Path(__file__).parent
def put(n,x):(P/n).write_bytes((json.dumps(x,indent=2,ensure_ascii=False)+'\n').encode())
def box(x,y,z,a,b,c):return Part.makeBox(a,b,c,V(x,y,z))
def bb(s):
 b=s.optimalBoundingBox(False,True);return[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def run():
 t=time.perf_counter();D.save();n=D.getObject('RG_FRONT_GRID_WITH_INTEGRAL_HEAD_RECEIVER').Shape.copy();d=D.getObject('P02_front_deck').Shape.copy();u=n.fuse(d).removeSplitter();u.exportBrep(str(P/'front-integral-before-source-bores.brep'))
 # SAME boughtsource4frontaxes. Restorefullclearshaft/countersunkseat+actualopenheadwell.
 # Never cut a boughtframe; original16mmscrew/threads remainconditionalP00.
 tools=[];axes=[]
 for x in [-80,-70]:
  for y in [-22.5,22.5]:
   tool=Part.makeCylinder(1.4,15.9,V(x,y,31.52)).fuse(Part.makeCone(1.4,2.5,1.1,V(x,y,47.42))).fuse(Part.makeCylinder(2.75,21.5,V(x,y,48.52)))
   tools.append(tool);axes.append([x,y])
 q=u
 for c in tools:q=q.cut(c)
 q=q.removeSplitter();o=D.addObject('PartDesign::Feature','A17_INTEGRAL_FRONT_DECK_AND_N1');o.Shape=q;o.Label='CURRENT one print: complete frontdeck + N1 / conditional sourcefit';o.ViewObject.ShapeColor=(.24,.28,.31)
 for nm in ['RG_FRONT_GRID_WITH_INTEGRAL_HEAD_RECEIVER','P02_front_deck']:
  a=D.getObject(nm);a.ViewObject.Visibility=False;a.Label='RETIRED separateprint reference / '+nm
 D.recompute();D.save();q.exportBrep(str(P/'A17_integral_front_world.brep'))
 put('front-integral-checkpoint.json',{'new_current_print':o.Name,'retired_separateprint_roles':['P02_front_deck','RG_FRONT_GRID_WITH_INTEGRAL_HEAD_RECEIVER'],'one_real_print_NOT_fictitious_separatefusion':True,'boughtparts_fused':[],'source_axes':axes,'bores':'R1.4throughshaft+source90degcone1.4to2.5@47.42..48.52+R2.75openheadwell48.52..70.02','source_counterseat_annular_floor1p9_retained':True,'no_new_hardware':True,'P00_actualthreadandrevision_still_required':True,'prior_summed_volume':n.Volume+d.Volume,'source_union_volume':u.Volume,'current_volume':q.Volume,'max_bounds':bb(q),'valid':q.isValid(),'solids':len(q.Solids),'source_overlap_now_single_material_NOT_mass_saving_claim':n.Volume+d.Volume-u.Volume,'floor_and_member_coverage_pending':True,'wholekit':False,'physicalPASS':False,'seconds':time.perf_counter()-t})
 # Sourceoutsideactualfourrestoredholetools mustallremain. Deliberate holesarefunction, notlostmember.
 pn=n.copy();pd=d.copy()
 for c in tools:pn=pn.cut(c);pd=pd.cut(c)
 p03=D.getObject('P03_rear_deck_integrated_load_yoke').Shape
 r={'protected_N1_missing':pn.cut(q).Volume,'protected_P02_missing':pd.cut(q).Volume,'N1_only_inside_source_bore_material_retired':n.Volume-pn.Volume,'P02_only_inside_source_bore_material_retired':d.Volume-pd.Volume,'separate_front_P03_common':q.common(p03).Volume,'native_valid':q.isValid(),'native_solids':len(q.Solids),'all_full8axes':'4frontrestored/4rearunchanged; no boughtdrill/threadclaim','initial_order':['Openactualseparaterootjaws before offeringONEfrontdeck-frame toactualP01rails','4sourceM2.5fasteners throughfullheadwells BEFOREmodules; original4rearsourceaxes/P03+2P04splices stay','All boardrootfullsets/tools BEFOREbanks. ActualsolderedPCA/E1keptwhole. Pi/sourceGPIO/coolingposesunchanged','Commonoperatorpanel on existing2fullM3sets beforeterminalbanks/latecowl','No virtualintegralprintdetach; rearfloorP03 staysseparatewithoriginalparting'], 'printorientation':'sourceXYZ/minZ0; feetbelowmainfloor need supports up to4mm, doNOTbridge164mmunsupported;8mmplanbrim/supportreserve','wholekit':False,'physicalPASS':False,'seconds':time.perf_counter()-t}
 put('front-integral-member-coverage.json',r);D.save();print(json.dumps(r))
run()
