"""Whole fixed local link allocation, not selected E1 or flexible-cable routing.

Use a documented fine prototyping wire candidate rather than assuming a
resistor offcut is long enough for a diagonal jumper. Three underside planes
are assigned together. The seven-ground bus solders directly to annuli, NOT
seven fabricated tines or two conductors forced through one hole.
"""
import json, math, time, heapq
from pathlib import Path
import FreeCAD as A
import Part
from plan_current_main_sources import ROOT, OUT, SHA


def xyz(v): return list(v)


def allocate(a,b,posts,used,boxes=(),circles=()):
    """Plan around ALL assigned vertical pad columns before forming any link."""
    step=1.27
    a=tuple(round(v/step) for v in a);b=tuple(round(v/step) for v in b)
    def point(q):return [q[0]*step,q[1]*step]
    def allowed(q):
        if not(-16<=q[0]<=16 and -19<=q[1]<=19):return False
        xy=point(q)
        if any(lo[0]-.45<=xy[0]<=hi[0]+.45 and lo[1]-.45<=xy[1]<=hi[1]+.45 for lo,hi in boxes):return False
        if any(math.dist(xy,c)<r+.45 for c,r in circles):return False
        return not any(math.dist(xy,p)<.95 for p in posts if math.dist(p,point(a))>.01 and math.dist(p,point(b))>.01) and (q not in used or q in (a,b))
    queue=[(0,0,a,None)];best={a:0};prev={};end=None
    while queue:
        _,cost,q,direction=heapq.heappop(queue)
        if cost>best[q]+1e-8:continue
        if q==b:end=q;break
        for d in ((1,0),(-1,0),(0,1),(0,-1)):
            v=q[0]+d[0],q[1]+d[1]
            if not allowed(v):continue
            c=cost+1+(.15 if direction and direction!=d else 0)
            if c<best.get(v,1e9):
                best[v]=c;prev[v]=q
                heapq.heappush(queue,(c+abs(v[0]-b[0])+abs(v[1]-b[1]),c,v,d))
    assert end is not None,('No whole allocated corridor',a,b)
    grid=[end]
    while grid[-1]!=a:grid.append(prev[grid[-1]])
    grid.reverse()
    # Keep a one-grid-step separation from a same-plane prior route.
    for x,y in grid:
        used.update((x+dx,y+dy) for dx,dy in ((0,0),(1,0),(-1,0),(0,1),(0,-1)))
    corners=[grid[0]]
    for i in range(1,len(grid)-1):
        if (grid[i][0]-grid[i-1][0],grid[i][1]-grid[i-1][1])!=(grid[i+1][0]-grid[i][0],grid[i+1][1]-grid[i][1]):corners.append(grid[i])
    corners.append(grid[-1]);return [point(q) for q in corners]


def path(a,b,z,via=None):
    a=A.Vector(*a);b=A.Vector(*b);u=A.Vector(b.x-a.x,b.y-a.y,0);length=u.Length;u.normalize()
    r=.5;up=A.Vector(0,0,1)
    assert length>2*r and min(abs(a.z-z),abs(b.z-z))>r
    if z>min(a.z,b.z) and not via:
        via=[[a.x,b.y]] if abs(a.x-b.x)>.01 and abs(a.y-b.y)>.01 else []
    if via or z>min(a.z,b.z):
        vertices=[a,A.Vector(a.x,a.y,z)]+[A.Vector(x,y,z) for x,y in via]+[A.Vector(b.x,b.y,z),b]
        edges=[];last=a
        for i,q in enumerate(vertices[1:-1],1):
            v0=(q-vertices[i-1]).normalize();v1=(vertices[i+1]-q).normalize()
            angle=math.acos(max(-1,min(1,v0.dot(v1))));t=r*math.tan(angle/2)
            assert (q-vertices[i-1]).Length>t and (vertices[i+1]-q).Length>t
            enter=q-v0*t;leave=q+v1*t;centre=enter+(v1-v0*v0.dot(v1)).normalize()*r
            mid=centre+((enter-centre)+(leave-centre)).normalize()*r
            if (enter-last).Length>1e-7:edges.append(Part.makeLine(last,enter))
            edges.append(Part.Arc(enter,mid,leave).toShape());last=leave
        edges.append(Part.makeLine(last,b));wire=Part.Wire(edges);assert wire.isValid();return wire
    p=A.Vector(a.x,a.y,z+r);q=p+u*r-up*r
    v=A.Vector(b.x,b.y,z+r);w=v-u*r-up*r
    edges=[Part.makeLine(a,p),Part.Arc(p,p+u*r-(up+u)*r/math.sqrt(2),q).toShape(),
           Part.makeLine(q,w),Part.Arc(w,v-u*r+(u-up)*r/math.sqrt(2),v).toShape(),Part.makeLine(v,b)]
    wire=Part.Wire(edges);assert wire.isValid()
    return wire


def run():
    tick=time.monotonic();f=OUT/'u1-socket-carrier-plan.json';p=json.loads(f.read_text())
    t={v['ref']:v for v in p['terminals']}
    # Whole-plan layer order, not a search over arbitrary heights.
    planes={'J1':80.8,'J2':87.5202,'J3':80.8,'J4':87.5202,'J5':81.5,
            'J6':80.8,'J7':80.8,'J8':79.4,'J9':80.8,'J10':80.8}
    curves={};rows=[];used={z:set() for z in planes.values()}
    posts=[[t[n]['x'],t[n]['y']] for q in p['links'] if q['ref']!='JG_COMB' for n in q['ends']]
    posts.extend([[17.78,-6.35],[15.24,-6.35]])
    # Longest coupled routes first; fixed columns are reserved for every link.
    for q in sorted(p['links'],key=lambda q:0 if q['ref']=='JG_COMB' else -math.dist([t[q['ends'][0]]['x'],t[q['ends'][0]]['y']],[t[q['ends'][1]]['x'],t[q['ends'][1]]['y']])):
        if q['ref']=='JG_COMB':continue
        aa,bb=[t[n] for n in q['ends']]
        z=planes[q['ref']];extra=[];circles=[];reserved=posts
        if z>84.3202:
            # Every component/header/entry pad is a possible occupied vertical
            # column, not just the ten local-link endpoints. This includes the
            # long R15/R16 drops to PCB1 before their formed leads are detailed.
            reserved=[[v['x'],v['y']] for v in p['terminals']]
            # Both retained M2 heads: actual OD3.8, Z85.3202..87.3202.
            # Allocate their complete projected head footprint, not just the
            # mounting shafts used for the underside layer.
            circles=[([-17.78,0],1.9),([17.78,0],1.9)]
            extra=[([-19.425,y-1.325],[11.805,y+1.325]) for y in (-11.43,3.81)]
            for c in p['parts']:
                x,y,h=c['body_center_local_mm'];dx,dy,dz=c['body_size_mm']
                if 84.3202+h-dz/2-.4<z<84.3202+h+dz/2+.4:extra.append(([x-dx/2,y-dy/2],[x+dx/2,y+dy/2]))
        elif z>81:
            reserved=[[v['x'],v['y']] for v in p['terminals']]
            circles=[([-17.78,0],2.25),([17.78,0],2.25)]
        occupied=set().union(*(cells for h,cells in used.items() if abs(z-h)<.95))
        allocated=allocate([aa['x'],aa['y']],[bb['x'],bb['y']],reserved,occupied,extra,circles)
        used[z]=occupied
        via=[[91.59+x,y] for x,y in allocated[1:-1]] or None
        a=[91.59+aa['x'],aa['y'],84.8202];b=[91.59+bb['x'],bb['y'],84.8202]
        c=path(a,b,planes[q['ref']],via);curves[q['ref']]=(c,.4)
        rows.append(dict(ref=q['ref'],net=q['net'],ends=q['ends'],start_mm=a,end_mm=b,
                         underside_plane_world_mm=planes[q['ref']],forming_radius_project_mm=.5,
                         guide_mm=c.Length,nominal_blank_mm=math.ceil(c.Length+4),
                         strip_each_mm=2.6,insulation_end_world_z_mm=87.4202 if z>84.3202 else 82.2202,
                         sku_candidate='Adafruit1446',OD_project_upper_mm=.8,
                         fixed_not_moving=True,via_xy_mm=via,
                         rationale='Whole grid allocation excludes every other jumper pad column and both E2 board entries',allocated_local_xy_mm=allocated))
    bus=Part.makeLine(A.Vector(86.51,-6.35,82.47),A.Vector(101.75,-6.35,82.47))
    curves['JG_COMB']=(bus,.25)
    pairs=[];conflicts=[]
    names=list(curves)
    for i,n in enumerate(names):
        a,ra=curves[n]
        for m in names[i+1:]:
            b,rb=curves[m];d=a.distToShape(b)[0];pairs.append(dict(a=n,b=m,gap_mm=d-ra-rb))
            if d<ra+rb+.1:conflicts.append(pairs[-1])
    out=dict(status='FIXED_LOCAL_LINKS_MUTUAL_SPACE_ONLY' if not conflicts else 'FIXED_LOCAL_LINK_ALLOCATION_REQUIRES_CHANGE',
             selected=False,E1_complete=False,physical_pass=False,links=rows,
             ground_bus=dict(ref='JG_COMB',net='G_SYS',ends=p['links'][-1]['ends'],
                             construction='One straight tinned0.5mm MRS16 lead offcut, soldered directly to seven same-net underside annuli. No tines or extra header. Bare bus inside insulating underside cover; no motor current.',
                             centreline_mm=[[86.51,-6.35,82.47],[101.75,-6.35,82.47]],
                             nominal_blank_mm=17,retained_offcut_required_mm=17,
                             pad_attachment_not_through_hole=True),
             wire_candidate=dict(sku='Adafruit1446',source='https://www.adafruit.com/product/1446',
                                 catalogue='30AWG fine prototyping/repair wire,200m spool',
                                 OD_max_mm=.8,OD_is_project_acceptance_limit_not_catalogue=True,
                                 current_scope='Fixed low-current logic/PWM links ONLY, not servo power or power return',
                                 delivery_gates=['Actual OD<=0.8mm and insulation survives soldering',
                                                 'Hand forming radius0.5mm without jacket/core damage; no repeated flex',
                                                 'Inspect continuity/shorts/retention and dry fit before phase2 power']),
             pairs=len(pairs),conflicts=conflicts,
             wire_nominal_sum_mm=sum(q['nominal_blank_mm'] for q in rows),
             open=['Retained board/carrier and complete E2 tails/body check',
                   'Individual resistor/regulator/cap leads and their lengths',
                   'Native insulating underside cover, fixed wire retention and external cable grips',
                   'Actual solder fillet envelope at every pad and adapter pin'],
             source_sha256={q.relative_to(ROOT).as_posix():SHA(q) for q in (f,Path(__file__))},
             worker_seconds=round(time.monotonic()-tick,4))
    (OUT/'u1-socket-links-plan.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:out[k] for k in ('status','pairs','conflicts','wire_nominal_sum_mm','worker_seconds')}))


if __name__=='__main__':run()
