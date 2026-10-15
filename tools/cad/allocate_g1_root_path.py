"""Choose one whole lower G1 load path against all nominal actual obstacles.

Six axis orders are a bounded common-space plan, not repeated CAD variants.
This snapshot preflight cannot qualify moving/changed material; the complete
current component gate and native union are still mandatory.
"""
import copy,itertools,json,time,zipfile
from pathlib import Path
import FreeCAD as A
import Part
from plan_g1_rooted_carrier import geometry,ROOT_POINT
from plan_body36_receiver_space import P,C
from current_body36_candidates import resolve
from current_work_guard import check as guard
from plan_axial_source_supports import arm_box

def root_orders(root,goal):
    for order in itertools.permutations((0,1,2)):
        path=[list(root)];p=list(root)
        for axis in order:p=p.copy();p[axis]=goal[axis];path.append(p)
        yield order,path

def run():
    guard();tick=time.monotonic();archive=P.OUT.parent/'current-view-60-20261012.zip'
    mf=P.OUT/'body36-shared-macro-layout.json';macro=json.loads(mf.read_text());routes,chain=resolve(macro,P.ROOT)
    native=P.OUT/'StationFramesCurrent.FCStd'
    assert P.SHA(native)=='62d7b5c691bfc696e8173467d1fedc8be8e4e4bcf54bbcf7ed70cec36b666ba9'
    d=A.openDocument(str(native));parent=d.getObject('FoundationStationSupports').Shape.copy();A.closeDocument(d.Name)
    assert arm_box(ROOT_POINT,ROOT_POINT,[2,2,2]).cut(parent).Volume<1e-6
    target={};wires={};bounds=C.ImmutableBounds()
    scope=Part.makeBox(65,54,70,A.Vector(-78,-88,108))
    with zipfile.ZipFile(archive) as z:
        for row in json.loads(z.read('index.json'))['entries']:
            name=row['label']
            if name=='Foundation':continue # Same physical print; final native union is mandatory.
            if name in {'wire/'+n for n in routes} or name.startswith('body/'):continue
            s=Part.Shape();s.importBrepFromString(z.read(row['file']).decode())
            radius=row.get('radius_mm',0)
            if not bounds.near(scope,s,radius+.25):continue
            assert s.isValid(),name
            if radius:wires[name]=(s,radius)
            else:target[name]=s
    positive=set(macro['retained_route_ids'])|set(macro['qualified_changed_routes'])
    for n in positive:
        s=P.wire(routes[n]['parts'])
        if bounds.near(scope,s,1.25):wires['currentbody/'+n]=(s,1)
    cache=C.AtomicMaterial(P.OUT/'g1-whole-root-pairs.json',bounds.near);checks=0;attempts=[];chosen=None
    def hit(a,b,r=0):
        nonlocal checks
        if not bounds.near(a,b,r+.0001):return False
        if r and len(b.Edges)>1:return any(hit(a,e,r) for e in b.Edges)
        checks+=1;gap,volume=cache.check(a,b,0,r)
        return volume>1e-5 or r and gap<r-1e-6
    def save():
        out=dict(status='STATIC_WHOLE_ROOT_PROPOSAL_MOTION_GATE_OPEN' if chosen else 'WHOLE_G1_ROOT_ALLOCATION_OPEN',
            root_path_mm=chosen,attempts=attempts,checks=checks,
            contained_root_cube_mm=ROOT_POINT,source_sha256={f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in (archive,mf,native,Path(__file__),Path(__file__).with_name('plan_g1_rooted_carrier.py'))},
            candidate_receipt_ancestry=chain,worker_seconds=round(time.monotonic()-tick,3),selected=False,physical_pass=False,
            mandatory_next='Full current source/receiver/36candidate/motion G1 gate; native one-solid parent union and stock/service')
        f=P.OUT/'g1-whole-root-choice.json';tmp=f.with_suffix('.tmp');tmp.write_text(json.dumps(out,indent=2)+'\n');tmp.replace(f);cache.save()
    save()
    goal=[-40,-54,144.5]
    for order,path in root_orders(ROOT_POINT,goal):
        guard()
        body,bands,_=geometry(path);contact=None
        for name,s in target.items():
            if hit(body,s):contact='material/'+name;break
        if not contact:
            for name,(s,r) in wires.items():
                if hit(body,s,r+.25):contact='curve/'+name;break
        attempts.append(dict(axis_order=list(order),path_mm=copy.deepcopy(path),contact=contact))
        if not contact:chosen=path
        save();print('G1 whole root',order,'contact',contact,'checks',checks,flush=True)
        if chosen:break
    save()

if __name__=='__main__':run()
