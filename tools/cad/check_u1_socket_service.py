"""Retainer first, then a continuous12mm vertical socket withdrawal.

Prismatic body sweeps use actual faces. Four formed capacitor leads use labelled
conservative motion reservations; overlap would require exact resolution, never
be reported as a real collision. No external wire is silently unplugged.
"""
import json,time
from pathlib import Path
import FreeCAD as A
import Part
from current_prototype_harness_scene import context,wire
from plan_current_main_sources import ROOT,OUT,SHA
import build_u1_socket_retainer as R


def box(b):
    return Part.makeBox(*(b[i+3]-b[i] for i in range(3)),A.Vector(*b[:3]))


def sweep(s,h=12):
    # All service bodies here are vertical prisms/steps: PCB, boxes and bar.
    faces=[f for f in s.Faces if isinstance(f.Surface,Part.Plane) and f.normalAt(0,0).z>.999999]
    assert faces,'Not a supported vertical-prismatic body'
    out=s.multiFuse([f.extrude(A.Vector(0,0,h)) for f in faces]).removeSplitter()
    assert out.isValid() and len(out.Solids)==1
    return out


def run():
    tick=time.monotonic();gf=OUT/'u1-socket-passives-resolved.json';g=json.loads(gf.read_text())
    cf=OUT/'u1-socket-carrier-native.json';c=json.loads(cf.read_text());pf=OUT/'u1-socket-population-native.json';p=json.loads(pf.read_text())
    rf=OUT/'u1-socket-retainer-native.json';rp=json.loads(rf.read_text())
    for receipt in (p,c):
        for n,h in receipt['source_sha256'].items():assert SHA(ROOT/n)==h,n
    reader,pins,targets,wires=context();print('Service context ready',round(time.monotonic()-tick,2),flush=True)
    for n in list(targets):
        if n.startswith(('U1BoardAllowance','U1Spacer','U1Insulator','U1Mount','U1_unknown_height')) or n in rp['replaces']:targets.pop(n)
    docs=[]
    for f in (ROOT/c['native'],ROOT/p['native'],ROOT/rp['native']):docs.append(A.openDocument(str(f)))
    carrier,pop,ret=docs;targets['UpperCarrier001']=carrier.UpperCarrier001.Shape.copy()
    for n in ('AnchorLeft','AnchorRight'):targets[n]=ret.getObject(n).Shape.copy()
    moving={'Adapter1208PCB':pop.Adapter1208PCB.Shape.copy()}
    for o in pop.FixedPurchasedReferences.Group:
        if o.Name.startswith(('Male','MaleTail')):moving[o.Name]=o.Shape.copy()
        else:targets['U1_'+o.Name]=o.Shape.copy()
    reservations={}
    for o in pop.TopFaceReferences.Group:
        if o.Name.startswith(('C1_','C2_')):
            b=o.Shape.BoundBox;reservations[o.Name]=box([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax+12])
        else:moving[o.Name]=o.Shape.copy()
    for n,q in g['changed_E2_routes'].items():
        wires['pwm-branch-checkpoint/'+n]=(wire(q['parts']),q['radius']);targets.pop(n,None)
        targets.pop(n+'_BoardInsulation',None)
    result=dict(status='PENDING',selected=False,E1_complete=False,E2_requalified=False,physical_pass=False,
                service_lift_mm=12,pairs=0,contacts=[],reservation_resolutions=[],errors=[],
                sequence=['Power disconnected and verified first; no live service',
                          'Cut ONLY two module-retainer ties, remove loose cuttings',
                          'Lift keyed RetainerBar12mm vertically; foam lifted with it',
                          'Lift populated1208 with both male headers12mm vertically; base passives/100pad ends stay fixed'],
                no_external_wire_disconnects_required_for_adapter=True,
                not_covered=['Hand grip/tool reach and supplier socket extraction force/tolerance',
                            'Whole carrier removal; external grips and complete E2 insulation remainOPEN'])
    def check(name,s,obstacles,ww,reservation=False):
        for other,t in obstacles.items():
            if not s.BoundBox.intersect(t.BoundBox):continue
            result['pairs']+=1
            try:
                v=s.common(t).Volume
                if v>1e-5:(result['reservation_resolutions'] if reservation else result['contacts']).append(dict(a=name,b=other,intersection_mm3=v))
            except Exception as e:result['errors'].append(dict(a=name,b=other,error=str(e)))
        for other,(w,r) in ww.items():
            bb=s.BoundBox;bb.enlarge(r)
            if not bb.intersect(w.BoundBox):continue
            result['pairs']+=1
            try:
                dist=s.distToShape(w)[0]
                if dist<r-1e-5:(result['reservation_resolutions'] if reservation else result['contacts']).append(dict(a=name,b=other,distance_mm=dist,radius_mm=r))
            except Exception as e:result['errors'].append(dict(a=name,b=other,error=str(e)))
    refs,_=R.references()
    # Ties are deliberately cut before service; anchors stay. Bar/foam move
    # before the adapter; no proof starts with the whole carrier on a bench.
    first={**targets,**moving,**{n:pop.getObject(n).Shape.copy() for n in reservations}}
    check('RetainerBarSweep',sweep(ret.RetainerBar.Shape.copy()),first,wires)
    for n,s in refs.items():
        if n.startswith('Foam'):check(n+'Sweep',sweep(s),first,wires)
    print('Retainer-first service checked',round(time.monotonic()-tick,2),flush=True)
    for n,s in moving.items():
        obstacles=targets
        if n.startswith('Male'):
            # Nominal supplier mating interface ONLY. All unrelated fixed parts
            # remain checked. MAX housing height seating is a delivery gate.
            obstacles={k:v for k,v in targets.items() if not k.startswith('U1_Female')}
        check(n+'Sweep',sweep(s),obstacles,wires)
    for n,s in reservations.items():check(n+'ConservativeSweep',s,targets,wires,True)
    result['status']='SOCKET_SERVICE_REQUIRES_RESOLUTION' if any(result[k] for k in ('contacts','reservation_resolutions','errors')) else 'SOCKET_NOMINAL_CONTINUOUS_SERVICE_CLEAR_EXTERNAL_INTERFACE_OPEN'
    result['source_sha256']={**reader.hashes,**{f.relative_to(ROOT).as_posix():SHA(f) for f in [gf,cf,pf,rf,Path(__file__),*pins,*[ROOT/q['native'] for q in (c,p,rp)]]}}
    result['worker_seconds']=round(time.monotonic()-tick,3)
    (OUT/'u1-socket-service-checks.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    for d in docs:A.closeDocument(d.Name)
    print(json.dumps({k:result[k] for k in ('status','pairs','contacts','reservation_resolutions','errors','worker_seconds')}),flush=True)


if __name__=='__main__':run()
