"""Reorganise the whole occupied core in its two anchored base halves, mm."""
from pathlib import Path
import json,math,datetime
import FreeCAD as A, FreeCADGui as G, Part
P=Path(__file__).parent
D=A.ActiveDocument; assert Path(D.FileName).resolve()==(P/'whole-cat19E.FCStd').resolve()
V=A.Vector
def box(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
def cyl(x,y,z,r,h,d=(0,0,1)):return Part.makeCylinder(r,h,V(x,y,z),V(*d))
def sh(n):return D.getObject(n).Shape
def group(*prefix):return [o.Name for o in D.Objects if o.Name.startswith(prefix)]
def wr(n,v):(P/n).write_text(json.dumps(v,indent=1)+'\n',encoding='utf8')
def bounds(s):
    b=s.BoundBox
    return [round(v,4) for v in [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]]
def add(n,s,col,kind):
    o=D.getObject(n) or D.addObject('Part::Feature',n)
    o.Shape=s;o.Label=n.replace('_',' ');o.ViewObject.ShapeColor=col;o.ViewObject.DisplayMode='Shaded'
    if 'Function' not in o.PropertiesList:o.addProperty('App::PropertyString','Function')
    o.Function=kind;o.ViewObject.Visibility=True
    return o
def join(parts):return parts[0].multiFuse(parts[1:]).removeSplitter() if len(parts)>1 else parts[0]
def hide(*names):
    for n in names:D.getObject(n).ViewObject.Visibility=False
moves=[]
def move(primary,follow,lower,rot=0):
    # Couple all members to an unmodified source pose, including hidden fasteners.
    names=list(dict.fromkeys([primary]+follow));r=A.Rotation(V(0,0,1),rot)
    rotpl=A.Placement(V(),r);q=sh(primary).copy();q.Placement=rotpl.multiply(q.Placement)
    b=q.BoundBox;t=A.Placement(V(*lower)-V(b.XMin,b.YMin,b.ZMin),r)
    for n in names:
        o=D.getObject(n);o.Placement=t.multiply(o.Placement)
    moves.append(dict(primary=primary,members=names,new_min=lower,rotation_Z=rot))
def rect(x0,x1,y0,y1,z,h):return box(x0,y0,z,x1-x0,y1-y0,h)
# Each board/power cluster remains whole. The S0 large key points to +Y, S1 to -Y.
move('S0_body',group('S0_'),[150,59,76],90)
move('OP_S1_PRIMARY_CASE_CONSERVATIVE',group('OP_S1_'),[160,-92,80])
move('Monitor_MOD05015',group('OP_MONITOR_'),[154,-74,146])
# The positive outer lane and negative outer lane each receive their own removable bank.
names=sorted(n for n in group('WAGO415_') if n!='WAGO415_data_1_0')
assert len(names)==15
for i,n in enumerate(names):
    y=-79 if i<8 else 66
    move(n,[],[-102+32*(i%8),y,114])
# Keep soldered E1+PCA and its floor bearing; move BUS complete above +Y fuse bank.
move('BUS25514_installed',group('CB_BUS_','CF17_BUS_CSK')+['D18C_DATA_BUS_FULL26_PROJECT_BOOT'],[33,46,131])
cat=P.parents[6]/'electronics/full-cat/pi-bus-primary-r1'
if not cat.exists():cat=next(q/'electronics/full-cat/pi-bus-primary-r1' for q in P.parents if (q/'electronics/full-cat/pi-bus-primary-r1').is_dir())
src=json.loads((cat/'catalog.json').read_bytes())
# Real port mouths, board, components, underside and header bodies in their supplier common frame.
# The manufacturer export includes duplicate graphics/object aliases. Use each selected finite
# physical body once by matching its source bounds; keep the published catalog as provenance.
br=A.Rotation(V(0,0,1),90);t=A.Placement(V(66,46,132.6),br)
pieces=[];seen=set();mapped=[]
for rec in src['parts']:
    if not rec['solids']:continue
    k=tuple(round(v,4) for v in rec['bounds'])
    if k in seen:continue
    seen.add(k);ss=Part.Shape();ss.read(str(cat/(rec['name']+'.brep')))
    ss.Placement=t.multiply(ss.Placement);pieces.append(ss);mapped.append(dict(source=rec['name'],label=rec['label'],bounds=bounds(ss)))
board=pieces[0];add('E19_BUS_PCB',board,(.10,.43,.24),'one supplier board, four hole datums')
add('E19_BUS_population',Part.makeCompound(pieces[1:]),(.27,.30,.32),'supplier population including actual USB-C, headers and power ports')
hide('BUS25514_installed')
# Move complete keyed yaw pair to an open longitudinal lane behind the jaw.
move('D19D_YawMatedPair',[],[-79,-40,110])
# A shaft collar stays fixed on the existing 8-anchor assembly. The hood is now a
# high yaw cover, entirely above the bearing bridge. The fixed low shroud takes the lower seam.
hood=sh('D19D_YawHood').common(box(-190,-115,123,120,230,120)).removeSplitter()
add('E19_UpperYawCover',hood,(.19,.24,.28),'yaw shell and aft tie tongue on the existing saddle')
hide('D19D_YawHood','D19D_RearShell','D19D_Shoulder','D19D_HeadServoWires','D19_DATA216_OPEN_RESERVE')
# Preserve the whole current chin shield and the front portion of the shoulder. The
# rectangular bay begins behind the joint. The shroud can lift separately before the lids.
nose=sh('D19D_Shoulder').common(box(-180,-120,0,104,240,240))
add('E19_FrontShroud',nose,(.22,.26,.28),'fixed overlap at chin, removable separately from the box')
# Source hollow root/journal and transverse key remain unchanged below z=159.
old=sh('TAIL_ROTATING_HOLLOW_REAL_ROOT')
def tailsection(z):
    sec=old.section(Part.makePlane(140,100,V(105,-42,z)))
    b=sec.BoundBox
    return [z,b.Center.x,b.Center.y,b.XLength,b.YLength]
sections=[tailsection(z) for z in [155,156,158,159,161]]
z,x,y,w,h=sections[2]
rows=[(x,y,157,max(5,w*.53)),(x+4,y,166,8),(x+22,y,186,10.2),(x+49,y,209,10.6),(x+70,y,234,9.4),(x+80,y,257,7),(x+81,y,271,3)]
def loft(rows):
    return Part.makeLoft([Part.Wire([Part.makeCircle(r,V(x,y,z),V(0,0,1))]) for x,y,z,r in rows],True,True)
body=loft(rows)
cavity=loft([(a,b,c,r-1.65) for a,b,c,r in rows[1:-1]])
tail=old.common(box(115,-35,105,120,80,54)).fuse(body.cut(cavity)).removeSplitter()
assert len(tail.Solids)==1 and tail.isValid(),sections
add('E19_KeyedTail',tail,(.79,.55,.29),'visible, hollow tail integral with original keyed and cross-pinned root')
hide('TAIL_ROTATING_HOLLOW_REAL_ROOT')
wr('module-poses.json',moves);wr('bus-source.json',dict(catalog_sha=src['source_sha256'],frame='local +X to +Y, +Y to -X, top at (66,46,132.6)',members=mapped));wr('tail-root.json',dict(source_sections=sections,upper_sections=rows,bounds=bounds(tail),axis=[140,0,130],direction=[0,1,0]))
D.recompute();D.save()
