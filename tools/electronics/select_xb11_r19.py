"""Consolidate the supported XB11 interface without duplicating prior prints."""
import json, hashlib, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PARENT=ROOT/'hardware/manufacturing/one-batch-prototype-r18'
OUT=ROOT/'hardware/manufacturing/one-batch-prototype-r19'
CAD=ROOT/'hardware/cad/studies/xb11-hangers-r2'
ROUTE=ROOT/'hardware/electronics/full-cat/xb11-upstream-route-r3'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

def checks():
    import FreeCAD as A
    import Part, math
    sys.path.insert(0,str(ROOT/'tools/cad'))
    from check_main_p0_placement import SavedShapes
    reader=SavedShapes();hanger=reader.shape(CAD/'XB11Hanger.FCStd','Hanger')
    old=reader.shape(ROOT/'hardware/cad/studies/xb11-hangers-r1/XB11Hanger.FCStd','Hanger')
    def nut(x):
        v=[A.Vector(x+4/math.sqrt(3)*math.cos(i*math.pi/3),4/math.sqrt(3)*math.sin(i*math.pi/3),100.4) for i in range(6)]
        return Part.Face(Part.Wire(Part.makePolygon(v+[v[0]]).Edges)).extrude(A.Vector(0,0,1.6)).cut(Part.makeCylinder(1,1.6,A.Vector(x,0,100.4)))
    old_hit=sum(s.Volume for s in nut(15).common(old).Solids)
    assert old_hit>1e-5
    gap=nut(13).distToShape(hanger)[0] # Nut seats at Z102, so contact distance zero.
    assert sum(s.Volume for s in nut(13).common(hanger).Solids)<1e-5
    cover=reader.shape(ROOT/'hardware/cad/studies/upper-cover-mount-r1/RaisedUpperCoverMount.FCStd','CoverMountHole4')
    rows=[]
    for y in (50.5,-50.5):
        h=hanger.copy();h.translate(A.Vector(0,y,0))
        rows.append(dict(part='hanger',y=y,cover_positive_mm3=sum(s.Volume for s in h.common(cover).Solids)))
        for x in (5,13):
            head=Part.makeCylinder(1.9,2,A.Vector(x,y,109.3))
            rows.append(dict(part='screw_head',x=x,y=y,cover_positive_mm3=sum(s.Volume for s in head.common(cover).Solids)))
    assert all(r['cover_positive_mm3']<1e-5 for r in rows)
    write(CAD/'fastener-cover-checks.json',dict(old_x15_nut_web_hit_mm3=old_hit,
        r1_assembly_rejected=True,r2_x13_nut_nominal_contact_distance_mm=gap,
        changed_hardware_and_cover_only=rows,source_sha256=reader.hashes,
        r2_nut_to_web_x_bbox_gap_mm=16-(13+4/math.sqrt(3)),
        physical_pass=False,new_stls=0))

def main():
    g=read(CAD/'geometry.json');r=read(ROUTE/'checks.json');plan=read(CAD/'plan.json')
    assert not g['hits'] and g['relocated_recompute_ok'] and r['geometry_nominal_clear']
    checks()
    OUT.mkdir(exist_ok=True)
    s=read(PARENT/'selection.json');q=read(PARENT/'one-order-quantities.json')
    assert len(s['prints'])==65
    for p in s['prints']:
        if p['identity']=='electronics:DeckP10-cover-mount':
            p.update(stl=(CAD/'Deck_XB11_hangers_candidate_x1.stl').relative_to(ROOT).as_posix(),
                sha256=sha(CAD/'Deck_XB11_hangers_candidate_x1.stl'),
                recipe=(CAD/'plan.json').relative_to(ROOT).as_posix(),status='selected_prototype_with_XB11_hanger_holes')
    s['prints'].append(dict(identity='electronics:XB11-under-deck-hangers',module='fixed AUX6 XB11',
        stl=(CAD/'XB11_hanger_candidate_x2.stl').relative_to(ROOT).as_posix(),sha256=sha(CAD/'XB11_hanger_candidate_x2.stl'),
        quantity=2,purpose='installed_candidate',status='conditional_hobby_prototype',material='PETG',
        orientation=plan['print_orientation'],recipe=(CAD/'plan.json').relative_to(ROOT).as_posix(),
        print_size_mm_including_5mm_brim=[58,16,30.25]))
    s.update(jobs=66,installed_jobs=s['installed_jobs']+1,installed_petg_parts=100,
        parent_selection_sha256=sha(PARENT/'selection.json'),xb11_mount_geometry_sha256=sha(CAD/'geometry.json'),
        xb11_route_sha256=sha(ROUTE/'checks.json'),phase1_complete=False)
    s['conditions'].append('R19 supersedes R18 Deck only and adds2 identical XB11 hangers. Full OD2.5/R15 geometric route and fixed supports selected; actual ports, tie pressure/edge finish and source fault coordination need delivered checks. Old ShellMounted20 is not selected: replaced raised cover explicitly checked. R1 hanger x15 nut/web conflict rejected; R2 x13 selected.')
    quantities={'fastener:DIN912 socket screws, nominal sizes:M2x10':4,
                'fastener:DIN934 nuts:M2 DIN934 AF4':4,
                'fastener:washers:P0 M2 DIN125 OD5/ID2.2/t0.3':4}
    found=set()
    for line in q['lines']:
        if line['id'] in quantities:
            delta=quantities[line['id']];line['planning_quantity']+=delta
            line['note']=line.get('note','')+f' R19 adds {delta} installed for two XB11 under-deck hangers.'
            found.add(line['id'])
        if line['id']=='tie:111-02370':
            line['installed']+=2
            line['note']+=' R19 adds two wire-support ties, one per hanger, using existing bag100.'
    assert found==set(quantities)
    q.update(selected_prints='hardware/manufacturing/one-batch-prototype-r19/selection.json',phase1_complete=False)
    assert len(q['lines'])==104 and all(sha(ROOT/p['stl'])==p['sha256'] for p in s['prints'])
    write(OUT/'selection.json',s);write(OUT/'one-order-quantities.json',q)
    route_spec=dict(status='CONDITIONAL_FIXED_XB11_INTERFACE_SELECTED',from_endpoint='P_AUX.2',
        to_endpoint='XB11 WAGO221-412 cageA',rail='AUX6 before F_HY branch fuse',
        wire_sku='HELU23502 red1mm2 OD2.5',nominal_axis_length_mm=r['path_length_mm'],
        fixed_radius_mm=15,support_y_mm=[50.5,-50.5],route_plan=(ROUTE/'plan.json').relative_to(ROOT).as_posix(),
        mount_plan=(CAD/'plan.json').relative_to(ROOT).as_posix(),
        source_restraint='Insulated lead linked to existing P_AUX connector mounting tie; no pull on cage',
        sink_restraint='R17 interlinked restraint ahead of XB11 WAGO; factory F_HY input unchanged',
        cut_length='Cut after fitting; nominal route272.710 + service30mm at each disconnectable end +11mm strip per WAGO end =354.710mm planning minimum. Round working blank to0.40m, not a measured cut length.',
        procurement='Existing red1mm2 stock; retain25% overall procurement reserve. Do not add a new roll solely for this route.',
        edge_guards='On clear open passage, no body-wall feedthrough. Deburr printed rail contact faces and round edges before tying; do not route against screw/nut edges.',
        service='Battery disconnected; remove raised cover, release source/cage and cut two hanger ties; hangers remain bolted. Replace cut ties; no splice under belly.',
        exclusions='No servo-motion duty for this fixed wire; no signal ground carrying servo current; no MAIN/AUX output merge',
        provisional=['Exact WAGO cage centers and wire exit need delivered dry fit; preserved minimum radius',
                     'Whole selected harness interference and source/AUX fault coordination remain open'],
        physical_pass=False,new_stls=2)
    write(OUT/'xb11-interface.json',route_spec)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    fig,axs=plt.subplots(1,3,figsize=(14,5))
    samples=r['centerline_samples_mm']
    for ax,(i,j,title) in zip(axs,[(0,1,'XY complete route'),(1,2,'YZ support positions'),(0,2,'XZ hanger section')]):
        ax.plot([p[i] for p in samples],[p[j] for p in samples],color='#ba3128',lw=2,label='XB11 R15 / OD2.5')
        ax.set_title(title);ax.set_xlabel('XYZ'[i]+' mm');ax.set_ylabel('XYZ'[j]+' mm');ax.grid(alpha=.2);ax.set_aspect('equal')
    for y in (50.5,-50.5):
        axs[0].add_patch(Rectangle((-29,y-3),48,6,facecolor='#5795b7',alpha=.5))
        axs[1].add_patch(Rectangle((y-3,74.75),6,30.25,facecolor='#5795b7',alpha=.5))
    for b in ([-29,74.75,19,77.75],[16,77.75,19,105],[2,102,19,105]):
        axs[2].add_patch(Rectangle(b[:2],b[2]-b[0],b[3]-b[1],facecolor='#5795b7',alpha=.6))
    axs[2].set_ylim(72,115);axs[2].legend(fontsize=8)
    fig.suptitle('R19 XB11 fixed route + two identical bolt-on hangers (section/bbox preview; no physical PASS)')
    fig.tight_layout();fig.savefig(OUT/'preview.png',dpi=150);plt.close(fig)
    files=[Path(__file__).resolve(),ROOT/'tools/cad/xb11_hangers_r1.py',ROOT/'tools/electronics/xb11_selected_route_r3.py',
           ROOT/'tools/electronics/xb11_upstream_route.py']
    for folder in (OUT,CAD,ROUTE):
        files.extend(p for p in folder.iterdir() if p.is_file() and p.suffix not in ('.FCBak',) and p.name!='manifest.json')
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in files}
    pins.update(r['source_sha256']);pins.update(g['source_sha256'])
    pins.update(read(CAD/'fastener-cover-checks.json')['source_sha256'])
    pins[DECK_SOURCE]=sha(ROOT/DECK_SOURCE)
    for name in ('geometry.json','plan.json'):
        p=ROOT/'hardware/cad/studies/xb11-hangers-r1'/name
        pins[p.relative_to(ROOT).as_posix()]=sha(p)
    write(OUT/'manifest.json',dict(status='PHASE1_INCOMPLETE_R19_SUPPORTED_XB11',files_sha256=pins,
        new_stls=2,selected_jobs=66,installed_petg_parts=100,physical_pass=False,
        next='XA02-XA06 fixed AUX routes, source protection, then complete moving head harness; no old route matrix repeat'))
    assert all(sha(ROOT/n)==h for n,h in pins.items())
    print(json.dumps(dict(jobs=66,parts=100,ledger_lines=104,files=len(pins),new_selected_petg=2)))

DECK_SOURCE='hardware/cad/studies/deck-aux-wago-r5/DeckAuxWagoR5.FCStd'
if __name__=='__main__':main()
