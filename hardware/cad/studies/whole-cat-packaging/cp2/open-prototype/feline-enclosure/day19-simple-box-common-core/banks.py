"""Finish the operator wall, fit removable lever banks and seat the supplier BUS PCB."""
from pathlib import Path
P=Path(__file__).parent
exec((P/'core.py').read_text().split('# Each board/power cluster')[0])
cat=next(q/'electronics/full-cat/pi-bus-primary-r1' for q in P.parents if (q/'electronics/full-cat/pi-bus-primary-r1').is_dir())
tr=A.Placement(V(66,46,132.6),A.Rotation(V(0,0,1),90))
def source(n):
    s=Part.Shape();s.read(str(cat/(n+'.brep')));s.Placement=tr.multiply(s.Placement);return s
# Take only the placed final assembly. Source file also contains the separate
# ECAD component library, which must not be populated again at its local origin.
allbus=source('PCB');board=sh('E19_BUS_PCB')
boardMatches=[k for k,s in enumerate(allbus.Solids) if all(abs(a-b)<.01 for a,b in zip(bounds(s),bounds(board)))]
assert len(boardMatches)==1,(len(allbus.Solids),boardMatches)
D.E19_BUS_population.Shape=Part.makeCompound([s for k,s in enumerate(allbus.Solids) if k!=boardMatches[0]])
wr('installed-bus.json',dict(final_source='PCB.brep',placed_solids=len(allbus.Solids),board_index=boardMatches[0],full_bounds=bounds(allbus),ports={n:bounds(source(n)) for n in ['Type_C1','DC1','H1','H2','H3','H4','H5']},prior_library_listing_superseded=True))
# Provide 1 mm recess around the S0 key shoulder; retain the seating plane at y99.
# The rear cover latch slots pass the full thickness of the undercut including the lead-in.
for key,xx in [('Fore',[-53,8]),('Rear',[31,193])]:
    base=D.getObject('E19_'+key+'Base');s=base.Shape
    for x in xx:
        for sg in [-1,1]:
            s=s.cut(box(x-.28,100.65 if sg==1 else -103.5,136.9,8.56,2.85,6.32))
    if key=='Rear':s=s.cut(box(160,101.95,86,38,3,37))
    if key=='Fore':
        # Trim only the underside closure skin at the frame. All eight anchor
        # paths and original jaw/driver bores belong to the anchored base.
        ns=sh('E19_FrontShroud').cut(s)
        D.E19_FrontShroud.Shape=ns.removeSplitter()
    base.Shape=s.removeSplitter()
# For each of four removable banks, two or more square pegs enter slotted
# sockets on the fixed floor, outside the fuse cases. Install after the fuses.
# 15 existing WAGO 415 plus the distinct lower PBAY_P_AUX remain physical units.
names=sorted(n for n in group('WAGO415_') if n!='WAGO415_data_1_0')
maps={};additions={'Fore':[],'Rear':[]}
for side,ids in [('Neg',names[:8]),('Pos',names[8:])]:
    sg=-1 if side=='Neg' else 1
    for j,sub in enumerate([ids[:4],ids[4:]]):
        key='Fore' if j==0 else 'Rear'
        bs=[sh(n).BoundBox for n in sub];x0=min(b.XMin for b in bs)-1.1;x1=max(b.XMax for b in bs)+1.1
        y0=bs[0].YMin;y1=bs[0].YMax
        yp=-98 if sg<0 else 95;parts=[];sockets=[]
        # Continuous backbone behind the terminal bodies leaves all mouths and top levers accessible.
        parts+=[rect(x0,x1,y0-1.25,y0+.8,111.3,3),rect(x0,x1,y1-.8,y1+1.25,111.3,3)]
        for b in bs:
            for x in [b.XMin+2.2,b.XMax-5.2]:
                parts.append(rect(x,x+3,y0-1.25,y1+1.25,111.4,2.6))
            # End cheeks with compliant overhang, located at two housing corners;
            # wider faces and lever sweep stay open. Fit to the purchased housing.
            for a,sign in [(b.XMin,-1),(b.XMax,1)]:
                u=a-1.15 if sign<0 else a+.15
                parts.append(box(u,y0+2,112.5,1,4,10.9))
                parts.append(box(a-1.15 if sign<0 else a-.5,y0+2,123.18,1.65,4,.8))
        for x in [x0+5,x1-9]:
            parts.append(box(x,min(yp,y0 if sg<0 else y1),111.3,4,max(abs(yp-(y0 if sg<0 else y1)),1)+1.1,3))
            parts.append(box(x,yp-.65,103.7,4,2.9,8.5))
            shaft=box(x-2,yp-2.5,41,8,6.8,70.3)
            shaft=shaft.cut(box(x-.24,yp-.88,103.4,4.48,3.36,9))
            sockets.append(shaft)
        rack=join(parts);n='E19_Wago'+key+side
        add(n,rack,(.27,.49,.46),'removable bank on two keyed posts, push-capture at housing corners');maps[n]=sub
        additions[key]+=sockets
# Shared open BUS bridge. Four countersunk screw seats start at z125, PCB underside z131.
# Install the four full steel sets before the soldered-deck wiring and BUS mating boots.
bp=[]
for x in [35.5,63.5]:
    for y in [48.5,85.5]:
        seat=cyl(x,y,125,3.8,6).cut(cyl(x,y,124.9,1.12,6.3)).cut(Part.makeCone(2.14,1.12,1.02,V(x,y,124.98)))
        bp.append(seat)
for y in [48.5,85.5]:bp.append(box(35.6,y+1.35,125.4,28,1.8,2.8))
for x in [36.9,64.8]:bp.append(box(x,50,125.4,1.7,37,2.8))
# Two outside posts bypass the WAGO springs and the 220/MTA open lane.
for x in [38.3,62.6]:
    bp.append(box(x,86,125.4,3.2,13.4,2.8))
    bp.append(box(x,96,41.2,3.2,3.6,86))
additions['Rear']+=bp
for key,pieces in additions.items():
    o=D.getObject('E19_'+key+'Base');o.Shape=join([o.Shape]+pieces)
wr('bank-bearing.json',dict(banks=maps,source_bus='4 CSK screws, nuts, PCB washers',modules={n:dict(solids=len(sh(n).Solids),valid=sh(n).isValid(),bounds=bounds(sh(n))) for n in list(maps)+['E19_ForeBase','E19_RearBase','E19_FrontShroud']}))
D.recompute();D.save()
