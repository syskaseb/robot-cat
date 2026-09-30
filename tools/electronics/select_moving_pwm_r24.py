"""Close one moving-wire placeholder without rerunning unchanged OD5 geometry."""
import hashlib,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'hardware/manufacturing/one-batch-prototype-r23'
OUT=ROOT/'hardware/manufacturing/one-batch-prototype-r24'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def dump(n,v):(OUT/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def main():
    OUT.mkdir(exist_ok=True);assert not (OUT/'selection.json').exists()
    sources=dict(reviewed_utc='2026-09-30T19:10:29Z',
      manufacturer=dict(url='https://assets-cdn.helukabel.com/suppliers/Helukabel/documents/db/HELUKABEL_M23201_EN_GB.pdf',document_date='2025-07-24',pages=[0,1],part='23308',colour='yellow',section_mm2=.5,outer_diameter_approx_mm=2.1,mass_g_per_m=8.6,fixed_bend_OD=6,flexible_bend_OD=15,temperature_flexible_C=[-25,180],nominal_voltage_V=[300,500]),
      supplier=dict(url='https://www.tme.eu/pl/details/sif0.50-y/przewody-silikonowe-jednozylowe/helu/23308/',symbol='SIF0.50-Y',manufacturer_part='23308',section_mm2=.5,outer_diameter_mm=2.1,cut_meter_listing=True),
      evidence='Read primary manufacturer two-page PDF/table and exact supplier SKU. Local JSON pins this transcription, not the remote PDF bytes. No availability/delivery or purchase promise.',
      scope='Selected flexible hobby wiring; no manufacturer cycle-life/dynamic drag-chain qualification inferred.')
    dump('wire-sources.json',sources)
    radius=2.1/math.sqrt(3)+2.1/2
    assert radius<2.5
    route=read(ROOT/'hardware/electronics/full-cat/head-complete-yaw-transitions-r3/checks.json')
    assert not route['hits'] and min(x['min_sampled_radius_mm'] for x in route['poses'])>=31.5
    interface=dict(status='SELECTED_MG92B_SIGNAL_WIRE_23308',
      sku='HELU23308 / TME SIF0.50-Y',section_mm2=.5,colour='yellow',planning_quantity_m=6,
      replaces='wire:moving-PWM-0.14:SKU_OPEN',
      signal_paths=['XS13 U1/R1.2 -> C_HY.PWM','XS23 U1/R2.2 -> C_HP.PWM','XS33 U1/R3.2 -> C_TY.PWM'],
      electrical='PWM5 logic signal only; not AUX6 power. Separate black0.5 power return, red0.5 AUX6 behind the selected branch fuse. Rigid local U1 adapter leads remain0.14mm2 <=50mm.',
      transitions='Keep factory250mm and premade JR22AWG end. Cut extension tails after fit, join to red/black/yellow0.5 with three separately insulated staggered lap joints on rigid seats, never in free-moving span. Do not crimp0.5 into contacts intended for22..26AWG.',
      packing=dict(wire_count=3,individual_OD_approx_mm=2.1,triangular_bundle_radius_mm=radius,existing_route_envelope_radius_mm=2.5,radial_margin_nominal_mm=2.5-radius,max_equal_individual_OD_for_envelope_mm=2.5/(1/math.sqrt(3)+.5),geometry_basis='Three equal circular wires tangent in triangular packing. No sheath/spiral wrap in the OD5 free span; loose retainers only at end seats. Actual combined OD <=5mm required after delivery.'),
      bending=dict(fixed_mm=12.6,moving_mm=31.5,min_sampled_existing_head_radius_mm=min(x['min_sampled_radius_mm'] for x in route['poses']),proof='All three selected wires share the same OD and bend requirements. Existing OD5 swept envelope is unchanged; no route-matrix rerun. Other routes still require their own construction.'),
      phase2=['Measure actual insulation/bundle and adjust replaceable seats if OD>5mm.','Unpowered fit/pinout, radius, joint insulation, strain relief and movement checks.','Refresh stock, meter-sale quantity, price and delivery for one order.'],
      new_stls=0,net_quantity_lines=0,physical_pass=False,phase1_complete=False)
    dump('signal-wire-interface.json',interface)
    s=read(P/'selection.json');q=read(P/'one-order-quantities.json')
    s['conditions'].append('R24 selects HELU23308 yellow0.5mm2 OD2.1 for all three MG92B signal harnesses. Three equal OD2.1 wires fit nominal OD5 envelope in triangular packing; head route unchanged. No new prints; actual bundle/joints checked in phase2. Other whole-harness and protection work remains.')
    s['parent_selection_sha256']=sha(P/'selection.json')
    line=next(x for x in q['lines'] if x['id']=='wire:moving-PWM-0.14:SKU_OPEN')
    line.update(id='wire:moving-PWM-HELU23308',name='HELU23308 SiF yellow0.5mm2 OD2.1, TME SIF0.50-Y',source=(OUT/'wire-sources.json').relative_to(ROOT).as_posix(),note='6m existing planning allowance, cut after fit, +30mm per detachable end and25% purchasing allowance already reserved. Rigid local U1 leads0.14 unchanged; JR22AWG tails joined outside motion. Flexible minimum31.5mm/fixed12.6. Meter listing, procurement refresh phase2; not ordered.')
    q['selected_prints']=(OUT/'selection.json').relative_to(ROOT).as_posix()
    assert len(q['lines'])==104 and len(s['prints'])==66
    dump('selection.json',s);dump('one-order-quantities.json',q)
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle
    fig,ax=plt.subplots(figsize=(6,5));ax.add_patch(Circle((0,0),2.5,fill=False,ec='black'))
    centres=[(0,2.1/math.sqrt(3)),(-1.05,-2.1/(2*math.sqrt(3))),(1.05,-2.1/(2*math.sqrt(3)))]
    for c,color,label in zip(centres,['#ffd046','#c63b34','#333'],['PWM','AUX6','GND']):ax.add_patch(Circle(c,1.05,color=color));ax.text(*c,label,ha='center',va='center',color='white' if label=='GND' else 'black')
    ax.set(xlim=(-3,3),ylim=(-3,3),aspect='equal',xlabel='mm',ylabel='mm',title='R24: trzy żyły OD2,1 w istniejącej obwiedni OD5\nNominalny przekrój, realny pakiet po dostawie')
    fig.tight_layout();fig.savefig(OUT/'preview.png',dpi=150);plt.close(fig)
    (OUT/'README.md').write_text('# R24: zamknięty SKU ruchomego sygnału MG92B\n\nHELU23308 żółty0,5mm² zastępuje ogólny sygnałowy SKU_OPEN;6m planowanego zapasu,0nowychSTL,66zadań/100PETG/4próbki. Adaptery U1 lokalne0,14mm² pozostają. Dane producenta i exactSKU dostawcy zapisane w wire-sources.json. Nominalny pakiet trzech żył mieści się w niezmienionej obwiedniOD5; stałyR12,6 i ruchomyR31,5. Złącza/fabryczny kabel bez cięcia, luty i izolacja na sztywnych odcinkach. To nie zamyka reszty wiązki ani fazy1.\n',encoding='utf-8')
    finalize()
def finalize():
    pins=read(P/'manifest.json')['files_sha256'].copy()
    for p in OUT.iterdir():
        if p.is_file() and p.name not in ('manifest.json','validation-manifest.json'):pins[p.relative_to(ROOT).as_posix()]=sha(p)
    pins[Path(__file__).relative_to(ROOT).as_posix()]=sha(Path(__file__))
    assert all(sha(ROOT/p)==h for p,h in pins.items())
    dump('manifest.json',dict(files_sha256=pins,new_stls=0,selected_jobs=66,installed_petg_parts=100,samples=4,physical_pass=False,phase1_complete=False))
    dump('validation-manifest.json',dict(schema_version=1,readiness='prototype',files=[dict(path=p,sha256=h) for p,h in pins.items()],gates={k:dict(status='open',reason='Exact wire selected; complete construction/physical validation still open') for k in ('geometry','assembly','fit','petg','loads','electrical','service')}))
    print(json.dumps(dict(pins=len(pins),new_stls=0,all_hashes_verified=True)))
if __name__=='__main__':
    import sys
    if '--finalize' in sys.argv:finalize()
    else:main()
