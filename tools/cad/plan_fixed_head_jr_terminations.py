"""Three real fixed JR pigtail/HELU joins, supports and stock before native.

No new electrical connector, no solder in a moving bend. All splice geometry
is on already planned straight fixed lanes, not an extra accounting joint.
Dimensions/OD/polarity remain explicit delivery-fit assumptions.
"""
import json,time,math
from pathlib import Path
import FreeCAD as A
import Part
import plan_fixed_head_feed_interface as I
H,S,C,Q=I.H,I.S,I.C,I.Q
V=A.Vector

def allocation(feeds):
    pads={};bands={};sleeves={};rows=[]
    for n,y,z,x,sx in [('XB23',68,51,-247,-216),('XB22',78,48,-227,-169),('XS23',88,45,-237,-187)]:
        es=feeds[n];cursor=0;station=None
        for i,e in enumerate(es):
            a=e.valueAt(e.FirstParameter);b=e.valueAt(e.LastParameter)
            if isinstance(e.Curve,Part.Line) and abs(a.x-x)<1e-6 and abs(b.x-x)<1e-6 and a.y>=55 and b.y<=15:
                assert abs(a.z-z)<1e-6 and abs(b.z-z)<1e-6 and a.y>b.y
                station=dict(edge=i,HELU_guide_to_lap_end_mm=cursor+a.y-31,
                    JR_guide_to_lap_end_mm=sum(f.Length for f in es[i+1:])+39-b.y,
                    splice_bounds_mm=[x-2.4,25,z-2.4,x+2.4,45,z+2.4])
                assert station['JR_guide_to_lap_end_mm']+20<300,'JR300 cannot reach intact trim reserve'
                assert abs(station['HELU_guide_to_lap_end_mm']+station['JR_guide_to_lap_end_mm']-sum(f.Length for f in es)-8)<1e-6
            cursor+=e.Length
        assert station is not None,('No full straight fixed splice corridor',n)
        pads[n+'SpliceRoot']=[-251,15,37,x+4,55,40]
        pads[n+'SpliceBed']=[x-4,15,40,x+4,55,z-2.4]
        for side,lo,hi,yy in [('JR',15,24,19.5),('HELU',46,55,50.5)]:
            pads[n+side+'Land']=[x-2,lo,z-2.4,x+2,hi,z-1.05]
            # The retained spine ends atZ40. Route the band's underside on
            # TOP of it, through only the NEW bed, not through that load path.
            bands[n+side+'Band']=I.strap(x,yy,41.2,z+1.25,1.25,head_side=-1 if side=='JR' else 1)
        sleeves[n]=Part.makeCylinder(2.4,20,V(x,25,z),V(0,1,0))
        rows.append(dict(wire=n,**station,project_lap_mm=8,raw_RNF100_3_16_9_mm=20,
            sleeve_nominal_finished_OD_max_mm=4.8,finished_length_fit_mm=[14,20],
            independent_intact_lands_Y_mm=[[15,24],[46,55]],
            HELU_nominal_trim_after_fit_mm=5*math.ceil((station['HELU_guide_to_lap_end_mm']+30)/5),
            JR_nominal_trim_after_fit_mm=5*math.ceil((station['JR_guide_to_lap_end_mm']+20)/5)))
    return pads,bands,sleeves,rows

def run():
    tick=time.monotonic();nf=H.OUT/'fixed-head-interface-native.json';native=H.read(nf)
    assert native['editable_parts']==2 and native['exact_material_matches_shared_gate']
    for n,h in native['source_sha256'].items():assert S.SHA(H.ROOT/n)==h,n
    p,feeds,roots,meta,fork,reader,alloc,archive=I.prepare()
    pads,bands,sleeves,rows=allocation(feeds)
    host=reader.shape(H.ROOT/native['model'],'FixedYawCarrier')
    support=S.fuse([host]+[H.T.box(row) for row in pads.values()])
    for band in bands.values():support=support.cut(band)
    support=support.removeSplitter()
    assert support.isValid() and len(support.Solids)==1
    assert host.cut(support).Volume<1e-5,'New retention must not remove inherited host material'
    additions=support.cut(host)
    assert additions.isValid() and additions.Volume>0
    report=dict(status='FIXED_JR_JOINS_SHARED_PLAN_MATERIAL_NATIVE_OPEN',selected=False,physical_pass=False,
        pads=pads,stock_rows=rows,new_bands=6,new_JR=0,existing_pitch_JR300_reused=1,
        sleeve_blanks_mm=[20]*3,new_solder_joins=3,new_electrical_connectors=0,
        source_pigtails='Keep original keyed pitch factory plug and one existingJR300 mating plug. Cut far extension end only after fit; separate three insulated leads into these fixed lanes. Never infer cavities from colors.',
        replaces='Three former moving pitch HELU/local splice roles; yaw3local joins and yaw/body routes unchanged. Not3extra joins added to old pitch joins.',
        uncertainty=['JR individual insulation OD<=2.1 and separability, cut length and cavity orientation after delivery',
            'Sleeve recoveredOD<=4.8, lap8mm coverage>=3mm intact each side, solder/insulation and tensile qualification phase2',
            'No factory cable ampacity or fuse coordination is claimed; E3 remainsOPEN'],
        assembly=['No sources. Dry-fit actualJR and full uncut250factory before trimming anything.',
            'Thread all replacement bands through native passages before seating the wires. Open head front/retainers per inherited bench sequence; do not force a plug through the flat exit slot.',
            'Prepare three individually labelled8mm laps with individual20mm sleeve blanks off PETG. Heat and solder on a supported bench, not in this cradle.',
            'Seat cooled sleeves on their lowered beds atY25..45; fix intact9mm lands atY15..24 and46..55. No tie over solder or heatshrink taper.',
            'Retain yaw interface and remaining complete head-source preparation. Final lengths, polarity, insulation/pull/continuous motion gates before energizing.'],
        service=['Routine headATO uses retained qualified access, no wholehead removal.',
            'Rare complete head removal is staged bench repair: sources removed, free dedicated wire/holder restraints, releaseG_AUX3 on supported loose case and desolder knownPCB B2/factoryHELU joint off PETG if necessary.',
            'Only with the complete fixed loom released, support head and reverse inherited neck/head fastener sequence. No taut connected lift or in-placeJR withdrawal sweep is claimed.',
            'Separate factory/JR on the supported bench; disposable straps replaced. No74routine WAGO disconnects.'],
        source_sha256={**native['source_sha256'],nf.relative_to(H.ROOT).as_posix():S.SHA(nf),
            (H.ROOT/native['model']).relative_to(H.ROOT).as_posix():S.SHA(H.ROOT/native['model']),
            Path(__file__).relative_to(H.ROOT).as_posix():S.SHA(Path(__file__))},
        worker_seconds=round(time.monotonic()-tick,3))
    H.save('fixed-head-jr-terminations-plan.json',report)
    additions.exportBrep(str(H.OUT/'FixedJRJoinAdditions.brep'))
    print(json.dumps(dict(status=report['status'],stock_rows=rows,worker_seconds=report['worker_seconds'])),flush=True)

if __name__=='__main__':run()
