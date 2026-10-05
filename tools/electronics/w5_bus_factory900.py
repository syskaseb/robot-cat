"""Complete BUS ground above cooling, using the catalog900mm whole cable.

Preserve the BUS plug and D lead route, remove V as before. One900mm cable
replaces the300mm cable for BOTH D/G, with trimming only after dry-fit.
The separate SKU fact sheet is the length source; no photo-sized plug or
measured usable length is claimed. No inline solder joint is introduced.
"""
from pathlib import Path
from datetime import datetime,timezone
import json
import math
import w5_received_central_scope as received
import w5_central_shared_routes as scope
from w5_s1_source_layout_r2 import CentreLine
from w5_parallel_connection import connect
from w5_bus_low_s_material import build
from servo_fuse_inputs_r1 import save,sha

OUT=scope.ROOT/'hardware/electronics/full-cat/w5-bus-factory900-r1'
FRONT=scope.ROOT/'hardware/electronics/full-cat/w5-front-paired-flights-r2/checks.json'
MAIN=scope.ROOT/'hardware/electronics/full-cat/w5-main-ground-low-return-r3/checks.json'
BUS=scope.ROOT/'hardware/electronics/full-cat/w5-bus-pair-r52-r4/intent.json'
FACTS=scope.ROOT/'hardware/reference/leg-cable-2026-10-04/facts.json'


def recipe(family,source):
    start=family['ends']['W003']['edges'][0]['start']
    c=CentreLine(start,[1,0,0]);c.line([start[0]+6,start[1],start[2]])
    c.arc([0,0,1],radius=10);c.arc([-1,0,0],radius=10)
    before_descent=[source[0]+10,source[1],c.p[2]]
    c.edges.extend(connect(c.p,before_descent,[-1,0,0],10));c.p=before_descent;c.t=[-1,0,0]
    c.arc([0,0,-1],radius=10);c.line(source)
    assert math.dist(c.p,source)<1e-7 and math.dist(c.t,[0,0,-1])<1e-7
    body=sum(e['length_mm'] for e in c.edges)
    return dict(wire='W003',edges=c.edges,OD_mm=2,radius_mm=10,
        body_mm=body,nominal_mm=body+41,trial_blank_mm=math.ceil((body+41+30)/10)*10,
        manufacturer_nominal_length_mm=900,manufacturer_sku='34172',
        factory_plug_and_wire_OD_provisional=True,delivered_usable_length_mm=None,
        remaining_nominal900_mm=900-math.ceil((body+41+30)/10)*10,
        source_end_straight_mm=c.edges[-1]['length_mm'],
        start=start,source=source)


def main():
    import FreeCAD as A,Part
    start=datetime.now(timezone.utc)
    assert not (OUT/'checks.json').exists()
    OUT.mkdir(parents=True,exist_ok=True)
    facts=json.loads(FACTS.read_text(encoding='utf-8'))
    assert facts['manufacturer_sku']=='34172' and facts['manufacturer_nominal_length_mm']==900
    fixed,printed,ends,family,rows,pins,reused,replaced=received.load(A,Part)
    for proof_path,wires in ((FRONT,('W025','W036')),(MAIN,('W060',))):
        proof=json.loads(proof_path.read_text(encoding='utf-8'));assert proof['complete'],str(proof_path)
        for rel,digest in proof['files'].items():
            assert sha(scope.ROOT/rel)==digest
            pins.append(scope.ROOT/rel)
        for wire in wires:
            fixed[wire]=Part.read(str(proof_path.parent/(wire+'_WORLD.brep')))
            ends.pop(wire,None)
        pins.append(proof_path)
    source=json.loads(BUS.read_text(encoding='utf-8'))['source_lead_datums']['W003']
    row=recipe(family,source);assert row['trial_blank_mm']<=900
    path,shape=build(A,Part,row)
    hits=scope.contacts(shape,{**fixed,**{w:s for w,s in ends.items() if w!='W003'}},Part)
    files=[]
    for suffix,s in (('WORLD',shape),('CENTERLINE',path)):
        p=OUT/('W003_'+suffix+'.brep');s.exportBrep(str(p));files.append(p)
    finish=datetime.now(timezone.utc)
    pins += [BUS,FACTS,Path(__file__),Path(scope.__file__),Path(received.__file__),
        scope.ROOT/'tools/electronics/w5_bus_low_s_material.py',scope.ROOT/'tools/electronics/w5_parallel_connection.py',
        scope.ROOT/'tools/electronics/w5_s1_source_layout_r1.py',scope.ROOT/'tools/electronics/w5_s1_source_layout_r2.py',
        scope.ROOT/'tools/electronics/w5_exact_separation.py']
    save(OUT/'checks.json',dict(status='WHOLE_BUS_900_CABLE_CANDIDATE',recipe=row,hits=hits,errors=[],complete=not hits,
        same_factory_cable_for_W002_W003=True,W002_route_preserved=True,W002_retrim_after_fit=True,V_contact_removed=True,
        stock_change=dict(factory900_cables_total=13,factory900_six_packs=3,
            factory900_spares=5,factory300_BUS_six_packs_superseded=1,purchase_performed=False,selected=False),
        printed_pending=sorted(printed),replacement_obligations=replaced,native_complete=False,selected=False,physical_pass=False,
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds(),
        source_sha256={p.relative_to(scope.ROOT).as_posix():sha(p) for p in dict.fromkeys(pins)},
        files={p.relative_to(scope.ROOT).as_posix():sha(p) for p in files}))
    print('BUS_FACTORY900_DONE',len(hits),round(path.Length,3),row['trial_blank_mm'],flush=True)


if __name__=='__main__':main()
