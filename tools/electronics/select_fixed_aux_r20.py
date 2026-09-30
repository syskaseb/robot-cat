"""Select one supported fixed AUX subassembly, preserving all other prints."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PARENT=ROOT/'hardware/manufacturing/one-batch-prototype-r19'
OUT=ROOT/'hardware/manufacturing/one-batch-prototype-r20'
CAD=ROOT/'hardware/cad/studies/aux-carrier-wire-ports-r1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def main():
    OUT.mkdir(exist_ok=True)
    folders={n:ROOT/'hardware/electronics/full-cat'/f for n,f in {
      'converter':'aux-converter-routes-r5','XA03':'aux-converter-routes-r2',
      'XA05':'xa05-main-aux-return-r2','XA06':'xa06-ground-bridge-r1'}.items()}
    c=read(folders['converter']/'checks.json');g=read(CAD/'geometry.json')
    assert not c['hits'] and not g['hits'] and g['relocated_recompute_ok']
    assert not read(folders['XA05']/'checks.json')['hits'] and not read(folders['XA06']/'checks.json')['hits']
    s=read(PARENT/'selection.json');q=read(PARENT/'one-order-quantities.json')
    selected=[p for p in s['prints'] if p['identity']=='electronics:Carrier service ports'];assert len(selected)==1
    selected[0].update(stl=(CAD/'Carrier_aux_wire_ports_candidate_x1.stl').relative_to(ROOT).as_posix(),
      sha256=sha(CAD/'Carrier_aux_wire_ports_candidate_x1.stl'),recipe=(CAD/'plan.json').relative_to(ROOT).as_posix(),
      status='selected_fixed_AUX_support_candidate',orientation='bottom localZ0 flat; wing coplanar; 5mm brim',print_size_mm_including_5mm_brim=[240,140.5,4])
    s.update(parent_selection_sha256=sha(PARENT/'selection.json'),fixed_aux_geometry_sha256=sha(CAD/'geometry.json'),phase1_complete=False)
    s['conditions'].append('R20 replaces only Carrier, adding two dedicated cable passages and one north-wing support. XA02–06 have nominal complete routes, fixed supports and assigned logical WAGO mouths. Physical pad solder/port/tie dry-fit remains phase2. Head moving harness, remaining SKU/endpoints and source protection still open.')
    additional_ties=14
    row=next(x for x in q['lines'] if x['id']=='tie:111-02370');row['installed']+=additional_ties
    assert row['installed']<=row['planning_quantity']
    row['note']+= ' R20 adds14:6 Carrier pad/port restraints,2 converter-WAGO ends,1 XA02 middle support,3 XA05 endpoints/midspan and2 XA06 endpoints. Existing bag100 covers37 installed.'
    q.update(selected_prints='hardware/manufacturing/one-batch-prototype-r20/selection.json',phase1_complete=False)
    routes={}
    lengths={**c['lengths_mm'],'XA05':read(folders['XA05']/'checks.json')['length_mm'],'XA06':read(folders['XA06']/'checks.json')['path_length_mm']}
    for n,length in lengths.items():
        red=n in ('XA02','XA03');soldered=n in ('XA02','XA03','XA04')
        routes[n]=dict(sku='HELU23502' if red else 'HELU23501',color='red' if red else 'black',section_mm2=1,OD_mm=2.5,fixed_R_mm=15,
          nominal_centerline_mm=length,cut_rule='Dry-fit actual joints/cages first.30mm service at each detachable end;11mm stripping per WAGO end. Board solder end: only exposed length needed on pad, no long bare strand.',
          conservative_working_blank_m=round((length+60+22+49)/50)*.05,
          procurement='Included in existing5m red/5m black stock, retain25percent overall reserve; not a second purchase line.')
    interface=dict(status='SELECTED_CONDITIONAL_FIXED_AUX_INTERFACE',routes=routes,
      endpoints={'XA02':['F_AUX.out','4092.VIN'],'XA03':['4092.VOUT','P_AUX.1'],'XA04':['4092.GND','G_AUX.2'],
        'XA05':['P0G2.5','G_AUX.1'],'XA06':['G_AUX.5','G_TAIL.1']},
      rails='BAT_SW before converter, AUX6 after converter, separate power-return conductors; never tie MAIN/AUX positive rails or use signal GND for motor return.',
      converter_pad_registration=read(folders['converter']/'plan.json')['pad_basis'],pads_world_mm=read(folders['converter']/'plan.json')['pads_world_mm'],
      unnumbered_WAGO_logical_cages={'G_AUX_negative_to_positive_Y':[{'label':4,'y':-81},{'label':2,'y':-75},{'label':5,'y':-69},{'label':3,'y':-63},{'label':1,'y':-57}],
        'P_AUX_cage1_Y':66,'P_AUX_cage2_Y':72,'G_TAIL_cage1_Y':-72,
        'rule':'Apply these wire labels yourself; not manufacturer cavity numbers. Remaining mouths allocated only when their routes are made.6mm cage pitch planning, dry-fit real exits.'},
      restraints={'Carrier':'Three port ties and three board-end ties; source plan describes supports and release order.',
        'XA02_middle':'One T18I around insulated wire(10,48,132), interlinked to existing P_AUX mounting tie at(10,55.5,109); approx24mm offset, no new hole or fastener.',
        'XA05_middle':'One T18I interlinked to existing G1 right Deck slot/mount tie at(86,-8.5,109), holding wire(90,-8.5,113.5). Nominal4mm lateral offset; support independent of G1 electric cage.',
        'WAGO_ends':'Separate insulated-lead ties to mounted connector ties. XA05 two ends; XA06 two ends; XA03/XA04 one WAGO end each; XA02 cassette output restraint already exists.'},
      guards='No wire against fastener edge; round/deburr all three Carrier5mm passages and strap slots before fitting. Wire remains fixed and centered; no dynamic duty through holes. Change guard/print if delivered sleeve or tie makes contact.',
      assembly='Bare Deck/hangers first, WAGO mounted, bare revised Carrier and loose support ties, then populated PCBs and shaped wiring. Solder with battery absent, sleeve joints, inspect bare bridges and polarity. Cover last.',
      service='Battery absent. Remove cover, loosen connector restraints and WAGO levers, release six Carrier wire ties before lifting cassette. No tugging on solder pads; retain at least30mm service reserve at detachable ends. Replace cut ties.',
      rejection_history='r2/r3 converter leads hit selected cover and each other; r4 XA04 hit XA06; r5 rerouted and requires native Carrier now supplied. XA05r1 hit old audio reference and XA06. r2 retains no audio as already approved scope and uses a different unused G_AUX logical mouth; actual selected cover remains tested.',
      open=['Moving head/yaw/PWM harness and complete remaining fixed harness','Source and branch DC fault/current/thermal sizing','Unresolved commercial SKU rows, actual terminations and final assembly consolidation'],
      phase2=['Delivered PCB revision/pads, solder quality/no bridges','Actual WAGO entry/pitch and tie pressure/sleeve clearance','PETG holes/flatness and cover fit','Disconnected continuity/polarity/tug checks before electrical tests'],
      additional_ties=additional_ties,new_stls=1,new_fasteners=0,new_skus=0,phase1_complete=False,physical_pass=False)
    write(OUT/'selection.json',s);write(OUT/'one-order-quantities.json',q);write(OUT/'fixed-aux-interface.json',interface)
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    fig,axs=plt.subplots(1,2,figsize=(14,6))
    samples={**c['samples'],'XA05':read(folders['XA05']/'checks.json')['samples'],'XA06':read(folders['XA06']/'checks.json')['centerline_samples_mm']}
    colors=['#d5422f','#ef8a36','#202d38','#538191','#926746']
    for (n,vs),color in zip(samples.items(),colors):
        for ax,(i,j) in zip(axs,[(0,1),(0,2)]):ax.plot([p[i] for p in vs],[p[j] for p in vs],color=color,label=n,lw=1.8)
    axs[0].add_patch(Rectangle((-94,-58.5),230,117,color='#92b4c5',alpha=.12))
    axs[0].add_patch(Rectangle((-35,58.5),20,13.5,color='#92b4c5',alpha=.5))
    for x,y in read(CAD/'plan.json')['wire_ports_world_xy_mm']:axs[0].add_patch(plt.Circle((x,y),2.5,color='#386280',fill=False))
    axs[1].add_patch(Rectangle((-94,144),230,4,color='#92b4c5',alpha=.3))
    for ax,title in zip(axs,['XY fixed AUX routes / Carrier passages','XZ routes / Carrier height']):
        ax.set_title(title);ax.set_aspect('equal');ax.grid(alpha=.2);ax.legend(fontsize=8);ax.set_xlabel('X mm')
    fig.suptitle('R20: five fixed AUX leads + supported removable Carrier / no physical PASS');fig.tight_layout();fig.savefig(OUT/'preview.png',dpi=150);plt.close(fig)
    files=[Path(__file__),ROOT/'tools/cad/aux_carrier_wire_ports_r1.py',ROOT/'tools/electronics/aux_converter_routes_r2.py',ROOT/'tools/electronics/aux_converter_routes_r3.py',ROOT/'tools/electronics/xa05_main_aux_return_r1.py',ROOT/'tools/electronics/xa06_ground_bridge_r1.py',ROOT/'tools/electronics/xb11_upstream_route.py',ROOT/'tools/electronics/full_cat_board_interfaces.py']
    for folder in {OUT,CAD,*folders.values()}:
        files.extend(p for p in folder.iterdir() if p.is_file() and p.name!='manifest.json' and p.suffix!='.FCBak')
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in files}
    for r in [c,read(folders['XA05']/'checks.json'),read(folders['XA06']/'checks.json')]:pins.update(r['source_sha256'])
    for f in [PARENT/'selection.json',ROOT/'hardware/reference/aux4092-2026-09-26/reg24d-drill.dxf',ROOT/'hardware/cad/studies/open-deck-p0/plate-r1/checks.json']:pins[f.relative_to(ROOT).as_posix()]=sha(f)
    assert len(s['prints'])==66 and s['installed_petg_parts']==100 and len(q['lines'])==104
    assert all(sha(ROOT/p['stl'])==p['sha256'] for p in s['prints'])
    assert all(sha(ROOT/n)==h for n,h in pins.items())
    write(OUT/'manifest.json',dict(status='PHASE1_INCOMPLETE_R20_FIXED_AUX_SELECTED',files_sha256=pins,new_stls=1,selected_jobs=66,installed_petg_parts=100,physical_pass=False))
    print(json.dumps(dict(jobs=66,parts=100,lines=104,pins=len(pins),ties=row['installed'])))
if __name__=='__main__':main()
