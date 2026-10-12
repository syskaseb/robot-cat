"""Shared remaining MAIN/USB/G_TAIL insulation grips, before native CAD.

Preserve all13 complete U1/Pi guides. One fixed four-core MAIN restraint uses
the existing common3mm insulated land, explicitly NOT an invented9mm land.
Two integral extensions root in the actual LowerCarrier and E2 west tab.
"""
import json,time,math
from pathlib import Path
import FreeCAD as A
import Part
from plan_current_main_sources import ROOT,OUT,BASE,SHA
from current_prototype_harness_scene import wire
from u1_socket_current_context import context
import plan_u1_grouped_grips as G
import plan_u1_board_grips as B


AXES=[(-52.701,23.321),(-34.159,23.321)]


def allocation():
    pads=[];bands={}
    def add(owner,n,b):pads.append(dict(owner=owner,name=n,bounds_mm=b))
    for i,(x,y) in enumerate(AXES):
        pads.append(dict(owner='MAINGrip',name='Foot'+str(i),kind='disc',
                         centre_mm=[x,y,48.0948],radius_mm=2.4,height_mm=1))
        add('MAINGrip','FootRoot'+str(i),[x-1.2,24.8,48.0948,x+1.2,28.321,49.0948])
        add('MAINGrip','Post'+str(i),[x-1.2,25.821,48.0948,x+1.2,28.321,55.8448])
    add('MAINGrip','Rail',[-53.901,25.821,48.0948,-32.959,28.321,50.0948])
    add('MAINGrip','TopReturn',[-53.901,24,53.8448,-32.959,28.321,55.8448])
    add('MAINGrip','InsulationSeat',[-49.73,22.339,51.0948,-37.13,24.839,54.0948])
    bands['MAINBand'],_=G.thin_tie_z(52.5948,-50.73,-36.13,19.239,25.839)
    bands['MAINHead']=G.box([-45.83,25.839,50.3448,-41.03,30.339,53.8448])
    # Root at actual solid floorY-26.85, not the bbox of a distant boss.
    add('LowerCarrier001','USBRoot',[44,-42,40.72,46,-26,42.72])
    add('LowerCarrier001','USBPost',[44,-42,42.72,46,-36.1,49.87])
    add('LowerCarrier001','USBSeat',[32.7,-41.7,48.37,46,-36.1,49.87])
    bands['USBBand']=G.box([35.95,-42.7,47.37,38.45,-35.1,52.97]).cut(
        G.box([35.8,-41.7,48.37,38.6,-36.1,51.97]))
    bands['USBHead']=G.box([34.8,-35.1,48.92,39.6,-30.6,52.42])
    # E2BridgeWestTab14..50X/-50..-23Y,129.5..132.3Z is retained.
    # Place the load path north of the complete37.5..46.5 straight wire.
    # The complete existingW4 pair occupiesY-35 and its bandX42.25..44.75.
    # End the toe before the XL09 bend; root beside, not under, that bend.
    # A thin lacing tie fits the4.75mm axial gap, unlike the nominal4.8mm
    # plastic locking-head budget. Its knot sits BELOW the wire pair.
    add('E2Fixture','GTailRoot',[46.5,-38.05,131.3,49,-36.1,134.3])
    add('E2Fixture','GTailPost',[46.5,-38.05,134.3,49,-36.1,140.3])
    # Load path joins the east end of the toe, outside the lacing plane.
    # A bridge starting at39.5 trapped the return leg of its own binding.
    add('E2Fixture','GTailBridge',[41.3,-38.05,138.6,49,-36.1,140.3])
    add('E2Fixture','GTailSeat',[37.5,-41.45,138.6,41.7,-38.05,140.3])
    t=.381;w=1.6764
    bands['GTailBand']=G.box([39.5-w/2,-41.45-t,138.6-t,39.5+w/2,-38.05+t,141.7+t]).cut(
        G.box([39.5-w,-41.45,138.6,39.5+w,-38.05,141.7]))
    bands['GTailHead']=G.box([38,-40.75,136.219,41,-38.75,138.219])
    return dict(pads=pads,bands=bands,MAIN_axes_mm=AXES,
        new_T18R=2,lacing_blanks_mm=[150],new_metal_fasteners=0,replaced_MAIN_upper_washers=2,
        existing_MAIN_screw_raise_mm=.7,MAIN_nut_protrusion_mm=.5252,
        MAIN_common_land_mm=3,USB_land_mm=9,GTail_land_mm=9,GTail_seat_span_mm=4.2,
        selected=False,physical_pass=False,
        gates=['Short fixed MAIN four-core grip is a nominal prototype assumption, not pull-load approval.',
               'Deburr PETG, hand tension without flattening insulation, fit/creep/pull check in phase2.',
               'Passive USB body/boot are project fit budgets; no manufacturer USB engagement dimensions invented.'])


def material(row):
    if row.get('kind')=='disc':return Part.makeCylinder(row['radius_mm'],row['height_mm'],A.Vector(*row['centre_mm']))
    return G.box(row['bounds_mm'])


def main_hardware():
    shapes={};underhead=49.0948
    for i,(x,y) in enumerate(AXES):
        shapes[f'MAIN_{i}_shaft']=Part.makeCylinder(1,12,A.Vector(x,y,underhead),A.Vector(0,0,-1))
        shapes[f'MAIN_{i}_head']=Part.makeCylinder(1.9,2,A.Vector(x,y,underhead))
        shapes[f'MAIN_{i}_lower_washer']=Part.makeCylinder(2.5,.3,A.Vector(x,y,39.22)).cut(
            Part.makeCylinder(1.1,.3,A.Vector(x,y,39.22)))
        shapes[f'MAIN_{i}_nut']=Part.makeCylinder(4/math.sqrt(3),1.6,A.Vector(x,y,37.62)).cut(
            Part.makeCylinder(1,1.6,A.Vector(x,y,37.62)))
    return shapes


def latest_scene():
    reader,pins,targets,curves=context()
    for tag,names in [('interface-carriers',('UpperCarrier001','LowerCarrier001')),
                      ('grouped-grips',('GPIOGrip','PCAGrip')),
                      ('board-grips',('AnchorLeft','AnchorRight'))]:
        f=OUT/('u1-'+tag+'-native.json');r=json.loads(f.read_text());model=ROOT/r['native']
        assert SHA(model)==r['native_sha256'];pins.update((f,model))
        d=A.openDocument(str(model))
        for n in names:targets['U1_'+n if tag=='board-grips' else n]=d.getObject(n).Shape.copy()
        A.closeDocument(d.Name)
    g=json.loads((OUT/'u1-grouped-grips-native.json').read_text())
    for n in g['replaced_upper_washers']:targets.pop(n)
    for r in g['changed_existing_hardware']:
        targets[r['name']]=targets[r['name']].copy();targets[r['name']].translate(A.Vector(*r['translation_mm']))
    targets.update({'Grouped/'+n:s for n,s in G.allocation()['bands'].items()})
    targets.update({'Board/'+n:s for n,s in B.allocation()['bands'].items()})
    f=OUT/'u1-common-wiring-plan.json';c=json.loads(f.read_text());pins.add(f)
    for n,r in {**c['complete_routes'],**c['changed_MAIN_pair']}.items():
        curves[n]=(wire(r['parts']),r.get('radius',r.get('radius_mm')))
    curves.update({n+'/bare':(wire(r['parts']),r['radius']) for n,r in c['bare'].items()})
    return reader,pins,targets,curves


def run():
    tick=time.monotonic();p=allocation();reader,pins,targets,curves=latest_scene()
    print('Power grip retained scene',round(time.monotonic()-tick,3),flush=True)
    # Current scene did not expose MAIN hardware names. Include the actual
    # source-backed stack explicitly, rather than treating empty space as proof.
    hardware=main_hardware();targets.update(hardware)
    r=dict(status='PENDING',pairs=0,contacts=[],errors=[],selected=False,physical_pass=False)
    new={};whole={}
    for owner in ('MAINGrip','LowerCarrier001','E2Fixture'):
        rows=[material(v) for v in p['pads'] if v['owner']==owner];s=rows[0].multiFuse(rows[1:])
        if owner=='MAINGrip':
            for x,y in AXES:s=s.cut(Part.makeCylinder(1.2,15,A.Vector(x,y,45)))
            whole[owner]=new[owner]=s.removeSplitter()
        else:
            original=targets[owner];whole[owner]=original.fuse(s).removeSplitter()
            new[owner]=whole[owner].cut(original).removeSplitter()
        try:
            assert whole[owner].isValid() and len(whole[owner].Solids)==1 and not whole[owner].check(True)
        except Exception as e:r['errors'].append(dict(part=owner,error=str(e)))
    new.update(p['bands']);bounds={n:s.BoundBox for n,s in {**targets,**new}.items()};valid={}
    cb={}
    for n,(c,rr) in curves.items():b=c.BoundBox;b.enlarge(rr);cb[n]=b
    for n,s in new.items():
        for m,t in {**targets,**new}.items():
            if m==n or m in new and m<n:continue
            if not bounds[n].intersect(bounds[m]):continue
            r['pairs']+=1
            try:
                if n not in valid:valid[n]=s.isValid()
                if m not in valid:valid[m]=t.isValid()
                assert valid[n] and valid[m]
                vol=sum(a.common(b).Volume for a in s.Solids for b in t.Solids)
                if vol>1e-5:r['contacts'].append(dict(a=n,b=m,volume_mm3=vol))
            except Exception as e:r['errors'].append(dict(a=n,b=m,error=str(e)))
        for m,(c,rr) in curves.items():
            if not cb[m].intersect(bounds[n]):continue
            r['pairs']+=1;gap=c.distToShape(s)[0]
            if gap<rr-1e-5:r['contacts'].append(dict(a=n,b=m,distance_mm=gap,required_mm=rr))
        print('Power grip',n,r['pairs'],len(r['contacts']),round(time.monotonic()-tick,2),flush=True)
    r.update(status='POWER_GRIPS_SHARED_CLEAR_NATIVE_OPEN' if not r['contacts'] and not r['errors'] else 'POWER_GRIPS_REJECTED',
        worker_seconds=round(time.monotonic()-tick,3),source_sha256={**reader.hashes,**{f.relative_to(ROOT).as_posix():SHA(f) for f in [*pins,Path(__file__),Path(B.__file__),Path(G.__file__),ROOT/'tools/cad/whole_cat_neck_main_mount.py']}})
    (OUT/'u1-power-grips-plan.json').write_text(json.dumps({k:v for k,v in p.items() if k!='bands'},indent=2)+'\n')
    (OUT/'u1-power-grips-checks.json').write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({k:v for k,v in r.items() if k!='source_sha256'}),flush=True)


if __name__=='__main__':run()
