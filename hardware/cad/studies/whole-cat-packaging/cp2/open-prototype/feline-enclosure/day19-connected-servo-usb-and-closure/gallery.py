"""Upper accessible cable gallery and new full mating stations on the 19E copy."""
from pathlib import Path
import hashlib
P=Path(__file__).parent;E=P.parent/'day19-simple-box-common-core'
exec((E/'core.py').read_text().split('# Each board/power cluster')[0].replace('19E.FCStd','19F.FCStd'))
lay=json.loads((P/'whole-lay.json').read_bytes())
def wr(n,v):(P/n).write_bytes((json.dumps(v,indent=1)+'\n').encode())
def transform(names,src,dst,angle):
    r=A.Rotation(V(0,0,1),angle);t=A.Placement(V(*dst)-r.multVec(V(*src)),r)
    for n in dict.fromkeys(names):
        o=D.getObject(n);o.Placement=t.multiply(o.Placement)
    return t
bp=transform(['BUS25514_installed','E19_BUS_PCB','E19_BUS_population','D18C_DATA_BUS_FULL26_PROJECT_BOOT']+group('CB_BUS_','CF17_BUS_CSK'),[92.804,78.11,133.77],[140,67.5,184],180)
cat=next(q/'electronics/full-cat/pi-bus-primary-r1' for q in P.parents if (q/'electronics/full-cat/pi-bus-primary-r1').is_dir())
s=Part.Shape();s.read(str(cat/'PCB.brep'));s.Placement=bp.multiply(A.Placement(V(66,46,132.6),A.Rotation(V(0,0,1),90))).multiply(s.Placement)
src=s.Solids;lookup=json.loads((E/'installed-bus.json').read_bytes())['board_index']
dst=sh('E19_BUS_population').Solids;dst.insert(lookup,sh('E19_BUS_PCB').Solids[0])
def prop(p):
    m=p.MatrixOfInertia
    return [p.Volume,*list(p.CenterOfMass),m.A11,m.A12,m.A13,m.A22,m.A23,m.A33,*bounds(p)]
errs=[max(abs(a-b) for a,b in zip(prop(i),prop(j))) for i,j in zip(src,dst)]
wr('module-binding.json',dict(BUS=dict(constructor='PCB.brep',source_sha256=hashlib.sha256((cat/'PCB.brep').read_bytes()).hexdigest(),source_count=len(src),retained_count=len(dst),board_index=lookup,corresponding_solid_errors_volume_centre_inertia_bounds=errs,comparison='same placed assembly order after board split; source library aliases excluded'),ReSpeaker=dict(installed_bounds=bounds(sh('E19_ReSpeakerSource')),source_solids=len(sh('E19_ReSpeakerSource').Solids),side_surface=103)))
pairnames={'yaw':'D19D_YawMatedPair','pitch':'BR_FLANK_HP_PAIR','tail':'B19_TailMatedPair'}
for k,old in [('yaw',[-49,-46,115]),('pitch',[-60,-24,160]),('tail',[145,-89,66.2])]:
    transform([pairnames[k]],old,lay['pairs'][k]['inlet'],180)
sb=sh('Speaker').BoundBox
transform(['Speaker'],[0,0,0],[8,78,0],0)
for n in group('E19_FieldMG','E19_FieldJR','E19_FieldDATA')+['B19_TailLaps','B19_TailJRUnderBank','BR_FLANK_THREE_LAPS']:
    hide(n)
def tube(q,pts,r):
    coords=pts[::3]+([pts[-1]] if (len(pts)-1)%3 else [])
    segs=[]
    for a,b in zip(coords,coords[1:]):
        delta=V(*b)-V(*a)
        if delta.Length>.0001:segs.append(Part.makeCylinder(r,delta.Length,V(*a),delta))
    return Part.makeCompound(segs)
for key,q in list(lay['fixed'].items())+[('JR_pitch',next(v for v in lay['pitch_transfer'] if v['yaw']==0))]:
    geo=tube(key,q['points'],3.4 if key=='DATA500' else 1.98)
    paths=[geo]
    for b in q.get('branches',[]):
        v=V(*b[-1])-V(*b[0]);paths.append(Part.makeCylinder(.9,v.Length,V(*b[0]),v))
    add('F19_Field_'+key,Part.makeCompound(paths),(.95,.57,.17) if key.startswith('MG') else (.35,.65,.88),'neutral occupied lay reference; see separate per-unit sections and allocated flexible lengths')
fore=sh('E19_ForeLid').cut(box(-90,-32.1,150,34.4,17,21.4))
rear=sh('E19_RearLid')
for x in [sb.XMin+2,sb.XMax-8]:
    for sg,y in [(-1,sb.YMin),(1,sb.YMax)]:
        rear=rear.cut(box(x-.1,y-1.7,148.8,6.2,3.45,22.6))
        x2=x+8;y2=y+78
        rear=rear.fuse(box(x2,y2-1.55 if sg<0 else y2+.17,sb.ZMin-1.45,6,1.38,173-sb.ZMin)).fuse(box(x2,y2-1.55 if sg<0 else y2-1.2,sb.ZMin-1.45,6,2.75,1.35))
# Through tool access: original complete CSK seats with lateral roots and a driver hole below.
for n in group('CB_BUS_'):
    if not n.endswith('PCBwasher'):continue
    b=sh(n).BoundBox;x=b.Center.x;y=b.Center.y;z=b.ZMin-1.6
    pad=cyl(x,y,z-6,3.8,6).cut(cyl(x,y,z-6.1,1.12,6.3)).cut(Part.makeCone(2.14,1.12,1.02,V(x,y,z-6.02)))
    rear=rear.fuse(pad.fuse(box(x+2.4,y-.9,172,2.2,1.8,z-173.7))).cut(cyl(x,y,171,2.48,3))
# Old roof is the new open service tray. Cut ports for the actual vertical approaches.
for key,q in lay['fixed'].items():
    pts=[v for v in q['points'] if 167<v[2]<178]
    if not pts:continue
    lo=[min(p[i] for p in pts)-4.4 for i in [0,1]];hi=[max(p[i] for p in pts)+4.4 for i in [0,1]]
    slot=box(*lo,170.4,hi[0]-lo[0],hi[1]-lo[1],3.5)
    rear=rear.cut(slot);fore=fore.cut(slot)
for x in [50,65,80,95,110,125]:
    rear=rear.cut(box(x,64,170.9,3,23,3.6))
def saddle(n):
    b=sh(pairnames[n]).BoundBox;pieces=[]
    for x in [b.XMin+3,b.XMax-7]:
        pieces.append(box(x,b.YMin-1.6,b.ZMin-1.55,4,17.2,1.55))
        for sg,y in [(-1,b.YMin-1.6),(1,b.YMax+.2)]:
            pieces.append(box(x,y,b.ZMin-1.55,4,1.4,4.5))
        if n!='pitch':pieces.append(box(x,b.YMin-1.6,172.4,4,2.4,b.ZMin-172.5))
    return pieces
fore=fore.multiFuse(saddle('yaw'));rear=rear.multiFuse(saddle('tail'))
hood=sh('E19_UpperYawCover')
# A yaw-carried external cheek keeps factory stock, the whole pair and attachment together.
outer=box(-153,-94.2,125.8,64,1.6,59.3)
outer=outer.fuse(box(-135,-93.1,183.4,24,38,1.7))
for w in saddle('pitch'):outer=outer.fuse(w)
for xx in [-109.83315,-89.83315]:
    outer=outer.fuse(box(xx,-93.6,125.8,4,19.5,1.15))
hood=hood.cut(box(-165,-94,128,83,33,55.3)).fuse(outer)
for key,lid,x0,x1 in [('Fore',fore,-63.5,19.85),('Rear',rear,20.15,209)]:
    cap=box(x0,-103,199.5,x1-x0,206,1.5)
    pieces=[cap]
    for y in [-103,101.5]:pieces.append(box(x0,y,173,x1-x0,1.5,27))
    if key=='Rear':pieces.append(box(x1-1.5,-102,173,1.5,204,27))
    if key=='Fore':
        pieces.append(box(x0,-103,173,1.5,206,27))
    cap=join(pieces)
    if key=='Rear':cap=cap.cut(box(143,-3,172,68,27,31))
    else:cap=cap.cut(box(x0-1,-100,172,3,107,18))
    # Open vent banks, audio perforations and mic duct communicate with atmosphere.
    for x in ([-47,-39,-31,-23] if key=='Fore' else [53,63,73,83,93,103,113,123]):
        cap=cap.cut(box(x,29 if key=='Fore' else 62,198.9,2.8,58 if key=='Fore' else 29,3))
    for x in [x0+8,x1-14]:
        for sg in [-1,1]:
            y=-100.8 if sg<0 else 98.75
            lid=lid.cut(box(x-.25,y-.25,170.7,6.5,2.65,3.2))
            cap=cap.fuse(box(x,min(y,-102) if sg<0 else y,173.05,6,3.5,2.2)).fuse(box(x,y,169.3,6,1.9,5.8))
            cap=cap.fuse(box(x,y-.5 if sg<0 else y+.55,169.35,6,1.9,1.25))
    D.getObject('E19_'+key+'Lid').Shape=lid.removeSplitter()
    add('F19_'+key+'Cap',cap.removeSplitter(),(.24,.34,.36),'removable gallery cover with four locating snap tongues into lower service lid')
D.E19_UpperYawCover.Shape=hood.removeSplitter()
changed=['E19_UpperYawCover','E19_ForeLid','E19_RearLid','F19_ForeCap','F19_RearCap']
wr('new-members.json',{n:dict(valid=sh(n).isValid(),members=[dict(mm3=v.Volume,bounds=bounds(v)) for v in sh(n).Solids]) for n in changed})
D.recompute();D.save()
view=(E/'views.py').read_text();view=view[view.index('v=G.activeDocument'):].replace("skins+=['E19_BatteryDoor']","skins+=['E19_BatteryDoor','F19_ForeCap','F19_RearCap'];air+=group('F19_Field');air=[n for n in air if not n.startswith(('E19_FieldMG','E19_FieldJR','E19_FieldDATA')) and n not in ['B19_TailJRUnderBank','B19_TailLaps']]")
exec(view)
