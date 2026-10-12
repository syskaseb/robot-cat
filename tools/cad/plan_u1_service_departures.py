"""Two coupled outward departures, reserving installed U1 service FIRST.

Keep all eleven other complete curves and every qualified grip land. The old
thirteen-route receipt is immutable; this is its explicit two-wire replacement.
Functional service boxes are planning reservations, not collision verdicts.
"""
import copy,json,math,time
from pathlib import Path
import FreeCAD as A
import Part
import plan_u1_free_channels as F
import plan_current_main_pi_wiring as M
import plan_u1_power_grips as P
import plan_u1_board_grips as B
import plan_u1_grouped_grips as G
from check_main_p0_placement import SavedShapes,prop
from check_u1_socket_service import sweep
ROOT,OUT,SHA=P.ROOT,P.OUT,P.SHA


def service_shapes(reader):
    pop=OUT/'U1SocketPopulation.FCStd';ret=OUT/'U1SocketRetainer.FCStd'
    shapes={'Retainer':sweep(reader.shape(ret,'RetainerBar'))}
    names=['Adapter1208PCB']
    for group in ('FixedPurchasedReferences','TopFaceReferences'):
        for link in prop(reader.doc(pop)[group],'Group').findall('.//Link'):
            n=link.get('value')
            if group=='TopFaceReferences' or n.startswith('Male'):names.append(n)
    for n in names:
        s=reader.shape(pop,n)
        if n.startswith(('C1_','C2_')):
            b=s.BoundBox;shapes[n]=P.G.box([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax+12])
        else:shapes[n]=sweep(s)
    return shapes


class ServiceSpace(F.Space):
    def __init__(self,cache,keepouts,pads=()):
        super().__init__(cache);self.keepouts=keepouts;self.pads=pads
    def clear(self,parts,ignore=()):
        for _,q in F.samples(F.sampling_parts(parts),step=.7):
            if any(all(b[i]-self.radius-.35<q[i]<b[i+3]+self.radius+.35 for i in range(3)) for b in self.keepouts):return False
            for shape,b in self.pads:
                if all(b[i]-self.radius<q[i]<b[i+3]+self.radius for i in range(3)):
                    # Intentional tangent insulation seats have no extra
                    # planning halo. A seat bbox is not material contact.
                    if shape.distToShape(Part.Vertex(A.Vector(*q)))[0]<self.radius-1e-5:return False
        return super().clear(parts,ignore)


def outward_prefixes(plan):
    # Same9mm vertical lands, but bend AWAY from the adapter/retainer cavity.
    # Both depart WEST, toward their receivers, outside the service cavity.
    logic=M.reverse(plan['complete_routes']['XL01']['parts'][-1:])
    M.turn(logic,M.U,M.W,10);M.straight(logic,[51.81,-13.97,104.3202])
    tail=copy.deepcopy(plan['complete_routes']['XL09']['parts'][:1])
    M.turn(tail,M.U,M.W,6);M.straight(tail,[55.81,19.05,100.3202])
    return logic,tail


def run():
    tick=time.monotonic();pf=OUT/'u1-common-wiring-plan.json';cf=OUT/'u1-current-routing-space.json'
    p=json.loads(pf.read_text());cache=json.loads(cf.read_text())
    for n,h in cache['source_sha256'].items():assert SHA(ROOT/n)==h,n
    reader=SavedShapes();service=service_shapes(reader);boxes=[]
    for s in service.values():
        b=s.BoundBox;boxes.append([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])
    # Seats are actual material, not expanded boxes blocking their own wires.
    pads=[]
    for a in (B.allocation(),G.allocation(),P.allocation()):
        for row in a['pads']:
            if row.get('bounds_mm'):pads.append((P.material(row),row['bounds_mm']))
    space=ServiceSpace(cache,boxes,pads)
    for n,r in {**p['complete_routes'],**p['changed_MAIN_pair']}.items():
        if n not in ('XL01','XL09'):space.insert(n,r['parts'],r.get('radius',r.get('radius_mm')))
    logic,tail=outward_prefixes(p)
    pi=copy.deepcopy(p['complete_routes']['XL01']['parts'][:2])
    gtail=M.reverse(p['complete_routes']['XL09']['parts'][2:])
    ends={'XL01':(pi,logic,F.AXES[2],M.W),'XL09':(tail,gtail,M.W,M.D)}
    for n,(a,b,_,__) in ends.items():
        space.insert(n+'/a',a,.7);space.insert(n+'/b',b,.7)
    rows={};fail=[]
    space.radius=.7
    for n,prefix in [('XL01',logic),('XL09',tail)]:
        if not space.clear(prefix[1:],(n+'/a',n+'/b')):
            fail.append(dict(wire=n,states=0,cause='NEW_DEPARTURE_PREFIX_BLOCKED'))
    for n,(a,b,axis,outward) in ends.items():
        if fail:break
        minimum=p['complete_routes'][n]['min_fixed_radius_mm'];space.radius=.7
        middle,states=F.search(space,a[-1]['end'],axis,b[-1]['end'],outward,minimum,
                              500 if n=='XL01' else 400,(n+'/a',n+'/b'),max_states=250)
        if middle is None:fail.append(dict(wire=n,states=states,cause='NO_BOUNDED_OUTWARD_SERVICE_CHANNEL'));break
        full=a+middle+M.reverse(b);length=F.validate(full,minimum)
        rows[n]=dict(parts=full,radius=.7,guide_mm=length,nominal_blank_mm=math.ceil(length+(36 if n=='XL01' else 6)),
                     min_fixed_radius_mm=minimum,search_states=states,source=p['complete_routes'][n]['source'],actual_cut_mm=None)
        space.insert(n,full,.7)
        print('Service departure allocated',n,states,round(length,3),round(time.monotonic()-tick,2),flush=True)
    result=dict(status='TWO_OUTWARD_SERVICE_ROUTES_SAMPLED_ONLY_EXACT_GATE_OPEN' if not fail else 'OUTWARD_SERVICE_PLAN_REQUIRES_CHANGE',
        replacements=rows,search_failures=fail,service_reservations=boxes[:len(service)],
        preserved_grip_lands=True,unchanged_complete_curves=11,selected=False,E1_complete=False,W5_complete=False,physical_pass=False,
        source_sha256={**reader.hashes,**{f.relative_to(ROOT).as_posix():SHA(f) for f in
            (pf,cf,Path(__file__),Path(F.__file__),Path(B.__file__),Path(G.__file__),Path(P.__file__))}},
        worker_seconds=round(time.monotonic()-tick,3))
    (OUT/'u1-service-departures-plan.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('replacements','source_sha256','service_reservations')}),flush=True)


if __name__=='__main__':run()
