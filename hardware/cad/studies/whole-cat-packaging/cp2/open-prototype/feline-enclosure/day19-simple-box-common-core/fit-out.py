"""Install keyed stations, fill the service deck and show connected regions."""
from pathlib import Path
P=Path(__file__).parent
exec((P/'core.py').read_text().split('# Each board/power cluster')[0])
layout=json.loads((P/'installed-looms.json').read_bytes());registry={}
# Restore continuous material between each translated microphone boss and the
# underside of its cover, including where the original roof vents were crossed.
lid=D.E19_ForeLid.Shape
before=[dict(V=s.Volume,box=bounds(s)) for s in lid.Solids]
for n in group('HB_MIC_'):
    if not n.endswith('headwasher'):continue
    b=sh(n).BoundBox;x=b.Center.x;y=b.Center.y
    lid=lid.fuse(box(x+3.9,y-2,169.8,4.3,4,2.25))
D.E19_ForeLid.Shape=lid.removeSplitter()
# Whole pitch mate above side fuse layer. Rib and two independent bearing lips
# are part of the lift-off front shroud. Mate and all three insulated laps remain separate.
move('BR_FLANK_HP_PAIR',[],[-90,-31,155])
o=D.E19_FrontShroud;s=o.Shape
for x in [-87,-68]:
    bed=box(x,-33,152.2,4.5,18,2.8)
    for y in [-33.5,-16.9]:bed=bed.fuse(box(x,y,152.5,4.5,1.3,6.2))
    # Link the two keyed seats to the stationary shroud, along the outside
    # of the electronics bay, with the positive Y body transfer left open.
    arm=box(x,-101,151.8,4.5,70,2.9)
    s=s.fuse(arm).fuse(bed)
o.Shape=s.removeSplitter()
# Separate axial-fuse landing next to P_REAR. Full sleeve and both leads are
# fitted openly, without entering a narrowed printed tube.
base=D.E19_ForeBase.Shape
cradle=box(-41,-48,58.4,17,13,2.5)
for x in [-38.5,-29.5]:cradle=cradle.cut(box(x,-46.5,58.3,2.8,9,2.9))
cradle=cradle.fuse(box(-40.7,-47.6,41.2,2.8,2.7,18.5))
D.E19_ForeBase.Shape=base.fuse(cradle).removeSplitter()
f=add('E19_FieldAxialFuse',box(-37,-47,61,8,10,7),(.83,.61,.22),'F_PWM sleeved pigtail source planning volume; axial fuse body, leads, strain relief pending dry fit');f.ViewObject.Visibility=False
# S0 body, captive rings and key enter before top deck. The two fixed U-shaped
# cradles take the body torque directly into the side panel.
sb=sh('S0_body').BoundBox;rear=D.E19_RearBase.Shape
for x in [sb.XMin+1.8,sb.XMax-5.2]:
    rear=rear.fuse(box(x,sb.YMin-1.1,sb.ZMin-3.1,3.4,43.2,3.1))
    rear=rear.fuse(box(x,sb.YMin-1.3,sb.ZMin-2.5,3.4,1.1,10.5))
rear=rear.fuse(box(sb.XMin-1.3,95.5,sb.ZMin-2.7,60,6,2.7))
for x in [sb.XMin-1.3,sb.XMax+.15]:rear=rear.fuse(box(x,96,sb.ZMin-2,1.15,6,17))
D.E19_RearBase.Shape=rear.removeSplitter()
# Actual midsection at the closed cover of each MTA0300330 determines the clip
# spacing. Both full TE ends stay outside the ribs. The banks continue to seat on
# their original z77 slats, with independent transverse clips.
mta=[];ribs={'Fore':[],'Rear':[]}
for n in group('Motor_ATO'):
    q=sh(n);b=q.BoundBox;x=b.Center.x
    sect=q.common(box(x-1.4,b.YMin-1,76.5,2.8,b.YLength+2,b.ZLength+2))
    bb=sect.BoundBox;y0=bb.YMin;y1=bb.YMax;top=bb.ZMax
    k='Fore' if x<20 else 'Rear'
    # Attach with a cross rung at the bottom of the unit. A leg clears the
    # case and leaves a 0.25 mm planned flexible gap; roof-overhang 0.65 each.
    rib=box(x-1.55,b.YMin-1.7,74.15,3.1,b.YLength+3.4,2.85)
    for yy in [y0-1.48,y1+.25]:
        rib=rib.fuse(box(x-1.5,yy,76.1,3,1.23,top-75.5))
    rib=rib.fuse(box(x-1.45,y0-1.48,top+.16,2.9,2.13,.92)).fuse(box(x-1.45,y1-.65,top+.16,2.9,2.13,.92))
    ribs[k].append(rib)
    mta.append(dict(unit=n,x=x,body_section=bounds(sect),rung=bounds(rib),key=k))
for k,rr in ribs.items():
    o=D.getObject('E19_'+k+'Base');o.Shape=join([o.Shape]+rr)
def field(name,pts,r,desc):
    # Sectional display of a connected allowance; neighboring segments meet at each station.
    vs=[V(*p) for p in pts];ss=[]
    for a,b in zip(vs,vs[1:]):
        d=b-a
        if d.Length>.001:ss.append(Part.makeCylinder(r,d.Length,a,d))
    o=add('E19_Field'+name,Part.makeCompound(ss),(.92,.55,.19),desc);o.ViewObject.Transparency=42;o.ViewObject.Visibility=False
    registry[name]=dict(first=list(vs[0]),last=list(vs[-1]),allowance_radius=r,role=desc)
for q in layout['rows']:
    if q.get('yaw',0)!=0:continue
    pp=q['centreline'];keep=pp[::3]+[pp[-1]]
    field(q['unit'],keep,3.4 if q['unit']=='DATA500' else 1.98,'unit capacity and indicative neutral lay; exact points and stock in installed-looms.json')
    if q['unit'].startswith('JR300'):
        v=V(*pp[-1])
        for j,target in enumerate(q['nets']):
            angle=.125*(j-1);d=V(math.cos(angle),math.sin(angle),0)
            field(q['unit']+'Fan'+str(j),[list(v),list(v+25*d),list(v+34*d),list(v+42*d)],1.05,'25 fan + 9 insulated + 8 lap to '+target+'; sleeve covers same wire')
for q in layout['E2']:field(q['wire'].replace('.',''),q['region_spine'],1.25,'one separate E2 contact wire and access; endpoint engagement and stock slack unmeasured')
for i,q in enumerate(layout['side_groups']):field('Body'+str(i),q['spine'],[3,3.7,4.8,1.9][i],q['name']+' project open group region to dry fit')
wr('installed-ports.json',dict(moves=moves,old_mic_cap_pieces=before,installed_clip_sections=mta,fields=registry,parts={n:dict(valid=sh(n).isValid(),solids=[dict(V=s.Volume,box=bounds(s)) for s in sh(n).Solids]) for n in ['E19_ForeBase','E19_RearBase','E19_FrontShroud','E19_ForeLid','E19_RearLid']}))
D.recompute();D.save()
