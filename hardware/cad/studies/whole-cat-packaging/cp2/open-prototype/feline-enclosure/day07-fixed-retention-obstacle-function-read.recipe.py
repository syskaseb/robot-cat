import time,json,hashlib
t102=time.monotonic();cpu102=time.process_time();u1102=ctx83['Underdeck:PositiveFoundation'];assert u1102.isValid();sections102=[]
for axis,val in [('Z',40.5),('Z',44),('X',-59.2),('X',-38.8)]:
    if axis=='Z':pl=Part.Face(Part.makePolygon([A.Vector(x,y,val) for x,y in [(-75,35),(-20,35),(-20,95),(-75,95),(-75,35)]]))
    else:pl=Part.Face(Part.makePolygon([A.Vector(val,y,z) for y,z in [(35,30),(95,30),(95,62),(35,62),(35,30)]]))
    sec=u1102.section(pl);curves=[]
    for e in sec.Edges:
        curves.append([[p.x,p.y] if axis=='Z' else [p.y,p.z] for p in e.discretize(Deflection=.08)])
    sections102.append(dict(axis=axis,value_mm=val,coordinates='XY' if axis=='Z' else 'YZ',curves=curves))
assert co.isValid() and abs(co.Volume-15.905377503769127)<1e-5
r102=dict(id='day07-SOURCE-fixed-retention-obstacle-function-read',status='CURRENT_U1_MATERIAL_SECTIONS_FOR_ONE_RETENTION_C1_NOT_NEW_VARIANT',source_actor='Underdeck:PositiveFoundation',source_current_role='U1complete_short_carrier, retainfeet/holes/lowerbranch/understep/foamC/metal/FHYsupport+screwaccess. No arbitraryownfusion.',current_valid=u1102.isValid(),current_export_sha256=hashlib.sha256(u1102.exportBrepToString().encode()).hexdigest(),current_volume_mm3=u1102.Volume,cached_first_falsifier_common_mm3=co.Volume,cached_common_bounds_mm=saved_bounds(co),no_pair_retest=True,sections=sections102,causal_C1_direction='Reversewholefixed100closure+head/25feed/fulltailparking toinboard(+X)side, ifactualcurrentsectionsandfullneighborsallow; root/open9capacity/sourceposeunchanged. Notpad/column/PCBoffset andno thirdretentionvariant. Preserve100/wholeuncuttail/R3/margins/foreign1.25. Ifinboardblockedreconsiderwholeguide/retention/loadinterface not scalarstockshift.',source_function_packet='day07-coordinator-fixed-print-source-functions.json',operation_seconds=time.monotonic()-t102,process_cpu_seconds=time.process_time()-cpu102,selected=False,N01_complete=False)
p102=OUT/'day07-SOURCE-fixed-retention-obstacle-function-read.json';assert not p102.exists();p102.write_bytes((json.dumps(r102,ensure_ascii=False,indent=2)+'\n').encode());print('RETAIN102_FINAL',r102['cached_common_bounds_mm'],[(q['axis'],q['value_mm'],len(q['curves'])) for q in sections102],r102['operation_seconds'],r102['process_cpu_seconds'],hashlib.sha256(p102.read_bytes()).hexdigest(),flush=True)
