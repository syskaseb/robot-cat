"""Exact sleeve SKU and longer safe insulation recipe inside unchanged seats."""
import json,hashlib,math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'hardware/manufacturing/one-batch-prototype-r25'
OUT=ROOT/'hardware/manufacturing/one-batch-prototype-r26'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def dump(n,v):(OUT/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def main():
    OUT.mkdir(exist_ok=True);assert not (OUT/'selection.json').exists()
    sources=dict(reviewed_utc='2026-09-30T19:42:46Z',
      supplier=dict(url='https://www.tme.eu/pl/details/rnf-100-1_8-9-stk/rurki-termokurczliwe/te-connectivity/',sku='RNF-100-1/8-9-STK',colour='white',stick_nominal_m=1.2,listed_package_sticks=5,listed_order_increment_m=6),
      manufacturer=dict(url='https://www.te.com/en/product-5053032136.html',description='RNF-100-1/8-WH-STK',part='5053032136',stick_mm=1220,expanded_ID_min_mm=3.17,recovered_ID_max_mm=1.57,wall_nominal_mm=.5,wall_tolerance_page_mm=.15),
      drawing=dict(url='https://www.te.com/commerce/DocumentDelivery/DDEController?Action=srchrtrv&DocFormat=pdf&DocLang=English&DocNm=RNF-100_USA_STANDARD_SIZES&DocType=Customer+Drawing&PartCntxt=NB19162001',name='RNF-100_USA_STANDARD_SIZES',revision='A2 2025-07-25',size='1/8',wall_min_mm=.43,wall_max_mm=.58,longitudinal_change_percent=[-5,0]),
      evidence='Primary dimensional drawing and matching white-family page plus exact white supplierSKU. Use larger0.65mm wall from page tolerance instead of smaller drawing maximum0.58. SKU9/WH is white family nomenclature, not a measured delivered revision. JSON hash does not pin remote PDF bytes.',
      no_purchase=True,stock_price_delivery_refresh='Phase2 one order; not promised from current crawl.')
    dump('insulation-sources.json',sources)
    # There are at most two larger insulated joints at any axial station.
    half=3.4/2;small=2.1/2;third_y=math.sqrt((half+small)**2-half**2)
    bound=max(2*half,third_y+small);assert bound<3.5
    centres={'pitch_y':[101.5,109.5,117.5],'yaw_x':[-98,-90,-82]}
    bounds={'pitch_y':[95.5,123.5],'yaw_x':[-104,-76]}
    for key,values in centres.items():
        assert min(values)-6>=bounds[key][0] and max(values)+6<=bounds[key][1]
        assert values[2]-values[0]>12
    blank_min,blank_max=11.3,11.7;recovered_min=blank_min*.95
    overlap=(recovered_min-4)/2;assert overlap>3 and blank_max<12
    interface=dict(status='SELECTED_EXACT_MG92B_SPLICE_INSULATION',sku='TE RNF-100-1/8-9-STK white, TME',
      procurement_m=6,procurement_note='Current supplier minimum increment6m = five nominal1.2m sticks; preserve existingP0 assortment for larger power joints. No ordering; recheck increment in phase2.',
      installed_sleeves=9,head_selected_sleeves=6,tail_reserved_sleeves=3,trial_spares=9,total_trial_stock_use_under_m=.25,
      sleeve_cut_nominal_mm=11.5,manual_cut_tolerance_mm=.2,final_length_design_max_mm=12,
      soldered_contact_design_max_length_mm=4,min_nominal_insulation_overlap_each_end_mm=overlap,
      bare_joint_max_OD_mm=2.1,finished_individual_sleeved_joint_design_max_OD_mm=3.4,
      head_joint_centres=centres,unchanged_rigid_reserved_axial_bounds_mm=bounds,
      packing=dict(raw_wire_OD_mm=2.1,max_overlapping_sleeved_joints=2,finished_large_OD_mm=3.4,
        circle_centres_mm=[[-half,0],[half,0],[0,third_y]],bound_radius_mm=bound,existing_seat_reserved_radius_mm=3.5,radial_nominal_margin_mm=3.5-bound,
        proof='Two OD3.4 sleeves side-by-side plus one OD2.1 unsleeved insulated wire fit within unchanged OD7 envelope.12mm sleeves staggered8mm prevent triple sleeve overlap; no common overwrap adding diameter.'),
      supersedes='R23/R25 joint-length <=8mm reservation and centres only. R26 uses <=12mm finished sleeves and shifted centres, still wholly contained in the same28mm/OD7 BRep reservations. No STL/source geometry change or old matrix rerun.',
      assembly=['Battery absent; preserve factory servo250mm. Slide separate sleeve onto each premade JR extension tail before joining to0.5 SiF.','Keep bare lap joint <=4mm axial and <=2.1mm diameter; cut12mm envelope sleeve blank11.5+/-0.2 and center it over joint. Remove burrs/stray strands; no bare copper outside sleeve.','Heat outside PETG cradle and away from battery/servo until snug; manufacturer recovery121C, do not melt nearby printed supports. No flame.','Verify continuous sleeve coverage at least3mm onto sound insulation at each side and finished individual OD<=3.4, length<=12. Otherwise remake joint before installation.','Place three joints at the assigned rigid head centres. Separate end ties act on intact insulation, not solder/sleeve. No joints in260mm moving zone. Label GND/V+/PWM despite white sleeves.','Tail uses same three sleeve blanks, but its actual joint seat/placement remains the tail construction input, not approved by head packing.'],
      checks_not_physical='Dimensions/packing/source arithmetic only. Actual shrink, solder continuity, polarity, tug and thermal quality in phase2.',
      new_stls=0,new_SKUs=1,physical_pass=False,phase1_complete=False)
    dump('splice-insulation-interface.json',interface)
    s=read(P/'selection.json');q=read(P/'one-order-quantities.json')
    s['parent_selection_sha256']=sha(P/'selection.json')
    s['conditions'].append('R26 exact RNF-100-1/8-9-STK head splice insulation:11.5mm blanks, <=12mm finished sleeves at shifted centres within unchanged28mm/OD7 reservations. No newSTL or old collision rerun. Tail3 sleeves reserved only; complete central feeds/other harness/protection remain open.')
    q['lines'].append(dict(id='insulation:RNF-100-1/8-9-STK',name='TE RNF-100 white1/8 sleeve3.17->1.57mm',planning_quantity=6,unit='m',installed_sleeves=9,source=(OUT/'insulation-sources.json').relative_to(ROOT).as_posix(),note='Current TME minimum6m/five1.2m sticks;9installed+9trialspares consume<0.25m. Exact insulation for smallMG92B joints; retain P0 assortment for largerpower joints. Procurement refresh phase2, not ordered.'))
    q.update(selected_prints=(OUT/'selection.json').relative_to(ROOT).as_posix(),line_count=105)
    assert len(q['lines'])==105 and len(s['prints'])==66
    dump('selection.json',s);dump('one-order-quantities.json',q)
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle,Rectangle
    fig,axs=plt.subplots(1,2,figsize=(11,4.5));ax=axs[0]
    ax.add_patch(Circle((0,0),3.5,fill=False,ec='black'))
    for c,r in zip([[-half,0],[half,0],[0,third_y]],[half,half,small]):ax.add_patch(Circle(c,r,fc='#afbac9',ec='#444'))
    ax.set(xlim=(-4,4),ylim=(-4,4),aspect='equal',title='Największy przekrój:2 koszulki+1 żyła\nw istniejącym OD7',xlabel='mm',ylabel='mm')
    ax=axs[1]
    for lane,x in enumerate(centres['pitch_y']):ax.add_patch(Rectangle((x-6,lane-.25),12,.5,fc='#afbac9',ec='#444'));ax.plot([x-2,x+2],[lane,lane],color='#a65f31',lw=4)
    ax.axvline(95.5,ls='--',color='#444');ax.axvline(123.5,ls='--',color='#444');ax.set(xlabel='Y mm na sztywnym ramieniu pitch',ylim=(-.7,2.7),title='Dłuższa izolacja bez nowego wydruku\nCo najwyżej2 koszulki w jednym przekroju');ax.grid(alpha=.2)
    fig.suptitle('R26: izolacja9połączeń MG92B / nominalny projekt, bez physicalPASS');fig.tight_layout();fig.savefig(OUT/'preview.png',dpi=150);plt.close(fig)
    (OUT/'README.md').write_text('# R26: dokładna izolacja małych połączeń MG92B\n\nTE RNF-100-1/8-9-STK,9koszulek+9prób,zapas handlowy6m przy obecnym minimum TME. P0 zestaw zostaje dla większych przewodów. Blanki11,5±0,2mm, final<=12mm, kontakt<=4mm, zakład izolacji>=3mm/stronę. Nowe środki head: pitchY101,5/109,5/117,5; yawX-98/-90/-82. Całość pozostaje w tych samych28mm/OD7.0nowychSTL;66zadań/100PETG/4próbki/105pozycji. Nie zatwierdza rzeczywistego lutu ani pozycji trzech złączy ogona; centralne feedy i reszta fazy1 otwarte.\n',encoding='utf-8')
    finalize()
def finalize():
    pins=read(P/'manifest.json')['files_sha256'].copy()
    for p in OUT.iterdir():
        if p.is_file() and p.name not in ('manifest.json','validation-manifest.json'):pins[p.relative_to(ROOT).as_posix()]=sha(p)
    pins[Path(__file__).relative_to(ROOT).as_posix()]=sha(Path(__file__))
    assert all(sha(ROOT/p)==h for p,h in pins.items())
    dump('manifest.json',dict(files_sha256=pins,new_stls=0,selected_jobs=66,installed_petg_parts=100,samples=4,physical_pass=False,phase1_complete=False))
    dump('validation-manifest.json',dict(schema_version=1,readiness='prototype',files=[dict(path=p,sha256=h) for p,h in pins.items()],gates={k:dict(status='open',reason='Exact head sleeve recipe; whole construction/physical readiness still open') for k in ('geometry','assembly','fit','petg','loads','electrical','service')}))
    print(json.dumps(dict(pins=len(pins),new_stls=0,lines=105,all_hashes_verified=True)))
if __name__=='__main__':
    if '--finalize' in sys.argv:finalize()
    else:main()
