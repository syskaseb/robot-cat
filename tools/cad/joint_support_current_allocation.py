"""Prototype-only bonded case cap, with independent jacket restraints.

Neither YZ nor XZ bands fit between retained chassis and child connector.
Keep the qualified cuff load path and use one exposed gap-filled bond to
actual casing surface. This is NOT WAGO glue masquerading as wire relief:
six separate jacket bands still restrain insulation per leg. Adhesive choice,
PETG/case adhesion, peel, load and creep remain explicit physical gates.
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
        casing=[m for m in members if m['stage']=='Motion_'+row['cad_code']+'_Hip'
                and m['label'].startswith(('ZK_','SG-ZIJI_','XG-ZIJI_'))]
        assert len(casing)==3,(leg,casing)
        # Restrict the bond to main housing, not a casing seam, shaft, vent,
        # connector, source screw or PCB. Rays confirm exposed top contact.
        housing=next(m for m in casing if m['label'].startswith('ZK_'))
        target=targets['P0_'+housing['name']]
        cb=target.BoundBox;cx=(cb.XMin+cb.XMax)/2
        bond=box(cx-4,8.75,30,cx+4,15,32.2)
        for m in casing:bond=bond.cut(targets['P0_'+m['name']])
        bond=bond.removeSplitter()
        assert bond.isValid() and len(bond.Solids)==1,(leg,'Ambiguous bond volume')
        assert bond.common(target).Volume<1e-6
        # Ensure the bottom is actual casing, not an unfilled floating gap.
        for xx in (cx-3.9,cx+3.9):
            for yy in (8.85,14.9):
                ray=Part.makeLine(A.Vector(xx,side*yy,29),A.Vector(xx,side*yy,32.2))
                hits=target.common(ray);assert hits.Vertexes,(leg,'No underlying case')
                top=max(v.Point.z for v in hits.Vertexes)
                assert 30<top<32.1,(leg,'Bond gap outside exposed top allocation',top)
        shapes[leg+'CaseShim']=bond
        shapes.pop(leg+'CaseBand');result[1].pop(leg+'CaseBand');result[2].pop(leg+'CaseBand')
        recipe=result[3][leg+'MovingCuff']
        old_bx=mx-16.5
        old=bound(old_bx-1.4,3.029,36.5,old_bx+1.4,60.931442,37.9)
        recipe['notches']=[b for b in recipe['notches'] if b!=old]
        if rear:
            # Actual inverse-motion witness atHip-15 reachesZ32.3493670273,
            # the exact mirror of the inherited frontHip+15 witness. Relieve
            # only the lower root corner, retaining cap/bond and all routes.
            root=recipe['pads'][1];root['bounds_mm'][2]=32.3493670273126+.5
            root['length_expression']='3.1506329726874 mm + CrownParameters.Thickness'
        uncut=P.fuse([P.box(p['bounds_mm']) for p in recipe['pads']])
        cuff=uncut
        for b in recipe['notches']:cuff=cuff.cut(P.box(b))
        shapes[leg+'MovingCuff']=cuff.removeSplitter()
        assert shapes[leg+'MovingCuff'].isValid() and len(shapes[leg+'MovingCuff'].Solids)==1
    return result if with_recipe else result[:3]
