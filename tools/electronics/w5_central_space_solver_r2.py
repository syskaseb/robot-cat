"""Plan both facing orientations and require a complete150mm battery lead.

The source XT60 datum and outward-Y lead direction are retained. Six mm
straight insulation preparation is a prototype allowance, not a measured cap.
The first spatial solution alone was insufficient to select a factory lead.
"""
from pathlib import Path
from itertools import product
import math
import w5_central_space_solver as base
from w5_s1_source_layout_r2 import CentreLine
from w5_s1_source_layout_r1 import add,mul


def placements(targets):
    result=[];datum=base.ports()
    for x,y,z,gap,direction in product(range(-70,71,20),range(-65,116,20),(109,129,149),(70,90),(1,-1)):
        gx=x+direction*gap
        if gx+9.5>140 or gx-9.5 < -98:continue
        shift={'G1':[x-66,y-5.5,z-109],'G2':[gx-111,y-5.5,z-109]}
        points={}
        for w,end in base.ENDS.items():
            name=end.split('.')[0];p=list(datum[end]['point_mm'])
            if direction==-1:p[:2]=[2*(66 if name=='G1' else 111)-p[0],11-p[1]]
            points[w]=[v+d for v,d in zip(p,shift[name])]
        if math.dist(points['W001'],targets['W001'])+19>150:continue
        if math.dist(points['W003'],targets['W003'])+41>300:continue
        result.append(dict(g1_centre=[x,y],g2_centre=[gx,y],floor=z,shift=shift,direction=direction,
            lower_bound_cost_mm=sum(math.dist(points[w],targets[w]) for w in base.ENDS),bridge_mm=gap-20.5))
    return sorted(result,key=lambda p:(p['lower_bound_cost_mm'],p['floor'],p['g1_centre'],p['direction']))


source=Path(base.__file__).read_text(encoding='utf-8')
source=source.replace("edge=Part.makeLine(A.Vector(x+11,y,z+4.5),A.Vector(gx-9.5,y,z+4.5))",
    "edge=Part.makeLine(A.Vector(x+c['direction']*11,y,z+4.5),A.Vector(gx-c['direction']*9.5,y,z+4.5))")
source=source.replace("A.Vector(x+11,y,z+4.5),A.Vector(1,0,0)",
    "A.Vector(x+c['direction']*11,y,z+4.5),A.Vector(c['direction'],0,0)")
needle="                    moved=s.copy();moved.translate(A.Vector(*delta))\n                    q=json.loads(json.dumps(recipe))"
assert needle in source
source=source.replace(needle,'''                    moved=s.copy()
                    q=json.loads(json.dumps(recipe))
                    if c['direction']==-1:
                        cx=66 if ENDS[w].startswith('G1.') else 111
                        moved.rotate(A.Vector(cx,5.5,113.5),A.Vector(0,0,1),180)
                        for e in q['edges']:
                            for field in ('start','mid','end'):
                                if field in e:e[field][:2]=[2*cx-e[field][0],11-e[field][1]]
                        q['tip'][:2]=[2*cx-q['tip'][0],11-q['tip'][1]]
                        q['tangent'][:2]=[-q['tangent'][0],-q['tangent'][1]]
                    moved.translate(A.Vector(*delta))''')
needle="            solution=dict(placement=c,ends={w:q for w,(q,s) in chosen.items()},"
assert needle in source
source=source.replace(needle,'''            # Qualify the complete battery path BEFORE accepting a placement.
            from w5_ground_network_r1 import from_recipe
            from w5_rounded_path import corner_offsets
            from w5_s1_source_layout_r2 import CentreLine
            from w5_s1_source_layout_r1 import add,mul
            a=chosen['W001'][0];src=targets['W001'];dx=a['tip'][0]-src[0];dz=a['tip'][2]-src[2]
            mag=math.hypot(dx,dz)
            bline=CentreLine(src,[0,-1,0]);bline.line(add(bline.p,mul(bline.t,6)))
            bline.arc([dx/mag,0,dz/mag],radius=12.4);bline.line(add(bline.p,mul(bline.t,6)))
            b=dict(edges=bline.edges,tip=bline.p,tangent=bline.t)
            full=None;last_reasons=[]
            options_whole=[]
            for la,lb in product((4,6,9,12.4,18,25),(4,6,9,12.4,18,25)):
                points=[a['tip'],add(a['tip'],mul(a['tangent'],la)),add(b['tip'],mul(b['tangent'],lb)),b['tip']]
                try:corner_offsets(points,12.4)
                except AssertionError:continue
                options_whole.append((sum(math.dist(p,q) for p,q in zip(points,points[1:])),points))
            for _,points in sorted(options_whole,key=lambda r:r[0]):
                recipe_full=dict(wire='W001',a=a,b=b,middle=points,radius_mm=12.4)
                path,whole=from_recipe(A,Part,recipe_full)
                if path.Length+19>150:
                    last_reasons.append('nominal_above150mm');continue
                owner=hit(whole,{**fixed,**family,**{w:s for w,(q,s) in chosen.items() if w!='W001'}})
                if owner:last_reasons.append(owner);continue
                full=dict(recipe=recipe_full,body_mm=path.Length,nominal_mm=path.Length+19,
                    source_straight_prototype_mm=6,source_outward_axis=[0,-1,0])
                whole_shape=whole;whole_path=path;break
            if full is None:
                attempts.append(dict(placement=c,blocked='whole_W001_not_qualified',reasons=sorted(set(last_reasons))));continue
'''+needle)
source=source.replace("solution=dict(placement=c,ends=", "solution=dict(placement=c,whole_W001=full,ends=")
source=source.replace("            attempts.append(dict(placement=c,complete_family_departures_clear=True));break",
    "            solution_shapes.update(W001_FULL=whole_shape,W001_CENTERLINE=whole_path)\n            attempts.append(dict(placement=c,complete_family_departures_clear=True,complete_W001_nominal_mm=full['nominal_mm']));break")
source=source.replace("pins += [Path(__file__),RECEIVED", "pins += [Path(__file__),ROOT/'tools/electronics/w5_central_space_solver_r2.py',ROOT/'tools/electronics/w5_ground_network_r1.py',RECEIVED")
ctx=dict(__name__='central_space_r2_definition',__file__=base.__file__,product=product)
exec(compile(source,base.__file__,'exec'),ctx)
ctx['placements']=placements
ctx['OUT']=base.ROOT/'hardware/electronics/full-cat/w5-central-space-solver-r2'
if __name__=='__main__':ctx['main']()
