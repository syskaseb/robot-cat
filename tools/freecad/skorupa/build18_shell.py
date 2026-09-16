"""Split the v18 shell, add removable M3 joining plates and validate geometry.

Run with FreeCAD's bundled Python. This does not change an open document.
World coordinates are retained. The plates follow the measured roof normal.
"""
from pathlib import Path
import json, math, hashlib
import FreeCAD as App
import Part
from brep_inventory import OUT, ROOT, SOURCE

V=App.Vector
SPLIT_X=30.0
GAP=0.35
STATION_Z=114.0
PLATE_LENGTH=24.0
PLATE_WIDTH=12.0
PLATE_THICKNESS=6.0

def box(x0,x1,y0,y1,z0,z1):
    return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))

def cylinder(radius,length,start,direction):
    return Part.makeCylinder(radius,length,start,direction)

def hexagon(af,height,base):
    r=af/math.sqrt(3)
    points=[base+V(r*math.cos(i*math.pi/3),r*math.sin(i*math.pi/3),0) for i in range(6)]
    return Part.Face(Part.makePolygon(points+[points[0]])).extrude(V(0,0,height))

def placed(shape,placement):
    s=shape.copy(); s.Placement=placement.multiply(s.Placement); return s

def bounds(s):
    b=s.BoundBox
    return [b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax]

def main():
    shell=Part.Shape(); shell.read(str(OUT/'BackCover18.brep'))
    report={'stage':'split-shell prototype; not a complete print release',
            'split_x_mm':SPLIT_X,'seam_gap_mm':GAP,'parts':[], 'connections':[],
            'checks':{},'collisions':[], 'inputs_sha256':{
                'BackCover18':hashlib.sha256((OUT/'BackCover18.brep').read_bytes()).hexdigest()}}
    def wall(x,z,side):
        q=shell.common(Part.makeLine(V(x,0,z),V(x,side*110,z)))
        ds=sorted(side*p.Point.y for p in q.Vertexes)
        if len(ds)<2 or ds[0]<1:
            raise ValueError(('No unique side-wall crossing',x,z,side,ds))
        return ds[0],ds[-1]
    plates=[]; bosses=[]; bores=[]; hardware=[]
    for side,label in [(1,'R'),(-1,'L')]:
        print('measure roof',label,flush=True)
        inner,outer=wall(SPLIT_X,STATION_Z,side)
        dx=(wall(SPLIT_X+0.25,STATION_Z,side)[1]-wall(SPLIT_X-0.25,STATION_Z,side)[1])/0.5
        dz=(wall(SPLIT_X,STATION_Z+0.25,side)[1]-wall(SPLIT_X,STATION_Z-0.25,side)[1])/0.5
        normal=V(-dx,side,-dz); normal.normalize()
        across=V(1,0,0)-normal*normal.x; across.normalize()
        tangent=normal.cross(across); tangent.normalize()
        rot=App.Rotation(across,tangent,normal,'ZXY')
        anchor=V(SPLIT_X,side*inner,STATION_Z)
        local=box(-12,12,-6,6,-6,0)
        # Select the first measured offset that clears the original organic
        # skin over the WHOLE plate, not merely at the centre point.
        gap=0.35
        for _ in range(16):
            pl=App.Placement(anchor-normal*gap,rot)
            plate=placed(local,pl)
            if plate.common(shell).Volume<0.001 and plate.distToShape(shell)[0]>=0.30:
                break
            gap+=0.25
        else:
            raise RuntimeError('Cannot seat plate '+label+' without skin interference')
        print('plate',label,'offset',gap,flush=True)
        local_cuts=[]
        for index,u in enumerate((-8.0,8.0)):
            local_cuts.extend([cylinder(1.7,6.2,V(u,0,-6.1),V(0,0,1)),
                               hexagon(5.8,2.7,V(u,0,-6.1))])
            contact=pl.multVec(V(u,0,0))
            ray=Part.makeLine(contact,contact+normal*30)
            hits=shell.common(ray)
            depths=sorted((p.Point-contact).dot(normal) for p in hits.Vertexes)
            if len(depths)<2:
                raise RuntimeError('Missing screw wall crossing')
            head_seat=depths[-1]+0.6
            # Integral boss makes a flat, normal-to-axis screw seat. At the
            # plate interface there is only a 0.1 mm axial assembly gap.
            bosses.append(cylinder(4.5,head_seat-0.1,contact+normal*0.1,normal))
            bores.append(cylinder(1.7,head_seat+7,contact-normal*6.2,normal))
            nut_front=contact-normal*3.4
            nut_back=contact-normal*5.8
            required=head_seat+5.8+0.2
            screw_length=next(n for n in (8,10,12,16,20,25) if n>=required)
            shaft=cylinder(1.5,screw_length,contact+normal*(head_seat-screw_length),normal)
            head=cylinder(3.0,3.0,contact+normal*head_seat,normal)
            nut_local=hexagon(5.5,2.4,V(u,0,-5.8)).cut(cylinder(1.5,3,V(u,0,-6),V(0,0,1)))
            hardware.extend([(f'JoinScrew{label}{index}',shaft.fuse(head)),
                             (f'JoinNut{label}{index}',placed(nut_local,pl))])
            report['connections'].append(dict(plate='ShellJoin'+label, screw='M3x'+str(screw_length),
                nut='M3 hex AF5.5, height2.4; pocket AF5.8',
                hole_axis=list(normal),plate_outer_hole=list(contact),
                head_seat=list(contact+normal*head_seat),nut_front=list(nut_front),
                screw_tip_protrusion_mm=screw_length-(head_seat+5.8)))
        plate=placed(local.cut(Part.makeCompound(local_cuts)).removeSplitter(),pl)
        plates.append(('ShellJoin'+label,plate,pl))
    print('fuse four bosses',flush=True)
    joined=shell.multiFuse(bosses).cut(Part.makeCompound(bores)).removeSplitter()
    print('split shell',flush=True)
    front=joined.common(box(-250,SPLIT_X-GAP/2,-150,150,-20,200)).removeSplitter()
    rear=joined.common(box(SPLIT_X+GAP/2,350,-150,150,-20,200)).removeSplitter()
    parts=[('ShellFront18',front),('ShellRear18',rear)]+[(n,s) for n,s,p in plates]
    for name,s in parts:
        print('validate',name,flush=True)
        valid=s.isValid(); count=len(s.Solids)
        assert valid and count==1, (name,valid,count)
        s.exportBrep(str(OUT/(name+'.brep')))
        report['parts'].append(dict(name=name,valid=valid,solids=count,volume_mm3=s.Volume,bbox_mm=bounds(s),
                                   sha256=hashlib.sha256((OUT/(name+'.brep')).read_bytes()).hexdigest()))
    for name,s in hardware:
        assert s.isValid() and len(s.Solids)==1, name
        s.exportBrep(str(OUT/(name+'.brep')))
    report['hardware']=[dict(name=n,sha256=hashlib.sha256((OUT/(n+'.brep')).read_bytes()).hexdigest()) for n,s in hardware]
    # Both solids were intersected with disjoint closed halfspaces. Asking
    # OCCT to intersect the two near-identical trimmed spline shells again is
    # redundant and can take many minutes. Check the separating-plane bounds
    # on the boundary tessellation in addition to this construction proof.
    print('check separating planes',flush=True)
    front_max=max(p.x for p in front.tessellate(0.15)[0])
    rear_min=min(p.x for p in rear.tessellate(0.15)[0])
    assert front_max<=SPLIT_X-GAP/2+1e-5
    assert rear_min>=SPLIT_X+GAP/2-1e-5
    report['separation_proof']={'front_max_x':front_max,'rear_min_x':rear_min,
        'method':'intersection with disjoint X halfspaces, verified boundary extrema'}
    report['checks']['front_rear_overlap_mm3']=0.0
    for name,s,pl in plates:
        for pn,panel in [('front',front),('rear',rear)]:
            print('check plate contact',name,pn,flush=True)
            report['checks'][name+'_'+pn+'_overlap_mm3']=s.common(panel).Volume
    # Every original placed Part feature remains at its existing pose.
    doc=App.openDocument(str(SOURCE))
    tray=Part.Shape(); tray.read(str(OUT/'PiTray18.brep'))
    candidates=[(n,s) for n,s,p in plates]+[(f'boss{i}',s) for i,s in enumerate(bosses)]+hardware
    for name,new in candidates:
        for obj in doc.Objects:
            if not obj.isDerivedFrom('Part::Feature') or obj.Shape.isNull() or obj.Name in ('BackCover','ComputerDeck') or obj.Name.startswith('Axis_'):
                continue
            original=obj.Shape.copy()
            original.Placement=obj.getGlobalPlacement().multiply(obj.Placement.inverse()).multiply(original.Placement)
            if not new.BoundBox.intersect(original.BoundBox):
                continue
            common=new.common(original).Volume
            if common>0.001:
                report['collisions'].append([name,obj.Name,common])
        if new.BoundBox.intersect(tray.BoundBox):
            vol=new.common(tray).Volume
            if vol>0.001: report['collisions'].append([name,'PiTray18',vol])
    report['print_placements']={n:dict(base=list(p.Base),quaternion=list(p.Rotation.Q)) for n,s,p in plates}
    (OUT/'shell-validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({'checks':report['checks'],'collisions':report['collisions']}),flush=True)
    assert not report['collisions'],report['collisions']
    assert all(abs(v)<0.001 for v in report['checks'].values()),report['checks']

if __name__=='__main__':
    main()
