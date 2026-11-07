import json,time,hashlib,zipfile,os
t186=time.monotonic();c186=time.process_time();assert first185 is None and cursor185==25
toolco186=base181.common(tool181);assert toolco186.isValid();lift186=up181.copy();lift186.translate(A.Vector(0,0,4));lay186=[];first186=None
for n,s in ctx182.items():
    req=.2 if n=='Station:D_FL:case' else 1.25;lo=bbox_lower_bound(lift186.BoundBox,bounds126[n] if n in bounds126 else s.BoundBox)
    if lo>=req-1e-7:continue
    ga,ww,_=lift186.distToShape(s);row=dict(actor=n,upper_lift_mm=4,gap_mm=ga,required_mm=req,status='INITIAL_LAY_CLEAR' if ga>=req-1e-7 else 'INITIAL_LAY_CONTEXT_HOLD');lay186.append(row)
    if ga<req-1e-7:first186=row;break
bb186=[saved_bounds(s) for n,s in parts182];lo186=[min(bb[0][i] for bb in bb186)-3.25 for i in range(3)];hi186=[max(bb[1][i] for bb in bb186)+3.25 for i in range(3)];cover186=box153([lo186,hi186]);out186=cover186.cut(BodyOuter31);assert out186.isValid()
if toolco186.Volume>1e-7 or out186.Volume>1e-7:first186=dict(stage='ACTUAL_TOOL_OR_OUTLINE',tool_common_mm3=toolco186.Volume,outside_BodyOuter_mm3=out186.Volume)
sections186=[]
for label,plane,proj in [('XY_Z48p5',Part.makePlane(60,70,A.Vector(40,-60,48.5),A.Vector(0,0,1),A.Vector(1,0,0)),[0,1]),('XZ_Ystockcentre',Part.makePlane(60,40,A.Vector(40,centreY181,70),A.Vector(0,1,0),A.Vector(1,0,0)),[0,2])]:
    for n,s in [('new_primary',base181),('new_upper',up181),('full_band',band181),('full_head',head181),('bought_DFLcase',Current35['Station:D_FL:case'])]:
        sc=s.section(plane);lines=[]
        for e in sc.Edges:lines.append([[list(v)[proj[0]],list(v)[proj[1]]] for v in e.discretize(Deflection=.1)])
        sections186.append(dict(view=label,actor=n,curves=lines))
ar186=OUT/'day07-five-D-south-initial-lay-and-outline.breps.zip';assert not ar186.exists();ge186=[]
with zipfile.ZipFile(ar186,'w',zipfile.ZIP_DEFLATED) as z:
    for i,(n,s) in enumerate([('ONLY_NEW_POSITIVE_PRIMARY_DELTA',newdelta184),('UPPER_INITIAL_LIFT4',lift186),('FULL_KIT_MARGIN325_COVER',cover186),('SOURCE_FULL_CLAMP3_TOOL_R4p25',tool181)]):
        f=Path('C:/Users/Sysq/AppData/Local/Temp/robot-cat81-lay-'+str(i)+'.brep');s.exportBrep(str(f));raw=f.read_bytes();en=str(i)+'.brep';z.writestr(en,raw);ge186.append(dict(name=n,entry=en,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s),valid=s.isValid()))
    z.writestr('manifest.json',(json.dumps(dict(geometry=ge186),indent=2)+'\n').encode())
p186=OUT/'day07-five-D-south-initial-lay-outline-and-sections.json';assert not p186.exists();r186=dict(id=p186.stem,status='NEW_FIVE_D_INITIAL_LAY_TOOL_OUTLINE_SCOPED_RECEIVED' if first186 is None else 'NEW_FIVE_D_INITIAL_LAY_TOOL_OR_OUTLINE_HOLD',source_toolR4p25_to_new_permanent_common_mm3=toolco186.Volume,source_tool_cut_before_wirelay_and_bandclosure=True,source_actualseat_andneck_read_untimed=dict(common_seat_mm3=312.66276180979537,common_neck_mm3=4.5,not_counted_in_script_timing=True),initial_upper_lift_mm=4,initial_lay_rows=lay186,full_newnominal_jacket_Zmax=50.05,lifted_upper_Zmin=lift186.BoundBox.ZMin,whole_kit_margin_mm=3.25,wholekit_cover_outside_actual_BodyOuter_mm3=out186.Volume,cover_bounds_mm=[lo186,hi186],sections=sections186,first_falsifier=first186,archive=ar186.name,archive_sha256=hashlib.sha256(ar186.read_bytes()).hexdigest(),geometry=ge186,new_D_motion_NOT_received=True,whole_SOURCE_freefans_andLi_NOT_received=True,legacyPad_halfmm_interface_OPEN=True,selected=False,N01_complete=False,actualcut=None,actualA_U_fit_slack=None,operation_seconds=time.monotonic()-t186,process_cpu_seconds=time.process_time()-c186,pid=os.getpid(),session_id=46493);p186.write_bytes((json.dumps(r186,indent=2)+'\n').encode());print('FIVE_D_LAY_OUTLINE',r186['status'],first186,'tool',toolco186.Volume,'outline',out186.Volume,r186['operation_seconds'],r186['process_cpu_seconds'],hashlib.sha256(p186.read_bytes()).hexdigest(),'OWNER81_IDLE',os.getpid(),flush=True)
