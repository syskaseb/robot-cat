"""Common source structures/bands vs CURRENT36, retained guides and material.

One coherent candidate, no positional search or blanket wire exclusions.
Only the actual same-parent printed structure may fuse with its own parent.
"""
import json,time
from pathlib import Path
import FreeCAD as A
from remaining_source_retention_material import geometry,internal_gate
from current_mixed_receiver_material import prepare
from current_body_restraint_material import prepare as other_retention
from current_body36_candidates import resolve
from plan_body36_receiver_space import P,C
from check_main_p0_placement import SavedShapes
from current_work_guard import check


def run():
    check();tick=time.monotonic();q=geometry()
    failures=internal_gate(q);assert not failures,('Internal source assembly first',failures)
    targets,wires,pins,_=prepare()
    extras,ep=other_retention();targets.update(extras);pins.update(ep)
    mf=P.OUT/'body36-shared-macro-layout.json';macro=json.loads(mf.read_text())
    assert not macro['remaining_wire_ids'];routes,_=resolve(macro,P.ROOT)
    wires={n:v for n,v in wires.items() if not n.startswith('body/')}
    wires.update({'body/'+n:(P.wire(r['parts']),1) for n,r in routes.items()})
    reader=SavedShapes();nf=P.OUT/'receiver-supports/manifest.json';native=json.loads(nf.read_text())
    assert native['status']=='FOUR_CURRENT_RECEIVER_FRAMES_SEVEN_CAPS_NATIVE_PREPARED'
    for n,h in native['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    model=P.OUT/'receiver-supports/ReceiverSupportsCurrent.FCStd'
    for r in native['parts']:targets['CurrentNative/'+r['part']]=reader.shape(model,r['object'])
    for r in native['feed_restraints']:
        name=r['lacing_reference'];targets['CurrentNative/'+name]=reader.shape(model,name)
    pins.update(reader.hashes);pins.update(q['source_sha256'])
    for f in (Path(__file__),nf,mf):pins[f.relative_to(P.ROOT).as_posix()]=P.SHA(f)
    records=[];errors=[];checks=0;bounds=C.ImmutableBounds()
    cache=C.AtomicMaterial(P.OUT/'remaining-source-retention-pairs.json',bounds.near)
    parts=q['components']
    def hit(a,b,r=0):
        nonlocal checks
        if not bounds.near(a,b,r+.0001):return False
        if r and not b.Solids and len(b.Edges)>1:return any(hit(a,e,r) for e in b.Edges)
        check();checks+=1
        try:
            gap,volume=cache.check(a,b,0,r)
            return volume>1e-5 or (r and gap<r-1e-6)
        except (RuntimeError,AssertionError,ValueError) as e:
            errors.append(str(e));return True
    def same_parent(owner,name):
        if owner in ('LeftRiser','RightRiser'):return name=='neck/'+owner or name.startswith('neck/'+owner+'/')
        return name=='UpperCarrier001' or name.startswith('UpperCarrier001/') or name in (
            'G1/carrier','FixedFeed/Heavy3/body','FixedFeed/BUS_G/body')
    def save():
        done=len(records)==len(parts)
        result=dict(status='REMAINING_SOURCE_COMMON_RETENTION_MATERIAL_CLEAR' if done and not errors and all(not r['contacts'] for r in records)
                    else 'REMAINING_SOURCE_COMMON_RETENTION_MATERIAL_OPEN',components=records,
            anchors=q['anchors'],recipes=q['recipes'],root_paths=q['paths'],checks=checks,errors=errors,
            source_sha256=pins,worker_seconds=round(time.monotonic()-tick,3),
            scope='Changed source retention only vs all current36/full retained scene/native receivers and all candidate structures/bands. Existing unmodified pairs reused, not rerun.',
            open=['Native replacements and source case retention/S0 fit',
                  'Other25 guide interfaces/whole assembly/stock/W5/M4'],
            selected=False,W5_complete=False,physical_pass=False)
        f=P.OUT/'remaining-source-retention-checks.json';tmp=f.with_suffix('.tmp')
        tmp.write_text(json.dumps(result,indent=2)+'\n');tmp.replace(f);cache.save()
    save()
    for name,s in parts.items():
        check();assert s.isValid() and len(s.Solids)==1 and not s.check(True),name
        owner=name.split('/',1)[1] if name.startswith('SourceStructure/') else None
        contacts=[]
        for target,t in targets.items():
            if owner and same_parent(owner,target):continue
            if hit(s,t):contacts.append('material/'+target)
        for target,(w,r) in wires.items():
            own=False
            if name.startswith('SourceLacing/'):
                wire=q['recipes'][name.split('/',1)[1]]['wire']
                own=target in ('wire/'+wire,wire) or target.startswith('wire/'+wire+'_') or target.startswith(wire+'_')
            if hit(s,w,r if own else r+.25):contacts.append('curve/'+target)
        for other,t in parts.items():
            if other==name:continue
            if hit(s,t):contacts.append('candidate/'+other)
        records.append(dict(name=name,contacts=contacts,nominal_case_reservations_not_manufacturer_metal=True))
        save();print('source retention',name,'contacts',contacts,'checks',checks,flush=True)
    save()


if __name__=='__main__':run()
