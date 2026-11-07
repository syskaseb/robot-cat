_t=time.monotonic();_c=time.process_time();p=OUT/'day30-four-factory-common-regions.json';d=json.loads(p.read_text(encoding='utf-8'))
assert d['current_foreign_common_bank_correction_review']['decision']=='GO'
q=d['current_foreign_common_bank_loadpath_correction1'];v=q['V3_receivers']['support'];rel=v['W024_riser_subset_relief'];x=rel['extrude_X'][0]
points=[A.Vector(x,y,z) for y,z in rel['polygon_YZ']];wire=Part.makePolygon(points+[points[0]]);haunch=Part.Face(wire).extrude(A.Vector(rel['extrude_X'][1]-x,0,0));strict30(haunch)
cells={n:(haunch if n==rel['replaces_cell'] else bx30(*b)) for n,b in v['cells'].items()}
new=fuse30(list(cells.values()));strict30(new);old=CentralVParts30['V:new_root_material'];added=retention.isolated(new).cut(retention.isolated(old));assert added.Volume<1e-7
caps=[retention.isolated(s) for n,s in DirectWorld30.items() if n.startswith('Station:Bank:') and any(w in n for w in ['W020/','W022/','W024/']) and n.endswith(':split_cap_exterior')]
pressure=fuse30([new]+caps);whole=fuse30([pressure,BankRetentionBed30]);assert len(whole.Solids)==1;strict30(pressure);strict30(whole)
start=len(NorthSupportRows30);support_pair(new,DirectWorld30['Station:P_SYS:case'],'corrected_support | full_actual_P_SYS',1.25)
for i in [1,2,3]:support_pair(new,DirectWorld30['CurrentFoundation:BankPad:Ref_Material_F_L'+str(i)+'_CP2_Housing_0_0:0'],'corrected_support | actual_pad'+str(i),root=True)
for i,s in enumerate(caps):support_pair(new,s,'corrected_support | full_original_cap'+str(i),root=True)
rr=NorthSupportRows30[start:];assert not any(a['hold'] for a in rr)
changed={'V:new_root_material':new,'V:functional_pressure_support':pressure,'Bank:whole_with_V_supports':whole};archive=OUT/'day30-astra-common-bank-v-correction1.breps.zip';assert not archive.exists();manifest=[]
with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
 for n,s in changed.items():
  raw=s.exportBrepToString().encode('utf-8');entry=str(len(manifest))+'.brep';z.writestr(entry,raw);manifest.append(dict(name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s)))
 z.writestr('manifest.json',json.dumps(manifest).encode('utf-8'))
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 for m in manifest:
  s=Part.Shape();s.importBrepFromString(z.read(m['entry']).decode('utf-8'));strict30(s)
CentralVParts30.update({n:s for n,s in changed.items() if n.startswith('V:')});CommonBankWithV30=whole
r=dict(status='COMMON_BANK_V_COMPLETE_SOURCE_STOCK_ROOT_SCOPED_RECEIVED',rows=rr,added_material_mm3=added.Volume,removed_material_mm3=old.Volume-new.Volume,whole_union_solids=len(whole.Solids),unchanged_V_geometry_ref=d['current_foreign_common_bank_V_functional_space']['archive'],unchanged_rows_reused=True,archive=archive.name,archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),geometry=manifest,operation_seconds=time.monotonic()-_t,process_cpu_seconds=time.process_time()-_c,changed_foreign_and_loose_guide_and_whole_integration_OPEN=True,N01_complete=False)
d['current_foreign_common_bank_V_correction1_receipt']=r;raw=json.dumps(d,ensure_ascii=False,indent=2).encode('utf-8');assert len(raw)<5000000;t=p.with_suffix('.astra.tmp');t.write_bytes(raw);t.replace(p)
print('COMMON_BANK_V_CORRECTION_RECEIVED',json.dumps(r,ensure_ascii=True),flush=True)
