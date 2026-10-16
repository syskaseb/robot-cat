"""One common functional-source protection layout, before native detailing.

Existing accepted W5 parts/wires are immutable. A filled supplier reservation
is not actual supplier material. No electrical or physical approval is implied.
"""
import json, math, time, zipfile
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT, SavedShapes, prop, sha
from current_work_guard import check

BASE=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype'
BODY=BASE/'body-harness-checkpoint'
OUT=BASE/'functional-protection'
SCENE=BODY/'current-w5-assembly/CurrentW5AssemblyNeutral.FCStd'
TIPS=[((-89,16),(-102.45,39.296083361801394),(-.5,math.sqrt(3)/2)),
      ((-65,16),(-41.703916638198606,29.45),(math.sqrt(3)/2,.5))]

def box(x,y,z,dx,dy,dz):return Part.makeBox(dx,dy,dz,A.Vector(x,y,z))
def cyl(x,y,z,r,h):return Part.makeCylinder(r,h,A.Vector(x,y,z))
def capsule(a,b,r,z,h):
    dx,dy=b[0]-a[0],b[1]-a[1];l=math.hypot(dx,dy)
    s=box(0,-r,z,l,2*r,h);s.rotate(A.Vector(),A.Vector(0,0,1),math.degrees(math.atan2(dy,dx)));s.translate(A.Vector(*a,0))
    return s.fuse(cyl(*a,z,r,h)).fuse(cyl(*b,z,r,h)).removeSplitter()
def profile(r,cr,z,h):
    s=cyl(-77,16,z,r,h)
    for a,b,u in TIPS:s=s.fuse(capsule(a,b,cr,z,h))
    return s.removeSplitter()
def portal(tip,u,z=75.5,h=8):
    # x is along the actual source's outward axis, local y across the port.
    s=box(-6,-3.3,z,18,6.6,h);s.rotate(A.Vector(),A.Vector(0,0,1),math.degrees(math.atan2(u[1],u[0])));s.translate(A.Vector(*tip,0));return s
def hexnut(x,y,z,af,h):
    r=af/math.sqrt(3);v=[A.Vector(x+r*math.cos(i*math.pi/3),y+r*math.sin(i*math.pi/3),z) for i in range(6)]
    return Part.Face(Part.makePolygon(v+[v[0]])).extrude(A.Vector(0,0,h))
def xhole(x,y,z,r,length):return Part.makeCylinder(r,length,A.Vector(x,y,z),A.Vector(1,0,0))
def xhex(x,y,z,af,length):
    s=hexnut(y,z,0,af,length);s.Placement=A.Placement(A.Vector(x,0,0),A.Rotation(A.Vector(0,1,0),A.Vector(0,0,1),A.Vector(1,0,0),'ZXY'));return s

def material(wall=2):
    outer=profile(31,6,59.4,45.6);inner=profile(31-wall,6-wall,61.4,44)
    guard=outer.cut(inner)
    web=box(-124,17.5,63.22,21,8,8.3).cut(inner)
    guard=guard.fuse(web)
    panel=profile(31,6,105,2.4)
    for x in (-88,-66):
        # One continuous bridge and boss, not tangent edges.
        guard=guard.fuse(box(x-4,-24,101,8,12,4))
        panel=panel.fuse(box(x-4,-24,105,8,12,2.4))
        guard=guard.cut(cyl(x,-20,100,1.2,6)).cut(hexnut(x,-20,101,4.3,1.8))
        panel=panel.cut(cyl(x,-20,104,1.2,5))
    panel=panel.cut(cyl(-77,16,104,12,5))
    for x in (-96,-58):panel=panel.cut(cyl(x,16,104,3.25,5))
    for a,b,u in TIPS:guard=guard.cut(portal(b,u))
    dock=box(47,-65.4,18.7,24.1,13.2,1.8).fuse(box(50,-65.4,20.5,21.1,13.2,.5))
    for q in [(69.3,-65.4,21,1.8,13.2,3),(50,-65.4,21,19.3,1.8,3),(50,-54,21,19.3,1.8,3)]:dock=dock.fuse(box(*q))
    bracket=box(113.5,22,77.72,18.7,51.5,5)
    for y in (25,37):bracket=bracket.fuse(box(132.2,y,77.72,35.5,6,5))
    bracket=bracket.fuse(box(164.7,23.5,77.72,3,24,39.28))
    bracket=bracket.cut(xhole(164,35.5,105,6.25,5)).cut(xhole(164,26.5,105,1.5,5))
    for y in (28,40):bracket=bracket.cut(cyl(126.2,y,77,1.7,7)).cut(hexnut(126.2,y,77.72,5.8,2.6))
    bracket=bracket.fuse(box(118.5,67.5,82.72,2,6,32.78))
    hood=box(116.7,3.5,84.7,1.8,64,28.6)
    for q in [(118.5,3.5,84.7,8.7,64,1.8),(118.5,3.5,111.5,8.7,64,1.8),
              (118.5,3.5,86.5,8.7,1.8,25),(118.5,65.7,86.5,8.7,1.8,25)]:hood=hood.fuse(box(*q))
    for z in (86,112):
        bracket=bracket.fuse(box(118.5,66.5,z-3.5,8,7,7))
        bracket=bracket.cut(xhole(118,70,z,1.2,10)).cut(xhex(120.5,70,z,4.3,6.1))
        hood=hood.fuse(box(116.7,66.5,z-3.5,1.8,7,7)).cut(xhole(116,70,z,1.2,4))
    for y in (3.3,65.5):
        for z in (93,105):hood=hood.cut(box(120.4,y,z-3.3,9.6,2.2,6.6))
    return {n:s.removeSplitter() for n,s in dict(S0Guard=guard,SourceTopMountPanel=panel,PostF0Dock=dock,S1BracketCurrent=bracket,S1TerminalHood=hood).items()}

def scene():
    r=SavedShapes();xml=r.doc(SCENE);targets={};wires={}
    # Radius metadata is pinned to the same accepted saved W5 centreline source.
    with zipfile.ZipFile(BODY/'remaining25-space-context.zip') as z:index=json.loads(z.read('index.json'))
    radii={q['name']:q['radius_mm'] for q in index['entries'] if q['kind']=='wire'}
    for n,o in xml.items():
        if not n.startswith(('Print_','Ref_')):continue
        label=prop(o,'Label')[0].get('value');s=r.shape(SCENE,n)
        if n.startswith('Ref_Wire'):
            assert label in radii,('Missing actual radius',label)
            wires[label]=(s,radii[label])
        else:targets[label]=s
    return r,targets,wires

def minimal_mounts():
    # Architecture change, not a cutout campaign: no enclosing S0/S1 box.
    # Protect exposed contacts individually with an explicit insulating-wrap
    # recipe; mounting material lives outside the source casing/wire galleries.
    left=box(-128,18,62.22,3,22,42.78).fuse(box(-128,18,105,27,7,2.4))
    plate=box(-103,2,105,52,28,2.4).cut(cyl(-77,16,104,12,5))
    for x in (-96,-58):plate=plate.cut(cyl(x,16,104,3.25,5))
    left=left.fuse(plate).removeSplitter()
    # One retained frame bolt plus one close-clearance antirotation locating
    # peg avoids unsupported thin feet in the W003 gallery. A countersunk
    # M3x50 replaces just UpperFrame8Screw/TopWasher; never duplicate these.
    mount=cyl(138,30,77.72,4,5.98).fuse(cyl(126.2,40,77.72,4,5.98))
    mount=mount.fuse(capsule((126.2,40),(138,30),3,81.22,2.48))
    mount=mount.fuse(box(126.2,37,81.22,41.5,6,2.48))
    mount=mount.fuse(cyl(126.2,40,74.72,1.6,3))
    mount=mount.fuse(box(164.7,23.5,81.22,3,24,35.78))
    mount=mount.cut(xhole(164,35.5,105,6.25,5)).cut(xhole(164,26.5,105,1.5,5))
    mount=mount.cut(cyl(138,30,77,1.7,8))
    mount=mount.cut(Part.makeCone(1.7,3,1.3,A.Vector(138,30,82.4)))
    return dict(S0MountCurrent=left,S1MountCurrent=mount.removeSplitter(),PostF0Dock=material()['PostF0Dock'])

def foundation_mount():
    # After two rejected load paths through the neck foundation, change the
    # owning structural part: root ABOVE static Foundation, outside yawBridge.
    s=box(-128,32,71.32,3,8,33.68)
    s=s.fuse(box(-128,32,105,29,8,2.4)).fuse(box(-103,24,105,4,16,2.4))
    panel=box(-103,2,105,52,28,2.4).cut(cyl(-77,16,104,12,5))
    for x in (-96,-58):panel=panel.cut(cyl(x,16,104,3.25,5))
    return s.fuse(panel).removeSplitter()

def run(minimal=False,foundation=False):
    check();OUT.mkdir(exist_ok=True);tick=time.monotonic()
    parts={'S0MountFoundation':foundation_mount()} if foundation else minimal_mounts() if minimal else material()
    r,targets,wires=scene()
    if foundation:
        for n in ('S1MountCurrent','PostF0Dock'):
            s=Part.Shape();s.read(str(OUT/(n+'.brep')));targets[n]=s
        # Retained sampled head material is additional changed-interface
        # checking, not repeated qualification of unrelated settled pairs.
        with zipfile.ZipFile(BODY/'remaining25-space-context.zip') as z:
            ix=json.loads(z.read('index.json'))
            for q in ix['entries']:
                if q['kind']!='target' or not q['name'].startswith(('head/','headref/','headwire/','factory/')):continue
                s=Part.Shape();s.importBrepFromString(z.read(q['file']).decode());targets['Motion/'+q['name']]=s
    print('shared current scene',len(targets),len(wires),flush=True)
    report=dict(status='PENDING',selected=False,physical_pass=False,contacts=[],reservation_contacts=[],errors=[],pairs=0,
        scope='Only new source guards/supports against current neutral W5 material and true-radius curves, plus all new/new pairs.')
    owners={'S0Guard':'Print_LeftRiser','S0MountCurrent':'Print_LeftRiser','PostF0Dock':'Print_FrontRightFixedCarrier','S0MountFoundation':'FoundationStationSupports/0/0'}
    replaced={'UpperFrame8Screw/0/0','UpperFrame8TopWasher/0/0'} if minimal else set()
    for n,s in parts.items():
        if not s.isValid() or len(s.Solids)!=1 or s.check(True):report['errors'].append([n,'invalid/multiple/BOP'])
        for other,t in list(targets.items())+[(m,t) for m,t in parts.items() if m<n]:
            if not s.BoundBox.intersect(t.BoundBox):continue
            if owners.get(n)==other or other in replaced:continue
            check();report['pairs']+=1
            if not t.isValid():report['errors'].append([other,'invalid source']);continue
            q=s.copy().common(t.copy());v=q.Volume
            if v>1e-5:
                row=dict(new=n,other=other,volume_mm3=v)
                # Explicit, limited supplier-control/neck reservation, not a waiver for rings/studs.
                if n in ('S1BracketCurrent','S1MountCurrent') and 'S1_control_CP2' in other:report['reservation_contacts'].append(row)
                else:report['contacts'].append(row)
        for other,(curve,radius) in wires.items():
            b=s.BoundBox;bb=A.BoundBox(b.XMin-radius,b.YMin-radius,b.ZMin-radius,b.XMax+radius,b.YMax+radius,b.ZMax+radius)
            if not bb.intersect(curve.BoundBox):continue
            check();report['pairs']+=1;distance=curve.copy().distToShape(s.copy())[0]
            if distance<radius-1e-6:report['contacts'].append(dict(new=n,wire=other,distance_mm=distance,required_mm=radius))
        s.exportBrep(str(OUT/(n+'.brep')))
        print(n,'shared checked',len(report['contacts']),'contacts',flush=True)
    report['source_sha256']={**r.hashes,Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__)),
        (BODY/'remaining25-space-context.zip').relative_to(ROOT).as_posix():sha(BODY/'remaining25-space-context.zip')}
    report['worker_seconds']=round(time.monotonic()-tick,3)
    report['status']='COMMON_LAYOUT_CLEAR_NATIVE_DETAIL_PENDING' if not report['contacts'] and not report['errors'] else 'COMMON_LAYOUT_REJECTED'
    report['architecture']='Static Foundation owned mount, full retained head motion context' if foundation else 'Minimal separate mount/individual contact insulation' if minimal else 'Rejected enclosing case'
    report['replaced_reference_objects']=sorted(replaced)
    (OUT/('foundation-space-check.json' if foundation else 'minimal-space-check.json' if minimal else 'space-check.json')).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)

if __name__=='__main__':
    import sys
    run('--minimal' in sys.argv,'--foundation' in sys.argv)
