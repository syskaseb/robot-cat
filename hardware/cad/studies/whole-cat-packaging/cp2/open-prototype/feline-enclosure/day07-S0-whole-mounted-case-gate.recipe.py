import json,time,hashlib,zipfile,math,os
t57=time.monotonic();c57=time.process_time()
sideface57=max([f for f in coupon57.Faces if type(f.Surface).__name__=='Plane' and f.normalAt(0,0).y>.999 and abs(f.CenterOfMass.y-rail56.BoundBox.YMax)<1e-7],key=lambda f:f.Area)
assert rail56.isInside(rootface57.CenterOfMass-A.Vector(0,0,.1),1e-7,False) and rail56.isInside(sideface57.CenterOfMass-A.Vector(0,.1,0),1e-7,False)
local57=A.Matrix()
for j,v in enumerate([stud56,fix56,out56]):
 for i in range(3):setattr(local57,'A'+str(i+1)+str(j+1),float(v[i]))
rot57=A.Rotation(local57);place57=A.Placement(A.Vector(*C56),rot57)
def loc57(s):
 s.Placement=place57*s.Placement;return s
def lcyl57(u,v,n,R,h):return loc57(Part.makeCylinder(R,h,A.Vector(u,v,n)))
def lhex57(u,v,n,AF,h,hole=0):
 rr=AF/math.sqrt(3);pts=[A.Vector(u+rr*math.cos(k*math.pi/3),v+rr*math.sin(k*math.pi/3),n) for k in range(7)];s=Part.Face(Part.Wire(Part.makePolygon(pts))).extrude(A.Vector(0,0,h))
 if hole:s=s.cut(Part.makeCylinder(hole,h,A.Vector(u,v,n)))
 return loc57(s)
panel57=Part.makeBox(32,22,3,A.Vector(-16,-11,0)).fuse(Part.makeCylinder(16,3,A.Vector(0,-11,0))).fuse(Part.makeCylinder(16,3,A.Vector(0,11,0)))
panel57=panel57.cut(Part.makeCylinder(12,3,A.Vector(0,0,0)))
for v in [-19,19]:panel57=panel57.cut(Part.makeCylinder(3.25,3,A.Vector(0,v,0)))
panel57=loc57(panel57)
topstart57=rootface57.copy();topstart57.translate(A.Vector(0,0,-.5));topfoot57=topstart57.extrude(A.Vector(0,0,3))
sidestart57=sideface57.copy();sidestart57.translate(A.Vector(0,-.5,0));sidefoot57=sidestart57.extrude(A.Vector(0,2.5,0))
rootTop57=rootface57.CenterOfMass+A.Vector(0,0,1.25);rootSide57=sideface57.CenterOfMass+A.Vector(0,1,0)
def rod57(a,b,r):
 a=A.Vector(*a) if not isinstance(a,A.Vector) else a;b=A.Vector(*b) if not isinstance(b,A.Vector) else b;d=b-a;return Part.makeCylinder(r,d.Length,a,d).fuse(Part.makeSphere(r,a)).fuse(Part.makeSphere(r,b))
bridge57=rod57(rootTop57,rootSide57,2)
end57=place57.multVec(A.Vector(-11,-18,2.5));leg57=rod57(rootTop57,end57,2)
fixture57=topfoot57.multiFuse([sidefoot57,bridge57,leg57,panel57]);assert fixture57.isValid() and len(fixture57.Solids)==1
rootcommon57=fixture57.common(rail56);contactsolids57=[]
for i,s in enumerate(rail56.Solids):
 if fixture57.common(s).Volume>1e-7:contactsolids57.append(i)
assert rootcommon57.isValid() and rootcommon57.Volume>1e-7 and len(contactsolids57)==1
rootunion57=fixture57.fuse(rail56.Solids[contactsolids57[0]]);assert rootunion57.isValid() and len(rootunion57.Solids)==1
hardware57={};tools57={}
for i,v in enumerate([-19,19]):
 # Original source direction: head outward. Project flange4, panel3, two washers1.6, nut5 ->4.8mm thread beyondnut.
 shaft=lcyl57(0,v,-15.4,3,20);head=lcyl57(0,v,4.6,5,6);hardware57['caseM6_'+str(i)+':DIN912x20']=shaft.fuse(head)
 for label,n in [('outer',3.),('inner',-5.6)]:hardware57['caseM6_'+str(i)+':washer_'+label]=lcyl57(0,v,n,6,1.6).cut(lcyl57(0,v,n,3.2,1.6))
 hardware57['caseM6_'+str(i)+':nut_AF10_h5']=lhex57(0,v,-10.6,10,5,3)
 tools57['caseM6_'+str(i)+':AF5_driver_approach']=lcyl57(0,v,10.6,3.2,35)
 tools57['caseM6_'+str(i)+':AF10_counterhold_approach']=lcyl57(0,v,-25.6,7,15)
physical57={'S0:compact_panel_twoface_root':fixture57,**hardware57}
proposal57=dict(id='day07-S0-current-case-whole-mount-proposal',status='ONE_ACTUAL_MATERIAL_ROOTED_NOMINAL_CASE_FIXING_PROPOSAL',selected=False,N01_complete=False,
 current_frame_source=p56.name,current_frame_sha256=hashlib.sha256(p56.read_bytes()).hexdigest(),casepose_unchanged=True,sourcecasefixingpattern='Nominal selected R6twoM6pitch38/neck24 mapped once byactualneck andlabelledstudfaces. Published pattern/prototype flange4, not an exact delivered recess assertion.',
 mounting=dict(panel_local_axes=['u=currentINOUTdirection','v=actualM6pairdirection','n=outwardneckaxis'],panel_capsule_mm=[32,54,3],neck_hole_mm=24,fix_holes_mm=6.5,M6_stack='2DIN912M6x20 +4OD12/ID6.4/t1.6washers +2AF10/h5nuts; n coordinates sourceflange[-4,0],panel[0,3],outerwasher[3,4.6],head[4.6,10.6],innerwasher[-5.6,-4],nut[-10.6,-5.6],shank[-15.4,4.6]. Nominalflange4 ->4.8threads beyondnut. No suppliednuts/spareclaim.',legacy_M2='OldDeck2M2 doesnotapply: thisnew supportis an integral branch ofactualrail, not a floating M2attachment or oldDeck reuse.'),
 loadpath=dict(actual_parent='CurrentFoundation:FoundationRail:-1',top_face_area_mm2=rootface57.Area,side_face_area_mm2=sideface57.Area,face_centres=[list(rootface57.CenterOfMass),list(sideface57.CenterOfMass)],actual_root_common_mm3=rootcommon57.Volume,contacted_parent_solid=contactsolids57[0],source_parent_solids=len(rail56.Solids),union_valid=True,union_solids=1,strut_R_mm=2,source_face_inside_below_or_behind=True),
 assembly=['Keepbattery/USB disconnected as sourceassembly condition; no actual power operation. Build actualsharedrail+newprintbranch before closingbody/head/looms; no virtualdetachingintegralprints.',
 'On accessiblebench insert selectedcase neck into24hole with source removablekey out of the way; sourcecheck_phase1 explicitlyallowsremove/offkey. Casefixings placedon published38pitch, complete2M6/washer/nut kit tightened using sourceAF5/AF10 before rings/wires. No physical operation performed.',
 'Only then install labelled realIN/OUTstud rings with originalfullmetal/insulation/currentW076/W066/W043sourceprefixes and sourceM10nuttool access. Keep currentcase/endposes and oldqualified lengths; no use of historical80/330/40 as currentcuts.',
 'InstallunchangedPi removablecarrier fromabove later; keepSOURCE/MODULE/J8/4MTA/all220 unchanged. RequiredS0key/routineoperatoraperture remainsselected, no silentkeyretirement.'],
 own_case_fit_scope='Currentbody/neck/key are filled HELLAfamily reserves, not flange/hole/recess material. Record own2M6/nominalcase overlaps as sourcefit assumptions, not metalcontact evidence; exact delivered flange/keyrecess/torque/creep phase2. OTHER rings/studs/insulation/parts remainforeign1.25; no blanketwholeframewaiver.',
 tool_scope='Full cylindricalsourceAF5 approachR3.2x35 andAF10counterholdR7x15; initialhardware BEFORE rings andwires. Opaque ownfamily recess access is explicitphase2fitgate, not declared materialvoid. Sourceownoriginal holes/boughttool fit only; no assembledrapidservice/fullN08.',
 first_falsifier='Whole actualrootedprint+complete8metal casefixingactors againstfullcurrent1292 excludingONLYownS0family body/neck/key fromforeignrule; keep8electricalterminalmetals andall actualsourceends asforeign. Rootparentpositivefunctionaljoint only. Firstforeign<1.25orinvalid isHOLD before dependent detail. Completeoperationalownoutline before selection.')
pp57=OUT/'day07-S0-current-case-whole-mount-proposal.json';assert not pp57.exists();pp57.write_bytes((json.dumps(proposal57,ensure_ascii=False,indent=2)+'\n').encode())
foreign57={n:s for n,s in Current35.items() if n not in ['Ref_Material_S0_body_CP2_0_0','Ref_Material_S0_neck_CP2_0_0','Ref_Material_S0_key_CP2_0_0', 'CurrentFoundation:FoundationRail:-1']}
tasks57=[(n,k) for n,s in physical57.items() for k,q in foreign57.items() if bbox_lower_bound(s.BoundBox,q.BoundBox)<=1.25]
tasks57.sort(key=lambda p:(0 if p[0].startswith('caseM6_') and p[1].startswith('Ref_Material_S0_') else 1,p))
rows57=[];stop57=None
for n,k in tasks57:
 s,q=physical57[n],foreign57[k];r=dict(a=n,b=k,a_valid=s.isValid(),b_valid=q.isValid())
 if r['a_valid'] and r['b_valid']:
  g,w,_=s.distToShape(q);r.update(gap_mm=g,required_foreign_mm=1.25,witnesses=[[list(a),list(b)] for a,b in w[:1]])
  if g<1e-7:
   co=s.common(q);r.update(common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None)
  r['status']='WHOLE_MOUNT_FOREIGN_SEPARATED125' if g>=1.25-1e-7 else 'S0_MOUNT_FIRST_FOREIGN_HOLD'
 else:r['status']='INVALID_SOURCE_NOT_CONTACT'
 rows57.append(r)
 if r['status']=='S0_MOUNT_FIRST_FOREIGN_HOLD':stop57=r;break
 if time.monotonic()-t57>45:break
outline57={}
for n,s in physical57.items():
 outside=s.cut(BodyOuter31);g=s.distToShape(boundary56)[0];outline57[n]=dict(valid=s.isValid(),outside_valid=outside.isValid(),outside_mm3=outside.Volume,boundary_gap_mm=g,required_mm=3.25,ok=s.isValid() and outside.isValid() and outside.Volume<1e-7 and g>=3.25-1e-7)
ar57=OUT/'day07-S0-current-case-whole-mount.breps.zip';assert not ar57.exists();ge57=[]
with zipfile.ZipFile(ar57,'w',zipfile.ZIP_DEFLATED) as z:
 for i,(n,s) in enumerate(list(physical57.items())+list(tools57.items())+[('SOURCE:twoface_root_coupon',coupon57),('SOURCE:contacted_parent_solid',rail56.Solids[contactsolids57[0]])]+[(k,foreign57[k]) for k in sorted({r['b'] for r in rows57})]):
  raw=s.exportBrepToString().encode();e=str(i)+'.brep';z.writestr(e,raw);ge57.append(dict(name=n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s)))
 z.writestr('manifest.json',(json.dumps(dict(geometry=ge57,scope='One actualrooted nominal selectedS0 mount withcomplete2M6kit/tools; sourcecaseposeunchanged'),indent=2)+'\n').encode())
r57=dict(id='day07-S0-current-whole-mount-first-gate',status='S0_MOUNT_C0_FOREIGN_HOLD' if stop57 else 'S0_MOUNT_ROOT_STATIC_OUTLINE_RECEIVED_TOOL_AND_OWNFIT_NEXT' if len(rows57)==len(tasks57) and all(v['ok'] for v in outline57.values()) else 'S0_MOUNT_STATIC_OR_OUTLINE_PENDING',rows=rows57,cursor=len(rows57),total=len(tasks57),unreceived=len(tasks57)-len(rows57),stop=stop57,outline=outline57,actualroot=proposal57['loadpath'],initial_top_only_root_screen='FirstROI highestface11.0875 failed a non-source12area screening choice. Fullactualparent-edge top11.6625+side12 is nowmeasuredactualtwoface L-root withpositiveunion. No priorcasepose/rootphysicalfailurewaived, no arbitrarybboxroot.',whole_tool_and_own_fit_NOT_yet_received=True,proposal=pp57.name,proposal_sha256=hashlib.sha256(pp57.read_bytes()).hexdigest(),archive=ar57.name,archive_sha256=hashlib.sha256(ar57.read_bytes()).hexdigest(),geometry=ge57,operation_seconds=time.monotonic()-t57,process_cpu_seconds=time.process_time()-c57,selected=False,N01_complete=False,pid=os.getpid(),session_id=46493)
p57=OUT/'day07-S0-current-whole-mount-first-gate.json';assert not p57.exists();p57.write_bytes((json.dumps(r57,ensure_ascii=False,indent=2)+'\n').encode());print('S0_MOUNT57',r57['status'],proposal57['loadpath'],len(rows57),len(tasks57),stop57,{n:v['boundary_gap_mm'] for n,v in outline57.items()},r57['operation_seconds'],r57['process_cpu_seconds'],hashlib.sha256(p57.read_bytes()).hexdigest(),flush=True)
