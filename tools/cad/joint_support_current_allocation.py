"""Transverse XZ case retention, outside the shaft and child connector.

Rejected YZ wraps encircled the child WConnector. Use actual three-part Hip
case section at absY32 and central low saddle joined to retained upper cuff.
No factory screw or unknown thread assumed. Head/fit remain provisional.
"""
import json,zipfile
import FreeCAD as A
import Part
import check_low_hip_loom_layout as P

original_allocate=P.allocate


def allocate(rows,targets,with_recipe=False):
    # Check the changed rear family first, but keep ALL108 final cases.
    order={'RearLeft':0,'RearRight':1,'FrontLeft':2,'FrontRight':3}
    rows.sort(key=lambda r:order[r['physical_leg']])
    result=original_allocate(rows,targets,True);shapes=result[0]
    with zipfile.ZipFile(P.ROOT/'hardware/simulation/v35/inputs.zip') as z:
        members=json.loads(z.read('geometry.json'))['components']
    for leg in ('FrontLeft','FrontRight','RearLeft','RearRight'):
        row=next(r for r in rows if r['physical_leg']==leg)
        rear=leg.startswith('Rear');side=row['side']
        mx=row['moving_anchor_rest_world_mm'][0]
        def box(x,y,z,X,Y,Z):
            y,Y=sorted((side*y,side*Y));return P.box([x,y,z,X,Y,Z])
        def bound(x,y,z,X,Y,Z):
            y,Y=sorted((side*y,side*Y));return [x,y,z,X,Y,Z]
        # Between shaftY16 and child connectorY38.7. Slice each valid casing
        # separately; overlapping source compounds are not Boolean operands.
        casing=[m for m in members if m['stage']=='Motion_'+row['cad_code']+'_Hip'
                and m['label'].startswith(('ZK_','SG-ZIJI_','XG-ZIJI_'))]
        assert len(casing)==3,(leg,casing)
        slab=box(mx-30,30.6,-10,mx+30,33.4,50)
        sections=[targets['P0_'+m['name']].common(slab) for m in casing]
        assert all(s.isValid() and s.Volume>0 for s in sections)
        bb=Part.makeCompound(sections).BoundBox
        x0,x1=bb.XMin-.3,bb.XMax+.3
        z0=bb.ZMin-.3;z1=31.6;thick=1.4
        assert bb.ZMax+.3<29.75,(leg,'Saddle intersects actual Hip case')
        ring=box(x0-thick,30.6,z0-thick,x1+thick,33.4,z1+thick).cut(
             box(x0,30.4,z0,x1,33.6,z1))
        idle=x1+thick if rear else x0-thick
        head=box(idle if rear else idle-6,28,20,idle+6 if rear else idle,36,28)
        shapes[leg+'CaseBand']=ring.fuse(head).removeSplitter()
        assert shapes[leg+'CaseBand'].isValid() and len(shapes[leg+'CaseBand'].Solids)==1
        recipe=result[3][leg+'MovingCuff']
        old_bx=mx-16.5
        old=bound(old_bx-1.4,3.029,36.5,old_bx+1.4,60.931442,37.9)
        recipe['notches']=[b for b in recipe['notches'] if b!=old]
        recipe['pads'] += [
            dict(bounds_mm=bound(mx-4,15,32.2,mx+4,35.5,36.2),length_expression='CrownParameters.Thickness'),
            dict(bounds_mm=bound(mx-4,28.5,29.75,mx+4,35.5,36.2),length_expression='2.45 mm + CrownParameters.Thickness')]
        uncut=P.fuse([P.box(p['bounds_mm']) for p in recipe['pads']])
        passages=[bound(x0-thick,30.6,z1,x1+thick,33.4,z1+thick),
                  bound(x0-thick,30.6,z0-thick,x1+thick,33.4,z0),
                  bound(x0-thick,30.6,z0,x0,33.4,z1),
                  bound(x1,30.6,z0,x1+thick,33.4,z1)]
        for b in passages:
            if b not in recipe['notches'] and uncut.common(P.box(b)).Volume>1e-7:
                recipe['notches'].append(b)
        cuff=uncut
        for b in recipe['notches']:cuff=cuff.cut(P.box(b))
        shapes[leg+'MovingCuff']=cuff.removeSplitter()
        assert shapes[leg+'MovingCuff'].isValid() and len(shapes[leg+'MovingCuff'].Solids)==1
    return result if with_recipe else result[:3]
