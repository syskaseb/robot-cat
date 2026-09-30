"""Select one fixed yaw connector/support replacement, not whole wiring."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'hardware/manufacturing/one-batch-prototype-r24'
C=ROOT/'hardware/cad/studies/head-fixed-yaw-feed-r3'
OUT=ROOT/'hardware/manufacturing/one-batch-prototype-r25'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def dump(n,v):(OUT/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def main():
    OUT.mkdir(exist_ok=True);assert not (OUT/'selection.json').exists()
    checks=read(C/'checks.json');plan=read(C/'plan.json');assert not checks['hits'] and len(checks['slot_checks'])==8
    s=read(P/'selection.json');q=read(P/'one-order-quantities.json')
    part=next(x for x in s['prints'] if x['identity']=='head:YawCarrier')
    file=C/'YawCarrierJRSeat_candidate_x1.stl'
    part.update(stl=file.relative_to(ROOT).as_posix(),sha256=sha(file),recipe=(C/'plan.json').relative_to(ROOT).as_posix(),status='selected_prototype_fixed_yaw_JR_splice_support',orientation='Carrier foot on bed, brim5; remove support from accessible underside ledges in phase2')
    s.update(parent_selection_sha256=sha(P/'selection.json'),phase1_complete=False)
    s['conditions'].append('R25 one stationaryYawCarrier replacement: JR housing cradle, separate factory/extension insulation restraints, three rigid staggered-splice seats. Factory250mm uncut,220mm stationaryR22 route plus30mm end/slack budget.808 changed nominal pairs0hits and8 real tie apertures. Fixed factoryU extendsX-221.04 below head: assess slack/snags unpowered. CentralF_HY/G_AUX/U1 and pitch feeds still incomplete.')
    row=next(x for x in q['lines'] if x['id']=='tie:111-02370');assert row['installed']==44;row['installed']=48
    row['note']+=' R25 adds4 fixed yaw:2 JR housing,1 factory insulation and1 extension insulation. Existingbag100 sufficient; cut/replace for removal.'
    q['selected_prints']=(OUT/'selection.json').relative_to(ROOT).as_posix()
    dump('selection.json',s);dump('one-order-quantities.json',q)
    interface=dict(status='SELECTED_CONDITIONAL_FIXED_YAW_JR_SUBASSEMBLY',
      factory250_uncut=True,reserved_centerline_mm=220,fit_end_budget_mm=30,factory_min_design_bend_radius_mm=22,
      factory_min_x_mm=plan['U_turn_x_mm']-22,factory_y_mm=[-56.8,-12.8],factory_z_mm=60.2,
      factory_profile_mm=plan['factory_flat_profile_mm'],JR_bbox_mm=plan['JR_bbox_mm'],
      splice_reservation=plan['splices'],fixed_harness_start_mm=[-70,-56.8,60.2],
      wire_paths=plan['wires'],pin_order='Delivered JR orientation check: GND,centerAUX6,PWM; do not infer viewing direction from wire colors alone.',
      restraints=plan['tie_stations'],new_stls=1,net_installed_parts=0,additional_ties=4,new_screws=0,new_skus=0,
      checked=dict(component_pairs=len(checks['rows']),hits=0,real_through_floor_slots=8,native=checks['geometry'],scope=checks['stationary_geometry_scope']),
      assembly=plan['assembly'],service=plan['service'],
      limitations=['Factory lead/JR/insulation dimensions provisional; physical fitting and no-crush tie pressure in phase2','Fixed U is an external nominal route, not gravity/snag qualification','CentralF_HY/G_AUX/U1 feeds and centralpitch feeds remain phase1 construction','Other complete robot harness and protection/assembly consolidation remain'],
      physical_pass=False,phase1_complete=False)
    dump('fixed-yaw-interface.json',interface)
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    import math
    fig,axs=plt.subplots(1,2,figsize=(12,5))
    ax=axs[0];D=-plan['U_turn_x_mm'];r=22
    xx=[-112.2,-D]+[-D-r*math.sin(t*math.pi/100) for t in range(101)]+[-135]
    yy=[-12.8,-12.8]+[-34.8+r*math.cos(t*math.pi/100) for t in range(101)]+[-56.8]
    ax.plot(xx,yy,label='fabryczny kabel:220mm+30mm budżetu',color='#bf753b')
    ax.add_patch(Rectangle((-122,-20),24,40,fill=False,ec='gray',label='oryginalnyCarrier'))
    for b in plan['additions_mm']:ax.add_patch(Rectangle((b[0],b[1]),b[3]-b[0],b[4]-b[1],color='#7aa4b4',alpha=.25))
    b=plan['JR_bbox_mm'];ax.add_patch(Rectangle((b[0],b[1]),b[3]-b[0],b[4]-b[1],color='#333',alpha=.4,label='JR30×12 prowizoryczne'))
    ax.plot([-104,-76],[-56.8,-56.8],color='#ca45a5',label='izolowane luty na sztywnej półce')
    ax.set(xlabel='X mm',ylabel='Y mm',title='Stały podzespół yaw, nie cała wiązka');ax.set_aspect('equal');ax.legend(fontsize=8);ax.grid(alpha=.2)
    ax=axs[1]
    for b in plan['additions_mm']:ax.add_patch(Rectangle((b[0],b[2]),b[3]-b[0],b[5]-b[2],color='#7aa4b4',alpha=.25))
    ax.add_patch(Rectangle((-135,55.2),30,10,fill=False,ec='#333'))
    ax.plot([-149,-135,-105,-65],[60.2]*4,color='#bf753b');ax.plot([-100,-92,-84],[60.2]*3,'o',color='#ca45a5')
    ax.set(xlabel='X mm',ylabel='Z mm',title='JR i osobne odciążenia izolacji',ylim=(48,70));ax.grid(alpha=.2)
    fig.suptitle('R25: zamiennyYawCarrier,4opaski,bez nowych śrub / bez physicalPASS');fig.tight_layout();fig.savefig(OUT/'preview.png',dpi=150);plt.close(fig)
    (OUT/'README.md').write_text('# R25: stałe mocowanie yaw/JR/lutów\n\nJeden zamiennyYawCarrier x1, bez zwiększenia liczby wydruków;66zadań/100PETG/4próbki.4T18I więcej,48zbag100. Fabryczny250mm niecięty; droga220mm zR22 i30mm budżetu końców/luzu. Trzy izolowane staggeredluty22AWG→0,5mm² na sztywnej półce, niezależne odciążenia izolacji i dwa złącza housingties.808zmienionych par nominalnych0hits;8realnych przelotów, singleSolid/strictBOP/parametr/reopen. To nie domyka centralnych doprowadzeń, całej głowy/wiązki ani fazy1. Długa zewnętrzna droga i rzeczywiste pasowania do przymiarki w fazie2.\n',encoding='utf-8')
    finalize()
def finalize():
    pins=read(P/'manifest.json')['files_sha256'].copy()
    checks=read(C/'checks.json');pins.update(checks['input_sha256']);pins.update(checks['additional_source_sha256'])
    for folder in (C,OUT):
        for p in folder.iterdir():
            if p.is_file() and p.suffix!='.FCBak' and p.name not in ('manifest.json','validation-manifest.json'):pins[p.relative_to(ROOT).as_posix()]=sha(p)
    for n in ('head_fixed_yaw_feed_r1.py','head_fixed_yaw_feed_r2.py','head_fixed_yaw_feed_r3.py','select_fixed_yaw_r25.py'):
        p=ROOT/'tools/electronics'/n;pins[p.relative_to(ROOT).as_posix()]=sha(p)
    assert all(sha(ROOT/p)==h for p,h in pins.items())
    dump('manifest.json',dict(files_sha256=pins,new_stls=1,selected_jobs=66,installed_petg_parts=100,samples=4,physical_pass=False,phase1_complete=False))
    dump('validation-manifest.json',dict(schema_version=1,readiness='prototype',files=[dict(path=p,sha256=h) for p,h in pins.items()],gates={k:dict(status='open',reason='Conditional fixed yaw support; whole construction/physical readiness remains open') for k in ('geometry','assembly','fit','petg','loads','electrical','service')}))
    print(json.dumps(dict(pins=len(pins),new_stls=1,jobs=66,parts=100,all_hashes_verified=True)))
if __name__=='__main__':
    if '--finalize' in sys.argv:finalize()
    else:main()
