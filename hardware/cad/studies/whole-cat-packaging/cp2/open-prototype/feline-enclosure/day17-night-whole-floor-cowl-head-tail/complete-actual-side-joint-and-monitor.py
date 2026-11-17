import FreeCAD as A,Part,json,math,time
from pathlib import Path
D=A.ActiveDocument;V=A.Vector;P=Path(__file__).parent
def box(x,y,z,a,b,c):return Part.makeBox(a,b,c,V(x,y,z))
def run():
 t=time.perf_counter();D.save();f=D.getObject('FC_F_NEG');r=D.getObject('FC_R_NEG');old=f.Shape.copy();cut=box(77.99,-117,100.99,10,17,8.02);retired=old.common(cut);q=old.cut(cut)
 # Actual available section X78..80/Z142..142.2: Y-107.096..-105.549, COM-106.323.
 # Relocate the COMPLETEjoint to that real wall, outside S0key circularaccess.
 lip=box(78,-105.5,138,10,2.5,8);root=box(78,-109,138,2,8.5,8);outer=box(80,-109,138,8,3.5,8)
 ff=q.fuse(lip).fuse(root)
 cage=box(80.4,-103,138.4,7.2,3.6,7.2).cut(box(81.8,-103.2,140,4.4,4.2,7))
 ff=ff.fuse(cage);rr=r.Shape.fuse(outer).cut(lip)
 bore=Part.makeCylinder(1.15,20,V(84,-116,142),V(0,1,0));ff=ff.cut(bore).removeSplitter();rr=rr.cut(bore).removeSplitter();f.Shape=ff;r.Shape=rr
 # Fullstandard M2x10 replaces oldwholejoint; never head-only shift.
 ns={'__file__':str(P/'finish-cowl-real-joints-and-port-side.py')};exec((P/'finish-cowl-real-joints-and-port-side.py').read_text(encoding='utf-8').split('def run():')[0],ns);ns['steel']('CJ_SIDE_N',[84,-109.5,142],[0,1,0],10,6.5)
 # Actual monitor topkeeper/full2M2x10, side feed before offering module.
 op=D.getObject('OP_COMMON_REMOVABLE_OPERATOR_PANEL');bar=box(106,-94,133,45,7,2)
 for i,x in enumerate([107,150]):
  # Full washer bearing and open side-fed nut; printedthread never assumed.
  bore=Part.makeCylinder(1.15,15,V(x,-90.5,123));op.Shape=op.Shape.cut(bore).cut(box(x-3,-94.5,126,6,8,1.8)).removeSplitter();bar=bar.cut(bore)
  ns['steel']('OP_MONITOR_M2_'+str(i),[x,-90.5,135.5],[0,0,-1],10,7.4)
 ob=D.getObject('OP_MONITOR_REMOVABLE_TOPKEEPER') or D.addObject('PartDesign::Feature','OP_MONITOR_REMOVABLE_TOPKEEPER');ob.Shape=bar;ob.ViewObject.ShapeColor=(.13,.135,.145)
 D.recompute();D.save()
 out={'retired_old_unbuilt_joint_volume':retired.Volume,'newjoint_available_actual_section_Y':[-107.096,-105.549],'negative_parts':[{'n':o.Name,'valid':o.Shape.isValid(),'solids':len(o.Shape.Solids),'v':o.Shape.Volume} for o in [f,r,op,ob]],'separate_cowl_common':ff.common(rr).Volume,'realwholejoint':'M2x10/head2/washer.5/rear3.5+front2.5/washer.5/nut1.6/tip1.4. Y+ entry outside-109.5, full nut sidefeed.','monitor':'Fullcase+2X unchanged after previous move; removable topkeeper, full2M2x10; safeplastic rim/tolerancesFIT3, no screenpressureclaim','physicalPASS':False,'wholekit':False,'seconds':time.perf_counter()-t}
 (P/'whole-cowl-joint-and-monitor-completed.json').write_bytes((json.dumps(out,indent=2)+'\n').encode());print(json.dumps(out))
run()
