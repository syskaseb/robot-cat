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
from check_main_p0_placement import SavedShapes

ROOT_POINT=[-74.0,-84.2375,112.0]
PORTS=[('W060',-53,1.05),('W001',-46.5,1.55),('W036',-40,2.1),('W061',-33.5,2.1),('W025',-27,2.1)]

def geometry(root_path=None,direct_upper=False,upper_portal=False):
    # The FIRST layout's floor overhung the ATO row. Put the whole floor,
    # spine and five restraints NORTH of that row instead of trimming fuses.
    # The narrow root crosses the actual gap between R1/R2, below G1 case.
    # Tail XB32 runs across the WHOLE former spine atY-41.875/Z151.49.
    # Allocate the whole spine north of that wire and its6mm sleeve, not
    # only west of the sleeve's first collision witness.
    north=-28 if direct_upper and not upper_portal else -35.5
    east=-14 if direct_upper and not upper_portal else -18.5
    pads=[dict(name='Tray',bounds_mm=[-61.5,-58.5,143.5,east,north,146.5]),
          dict(name='BackSpine',bounds_mm=[-61.5,north-3,143.5,east,north,175.75]),
          dict(name='LeftKey',bounds_mm=[-61.5,-58.5,146.5,-59,north,150]),
          dict(name='RightKey',bounds_mm=[-21,-58.5,146.5,-18.5,-47.5,150])]
    # The previous upper root was a wired head-source collar. Start at the
    # separate measured lower parent root; plan its whole path below MTA.
    path=([[-56,-22,76.72],[-56,-22,140],[-56,-37,140],[-56,-37,144.5]] if upper_portal else
          [[-16,-30,76.72],[-16,-30,145]] if direct_upper else
          root_path or [ROOT_POINT,[-40,-84.2375,112],[-40,-54,112],[-40,-54,144.5]])
    if not direct_upper and not upper_portal:assert path[0]==ROOT_POINT and path[-1]==[-40,-54,144.5]
    pieces=[box(p['bounds_mm']) for p in pads]
    post=([-58,-24,76.72,-54,-20,142] if upper_portal else
          [-18,-32,76.72,-14,-28,146.5] if direct_upper else None)
    pieces.extend(([box(post)]+[arm_box(a,b,[2,2,2]) for a,b in zip(path[1:],path[2:])]) if upper_portal else
                  [box(post)] if direct_upper else
                  [arm_box(a,b,[2,2,2]) for a,b in zip(path,path[1:])])
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
        # Local normal=+Y, lateral=-X, axial=+Z; datum is middle of3mm mouth.
        m=A.Matrix();m.A11=0;m.A21=1;m.A12=-1;m.A22=0;m.A33=1
        m.A14=x;m.A24=-54;m.A34=170.5
        frame=A.Placement(m)
        for q in (s,band):
            assert q.isValid() and len(q.Solids)==1 and not q.check(True),wire
            q.Placement=frame*q.Placement
        bridge=[x-2,-54+r+.5,171.75,x+2,north,175.75]
        pieces.extend([s,box(bridge)]);bands[wire]=band
        recipes.append(dict(wire=wire,radius_mm=r,centre_mm=[x,-54,170.5],land_mm=3,
            seat=seat,foot=foot,ring_cut=dict(outer=outer,inner=inner),knot=knot,
            bridge_mm=bridge,local_to_world=list(m.A),lacing_blank_mm=150))
    body=pieces[0].multiFuse(pieces[1:]).removeSplitter()
    assert body.isValid() and len(body.Solids)==1 and not body.check(True),'Carrier disconnected/invalid'
    for n,b in bands.items():assert body.common(b).Volume<1e-6,('own band',n)
    return body,bands,dict(pads=pads,root_path_mm=path,root_post_bounds_mm=post,
                          arm_half_width_mm=2,lands=recipes,direct_upper=direct_upper,upper_portal=upper_portal)

def run(diagnose_all=False,direct_upper=False,upper_portal=False):
    guard();tick=time.monotonic()
    choicefile=P.OUT/'g1-whole-root-choice.json'
    if direct_upper or upper_portal:
        native=P.OUT/'U1InterfaceCarriersCurrent.FCStd';parent_name='UpperCarrier001'
        assert P.SHA(native)=='fd09de30744aa0ea26bad789779980172ee078b650ae80070729254ee259e9c1'
        body,bands,recipe=geometry(direct_upper=True,upper_portal=upper_portal)
        root_patch=box([-58,-24,76.72,-54,-20,77.72] if upper_portal else [-18,-32,76.72,-14,-28,77.72])
    else:
        assert choicefile.exists(),'Allocate the whole new root path before a third component gate'
        choice=json.loads(choicefile.read_text());assert choice['status']=='STATIC_WHOLE_ROOT_PROPOSAL_MOTION_GATE_OPEN'
        for n,h in choice['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,('Changed shared root choice input',n)
        body,bands,recipe=geometry(choice['root_path_mm'])
        native=P.OUT/'StationFramesCurrent.FCStd';parent_name='FoundationStationSupports'
        assert P.SHA(native)=='62d7b5c691bfc696e8173467d1fedc8be8e4e4bcf54bbcf7ed70cec36b666ba9'
        root_patch=arm_box(ROOT_POINT,ROOT_POINT,[2,2,2])
    # Saved BRep is the exact qualified native tip. Preflight must not
    # recompute its entire history merely to read material. Editing still
    # requires the later parameter/reopen checks on a separate native copy.
    parent=SavedShapes().shape(native,parent_name)
    outside=root_patch.cut(parent).Volume
    assert outside<1e-6,('Unrooted carrier',outside)
    union=parent.fuse(body).removeSplitter()
    assert union.isValid() and len(union.Solids)==1 and not union.check(True)
    targets,wires,pins,grips=prepare()
    from current_fixed_feed_material import prepare as fixed_feeds
    extra,extra_pins=fixed_feeds();targets.update(extra);pins.update(extra_pins)
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
    pins.update({f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in (native,choicefile,Path(__file__),Path(__file__).with_name('check_main_p0_placement.py'),Path(__file__).with_name('current_body36_candidates.py'),Path(__file__).with_name('short_feed_lacing_saddle.py'),rootsfile,macrofile,basefile)})
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
            contained_root_patch_outside_mm3=outside,replacement_parent=parent_name,
            parent_union_one_solid=True,worker_seconds=round(time.monotonic()-tick,3),
            selected=False,W5_complete=False,physical_pass=False,native_complete=False,
            full36accepted=not macro['remaining_wire_ids'],new_separate_prints=0,new_screws=0,
            candidate_receipt_ancestry=ancestry,
            lacing_candidate_mm=750,adhesive_gap_project_mm=.5,
            assembly_plan=[parent_name+' with integrated carrier before later bank/boards, installed access still requires A2 proof',
                'Insert bank fuses before G1 casing if that casing obstructs the extraction approach',
                'Bench prepare five untinned ends; retain actual first3mm UP lands; support case while opening levers',
                'Five dedicated lacing bindings carry insulation load into the printed carrier, never case adhesive'],
            service_plan=['All sources including monitor/USB absent; robot supported',
                'Support G1, release five dedicated bindings and five labeled G1 ends before deeper bank work; park/cover ends without tension',
                'Remove provisional casing bond; do not claim bank can move through the empty integral carrier until installed A2 path is proved'],
            gates=['Provisional3mm fixed mouth retention/creep/diameter','Removable adhesive fit/compatibility','Lever access and assembly','Native editable replacement/export','WholeW5/stock'])
        f=P.OUT/'g1-rooted-carrier-plan.json';tmp=f.with_suffix('.tmp');tmp.write_text(json.dumps(out,indent=2)+'\n');tmp.replace(f);cache.save()
    save()
    for kind,s in [('carrier',body)]+list(bands.items()):
        guard();contact=None;contacts=[]
        for n,t in targets.items():
            if kind=='carrier' and n.split('/')[0]==parent_name:continue
            if hit(s,t):
                contact='material/'+n;contacts.append(contact)
                if not diagnose_all:break
        if not contact or diagnose_all:
            for n,(wire,r) in wires.items():
                own=n=='wire/'+kind
                if hit(s,wire,r if own else r+.25):
                    contact='curve/'+n;contacts.append(contact)
                    if not diagnose_all:break
        if not contact or diagnose_all:
            for n,b in bands.items():
                if n==kind:continue
                if hit(s,b):
                    contact='band/'+n;contacts.append(contact)
                    if not diagnose_all:break
        records.append(dict(component=kind,contact=contact,all_contacts=contacts));save()
        print('G1',kind,'contacts',contacts,'checks',checks,flush=True)
    save()

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--diagnose-all',action='store_true')
    parser.add_argument('--direct-upper',action='store_true');parser.add_argument('--upper-portal',action='store_true');args=parser.parse_args()
    run(args.diagnose_all,args.direct_upper,args.upper_portal)
