"""N01 constructive underframe carrier volume, not a production print release.

Same selected components; native additive/pocket details, tie slots, physical fit
and pull/creep checks belong to N03/phase2. Retains the existing battery-plate
hole axes and preserves F0+1.25. No individual harness paths are generated.
"""
import FreeCAD as A
import Part


def build_carrier(world, cases):
 piecesC26={}
 def bb(n,lo,hi):piecesC26[n]=Part.makeBox(*(b-a for a,b in zip(lo,hi)),A.Vector(*lo))
 bb('OpenFloorLeft',[-21.25,-18,-40.5],[-19.25,18,-38.5])
 bb('OpenFloorRight',[38.5,-18,-40.5],[40.5,18,-38.5])
 bb('OpenFloorNEG',[-21.25,-18,-40.5],[40.5,-16,-38.5])
 bb('OpenFloorPOS',[-21.25,16,-40.5],[40.5,18,-38.5])
 bb('P_FRONT_BaseRailNEG',[-21.25,-11,-40.5],[20,-8,-38.5])
 bb('P_FRONT_BaseRailPOS',[-21.25,8,-40.5],[20,11,-38.5])
 bb('OpenFloorMid',[18,-18,-40.5],[20,18,-38.5])
 for side,(x0,x1) in [('left',(-21.25,-19.25)),('right',(38.5,40.5))]:
  for sign in [-1,1]:
   y0,y1=(13,16) if sign>0 else(-16,-13);bb('Post_'+side+str(sign),[x0,y0,-40.5],[x1,y1,-5.5]);y0,y1=(13,38) if sign>0 else(-38,-13);bb('UpperCross_'+side+str(sign),[x0,y0,-5.5],[x1,y1,-1.5])
 for sign in [-1,1]:
  y0,y1=(34,38) if sign>0 else(-38,-34);bb('LongBearingRail'+str(sign),[-21.25,y0,-5.5],[64,y1,-1.5]);y0,y1=(20,38) if sign>0 else(-38,-20);bb('RearRootBridge'+str(sign),[60,y0,-5.5],[68,y1,-1.5]);piecesC26['RearPad'+str(sign)]=Part.makeCylinder(4,4,A.Vector(64,sign*23.5,-5.5))
 bb('UpperCaseShelf',[-21.25,-32.5,-17.25],[4.5,32.5,-15.25])
 bb('FL_P_CaseShelf',[17.25,-11,-27.5],[38.5,11,-25.5])
 for sign in [-1,1]:
  y0,y1=(10,16) if sign>0 else(-16,-10);bb('MidBridge'+str(sign),[33,y0,-27.5],[40.5,y1,-25.5])
 bb('P_FRONT_JacketBed',[-4.6,11,-37.1],[12.6,20,-35.1]);bb('P_FRONT_BedRoot',[6,11,-39],[10,15,-35.1])
 bb('FL_P_JacketBed',[8,-18.5,-24.6],[29,-9.5,-22.6]);bb('FL_P_BedRoot',[24,-11.5,-25.5],[28,-9.5,-22.6])
 for sign in [-1,1]:
  y0,y1=(-28.5,-3.5) if sign<0 else(3.5,28.5);bb('UpperJacketBed'+str(sign),[6.5,y0,-13.8],[15.5,y1,-11.8]);y0,y1=(-30,-28) if sign<0 else(28,30);bb('UpperBedRoot'+str(sign),[3,y0,-17.25],[8.5,y1,-11.8])
 raw=list(piecesC26.values())[0].multiFuse(list(piecesC26.values())[1:]).removeSplitter();raw.check(True)
 f0keep=world['Ref_Material_F0_CP2_0_0'].Solids[0].makeOffsetShape(1.25,.0001);f0keep.check(True)
 shaped=raw.cut(f0keep)
 for n in ['Ref_Material_P0_SideLeft22_0_0','Ref_Material_P0_SideRight22_0_0']:world[n].check(True);shaped=shaped.cut(world[n])
 for sign in [-1,1]:shaped=shaped.cut(Part.makeCylinder(1.45,7,A.Vector(64,sign*23.5,-7)))
 # Pocket only our printed study around complete current case allocations.
 # Intentional base/side interfaces may touch; positive-volume penetration is forbidden.
 for case in cases.values():shaped=shaped.cut(case)
 shaped=shaped.removeSplitter();shaped.check(True)

 return shaped, piecesC26
