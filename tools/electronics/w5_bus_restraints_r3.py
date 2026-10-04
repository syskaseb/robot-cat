"""Canonical shared BUS restraints: retain P0 support and all bought parts.

One existing W061 band now grips both G2 insulation seats using its retained
left slot and ONE new right slot. Three new ties, not four. D head faces west;
middle G seat atX98 is beyond the complete selected W050 loop XMax93.683.
All strap shapes are nominal tightened design envelopes, not material tests.
"""
def supports(sx):
    return [('Plug',[sx-5.5,26.5,84,sx+5.5,30.3,110]),
            ('Dend',[-12.5,27.5,108.8,-8.5,30,114]),
            ('Gend',[115,9.75,108.8,119,12.25,114]),
            ('Gmiddle',[95,59,105,101,63,113])]

def removed_owners():
    return ['CandidateDeck']+[f'W061_tie/G2_end/{i}' for i in range(4)]

def restraints(A,Part,sx):
    def box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    def xz_polygon(points,y,width):
        vs=[A.Vector(x,y,z) for x,z in points]
        return Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(A.Vector(0,width,0))
    def bands(x,y,top,half=3):
        return [box([x+v-.6,y-1.25,103.8,x+v+.6,y+1.25,top+1.2]) for v in (-half,half)]+[
            box([x-half-.6,y-1.25,top,x+half+.6,y+1.25,top+1.2]),
            box([x-half-.6,y-1.25,103.8,x+half+.6,y+1.25,105]),
            box([x+half-1,y-2.5,100.1,x+half+5,y+2.5,104.1])]
    out={}
    d=bands(-10.5,28.75,114.5)
    d[-1]=box([-18.5,26.25,100.1,-12.5,31.25,104.1])
    for i,s in enumerate(d):out['D/'+str(i)]=s
    for i,s in enumerate(bands(61,-98,108.1)):
        s.rotate(A.Vector(),A.Vector(0,0,1),90);out['Gmid/'+str(i)]=s
    for i,b in enumerate([[sx-6.1,25.3,84.5,sx-4.9,32,87],
                           [sx+4.9,25.3,84.5,sx+6.1,32,87],
                           [sx-6.1,25.3,84.5,sx+6.1,26.5,87],
                           [sx-6.1,31.5,84.5,sx+6.1,32.7,87],
                           [sx+5.5,26,83,sx+11.5,31,87]]):out['Plug/'+str(i)]=box(b)
    out['G2shared/left']=box([104.9,9.75,103.8,106.1,12.25,116.9])
    out['G2shared/right']=box([119.6,9.75,103.8,120.8,12.25,115.7])
    out['G2shared/bottom']=box([104.9,9.75,103.8,120.8,12.25,105])
    out['G2shared/top']=xz_polygon([(104.9,115.7),(113.1,115.7),(115.5,114.5),
        (120.8,114.5),(120.8,115.7),(115.5,115.7),(113.1,116.9),(104.9,116.9)],9.75,2.5)
    return out
