import FreeCAD as A,FreeCADGui as G,Part,Mesh,MeshPart,json,math,time
from pathlib import Path
P=Path(__file__).parent;D=A.ActiveDocument;V=A.Vector;t0=time.perf_counter()
put=lambda n,j:(P/n).write_bytes((json.dumps(j,indent=2)+'\n').encode())
def bx(x,y,z,a,b,c):return Part.makeBox(a,b,c,V(x,y,z))
D.save();base=D.getObject('CF17_SHARED_FIXED_PI_BUS_POWER_CARRIER');before=base.Shape.copy();relief=bx(-36.5,21,135.7,7,.8,5.3);base.Shape=base.Shape.cut(relief)
keeper=D.getObject('CF17_REMOVABLE_COMMON_E1_ROOT_KEEPER').Shape
put('matched-keeper-foot-clearance-completion.json',{'actual_keeper_gap':base.Shape.distToShape(keeper)[0],'parting_common':base.Shape.common(keeper).Volume,'wholefoot_except_planned_relief_missing':before.cut(relief).cut(base.Shape).Volume,'relief':'local.8side-notch Z135.7..141 only, retains useful6.2foot atcrossing andfull7x7rest; sourcebeamroot remainspositive; no board/stockposechange'})
# SameguardfunctionalOPEN-TO-EDGE inlet; the movingcrown owns coverage of this overlap.
hood=D.getObject('FU17_LATE_FIXED_SHOULDER_HOOD');old=hood.Shape.copy();slot=bx(-134,-49,170,40,21,44);q=old.cut(slot);hood.Shape=q
f=D.getObject('N17_FFC200_OCCUPIED_20_10').Shape;local=f.common(slot);local.rotate(V(-106,0,127),V(0,0,1),-20);local.rotate(V(-135,0,121),V(0,1,0),-10)
pts=[v.Point for v in local.Vertexes];bounds=[[min(getattr(p,a) for p in pts),max(getattr(p,a) for p in pts)] for a in ['x','y','z']] if pts else None
inside=bool(pts) and all(-219<=p.x<=-126 and -44<=p.y<=44 and 153<=p.z<=210 for p in pts)
d=f.distToShape(q)[0]
put('final-guard-inlet-and-moving-coverage.json',{'new_fixed_guard_valid':q.isValid(),'solids':len(q.Solids),'old_rawcommon469':469.0698348580651,'current20_10_fullprofile_gap':d,'current20_10_common':f.common(q).Volume if d<1.25 else 0,'required':1.25,'other2_prior_fixed_gaps_reuse':'materialremovalsubset, unchangedprofiles; no replays','moving_fixed_parting_reuse':'all3priorguardseparationsclear, removalsubsetcannotdecreasegap','inletslot':str(slot.BoundBox),'openedge_wire_covered_by_MOVING_arch_core_box':inside,'removed_region_headlocal_vertex_bounds':bounds,'coverage_box':'[-219,-126]x[-44,44]x[153,210] is below220circulararchroof andinside48halfwidth; actualruledprofile corners convexcover. This is sample20/+10scope not continuouscertificate','outside_planned_inlet_missing':old.cut(slot).cut(q).Volume,'not_fakeclosure':'Ifcoveragefalse orfullprofilegap<1.25 fixedguardHOLD; no STL'})
# Bodyupperforecrown remnant explicitlyUNBUILT/retired; its enclosurefunction now newmovingcrown+fixedhood. Retain exactsource asunselectedreference.
o=D.getObject('FC_F_NEG');ss=o.Shape.Solids;retired=[]
if len(ss)==2:
 candidates=[s for s in ss if s.BoundBox.ZMin>=153.9 and s.Volume<2100]
 if len(candidates)==1:
  r=candidates[0];n=D.getObject('FU17_RETIRED_SOURCE_UPPER_FORECROWN_REFERENCE') or D.addObject('PartDesign::Feature','FU17_RETIRED_SOURCE_UPPER_FORECROWN_REFERENCE');n.Shape=r;n.Label='RETIRED_UNBUILT upperforecrown / replacedbyenclosingguard';n.ViewObject.Visibility=False
  kept=[s for s in ss if s is not r and abs(s.Volume-r.Volume)>1e-6];o.Shape=Part.makeCompound(kept);retired=[{'V':r.Volume,'bounds':str(r.BoundBox),'role':'unbuilt upperforecrown left bynewhoodwindow; no module/port/stock deleted; sourcebelow155/6flooranchors retained'}]
put('explicit-forecrown-effectivity.json',{'retired_roles':retired,'source_full_negative_brep':'source87c_FC_F_NEG.brep','current_negative_solids':len(o.Shape.Solids),'wholebody_closed':False,'remaining':'headJR/cowlports/MTA4fullsampleandcontinuousmanualmovement; notallclosedcatPASS'})
# Conditional usefullocalparts, notwholefront/skinapproval. Exactnewsource versions only.
parts=[('front_common_carrier_FIT','CF17_SHARED_FIXED_PI_BUS_POWER_CARRIER',A.Rotation()),('E1_root_keeper_FIT','CF17_REMOVABLE_COMMON_E1_ROOT_KEEPER',A.Rotation(V(1,0,0),180)),('POWER_boot_keeper_FIT','CF17_POWER_INDEPENDENT_BOOT_AND_ADAPTER_KEEPER',A.Rotation(V(1,0,0),180))]
sourcecoupon=[('AMP_edge_coupon',D.getObject('A17_INTEGRAL_FRONT_DECK_AND_N1').Shape.common(bx(-15,-25,94,12,12,11)),A.Rotation()),('BUS90_seat_coupon',base.Shape.common(bx(-8.5,-20,93,9.5,7.8,9)),A.Rotation(V(1,0,0),90))]
rows=[]
for name,n,R in parts+sourcecoupon:
 shape=D.getObject(n).Shape.copy() if isinstance(n,str) else n.copy()
 if shape.isNull() or not shape.isValid() or len(shape.Solids)!=1:
  rows.append({'file':name,'released':False,'reason':'sourcecut/valid/1solid fails'});continue
 shape.exportBrep(str(P/(name+'.brep')));shape.rotate(V(),R.Axis,R.Angle*180/math.pi);b=shape.BoundBox;shift=V(-b.XMin,-b.YMin,-b.ZMin);shape.translate(shift);b=shape.BoundBox
 mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.1,AngularDeflection=.25,Relative=False);path=P/(name+'.stl');mesh.write(str(path));read=Mesh.Mesh(str(path));closed=read.isSolid();valid=shape.isValid() and shape.Volume>0 and closed and max(b.XLength,b.YLength,b.ZLength)+8<=256
 if not valid:path.rename(P/(name+'.stl.unreceived'))
 rows.append({'file':name+'.stl' if valid else name+'.stl.unreceived','source_object':n if isinstance(n,str) else 'actualcurrentA17/BUSBsourceROI one2piececoupon','qty':1,'released':valid,'status':'CONDITIONAL_UNPOWERED_FIT_ONLY_AFTER_P00' if isinstance(n,str) else 'ONE_ASSEMBLY_COUPON_TWO_PIECES_MEASURE_ONLY','valid_BRep':shape.isValid(),'solids':len(shape.Solids),'source_V':shape.Volume,'PETG_g':shape.Volume*.00127,'mesh_reopened_closed':closed,'facets':read.CountFacets,'local_Zmin':b.ZMin,'dimensions':[b.XLength,b.YLength,b.ZLength],'max_plus8':max(b.XLength,b.YLength,b.ZLength)+8,'rotation_Q':list(R.Q),'world_to_local_translation':list(shift),'orientation_notes':'mainnaturalZ/supportunderupperPiPOWERbridges; keeper180Xflatbarbed; couponBUS90backfacebed. No slicer/print. Couponfirstactualscrewseat+AMPcornerload/fit; no strengthPASS'})
put('current-conditional-print-index.json',{'parts':rows,'wholecat':False,'guard_STL':False,'guardwhy':'fullJR/DATA/poweractualends/bodyports/motionremaining, guardinletcriticalgateresultaloneNOTrelease','main_condition':'Emptystructuraldryfit/coupon first; actualP00/sourceaxes/thread/Pi/BUS/POWERsafecontact. NewcarrierwithhoodfeetrequirescurrentA17 from87c notoldSTLbyname. No realdrill/forcedsourceframe','coupon':'onecoupledinterface test TWOsmallpieces withactualM2CSK10/frontwasher/fullnut + AMPcasebearing. Sourcepose transforms preservecouponrelativeassembly, no metalSTL'})
D.recompute();D.save();print(json.dumps({'guard_gap':d,'movingcoverbox':inside,'exported':[r['file'] for r in rows if r['released']],'seconds':time.perf_counter()-t0}))
