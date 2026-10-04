"""One complete D/G pigtail candidate; one factory cable, never a V branch.

Use the official H3 CAD envelope and selected W061 cage-label remapping.
Cable OD, plug projection and R10 are prototype assumptions, not Waveshare
dimensions. No physical continuity, purchase or full-W5 completion inferred.
"""
from datetime import datetime, timezone
from pathlib import Path
import json
import math
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools/electronics'))
sys.path.insert(0, str(ROOT/'tools/cad'))
from servo_fuse_inputs_r1 import save, sha
OUT = ROOT/'hardware/electronics/full-cat/w5-bus-pair-r52-r1'


def main():
    import FreeCAD as A
    import Part
    import body_ground_routes_r1 as curves
    from xb11_upstream_route import rounded
    from w5_selected_owners_r52 import cached
    start = datetime.now(timezone.utc)
    OUT.mkdir(parents=True, exist_ok=True)
    assert not (OUT/'checks.json').exists()
    catalog = ROOT/'hardware/electronics/full-cat/pi-bus-primary-r1/catalog.json'
    mounting = ROOT/'hardware/electronics/full-cat/pi-bus-mount-r3/plan.json'
    mapping = ROOT/'hardware/electronics/full-cat/body-ground-bridge-finish-r5/interface.json'
    graph = ROOT/'hardware/electronics/power-platform/wiring-p0.json'
    h3 = next(r for r in json.loads(catalog.read_text(encoding='utf-8'))['parts'] if r['name']=='H3')
    translation = json.loads(mounting.read_text(encoding='utf-8'))['board_world_translation']
    center = [(h3['bounds'][i]+h3['bounds'][i+3])/2+translation[i] for i in range(3)]
    top = h3['bounds'][5]+translation[2]
    g = json.loads(mapping.read_text(encoding='utf-8'))
    assert g['cage_labels']['G2']==['.2','.3','.1','.4','.5']
    assert g['specs']['W061'][4] == [111,9.5,113.5]
    wires = {r['id']:r for r in json.loads(graph.read_text(encoding='utf-8'))['wires']}
    assert (wires['W002']['a'],wires['W002']['b'])==('BUS.D','D_FL.1')
    assert (wires['W003']['a'],wires['W003']['b'])==('BUS.G','G2.4')
    # Project lead exits over the shared plug, not claimed PCB pin cavities.
    sources={'W002':[center[0]-1,center[1],top+8],
             'W003':[center[0]+1,center[1],top+8]}
    ends={'W002':[-10.5,30.5,113.5], 'W003':[117,9.5,113.5]}
    intent=dict(status='SAVED_BEFORE_TWO_COMPLETE_BUS_ROUTES',parent='one-batch-prototype-r52',
        cable='ONE Waveshare34171 300mm cable from ONE six-pack',
        schematic_roles={'H3.1':'D','H3.2':'V_REMOVE','H3.3':'G'},
        not_physical_left_right_cavity_assignment=True,source_lead_datums=sources,
        destination_datums=ends,prototype_assumptions=dict(OD_mm=2,static_R_mm=10,
            plug_height_above_official_header_mm=8,each_lead_exit_offset_from_center_mm=1),
        supplier_copper_mm2=None,supplier_OD_mm=None,supplier_plug_dimensions=None,
        strip_mm=11,strip_confirm_delivered_marking=True,one_untinned_wire_per_port=True,
        shared_stock_units=1,spare_factory_cables_from_pack=5,
        endpoint_and_middle_restraints_complete=False,selected=False,physical_pass=False,W5_complete=False,
        assembly=['Remove V contact/lead with all sources disconnected; identify D/G by schematic and continuity, not colour.',
            'Keep the adapter-end factory plug; do not cut the cable in half.',
            'Fit both complete paths and grips before trimming the far end; confirm copper fits221-415 .14..4mm2.',
            'For BUS removal, release the cable grips and unplug H3 before removing the retained BUS bracket.'])
    save(OUT/'intent.json',intent)
    curves.R=10; curves.STRAIGHT=2
    owners, cache=cached()
    g1proof=ROOT/'hardware/electronics/full-cat/w5-g1-saved-export-r1/checks.json'
    deck=ROOT/'hardware/cad/studies/w5-g1-passage-native-r2/Deck_WORLD.brep'
    assert sha(deck)==json.loads(g1proof.read_text(encoding='utf-8'))['files'][deck.relative_to(ROOT).as_posix()]
    owners['CandidateDeck']=Part.read(str(deck))
    rows=[]; allpieces={}; hits=[]; errors=[]; pairs=0
    for wire in ('W002','W003'):
        src=A.Vector(*sources[wire]); dst=ends[wire]; direction=-1 if wire=='W002' else 1
        up,end=curves.elevated_start(dst,direction,2*dst[2]-95.5)
        def mirror(v): return A.Vector(v.x,v.y,2*dst[2]-v.z)
        down=[]
        for e in up:
            p,q=mirror(e.valueAt(e.FirstParameter)),mirror(e.valueAt(e.LastParameter))
            down.append(Part.Arc(p,mirror(e.valueAt((e.FirstParameter+e.LastParameter)/2)),q).toShape()
                        if hasattr(e.Curve,'Radius') else Part.makeLine(p,q))
        end=mirror(end)
        lane=-12 if wire=='W002' else 55
        route=rounded([src,A.Vector(src.x,src.y,95.5),A.Vector(src.x,lane,95.5),
                       A.Vector(end.x,lane,95.5),end],10)
        reverse=[]
        for e in reversed(down):
            p,q=e.valueAt(e.LastParameter),e.valueAt(e.FirstParameter)
            reverse.append(Part.Arc(p,e.valueAt((e.FirstParameter+e.LastParameter)/2),q).toShape()
                           if hasattr(e.Curve,'Radius') else Part.makeLine(p,q))
        route=Part.Wire(route.Edges+reverse)
        assert route.isValid()
        for a,b in zip(route.Edges,route.Edges[1:]):
            assert (a.valueAt(a.LastParameter)-b.valueAt(b.FirstParameter)).Length<1e-7
            assert (a.tangentAt(a.LastParameter)-b.tangentAt(b.FirstParameter)).Length<1e-7
        assert min(e.Curve.Radius for e in route.Edges if hasattr(e.Curve,'Radius'))>=10-1e-7
        pieces=[Part.Wire([e]).makePipeShell([Part.Wire([Part.makeCircle(1,e.valueAt(e.FirstParameter),e.tangentAt(e.FirstParameter))])],True,False)
                for e in route.Edges]
        assert all(s.isValid() and len(s.Solids)==1 for s in pieces)
        Part.makeCompound(pieces).exportBrep(str(OUT/(wire+'_DESIGN.brep')))
        route.exportBrep(str(OUT/(wire+'_CENTERLINE.brep')))
        allpieces[wire]=pieces
        for i,s in enumerate(pieces):
            for key,owner in owners.items():
                if not s.BoundBox.intersect(owner.BoundBox): continue
                for j,solid in enumerate(owner.Solids):
                    if not s.BoundBox.intersect(solid.BoundBox):continue
                    pairs+=1
                    try:
                        witness=s.common(solid)
                        if witness.Volume>1e-5:
                            hits.append(dict(wire=wire,segment=i,owner=key,solid=j,mm3=witness.Volume,
                                bounds_mm=[getattr(witness.BoundBox,n) for n in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]))
                    except Exception as exc: errors.append(dict(wire=wire,segment=i,owner=key,error=str(exc)))
            print(wire,'segment',i,'contacts',len(hits),flush=True)
        rows.append(dict(wire=wire,centerline_mm=route.Length,
                         nominal_trim_bound_mm=math.ceil((route.Length+30)/10)*10,
                         reserve30mm_is_design_allowance_not_supplier_plug_length=True))
    mutual=[]
    for i,a in enumerate(allpieces['W002']):
        for j,b in enumerate(allpieces['W003']):
            if a.BoundBox.intersect(b.BoundBox):
                v=a.common(b).Volume
                if v>1e-5:mutual.append(dict(D_segment=i,G_segment=j,mm3=v))
    end=datetime.now(timezone.utc)
    paths=[catalog,mounting,mapping,graph,deck,g1proof,Path(__file__),
        ROOT/'tools/electronics/body_ground_routes_r1.py',ROOT/'tools/electronics/xb11_upstream_route.py',
        ROOT/'hardware/electronics/full-cat/w5-installed-r52/owners.json',
        ROOT/'hardware/electronics/full-cat/w5-installed-r52/installed.brep',
        ROOT/'hardware/electronics/power-platform/ADAPTER-PIGTAIL-P0.md']
    save(OUT/'checks.json',dict(status='BUS_PAIR_FULL_CANDIDATE_CLEAR_GRIPS_PENDING' if not hits and not errors and not mutual else 'BUS_PAIR_FULL_CANDIDATE_CONFLICTS',
        hits=hits,errors=errors,mutual_contacts=mutual,pairs=pairs,lengths=rows,
        within_one_factory300mm_cable=all(r['nominal_trim_bound_mm']<=300 for r in rows),
        one_cable_not_two=True,V_in_installed_harness=False,selected=False,
        restraints_complete=False,W5_complete=False,physical_pass=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in paths},
        files={p.relative_to(ROOT).as_posix():sha(p) for p in OUT.glob('*.brep')},
        started_utc=start.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-start).total_seconds()))
    print('BUS_PAIR_RESULT',json.dumps(dict(contacts=len(hits),mutual=len(mutual),lengths=rows)),flush=True)


if __name__=='__main__':main()
