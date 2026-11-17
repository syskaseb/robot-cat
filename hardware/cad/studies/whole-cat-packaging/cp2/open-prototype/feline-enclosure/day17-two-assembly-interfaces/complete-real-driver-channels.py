import FreeCAD as A,Part,json,math,time
from pathlib import Path
D=A.ActiveDocument;V=A.Vector;P=Path(__file__).parent
def box(x,y,z,a,b,c):return Part.makeBox(a,b,c,V(x,y,z))
def put(n,x):(P/n).write_bytes((json.dumps(x,indent=2)+'\n').encode())
def run():
 t=time.perf_counter();D.save();o=D.getObject('A17_INTEGRAL_FRONT_DECK_AND_N1');old=o.Shape.copy();old.exportBrep(str(P/'front-before-real-driver-channels.brep'));q=old;fields=[];cuts=[]
 # ONEaccessible +Y toolface avoids fixed P_SYS loadbeam at negativeY.
 # Keepfull80mmshank/20deg/nominal1.5mmhex-compatibletip; no shorter-toolgreen.
 a=V(0,math.sin(math.radians(20)),math.cos(math.radians(20)))
 for x,y in [(x,y) for x in [-80,-70] for y in [-22.5,22.5]]:
  p=V(x,y,48.52);actual=Part.makeCylinder(1,4,p,a).fuse(Part.makeCylinder(1.5,80,p+a*4,a));clear=Part.makeCylinder(1.25,4,p,a).fuse(Part.makeCylinder(1.75,80,p+a*4,a));cut=clear.common(box(x-4,y-4,50.52,8,42,90));q=q.cut(cut);fields.append((x,y,actual));cuts.append(cut)
 q=q.removeSplitter();o.Shape=q;D.recompute();D.save();rows=[]
 for x,y,s in fields:rows.append({'axis':[x,y],'tool_direction':[0,a.y,a.z],'complete_same80mm_shank_common':q.common(s).Volume,'fixture_clearance_nominal':.25,'phase':'BEFOREboardsandterminalbanks; samewholepreterminatedE1kit later, no virtualunplug'})
 # Exactpreservedprimaryfloor+sourcecounterseats; accesscutsstartabove50.52.
 low=old.common(box(-150,-100,30,250,200,20.52));protectedlow=low.cut(q).Volume
 # Actualfinite bearingarea tosourceP01, separateP03/P04 relations inherited byremovalsubset.
 contacts=[]
 for n in ['P01_load_rail','P01_load_rail_instance2']:
  c=q.common(D.getObject(n).Shape);contacts.append({'source':n,'common_volume':c.Volume,'finite_bearing_area':c.Area,'valid':c.isValid()})
 put('front-real-driver-channels-completed.json',{'rows':rows,'native_valid':q.isValid(),'solids':len(q.Solids),'retired_print_only_toolobstruction_mm3':old.Volume-q.Volume,'primary_floor_and_counterseat_below50p52_missing':protectedlow,'P01_contacts':contacts,'all_source_H01_stock_and_insertion_checks_reused':'priorcommon0 + thisoperation ONLYremovesmaterial; all4full16mmunits unchanged','sourceP03P04parting_checks_reused':'prior0common + removalsubset','activePCB_mounts':'PiY-76..-66 unaffected; PCA/E1bearingY<=20 atZ>100, negativebolt +YfieldendsY<8 andpositivebolt +YfieldstaysY>40 there; no mountingannuli removed','old_outboard_PSYS_beam24p498_failure':'preservedactual-driver-obstruction-source.json; chooseone+Yaccessface, notshortertool/cutloadbeam','wholekit':False,'physicalPASS':False,'seconds':time.perf_counter()-t})
 q.exportBrep(str(P/'A17_integral_front_world.brep'));D.save();print(json.dumps({'rows':rows,'primaryfloorMissing':protectedlow,'contacts':contacts,'valid':q.isValid(),'solids':len(q.Solids),'seconds':time.perf_counter()-t}))
run()
