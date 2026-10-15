"""One joint G1 carrier and five short fixed lands; no native/stock selection.

Existing Foundation owns the load path. WAGO adhesive does NOT carry wires.
Short three-mm lacing, knot, glue thickness and retention are prototype gates.
"""
import json,time
from pathlib import Path
import FreeCAD as A
import Part
from loom_land_port import box
from plan_axial_source_supports import arm_box
from current_mixed_receiver_material import prepare,material
from plan_body36_receiver_space import P,C
from current_work_guard import check as guard
from current_body36_candidates import resolve
from short_feed_lacing_saddle import build as feed_material

ROOT_POINT=[-100.5,-85.05,132.4224451363255]
PORTS=[('W060',-53,1.05),('W001',-46.5,1.55),('W036',-40,2.1),('W061',-33.5,2.1),('W025',-27,2.1)]

def geometry():
    pads=[dict(name='Tray',bounds_mm=[-61.5,-69.5,143.5,-18.5,-45.5,146.5]),
          dict(name='BackSpine',bounds_mm=[-61.5,-69.5,143.5,-18.5,-66.5,175.75]),
          dict(name='LeftKey',bounds_mm=[-61.5,-69.5,146.5,-59,-45.5,150]),
          dict(name='RightKey',bounds_mm=[-21,-69.5,146.5,-18.5,-45.5,150])]
    path=[ROOT_POINT,[-100.5,-85.05,145.5],[-40,-85.05,145.5],[-40,-68,145.5]]
    pieces=[box(p['bounds_mm']) for p in pads]+[arm_box(a,b,[2,2,2]) for a,b in zip(path,path[1:])]
    bands={};recipes=[]
    for wire,x,r in PORTS:
        t,w=.381,1.6764
        seat=[r+.5,-2,-1.5,r+4.5,2,1.5]
        foot=[r+.5,-2,1.25,r+4.5,2,5.25]
        outer=[-r-.2-t-.15,-r-.2-t-.15,-w/2-.15,r+4.5+t+.15,r+.2+t+.15,w/2+.15]
        inner=[-r-.2+.15,-r-.2+.15,-w,r+4.5-.15,r+.2-.15,w]
        s=box(seat).fuse(box(foot)).cut(box(outer).cut(box(inner))).removeSplitter()
        band=box([-r-.2-t,-r-.2-t,-w/2,r+4.5+t,r+.2+t,w/2]).cut(box([-r-.2,-r-.2,-w,r+4.5,r+.2,w]))
        knot=[r+4.5+t,-1,-1.5,r+7.5+t,1,.5]
        band=band.fuse(box(knot)).removeSplitter()
        # Local normal=-Y, lateral=+X, axial=+Z; datum is middle of3mm mouth.
        m=A.Matrix();m.A11=0;m.A21=-1;m.A12=1;m.A22=0;m.A33=1
        m.A14=x;m.A24=-54;m.A34=170.5
        frame=A.Placement(m)
        for q in (s,band):
            assert q.isValid() and len(q.Solids)==1 and not q.check(True),wire
            q.Placement=frame*q.Placement
        bridge=[x-2,-69.5,171.75,x+2,-54-r-.5,175.75]
        pieces.extend([s,box(bridge)]);bands[wire]=band
        recipes.append(dict(wire=wire,radius_mm=r,centre_mm=[x,-54,170.5],land_mm=3,
            seat=seat,foot=foot,ring_cut=dict(outer=outer,inner=inner),knot=knot,
            bridge_mm=bridge,local_to_world=list(m.A),lacing_blank_mm=150))
    body=pieces[0].multiFuse(pieces[1:]).removeSplitter()
    assert body.isValid() and len(body.Solids)==1 and not body.check(True),'Carrier disconnected/invalid'
    for n,b in bands.items():assert body.common(b).Volume<1e-6,('own band',n)
    return body,bands,dict(pads=pads,root_path_mm=path,arm_half_width_mm=2,lands=recipes)

def run():
    guard();tick=time.monotonic();body,bands,recipe=geometry()
    native=P.OUT/'StationFramesCurrent.FCStd'
    assert P.SHA(native)=='62d7b5c691bfc696e8173467d1fedc8be8e4e4bcf54bbcf7ed70cec36b666ba9'
    doc=A.openDocument(str(native));parent=doc.getObject('FoundationStationSupports').Shape.copy();A.closeDocument(doc.Name)
    outside=arm_box(ROOT_POINT,ROOT_POINT,[2,2,2]).cut(parent).Volume
    assert outside<1e-6,('Unrooted carrier',outside)
    union=parent.fuse(body).removeSplitter()
    assert union.isValid() and len(union.Solids)==1 and not union.check(True)
    targets,wires,pins,grips=prepare()
    for name,g in grips['groups'].items():
        profile,components=material(g)
        targets.update({'Group_'+name+'/'+k:s for k,s in components.items() if k!='seed'})
        if g['kind']=='triple':
            for feed in g['feeds']:
                support='cap' if name=='D_FL' and feed['wire']=='W002' else 'body'
                new=feed_material(profile['recipe'],feed,support=support)
                targets.update({'Feed_'+name+'/'+feed['wire']+'/'+k:new[k] for k in ('body','band')})
    rootsfile=P.OUT/'body36-receiver-support-reservations.json';roots=json.loads(rootsfile.read_text())
    for row in roots['groups']:
        for path in row['paths']:
            for i,(a,b) in enumerate(zip(path['points_mm'],path['points_mm'][1:])):
                targets['ReceiverRoot/'+row['name']+'/'+row['wire']+'/'+str(i)]=arm_box(a,b,row['arm_half_widths_world_mm'])
    macrofile=P.OUT/'body36-shared-macro-layout.json';macro=json.loads(macrofile.read_text())
    basefile=P.ROOT/macro['inherited_receipt'];base=json.loads(basefile.read_text())
    effective,ancestry=resolve(macro,P.ROOT)
    wires={n:v for n,v in wires.items() if not n.startswith('body/')}
    wires.update({'body/'+n:(P.wire(r['parts']),1) for n,r in effective.items()})
    pins.update({f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in (native,Path(__file__),Path(__file__).with_name('current_body36_candidates.py'),Path(__file__).with_name('short_feed_lacing_saddle.py'),rootsfile,macrofile,basefile)})
    bounds=C.ImmutableBounds();cache=C.AtomicMaterial(P.OUT/'g1-carrier-pairs.json',bounds.near)
    checks=0;errors=[];records=[]
    def hit(a,b,r=0):
        nonlocal checks
        if not bounds.near(a,b,r+.0001):return False
        if r and not b.Solids and len(b.Edges)>1:return any(hit(a,e,r) for e in b.Edges)
        checks+=1
        try:
            gap,volume=cache.check(a,b,0,r)
            return volume>1e-5 or (r and gap<r-1e-6)
        except (RuntimeError,AssertionError,ValueError) as e:errors.append(str(e));return True
    def save():
        out=dict(status='G1_ROOTED_COMPONENT_GATE_CLEAR' if len(records)==6 and all(not r['contact'] for r in records) and not errors else 'G1_ROOTED_COMPONENT_GATE_OPEN',
            recipe=recipe,components=records,checks=checks,errors=errors,source_sha256=pins,
            contained_root_cube_outside_mm3=outside,replacement_parent='FoundationStationSupports',
            parent_union_one_solid=True,worker_seconds=round(time.monotonic()-tick,3),
            selected=False,W5_complete=False,physical_pass=False,native_complete=False,
            full36accepted=not macro['remaining_wire_ids'],new_separate_prints=0,new_screws=0,
            candidate_receipt_ancestry=ancestry,
            lacing_candidate_mm=750,adhesive_gap_project_mm=.5,
            gates=['Provisional3mm fixed mouth retention/creep/diameter','Removable adhesive fit/compatibility','Lever access and assembly','Native editable replacement/export','WholeW5/stock'])
        f=P.OUT/'g1-rooted-carrier-plan.json';tmp=f.with_suffix('.tmp');tmp.write_text(json.dumps(out,indent=2)+'\n');tmp.replace(f);cache.save()
    save()
    for kind,s in [('carrier',body)]+list(bands.items()):
        guard();contact=None
        for n,t in targets.items():
            if kind=='carrier' and n.split('/')[0]=='FoundationStationSupports':continue
            if hit(s,t):contact='material/'+n;break
        if not contact:
            for n,(wire,r) in wires.items():
                own=n=='wire/'+kind
                if hit(s,wire,r if own else r+.25):contact='curve/'+n;break
        if not contact:
            for n,b in bands.items():
                if n==kind:continue
                if hit(s,b):contact='band/'+n;break
        records.append(dict(component=kind,contact=contact));save()
        print('G1',kind,'first',contact,'checks',checks,flush=True)
    save()

if __name__=='__main__':run()
