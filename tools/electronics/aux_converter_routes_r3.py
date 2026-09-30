"""Repair only the two rejected r2 leads against saved physical-owner solids."""
import json,math,sys
from pathlib import Path
import xb11_upstream_route as R
A,Part,ROOT=R.A,R.Part,R.ROOT
P=ROOT/'hardware/electronics/full-cat/aux-converter-routes-r2'
OUT=ROOT/'hardware/electronics/full-cat/aux-converter-routes-r3'
REPAIR_PORTS='--r4' in sys.argv or '--r5' in sys.argv
if REPAIR_PORTS:OUT=ROOT/'hardware/electronics/full-cat/aux-converter-routes-r4'
if '--r5' in sys.argv:OUT=ROOT/'hardware/electronics/full-cat/aux-converter-routes-r5'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def dump(n,v):(OUT/n).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
def main():
    assert not (OUT/'checks.json').exists()
    OUT.mkdir(exist_ok=True);plan=read(P/'plan.json');old=read(P/'checks.json')
    plan['routes']['XA02']['points']=[[96,17.6,132],[112,17.6,132],[112,17.6,171],[-15,17.6,171],[-15,-32,171],[17.27,-32,171],[17.27,-1.27,171],[17.27,-1.27,155.6002]]
    plan['routes']['XA04']['points']=[[17.27,1.27,155.6002],[17.27,1.27,176],[-35,1.27,176],[-35,-75,176],[-35,-75,121],[90,-75,121]]
    plan['routes']['XA04']['end']='R15 opposite arcs drop7.5mm over19.843mm X, then straight to G_AUX.2(110.5,-75,113.5)'
    if REPAIR_PORTS:
        plan['routes']['XA02']['points']=[[96,17.6,132],[116,17.6,132],[116,48,132],[-20,48,132],[-20,48,171],[-20,-1.27,171],[17.27,-1.27,171],[17.27,-1.27,155.6002]]
        plan['routes']['XA04']['points']=[[17.27,1.27,155.6002],[17.27,1.27,176],[-35,1.27,176],[-35,-44,176],[-35,-44,132],[80,-44,132],[80,-75,132]]
        plan['routes']['XA04']['end']='R15 opposite arcs drop18.5mm, then straight to G_AUX.2(110.5,-75,113.5)'
        plan['carrier_ports_world_xy_mm']=[[-20,48],[-35,-44]]
        plan['carrier_port_diameter_mm']=5
        plan['carrier_revision_required']='Two dedicated vertical wire clearance holes; no wire through existing servo tool port. This diagnostic cuts cached Carrier only; native source/export must follow before selection.'
        if '--r5' in sys.argv:
            plan['routes']['XA04']['points']=[[17.27,1.27,155.6002],[17.27,1.27,176],[-35,1.27,176],[-35,-44,176],[-35,-44,129],[83.5,-44,129],[83.5,-75,129]]
            plan['routes']['XA04']['end']='R15 opposite arcs drop15.5mm, then straight to G_AUX.2(110.5,-75,113.5); bypass XA06 riser X80 by3.5mm'
    plan['status']='SOURCE_SAVED_BEFORE_REPAIRING_TWO_DEMONSTRATED_CONFLICTS'
    plan['parent_checks_sha256']=R.sha(P/'checks.json');dump('plan.json',plan)
    tubes={};paths={}
    for n in ('XA02','XA04'):
        p=[A.Vector(*v) for v in plan['routes'][n]['points']];path=R.rounded(p,15)
        if n=='XA04':
            r=15;drop=p[-1].z-113.5;theta=math.acos(1-drop/30);start=p[-1]
            mid=A.Vector(start.x+r*math.sin(theta),-75,start.z-r*(1-math.cos(theta)))
            end=A.Vector(start.x+2*r*math.sin(theta),-75,113.5)
            c1=A.Vector(start.x,-75,start.z-15);c2=A.Vector(end.x,-75,128.5)
            def arc(a,b,c):return Part.Arc(a,c+((a-c)+(b-c)).normalize()*r,b).toShape()
            path=Part.Wire(list(path.Edges)+[arc(start,mid,c1),arc(mid,end,c2),Part.makeLine(end,A.Vector(110.5,-75,113.5))])
        w=path.makePipeShell([Part.Wire([Part.makeCircle(1.25,p[0],p[1]-p[0])])],True,False)
        assert w.isValid() and len(w.Solids)==1;w.exportBrep(str(OUT/(n+'_DESIGN.brep')));tubes[n]=w;paths[n]=path
    s=Part.Shape();s.read(str(P/'XA03_DESIGN.brep'));tubes['XA03']=s
    rows=[]
    for o in old['obstacle_cache']:
        s=Part.Shape();s.read(str(P/o['file']))
        if REPAIR_PORTS and o['owner']=='Carrier_world21_0_144':
            for x,y in plan['carrier_ports_world_xy_mm']:s=s.cut(Part.makeCylinder(2.5,4,A.Vector(x,y,144)))
            s.exportBrep(str(OUT/'Carrier_TWO_PORTS_DIAGNOSTIC.brep'))
        for n in ('XA02','XA04'):
            w=tubes[n]
            if R.overlap(w.BoundBox,s.BoundBox):
                hit=s.common(w);v=R.volume(hit)
                rows.append(dict(wire=n,owner=o['owner'],solid=o['solid'],positive_mm3=v,
                  positive_solid_centers_mm=[list(t.CenterOfMass) for t in hit.Solids] if v>1e-5 else [],distance_mm=s.distToShape(w)[0] if v<1e-5 else 0))
    for n,w in tubes.items():
        for m,s in tubes.items():
            if n<m:rows.append(dict(wire=n,owner=m,positive_mm3=R.volume(s.common(w)),distance_mm=s.distToShape(w)[0]))
    hits=[r for r in rows if r['positive_mm3']>1e-5]
    dump('checks.json',dict(status='REJECTED' if hits else 'NOMINAL_FIXED_CONVERTER_CANDIDATE',hits=hits,exact_pairs=rows,
      unchanged_XA03_sha256=R.sha(P/'XA03_DESIGN.brep'),parent_checks_sha256=R.sha(P/'checks.json'),
      source_sha256=old['source_sha256'],plan_sha256=R.sha(OUT/'plan.json'),script_sha256=R.sha(Path(__file__)),
      lengths_mm={**old['lengths_mm'],**{n:p.Length for n,p in paths.items()}},
      samples={**old['samples'],**{n:[[v.x,v.y,v.z] for e in p.Edges for v in e.discretize(Deflection=.15)] for n,p in paths.items()}},
      scope='Two changed leads only against saved owner solids; inherited XA03 unchanged. End restraints/intermediate supports and full harness remain open.',new_stls=0,physical_pass=False,phase1_complete=False))
    print(json.dumps(dict(hits=hits,pairs=len(rows))),flush=True)
if __name__=='__main__':main()
