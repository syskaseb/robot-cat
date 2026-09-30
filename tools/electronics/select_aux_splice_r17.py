"""Select one ordinary WAGO and one removable XB11 shelf; keep all64 parent STLs."""
import hashlib,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PARENT=ROOT/'hardware/manufacturing/one-batch-prototype-r16'
OUT=ROOT/'hardware/manufacturing/one-batch-prototype-r17'
CAD=ROOT/'hardware/cad/studies/aux-splice-shelf-r2'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def preview(plan):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    fig,(a,b)=plt.subplots(1,2,figsize=(12,5))
    for ax in (a,b):ax.set_aspect('equal');ax.grid(alpha=.2)
    def xy(box,color,label):
        a.add_patch(Rectangle((box[0],box[1]),box[3]-box[0],box[4]-box[1],facecolor=color,alpha=.4,edgecolor='black'))
        a.text((box[0]+box[3])/2,(box[1]+box[4])/2,label,ha='center',va='center',fontsize=8)
    xy(plan['plate_world_bbox_mm'],'#acb7bd','')
    w=plan['wire_window_world_xyxy_mm'];a.add_patch(Rectangle(w[:2],w[2]-w[0],w[3]-w[1],facecolor='white',edgecolor='black'))
    xy(plan['shifted_F_HY_bbox_mm'],'#e4ae49','F_HY\nbelow')
    xy(plan['connector_closed_bbox_mm'],'#6ca7dd','221-412\nabove')
    for key,size in (('holder_slots_world_xy_mm','holder_slot_xy_mm'),('connector_slots_world_xy_mm','connector_slot_xy_mm')):
        sx,sy=plan[size]
        for x,y in plan[key]:a.add_patch(Rectangle((x-sx/2,y-sy/2),sx,sy,facecolor='white',edgecolor='black'))
    a.set_xlim(-3,78);a.set_ylim(-94,-56);a.set_title('XY: inherited holder slots + WAGO ties')
    for box,col,label in ((plan['plate_world_bbox_mm'],'#acb7bd','PETG3mm'),(plan['shifted_F_HY_bbox_mm'],'#e4ae49','F_HY'),(plan['connector_closed_bbox_mm'],'#6ca7dd','221-412')):
        b.add_patch(Rectangle((box[0],box[2]),box[3]-box[0],box[5]-box[2],facecolor=col,alpha=.4,edgecolor='black'))
        b.text((box[0]+box[3])/2,(box[2]+box[5])/2,label,ha='center',va='center',fontsize=8)
    # Draw a cutaway of the window, not a solid plate intersecting the route.
    b.add_patch(Rectangle((w[0],102),w[2]-w[0],3,facecolor='white',edgecolor='black',linestyle=':'))
    theta=math.acos(1-13/30);r=15
    steps=[theta*i/50 for i in range(51)]
    x=[20+r*math.sin(t) for t in steps];z=[96.15+r*(1-math.cos(t)) for t in steps]
    endx=20+2*r*math.sin(theta)
    x += [endx-r*math.sin(theta-t) for t in steps];z += [94.15+r*math.cos(theta-t) for t in steps]
    x+=[50];z+=[109.15]
    b.plot(x,z,color='#c0392b',linewidth=3,label='local DESIGN R15')
    b.set_xlim(-3,78);b.set_ylim(87,123);b.set_title('XZ cutaway: assumed lead exit + S bend');b.legend(fontsize=8,loc='upper left')
    for ax in (a,b):ax.set_xlabel('World X mm')
    a.set_ylabel('World Y mm');b.set_ylabel('World Z mm')
    fig.suptitle('R17 conditional XB11 mount: no physical PASS; full upstream path OPEN')
    fig.tight_layout();fig.savefig(CAD/'preview.png',dpi=150);plt.close(fig)
def main():
    selection=read(PARENT/'selection.json');ledger=read(PARENT/'one-order-quantities.json')
    g=read(CAD/'geometry.json');wire=read(CAD/'wire-e6.json');plan=read(CAD/'plan.json')
    assert g['nominal_clear'] and wire['nominal_clear'] and not g['physical_pass']
    assert g['relocated_reopen_ok'] and g['strict_bop_errors']==0 and g['export_bed_correction']['corrected_min_z_mm']==0
    assert all(all(v<1e-5 for v in p['local_positive_hits_mm3'].values()) for p in g['local_wire_design_checks'])
    assert len(selection['prints'])==64 and len(ledger['lines'])==102
    stl='hardware/cad/studies/aux-splice-shelf-r2/AuxSpliceShelf_R2_candidate_x1.stl'
    assert sha(ROOT/stl)==g['stl_sha256']
    preview(plan)
    selection['prints'].append({'identity':'electronics:XB11-SpliceShelf','module':'AUX6 input to F_HY',
        'stl':stl,'quantity':1,'purpose':'installed_candidate','status':'conditional_hobby_prototype_local_route_only',
        'material':'PETG','orientation':'flat74x30x3,5mm planning brim; supports/profile in phase2',
        'print_size_mm_including_5mm_brim':[84,40,3],
        'recipe':'hardware/cad/studies/aux-splice-shelf-r2/README.md','sha256':sha(ROOT/stl)})
    selection.update(jobs=65,installed_jobs=selection['installed_jobs']+1,installed_petg_parts=98,
                     parent_selection_sha256=sha(PARENT/'selection.json'))
    selection['aux_splice_shelf_geometry_sha256']=sha(CAD/'geometry.json')
    selection['aux_splice_assembly_sha256']=sha(CAD/'assembly.json')
    selection['wire_material_override_sha256']=sha(OUT/'wire-material-overrides.json')
    selection['conditions'].append('R17 adds ONLY XB11 shelf + WAGO221-412; F_HY below shelf at90..102Z replaces93..105. Existing Deck/P0 unchanged. Native/corridor screens nominal clear, actual exit/OD/cages and full upstream path unresolved.')
    selection['conditions'].append('R17 invalidates R16 loose HELU23302 mapping for XP02: preserve factory Molex2147612112/2147632112. XP03 keeps2147611112/2147631112, not inferred1111 length variants. No silicone OD2.1mm wire is manually crimped into MicroFit1.42..1.85mm contacts.')
    ledger['lines'].append({'id':'splice:WAGO221-412','name':'WAGO221-412 two-conductor lever splice for XB11 only',
        'manufacturer_sku':'221-412','supplier':'Kamami','supplier_sku':'1188364','planning_quantity':2,'installed':1,
        'unit':'pcs','url':'https://kamami.pl/szybkozlacza/1188364-wago-221-412-zlaczka-instalacyjna-2-przewody-4mm-5902186324565.html',
        'source':'https://www.wago.com/global/installation-terminal-blocks-and-connectors/splicing-connector-with-levers/p/221-412',
        'note':'1 installed +1 spare; exact voltage/section family fits6V,1mm2 and16AWG. Refresh stock/price/delivery in phase2, not ordered; no crimper required.'})
    for row in ledger['lines']:
        if row['id']=='tie:111-02370':
            row['installed']=row.get('installed',17)+4
            row['note']+=' R17 adds four working ties for XB11:two connector and two interlinked insulated-wire restraints, from existing bag100. Not a whole-robot tie census.'
    ledger.update(selected_prints='hardware/manufacturing/one-batch-prototype-r17/selection.json',line_count=103,phase1_complete=False)
    assert len({r['id'] for r in ledger['lines']})==103
    assert all(sha(ROOT/r['stl'])==r['sha256'] for r in selection['prints'])
    OUT.mkdir(exist_ok=True);write(OUT/'selection.json',selection);write(OUT/'one-order-quantities.json',ledger)
    files=[OUT/'selection.json',OUT/'one-order-quantities.json',OUT/'README.md',OUT/'wire-material-overrides.json',Path(__file__).resolve()]
    files += [CAD/n for n in ('plan.json','geometry.json','wire-e6.json','assembly.json','preview.png','README.md','AuxSpliceShelfR2.FCStd','AuxSpliceShelf_R2_candidate_x1.stl','factory16AWG_DESIGN.brep','HELU23502_DESIGN.brep')]
    files += [ROOT/'tools/cad'/n for n in ('aux_splice_shelf_r1.py','aux_splice_shelf_r2.py','aux_splice_shelf_finish.py','fuse_aux_cradle_r1.py')]
    files.append(ROOT/'tools/electronics/aux_splice_wire_e6.py')
    manifest={'status':'PHASE1_INCOMPLETE_R17_LOCAL_XB11_CONDITIONAL_MOUNT','files_sha256':{p.relative_to(ROOT).as_posix():sha(p) for p in files},
        'jobs':65,'installed_petg_parts':98,'fit_samples':4,'ledger_lines':103,'new_stls':1,'new_skus':1,'physical_pass':False,'phase1_complete':False}
    write(OUT/'manifest.json',manifest)
    print(json.dumps({'jobs':65,'petg':98,'ledger':103,'new_stls':1,'nominal_local_screen':True,'full_route':False}))
if __name__=='__main__':main()
