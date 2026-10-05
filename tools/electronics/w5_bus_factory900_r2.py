"""Whole BUS flight at147.5, above the received three material witnesses.

F_AUX ends at142mm, P_REAR at135mm and RR source at138.449mm.
The14mm rise is made before the west turn, not by moving registered ports.
"""
import json
import math
from pathlib import Path
import w5_bus_factory900 as B
from w5_s1_source_layout_r2 import CentreLine
from w5_parallel_connection import connect

OUT=B.scope.ROOT/'hardware/electronics/full-cat/w5-bus-factory900-r2'


def recipe(family,source):
    start=family['ends']['W003']['edges'][0]['start']
    c=CentreLine(start,[1,0,0]);c.line([start[0]+6,start[1],start[2]])
    c.arc([0,0,1],radius=10)
    c.line([c.p[0],c.p[1],c.p[2]+14])
    c.arc([-1,0,0],radius=10)
    before=[source[0]+10,source[1],c.p[2]]
    c.edges.extend(connect(c.p,before,[-1,0,0],10));c.p=before;c.t=[-1,0,0]
    c.arc([0,0,-1],radius=10);c.line(source)
    body=sum(e['length_mm'] for e in c.edges)
    return dict(wire='W003',edges=c.edges,OD_mm=2,radius_mm=10,
        body_mm=body,nominal_mm=body+41,trial_blank_mm=math.ceil((body+71)/10)*10,
        manufacturer_nominal_length_mm=900,manufacturer_sku='34172',
        factory_plug_and_wire_OD_provisional=True,delivered_usable_length_mm=None,
        remaining_nominal900_mm=900-math.ceil((body+71)/10)*10,
        source_end_straight_mm=c.edges[-1]['length_mm'],start=start,source=source)


def main():
    B.OUT=OUT;B.recipe=recipe;B.main()
    p=OUT/'checks.json';proof=json.loads(p.read_text(encoding='utf-8'))
    proof['source_sha256'][Path(__file__).relative_to(B.scope.ROOT).as_posix()]=B.sha(Path(__file__))
    proof['changed_interface']='BUS whole west flight147.5mm; registered ports unchanged'
    B.save(p,proof)


if __name__=='__main__':main()
