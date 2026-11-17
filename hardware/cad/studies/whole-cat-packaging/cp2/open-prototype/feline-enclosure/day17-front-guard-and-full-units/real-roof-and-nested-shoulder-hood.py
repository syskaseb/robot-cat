import FreeCAD as A,FreeCADGui as G,Part,json,math,time
from pathlib import Path
P=Path(__file__).parent;D=A.ActiveDocument;V=A.Vector;t0=time.perf_counter()
put=lambda n,j:(P/n).write_bytes((json.dumps(j,indent=2)+'\n').encode())
def bx(x,y,z,a,b,c):return Part.makeBox(a,b,c,V(x,y,z))
def add(n,s,col=(.17,.18,.2),scope='PRINT_MATERIAL_PENDING_LOCAL_FIT'):
 o=D.getObject(n) or D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=col;o.ViewObject.Visibility=True
 if not hasattr(o,'Scope'):o.addProperty('App::PropertyString','Scope')
 o.Scope=scope;return o
D.save();old=D.getObject('HC_BACK_UPPER').Shape.copy();cut=bx(-220,-46,153.5,104,92,100)
# Same precisefunctionalparting, no refinement retry or freewireloft.
raw=old.cut(cut)
put('raw-roof-parting-no-refinement.json',{'isNull':raw.isNull(),'valid':False if raw.isNull() else raw.isValid(),'solids':len(raw.Solids),'seconds':time.perf_counter()-t0,'previous_error':'removeSplitterexception is NOTproof voidimpossible'})
if not raw.isNull() and raw.isValid():
 def profile(x,ym,yp,zb,zt,arch=8):
  a=V(x,ym,zb);b=V(x,ym,zt-arch);c=V(x,(ym+yp)/2,zt);d=V(x,yp,zt-arch);e=V(x,yp,zb)
  return Part.Wire([Part.makeLine(a,b),Part.Arc(b,c,d).toShape(),Part.makeLine(d,e),Part.makeLine(e,a)])
 outer=Part.makeLoft([profile(x,-48,48,153,220) for x in [-219,-126]],True,True)
 inner=Part.makeLoft([profile(x,-46,46,151,218,6) for x in [-220,-125]],True,True)
 arch=outer.cut(inner);joined=raw.fuse(arch)
 joins=raw.common(arch).Volume
 if joined.isValid() and len(joined.Solids)==1:
  D.getObject('HC_BACK_UPPER').Shape=joined
  state={'selected':True,'joined_valid':joined.isValid(),'solids':len(joined.Solids),'positive_arch_source_common':joins,'protected_outside_retired_roof_missing':old.cut(cut).cut(joined).Volume,'arch_missing':arch.cut(joined).Volume,'oldV':old.Volume,'newV':joined.Volume,'nominal_newmass_g_delta':(joined.Volume-old.Volume)*.00127,'source_primarylands':'Y+-49/Z146 withallsource material below153.5 untouched; alloutsidecentralwindowretained; oldcamupperlands144.9 intact','parting':'movingHC uppercover ONErealpiece withnewcentralarch. Fixedlatehood separate; no boughtfusion','seconds':time.perf_counter()-t0}
 else:
  add('FU17_MOVING_ARCH_UNQUALIFIED_REFERENCE',arch,scope='UNSELECTED_material_jointOPEN');state={'selected':False,'rawvalid':raw.isValid(),'joinedvalid':joined.isValid(),'solids':len(joined.Solids),'joinV':joins,'reason':'assemblymaterialconnectionnotqualified; sourceHCnotreplaced'}
 put('moving-central-roof-realization.json',state)
 # One latefixedshoulderhood, frontnestedinside raisedmovingcrown, wholeports/coolingoutsidewall.
 specs=[(-133,-32,37,155,207),(-65,-48,37,155,207),(90,-48,37,155,195)]
 oo=Part.makeLoft([profile(*r) for r in specs],True,True)
 ii=Part.makeLoft([profile(x,ym+2,yp-2,zb-2,zt-2,6) for x,ym,yp,zb,zt in specs],True,True)
 hood=oo.cut(ii)
 add('FU17_LATE_FIXED_SHOULDER_HOOD',hood)
 put('fixed-hood-material-checkpoint.json',{'valid':hood.isValid(),'solids':len(hood.Solids),'V':hood.Volume,'specs':specs,'wall':2,'role':'localshoulder/pitop/wholeDATAstockguard; notentirebodyroofraise','root_ANDbodyparting':'NEXT actualtwofeet/fixings/currentbodywindow; notfloatinghoodPASS'})
D.recompute();D.save();print('movingroof_and_fixedhood_material_checkpoint',time.perf_counter()-t0)
