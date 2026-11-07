import time,json,hashlib,math,zipfile,os
t127=time.monotonic();c127=time.process_time();assert first126['other']=='DGGrip:D:band';ob127=ctx121['DGGrip:D:band'];sourceproof127={}
with zipfile.ZipFile(OUT/'day30-astra-complete-receiver-stock-gate.breps.zip') as zz:
 raw=zz.read('09.brep');ss=Part.Shape();ss.importBrepFromString(raw.decode());sourceproof127=dict(archive='day30-astra-complete-receiver-stock-gate.breps.zip',archive_sha256=hashlib.sha256((OUT/'day30-astra-complete-receiver-stock-gate.breps.zip').read_bytes()).hexdigest(),entry='09.brep',stored_member_sha256=hashlib.sha256(raw).hexdigest(),normalized_source_brep_sha256=hashlib.sha256(ss.exportBrepToString().encode()).hexdigest(),current_actor='CurrentDFL:DFL:cap',current_normalized_brep_sha256=hashlib.sha256(ctx121['CurrentDFL:DFL:cap'].exportBrepToString().encode()).hexdigest())
 sourceproof127['normalized_bytes_identical']=sourceproof127['normalized_source_brep_sha256']==sourceproof127['current_normalized_brep_sha256']
def exact127(d):
 R=35.1;hw=1.95;z=58.95;cx=84.6+d
 arc=half126(R+hw,3.9,cx,z).cut(half126(R-hw,4.1,cx,z-.1));a=Part.makeBox(d+2*hw,2*hw,3.9,A.Vector(84.6-hw,-R-hw,z));b=Part.makeBox(d+2*hw,2*hw,3.9,A.Vector(84.6-hw,R-hw,z));s=arc.fuse(a).fuse(b);assert s.isValid();return s
exactmin127=exact127(dl126);gap,ww,_=exactmin127.distToShape(ob127);co=exactmin127.common(ob127);assert co.isValid();fullco=look126['D'].common(ob127);assert fullco.isValid()
section127=[];plane=Part.makePlane(100,120,A.Vector(70,-60,60.9),A.Vector(0,0,1))
items127=[('D_FULL_ADAPTIVE_CAPACITY',look126['D']),('D_REQUIRED_E55_CAPACITY',exactmin127),('CURRENT_DGGRIP_D_FULL_BAND',ob127),('CURRENT_DGGRIP_D_CAP',ctx121['DGGrip:D:cap']),('CURRENT_DGGRIP_D_HEAD',ctx121['DGGrip:D:head']),('E55_ALLOCATED_COMMON_NOT_WIRECONTACT',co),('FULL_FAMILY_ALLOCATED_COMMON_NOT_WIRECONTACT',fullco)]
for name,sh in items127[:5]:
 sec=sh.section(plane);curves=[]
 for e in sec.Edges:
  ps=e.discretize(Deflection=.08)
  if len(ps)>1:curves.append([[v.x,v.y] for v in ps])
 section127.append(dict(name=name,Z_mm=60.9,curves_xy=curves))
ar127=OUT/'day07-SOURCE-receiver-U-DGGrip-function-local.breps.zip';assert not ar127.exists();geo127=[]
with zipfile.ZipFile(ar127,'w',zipfile.ZIP_DEFLATED) as zz:
 for i,(name,sh) in enumerate(items127):
  raw=sh.exportBrepToString().encode();entry=str(i)+'.brep';zz.writestr(entry,raw);geo127.append(dict(name=name,entry=entry,sha256=hashlib.sha256(raw).hexdigest(),valid=sh.isValid(),volume_mm3=sh.Volume,bounds_mm=saved_bounds(sh)))
 zz.writestr('manifest.json',(json.dumps(dict(geometry=geo127),indent=2)+'\n').encode())
r127=dict(id='day07-SOURCE-receiver-U-DGGrip-function-local',status='RECEIVER_U_D_E55_OCCUPIED_BY_EXISTING_BUS_D_RETENTION' if gap<1.25-1e-7 else 'FULL_VARIABLE_FAMILY_RETENTION_OVERLAP_E55_ONLY_SEPARATE_OTHER_STATES_OPEN',case_classification='DGGrip:D:band is source splitclamp closedbandmaterialreservation tied to full9BUS.D andSharedBUS:TailCarrier. Projectretentionvariableinwholeplan, notboughtmodule/notfreeillustrativewire. ItisNOTownSOURCEFL2/W005interface; owningchannelwaiveronlyCurrentBUS:BUS.D toitsnamedcap/carrier. Actualcurrentownleadaliasmappingnotinctx; donotdeletebandbecauseoldleadactornameabsent.',source_DFL3_cap_identity=sourceproof127,first_received_full_family_common_mm3=fullco.Volume,full_family_common_valid=True,required_E55=dict(d_mm=dl126,L_local_U_mm=math.pi*35.1+2*dl126,E_local_mm=(math.pi-2)*35.1+2*dl126,full_field_valid=exactmin127.isValid(),gap_mm=gap,common_valid=co.isValid(),allocated_common_mm3=co.Volume,witnesses=[[list(a),list(b)] for a,b in ww[:1]]),sections=section127,archive=ar127.name,archive_sha256=hashlib.sha256(ar127.read_bytes()).hexdigest(),geometry=geo127,new_material=False,new_leg_geometry=False,actual_A_U_minfit_slack=None,counter=dict(cursor=5,total=35,unreceived=30,stop_first_falsifier=True),selected=False,N01_complete=False,operation_seconds=time.monotonic()-t127,process_cpu_seconds=time.process_time()-c127,pid=os.getpid(),session_id=46493)
rp127=OUT/'day07-SOURCE-receiver-U-DGGrip-function-local.json';assert not rp127.exists();rp127.write_bytes((json.dumps(r127,indent=2)+'\n').encode());print('BODY127',r127['status'],'E55gap',gap,'E55common',co.Volume,'fullcommon',fullco.Volume,'DFL_normalizedidentity',sourceproof127['normalized_bytes_identical'],'wall',r127['operation_seconds'],'CPU',r127['process_cpu_seconds'],flush=True);print('OWNER63_IDLE',os.getpid(),flush=True)
