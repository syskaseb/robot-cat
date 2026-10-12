"""Bind all twelve five-port leg stations to their CURRENT world solids.

Old endpoint registers predate several D/G placements. Reusing them would
route through an empty historical pose. Port pitch/top exit are explicitly
provisional project datums, not a claim about supplier cavity measurements.
"""
import json
import time
import zipfile
from pathlib import Path
import FreeCAD
import Part
from plan_current_main_sources import ROOT,BASE,OUT,SHA


def build():
    tick=time.monotonic();archive=BASE/'current-view-60-20261012.zip';ef=OUT/'harness-interfaces-plan.json'
    gf=OUT/'ground-tree-plan.json';ground=json.loads(gf.read_text())
    old=json.loads(ef.read_text());old_ports={e['role']:e for r in old['body_conductors'] for e in r['current_ends']}
    names=[n for leg in ('FL','FR','RL','RR') for n in ('D_'+leg,leg+'_G',leg+'_P')]
    ports={};stations=[];changes=[]
    with zipfile.ZipFile(archive) as z:
        entries={r['label']:r for r in json.loads(z.read('index.json'))['entries']}
        for name in names:
            shape=Part.Shape();shape.importBrepFromString(z.read(entries[name]['file']).decode())
            assert shape.isValid() and shape.Solids,name
            b=shape.BoundBox;x=(b.XMin+b.XMax)/2;y=(b.YMin+b.YMax)/2
            assert abs(b.XLength-30)<1e-6 and abs(b.YLength-9)<1e-6 and abs(b.ZLength-19)<1e-6,(name,'Changed nominal casing')
            stations.append(dict(name=name,bounds_world_mm=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax],
                world_geometry_placement_applied_twice=False,port_basis='Project five-port pitch4.75mm centred on actual case, exit at current top; delivered cavity fit gate'))
            for i in range(1,6):
                role=name+'.'+str(i);cavity=i
                if name in ground['rear_gallery'] and name.endswith('_G'):
                    cavity=ground['rear_ground_same_rail_mapping'][str(i)]
                elif name=='FR_G':cavity=ground['FR_ground_same_rail_mapping'][str(i)]
                point=[x+(cavity-3)*4.75,y,b.ZMax]
                ports[role]=dict(role=role,physical_project_cavity=cavity,point_mm=point,departure=[0,0,1],datum_is_project_provisional=True)
                if role in old_ports:
                    delta=[a-b for a,b in zip(point,old_ports[role]['point_mm'])]
                    if max(map(abs,delta))>1e-6:changes.append(dict(role=role,previous_mm=old_ports[role]['point_mm'],current_mm=point,delta_mm=delta))
    report=dict(status='CURRENT_LEG_RECEIVER_PROJECT_DATUMS_DELIVERY_FIT_OPEN',ports=ports,stations=stations,
        changed_occupied_datums=changes,selected=False,native_changed=False,W5_complete=False,physical_pass=False,
        scope='Only current12station/60port coordinates; no conductor reroute, lever qualification, support or W5 credit.',
        worker_seconds=round(time.monotonic()-tick,3),source_sha256={p.relative_to(ROOT).as_posix():SHA(p) for p in (archive,ef,gf,Path(__file__))})
    (OUT/'current-leg-receiver-datums.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=report['status'],stations=len(stations),ports=len(ports),changed_occupied=len(changes),worker_seconds=report['worker_seconds'])),flush=True)


if __name__=='__main__':build()
