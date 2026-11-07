import json,time,hashlib,os,zipfile,math
t209=time.monotonic();c209=time.process_time();assert first208 is None and len(rows208)==len(tasks208)
root209=Current35['Station:FR_G:shared_near_root'];upold209=root209.common(box153([[30,-57,45.26],[59,-45,52]]));lower209=root209.cut(upold209)
extension209=comb206.copy();extension209.translate(A.Vector(0,.8,0));extension209=extension209.common(box153([[30,-47.25,40],[59,-46.45,52]]));extlo209=extension209.common(box153([[30,-48,40],[59,-46,45.26]]));exthi209=extension209.cut(extlo209)
postspec209={'RearKeyLeft':[[31.325,-55,40.32],[34.325,-53,48.81]],'RearKeyRight':[[54.675,-55,40.32],[57.675,-53,48.81]]}
pockets209={'RearKeyLeft':[[32.325,-55.2,45.06],[34.525,-52.8,47.46]],'RearKeyRight':[[54.475,-55.2,45.06],[56.675,-52.8,47.46]]}
posts209={n:box153(b).cut(box153(pockets209[n])) for n,b in postspec209.items()}
wing209={'RearWingLeft':box153([[32.525,-55,45.26],[34.325,-53,47.26]]),'RearWingRight':box153([[54.675,-55,45.26],[56.475,-53,47.26]])}
sweeps209=[]
for n,b in postspec209.items():
    p=[list(b[0]),list(b[1])];p[0][1]-=2.2;pk=[list(pockets209[n][0]),list(pockets209[n][1])];pk[0][1]-=2.2;sweeps209.append(box153(p).cut(box153(pk)))
postrel209=fuse181(sweeps209)
newup209=fuse181([upold209,exthi209,*wing209.values()]).cut(postrel209)
bandfeed209=box153([[32.425,Y208-1.45,40.31],[56.575,Y208+1.45,41.91]])
def narrowarc209(cx,cz,a,b):
    at=lambda r,t:A.Vector(cx+r*math.cos(t),Y208-1.45,cz+r*math.sin(t));ed=[Part.Arc(at(3.8,a),at(3.8,(a+b)/2),at(3.8,b)).toShape(),Part.makeLine(at(3.8,b),at(2.2,b)),Part.Arc(at(2.2,b),at(2.2,(a+b)/2),at(2.2,a)).toShape(),Part.makeLine(at(2.2,a),at(3.8,a))];return Part.Face(Part.Wire(ed)).extrude(A.Vector(0,2.9,0))
tailguide209=narrowarc209(27.475,42.61,0,-math.pi/2);feed209=bandfeed209.fuse(tailguide209)
allowed209=kit199['Neck'].fuse(root209);forensic209=frame204.common(feed209).cut(allowed209)
assert forensic209.isValid() and forensic209.Volume<1e-7,'No accidentalotherframechannelcut'
shim209=box153([[31.875,-60,40.26],[61.875,-56.5,40.76]])
kept209=frame204.cut(upold209).cut(feed209)
newframe209=fuse181([kept209,extlo209,*posts209.values(),shim209]).cut(feed209);assert newframe209.isValid() and newup209.isValid()
coverage209=[]
for half,mem,target in [('permanent',{'ProtectedCurrentFrame':kept209,'ForeSeatLower':extlo209,**posts209,'ActualCaseBearingShim':shim209},newframe209),('upper',{'OldUpperWithPlannedKeyNotches':upold209.cut(postrel209),'ForeSeatUpper':exthi209.cut(postrel209),**wing209},newup209)]:
    for n,s in mem.items():
        expected=s.cut(feed209) if half=='permanent' else s;m=expected.cut(target);coverage209.append(dict(half=half,member=n,missing_valid=m.isValid(),missing_mm3=m.Volume if m.isValid() else None))
strips209=[]
for q in prop206['all4_ports']:
    x=q['actual_project_port_mm'][0]
    for half,lo,hi,target in [('lower',43.06,43.56,newframe209),('upper',46.96,47.46,newup209)]:
        s=box153([[x-.4,-56.25,lo],[x+.4,-47.25,hi]]);m=s.cut(target);strips209.append(dict(wire=q['wire'],half=half,full9_volume_mm3=s.Volume,missing_valid=m.isValid(),missing_mm3=m.Volume if m.isValid() else None))
joints209=[]
for n,s in posts209.items():
    co=s.common(lower209);joints209.append(dict(member=n,target='ActuallowerFRGroot',common_valid=co.isValid(),positive_common_mm3=co.Volume if co.isValid() else None))
for n,s in wing209.items():
    co=s.common(upold209.cut(postrel209));joints209.append(dict(member=n,target='ActualupperFRGpressure',common_valid=co.isValid(),positive_common_mm3=co.Volume if co.isValid() else None))
rootguards209=[]
for n,s in [('CasebackRailRoot',rootco199),('CasebackFlangeRoot',rootco203),('CasebackSharedBaseRoot',co204)]:
    m=s.cut(newframe209);rootguards209.append(dict(joint=n,received_material_missing_mm3=m.Volume,missing_valid=m.isValid()))
first209=None
if len(newframe209.Solids)!=1 or len(newup209.Solids)!=1 or any(not q['missing_valid'] or q['missing_mm3']>1e-7 for q in coverage209+strips209) or any(not q['missing_valid'] or q['received_material_missing_mm3']>1e-7 for q in rootguards209) or any(not q['common_valid'] or q['positive_common_mm3']<=1e-7 for q in joints209):first209=dict(stage='COMPLETE_FUNCTIONAL_PRESSURE_LOAD_MATERIAL_GUARD',permanent_solids=len(newframe209.Solids),upper_solids=len(newup209.Solids),coverage=coverage209,strips=strips209,joints=joints209)
ownrows209=[]
if first209 is None:
    for sn,a in [('WholeBand',band208),('WholeHead',head208),('TailActualPlusNominalPoint2',tailguide209),*[(n,s) for n,s in extra3profiles208]]:
        for pn,b in [('Permanent',newframe209),('RemovableUpper',newup209)]:
            co=a.common(b);row=dict(stock_or_wire=sn,print=pn,common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None);ownrows209.append(row)
            if not co.isValid() or co.Volume>1e-7:first209=dict(stage='ACTUAL_OWN_CHANNEL_PRESSURE_STOCK_NONPENETRATION',row=row);break
        if first209:break
caseco209=shim209.common(Current35['Station:FR_G:case']);bear209=30*3.5
newdelta209=newframe209.cut(frame204);upperdelta209=newup209
ar209=OUT/'day07-FRG-open-front-pressure-feed-constructive-first-gate.breps.zip';assert not ar209.exists();ge209=[]
with zipfile.ZipFile(ar209,'w',zipfile.ZIP_DEFLATED) as z:
    for i,(n,s) in enumerate({'NEW_WHOLE_FRAME_PERMANENT':newframe209,'NEW_SEPARATE_KEYED_PRESSURE_UPPER':newup209,'ACTUAL_LOCAL_FEED_VOID':feed209,'NEW_POSITIVE_FRAME_DELTA':newdelta209,'CASE_BEARING_SHIM':shim209,**posts209,**wing209}.items()):
        raw=s.exportBrepToString().encode();en=str(i)+'.brep';z.writestr(en,raw);ge209.append(dict(name=n,entry=en,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s)))
    z.writestr('manifest.json',json.dumps(dict(geometry=ge209),indent=2))
p209=OUT/'day07-FRG-open-front-pressure-feed-constructive-first-gate.json';assert not p209.exists()
r209=dict(id=p209.stem,status='OPEN_FRONT_PRESSURE_FEED_FIRST_FUNCTIONAL_FALSIFIER' if first209 else 'OPEN_FRONT_PRESSURE_FEED_CONSTRUCTIVE_SCOPED_POSITIVE_NEW_FOREIGN_ASSEMBLY_MOTION_OPEN',source_wholestock_gate=p208.name,source_wholestock_sha256=hashlib.sha256(p208.read_bytes()).hexdigest(),permanent_solids=len(newframe209.Solids),separate_upper_solids=len(newup209.Solids),all_intended_material_coverage=coverage209,all4_full9_eight_half_guards=strips209,actual_rear_key_useful_joints=joints209,all3_received_caseback_load_joints=rootguards209,other_source_frame_feed_cut_mm3=forensic209.Volume,own_actual_fullunit_and_source_interfaces=ownrows209,whole_selected_stock145_83p3_preserved=True,free_capacity_profile_3p3x2_unchanged=True,matched_fixture_nominal_feed='Actualband2.5x1.2+.2eachside; actuallocaltail1.2x2.5+.2eachside. NOstockshrink/foreign125waiver; full3.3x2loosebay retainedOTHERparts.',upper_open_lay='Separateupper keyedrearwings; nominalpocket.2; initial+Y2.2 then−Y2.2 slide beforebandclosure. Exactpostmaterialrelative-sweep void, notwholeBBoxaircut.',actual_casebearing=dict(shim_common_case_valid=caseco209.isValid(),shim_common_case_mm3=caseco209.Volume,nominal_planar_contact_mm2=bear209,currentRail_source_bearing_height=40.52,case_floor=40.76,scope='Newsupportednominalcasebearing/weightpath; assembly/pullfitphase2 andcurrentcontext stillOPEN, notdeliveredcertification'),first_falsifier=first209,newforeign_motion_outline_initialcase_lay_OPEN=True,selected=False,N01_complete=False,actualcut=None,archive=ar209.name,archive_sha256=hashlib.sha256(ar209.read_bytes()).hexdigest(),geometry=ge209,operation_seconds=time.monotonic()-t209,process_cpu_seconds=time.process_time()-c209,pid=os.getpid(),session_id=46493)
p209.write_bytes((json.dumps(r209,indent=2)+'\n').encode());print('OPEN_FRONT_CONSTRUCTIVE',r209['status'],'solids',len(newframe209.Solids),len(newup209.Solids),'guards',len(coverage209),len(strips209),'joints',joints209,'own',len(ownrows209),'first',first209,'wall',r209['operation_seconds'],'CPU',r209['process_cpu_seconds'],hashlib.sha256(p209.read_bytes()).hexdigest(),flush=True)
