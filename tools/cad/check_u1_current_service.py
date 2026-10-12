"""Changed-only U1 withdrawal after removing the entire disconnected BUS cable.

Reuse the pinned previous372-pair gate for unchanged material/wires. Its ONLY
contacts are W003, which is explicitly disconnected at BOTH ends and removed
before service. This does not prove lever reach or the preceding BUS removal.
New grips/current thirteen conductors are checked against continuous sweeps.
"""
import json,time
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import SavedShapes,prop
from check_u1_socket_service import sweep,box
import plan_u1_power_grips as P
import plan_u1_grouped_grips as G
import plan_u1_board_grips as B
ROOT,OUT,BASE,SHA=P.ROOT,P.OUT,P.BASE,P.SHA


def prior_gate(g):
    assert g['pairs']==372 and not g['errors']
    hits=g['contacts']+g['reservation_resolutions']
    assert hits and all(h['b']=='W003' for h in hits)
    for n,h in g['source_sha256'].items():assert SHA(ROOT/n)==h,n


def group_names(reader,model,group):
    return [n.get('value') for n in prop(reader.doc(model)[group],'Group').findall('.//Link')]


def run():
    tick=time.monotonic();reader=SavedShapes();pins={Path(__file__)}
    oldfile=OUT/'u1-socket-service-checks.json';old=json.loads(oldfile.read_text());prior_gate(old);pins.add(oldfile)
    receipts={}
    for tag in ('interface-carriers','grouped-grips','board-grips','power-grips','socket-population','socket-retainer'):
        f=OUT/('u1-'+tag+'-native.json');r=json.loads(f.read_text());m=ROOT/r['native']
        assert SHA(m)==r['native_sha256'],m;receipts[tag]=(r,m);pins.update((f,m))
    pop=receipts['socket-population'][1];ret=receipts['socket-retainer'][1]
    moving={'Adapter1208PCB':reader.shape(pop,'Adapter1208PCB')};reserves={}
    for n in group_names(reader,pop,'FixedPurchasedReferences'):
        if n.startswith('Male'):moving[n]=reader.shape(pop,n)
    for n in group_names(reader,pop,'TopFaceReferences'):
        s=reader.shape(pop,n)
        if n.startswith(('C1_','C2_')):
            b=s.BoundBox;reserves[n]=box([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax+12])
        else:moving[n]=s
    changed={}
    # Old carrier/anchor material remains covered by the pinned original gate.
    # Removing material cannot newly obstruct withdrawal; check only additions.
    oldlower=BASE/'mounting-checkpoint/CurrentBoardMounts.FCStd'
    oldupper=OUT/'SocketCarrierCurrent.FCStd'
    for name,tag,base in [('UpperCarrier001','interface-carriers',oldupper),
                          ('LowerCarrier001','power-grips',oldlower),
                          ('E2Fixture','power-grips',BASE/'aux-wiring-checkpoint/AUXPowerCurrent.FCStd'),
                          ('AnchorLeft','board-grips',ret),('AnchorRight','board-grips',ret)]:
        new=reader.shape(receipts[tag][1],name);original=reader.shape(base,name);pins.add(base)
        delta=new.cut(original).removeSplitter()
        if name=='UpperCarrier001':assert delta.Volume<1e-5,'Carrier unexpectedly adds material'
        elif delta.Volume>1e-5:changed[name+'/added']=delta
    for name,tag in [('GPIOGrip','grouped-grips'),('PCAGrip','grouped-grips'),('MAINGrip','power-grips')]:
        changed[name]=reader.shape(receipts[tag][1],name)
    for tag,allocation in [('Grouped',G.allocation()),('Board',B.allocation()),('Power',P.allocation())]:
        changed.update({tag+'/'+n:s for n,s in allocation['bands'].items()})
    # Updated hardware at affected bolt stacks is NOT inherited at old Z.
    r,m=receipts['grouped-grips']
    mount=BASE/'mounting-checkpoint/CurrentBoardMounts.FCStd';pins.add(mount)
    for v in r['changed_existing_hardware']:
        s=reader.shape(mount,v['name']);s.translate(A.Vector(*v['translation_mm']))
        changed[v['name']]=s
    changed.update(P.main_hardware())
    f=OUT/'u1-common-wiring-plan.json';plan=json.loads(f.read_text());pins.add(f)
    curves={n:(P.wire(v['parts']),v.get('radius',v.get('radius_mm')))
            for n,v in {**plan['complete_routes'],**plan['changed_MAIN_pair']}.items()}
    curves.update({n+'/bare':(P.wire(v['parts']),v['radius']) for n,v in plan['bare'].items()})
    result=dict(status='PENDING',pairs=0,contacts=[],reservation_resolutions=[],errors=[],
        selected=False,physical_pass=False,reused_prior_pairs=old['pairs'],service_lift_mm=12,
        prerequisite='All sources absent. Disconnect H5 keyed BUS plug and W002 atD_FL.1/W003 atG2.4, release its own bindings and remove ENTIRE cable to insulated bench before U1 service.',
        sequence=['Support disconnected BUS cable, remove it completely; no connected parking assumed',
                  'Cut only two U1 module-retainer ties; leave ALL external wire grips installed',
                  'Lift retainer bar/foam12mm, then populated1208/maleheaders12mm; fixed100pad ends stay',
                  'Reinstall module/bar/new module ties, reconnect BUS by documented pinout with power still absent'],
        not_covered=['Access to the two WAGO levers/H5 and continuous BUS removal before this gate',
                     'Socket extraction force, hand grip, fit after delivery; no live-service approval'])
    def check(n,s,reservation=False):
        output=result['reservation_resolutions'] if reservation else result['contacts']
        assert s.isValid(),n
        for other,t in changed.items():
            if not s.BoundBox.intersect(t.BoundBox):continue
            result['pairs']+=1
            try:
                assert t.isValid(),other
                v=sum(a.common(b).Volume for a in s.Solids for b in t.Solids)
                if v>1e-5:output.append(dict(a=n,b=other,volume_mm3=v))
            except Exception as e:result['errors'].append(dict(a=n,b=other,error=str(e)))
        for other,(c,radius) in curves.items():
            bb=s.BoundBox;bb.enlarge(radius)
            if not bb.intersect(c.BoundBox):continue
            result['pairs']+=1
            try:
                distance=s.distToShape(c)[0]
                if distance<radius-1e-5:output.append(dict(a=n,b=other,distance_mm=distance,radius_mm=radius))
            except Exception as e:result['errors'].append(dict(a=n,b=other,error=str(e)))
    check('RetainerBarSweep',sweep(reader.shape(ret,'RetainerBar')))
    for n in reader.doc(ret):
        if n.startswith('Foam'):check(n+'Sweep',sweep(reader.shape(ret,n)))
    print('Current retainer service',result['pairs'],round(time.monotonic()-tick,2),flush=True)
    for n,s in moving.items():check(n+'Sweep',sweep(s))
    for n,s in reserves.items():check(n+'ConservativeSweep',s,True)
    result.update(status='U1_WITHDRAWAL_AFTER_BUS_REMOVAL_NOMINAL_CLEAR' if not any(result[k] for k in ('contacts','reservation_resolutions','errors')) else 'U1_CHANGED_SERVICE_REQUIRES_RESOLUTION',
        source_sha256={**reader.hashes,**{p.relative_to(ROOT).as_posix():SHA(p) for p in pins|{Path(P.__file__),Path(G.__file__),Path(B.__file__),ROOT/'tools/cad/check_u1_socket_service.py'}}},
        worker_seconds=round(time.monotonic()-tick,3))
    (OUT/'u1-current-service-checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='source_sha256'}),flush=True)


if __name__=='__main__':run()
