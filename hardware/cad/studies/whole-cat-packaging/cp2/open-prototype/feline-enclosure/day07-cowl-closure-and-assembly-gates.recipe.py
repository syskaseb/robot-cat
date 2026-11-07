import time,json,hashlib,zipfile,os,xml.etree.ElementTree as ET
t77=time.monotonic();cpu77=time.process_time()
boundary77=Part.makeShell(BodyOuter31.Faces);gap77=guard76.distToShape(boundary77)[0];tight77=guard76.optimalBoundingBox();assert outside76.Volume<1e-5
outline77=dict(raw_receipt=p76.name,raw_solid_distance_zero_not_outline_failure=True,why='BodyOuter31isSOLID: containeddifferentmaterial has zero solid-to-solid distance. Correctboundaryshell distance isrequired; no materialposechange/retestforeignpairs.',actual_outer_boundary_gap_mm=gap77,actual_outside_volume_mm3=outside76.Volume,tight_bounds_mm=[[tight77.XMin,tight77.YMin,tight77.ZMin],[tight77.XMax,tight77.YMax,tight77.ZMax]],required_mm=3.25,scoped_received=gap77>=3.25-1e-7)
assert outline77['scoped_received']
assembly77=[]
for kind,source in [('M6_mount_tool',tools57),('M10_terminal_tool',tools65),('real_TE_ring_install',ringpieces67),('initial_complete_case_50mm',fullcovers65)]:
    for n,s in source.items():
        lower=bbox_lower_bound(delta76.BoundBox,s.BoundBox)
        if lower>=1.25:
            assembly77.append(dict(kind=kind,source=n,bbox_lower_mm=lower,status='SEPARATED125_BY_WHOLE_BOUNDS'));continue
        gap,w,_=delta76.distToShape(s);r=dict(kind=kind,source=n,gap_mm=gap,witnesses=[[list(a),list(b)] for a,b in w[:1]])
        if gap<1e-7:
            c=delta76.common(s);r.update(common_valid=c.isValid(),common_mm3=c.Volume if c.isValid() else None)
        r['status']='SEPARATED125' if gap>=1.25-1e-7 else 'NEW_COWL_ASSEMBLY_ACCESS_HOLD_NOT_PHYSICAL_TOOL_CONTACT'
        assembly77.append(r)
        print('COWL_ASSEMBLY77',r,flush=True)
    if any(r['status'].startswith('NEW_COWL') for r in assembly77):break
# Savedfourpanels: importjustfinalBReps, noDocument/recompute/ancestraltestreplay.
source77=OUT/'FelineTorsoPanels.FCStd';sourcehash77=hashlib.sha256(source77.read_bytes()).hexdigest();assert sourcehash77=='1055534030241b90582863b7b7055e513010c1fdadf33a8669113a7db02c1b65'
panels77={};panelrows77=[];newpanels77={};rims77={}
with zipfile.ZipFile(source77) as z:
    xml=ET.fromstring(z.read('Document.xml'))
    for n in ['FrontLeftPanel','FrontRightPanel','RearLeftPanel','RearRightPanel']:
        ob=next(o for o in xml.findall('.//ObjectData/Object') if o.attrib['name']==n);e=ob.find("Properties/Property[@name='Shape']/Part").attrib['file'];pl=ob.find("Properties/Property[@name='Placement']/PropertyPlacement").attrib
        assert all(abs(float(pl[k]))<1e-12 for k in ['Px','Py','Pz','Q0','Q1','Q2']) and abs(float(pl['Q3'])-1)<1e-12
        raw=z.read(e);s=Part.Shape();s.importBrepFromString(raw.decode('utf-8'));assert s.isValid();panels77[n]=s
        changed=s.cut(portal76) if n.startswith('Front') else s.copy();assert changed.isValid();newpanels77[n]=changed
        added=changed.cut(s);removed=s.cut(changed);opgap=fullop75.distToShape(changed)[0]
        outertool=Part.makeCylinder(18.25,length74+extra75+40,tip68-axis74*20,axis74);annulus=outertool.cut(portal76);rim=changed.common(annulus);assert rim.isValid();rims77[n]=rim
        row=dict(name=n,source_entry=e,source_member_sha256=hashlib.sha256(raw).hexdigest(),identity_XML_NOT_applied_twice=True,source_solids=len(s.Solids),result_solids=len(changed.Solids),added_mm3=added.Volume,removed_mm3=removed.Volume,full_source_R15_operator_gap_mm=opgap,retained_2mm_radial_annulus_material_mm3=rim.Volume,annulus_solids=len(rim.Solids),old_panel_connected_preserved=len(s.Solids)==len(changed.Solids)==1)
        panelrows77.append(row);print('COWL_PANEL77',row,flush=True)
        if time.monotonic()-t77>18:break
ar77=OUT/'day07-S0-fixed-cowl-closure-and-assembly.breps.zip';assert not ar77.exists();ge77=[]
with zipfile.ZipFile(ar77,'w',zipfile.ZIP_DEFLATED) as z:
    items=list(newpanels77.items())+[(n+':actual_retained_aperture_annulus',s) for n,s in rims77.items() if s.Volume>1e-8]+[('S0:fixed_guard_candidate',guard76)]
    for i,(n,s) in enumerate(items):
        raw=s.exportBrepToString().encode();e=str(i)+'.brep';z.writestr(e,raw);ge77.append(dict(name=n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s)))
    z.writestr('manifest.json',(json.dumps(dict(geometry=ge77,scope='Candidateclosurepanels: onlyactualnewfunctionaloperatorcut/materialsubset; anchors/seamsnotinvented. No oldE6framecut/selectedcurrentchange.'),indent=2)+'\n').encode())
r77=dict(id='day07-S0-fixed-cowl-closure-and-assembly',status='BOUNDED_FIXED_COWL_ACCESS_OR_CLOSURE_HOLD' if any(r['status'].startswith('NEW_COWL') for r in assembly77) else 'LOCAL_FIXED_COWL_ASSEMBLY_AND_APERTURE_RECEIVED_ANCHOR_CLOSURE_OPEN',outline_correction=outline77,assembly_rows=assembly77,all_affected_assembly_scopes_received=not any(r['status'].startswith('NEW_COWL') for r in assembly77) and len(assembly77)==14,panel_source=source77.name,panel_source_sha256=sourcehash77,panel_rows=panelrows77,panel_cursor=len(panelrows77),panel_total=4,frame_disposition='ActualcurrentE6mechanical1311frameuntouched. Source4torsoPANELSarefunctionalclosurecandidates; existingsource frame_mounts_complete=false/panel-frameanchorsandseamsOPEN. CutandretainedannulusdoNOTbythemselvesprovepanelattachment orfullstructuralclosure; cannotclaimarbitraryskin nonstructural.',terminal_protection_disposition='Fixedfrontguard/operatorbaffle isrealmaterial butterminalshieldingmustinclude actualrear/lateralclosure aroundcurrentstuds/rings. Apertureray/totoolclearancealoneisnotcompleteinsulationorhandprotectionproof. No oldControl_S0inheritance.',archive=ar77.name,archive_sha256=hashlib.sha256(ar77.read_bytes()).hexdigest(),geometry=ge77,current1292_and_effective1311_unchanged=True,new_guard_not_selected=True,no_hinge_or_new_purchased_hardware=True,no_old_static_or_ring_pair_replay=True,selected=False,N01_complete=False,operation_seconds=time.monotonic()-t77,process_cpu_seconds=time.process_time()-cpu77,pid=os.getpid(),session_id=46493)
p77=OUT/'day07-S0-fixed-cowl-closure-and-assembly.json';assert not p77.exists();p77.write_bytes((json.dumps(r77,ensure_ascii=False,indent=2)+'\n').encode());print('COWL_FINAL77',r77['status'],gap77,len(assembly77),len(panelrows77),r77['operation_seconds'],r77['process_cpu_seconds'],hashlib.sha256(p77.read_bytes()).hexdigest(),flush=True)
