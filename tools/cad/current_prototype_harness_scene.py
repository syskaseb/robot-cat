"""Current planning overlay: native MAIN and BUS must not disappear.

This does not select unfinished W5 modules. The previous context deliberately
remains immutable because older scoped receipts pin it. Historical DataShelf
and MTA mounts are NOT added at obsolete poses merely because a file exists.
"""
import json
from pathlib import Path
from current_complete_harness_context import context as previous, W, Part
from plan_current_main_sources import ROOT, BASE, OUT, SHA
from plan_current_tail_complete import tie_z


def wire(parts):
    edges=[]
    for q in parts:
        if q['kind']=='bezier':
            c=Part.BezierCurve();c.setPoles([W.A.Vector(*v) for v in q['poles_mm']])
            edges.append(c.toShape())
        else:edges.extend(W.makewire([q]).Edges)
    result=Part.Wire(edges)
    assert result.isValid()
    return result


def context():
    reader,pins,targets,old=previous();pins.add(Path(__file__))
    head=BASE/'head-mount-checkpoint/HeadNeckCurrent.FCStd'
    main=reader.shape(head,'CurrentMainSupplierReference')
    assert main.isValid() and len(main.Solids)==3
    assert abs(main.BoundBox.ZMin-46.52)<1e-6,'No second placement/SHIFT'
    targets['MAIN/CurrentMainSupplierReference']=main
    receipt=OUT/'BUS-native-checks.json';g=json.loads(receipt.read_text())
    assert g['status']=='BUS_NATIVE_CARRIER_PREPARED_W5_OPEN'
    model=ROOT/g['model'];assert SHA(model)==g['model_sha256']
    for n,h in g['source_sha256'].items():assert SHA(ROOT/n)==h,n
    bus=reader.shape(model,'UpperCarrier001')
    assert bus.isValid() and len(bus.Solids)==1
    targets['UpperCarrier001']=bus
    plan=OUT/'BUS-routes-plan.json';p=json.loads(plan.read_text())
    for n,h in p['source_sha256'].items():assert SHA(ROOT/n)==h,n
    for n,r in p['routes'].items():old[n]=(wire(r['parts']),r['radius_mm'])
    cols=[q[2]['start'] for q in p['source_prefixes'].values()]
    x=sum(c[0] for c in cols)/2;z=cols[0][2]+4.5
    targets['BUSBand'],targets['BUSHead']=tie_z(z,x-5.8,x+2.3,
        min(c[1] for c in cols)-2.2,max(c[1] for c in cols)+2.2)
    pins.update((head,receipt,model,plan))
    return reader,pins,targets,old
