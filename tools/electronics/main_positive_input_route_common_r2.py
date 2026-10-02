"""Complete W043/W077/W078 routing candidate; no incomplete route selection."""
from datetime import datetime, timezone
from pathlib import Path
import json, math, sys
import main_positive_input_r1 as C
import main_input_return_r1 as B
ROOT=C.ROOT; M=C.M
OUT=ROOT/'hardware/electronics/full-cat/main-positive-input-route-r1'
PAD=[114.869,4.91,62.5748]
SOURCE=[-76.5,-11,113.5]
HOLDER=[-65.5,-29.85,109,-14.5,-12.15,131]
PREF=[[-76.5,-13,113.5],[-76.5,-17.4182779986,113.5],[-72.9182779986,-21,115],[-68.5,-21,115]]
RISE=[[-11.5,-21,115],[-3.5,-21,115],[4.5,-21,122],[12.5,-21,122]]
FAN=[[129,-5.9,95],[129,-5.9,84.8582666667],[114.869,4.91,74.7165333333],[114.869,4.91,64.5748]]

def geometry():
    import FreeCAD as A
    import Part
    from xb11_upstream_route import rounded
    def line(a,b):return Part.makeLine(A.Vector(*a),A.Vector(*b))
    def bez(p):
        c=Part.BezierCurve();c.setPoles([A.Vector(*q) for q in p]);return c.toShape()
    wires={
        'W043':[line(SOURCE,PREF[0]),bez(PREF),line(PREF[-1],[-65.5,-21,115])],
        'W077':[line([-14.5,-21,115],RISE[0]),bez(RISE),line(RISE[-1],[52.5,-21,122])],
        'W078':list(rounded([A.Vector(*p) for p in [[52.5,-21,122],[129,-21,122],[129,-5.9,122],[129,-5.9,95]]],6).Edges)+[bez(FAN),line(FAN[-1],PAD)]}
    return wires

def main():
    import FreeCAD as A
    import Part
    OUT.mkdir(parents=True,exist_ok=True);assert not (OUT/'checks.json').exists()
    begin=datetime.now(timezone.utc)
    bounds={n:B.radius_bound(p) for n,p in [('prefuse',PREF),('factory_rise',RISE),('MAIN_fan',FAN)]}
    M.save(OUT/'intent.json',dict(parent='one-batch-prototype-r41',source='P_SYS.2',destination='MAIN.VIN',
        source_mm=SOURCE,holder_bbox_mm=HOLDER,pad_mm=PAD,splice_centre_mm=[52.5,-21,122],
        poles_mm=dict(prefuse=PREF,factory_rise=RISE,MAIN_fan=FAN),radius_bounds_mm=bounds,
        allowances=dict(factory_OD_mm=3.4,red_OD_mm=3,minimum_radius_mm=6,closed_holder_height_mm=22),
        limits=dict(W043_blank_mm=40,W077_blank_mm=80,W078_blank_mm=180,total_blank_mm=300),
        conditions=['OD/static-radius and closed-cover height are project reserves, not supplier ratings.',
                    'Factory lead minimum84.5mm includes its bare tip; final solder/WAGO ends must be trimmed to actual delivered wire.',
                    'Do not use delivered6.35mm bare tip as WAGO strip12..14mm. Prepare a fresh untinned end.',
                    'No PCB terminal installed; solder only off PETG. E3 remains open.'],
        physical_pass=False,selected=False,W5_complete=False,restraints_complete=False,started_utc=begin.isoformat()))
    assert min(bounds.values())>=6,bounds
    paths=geometry();pieces={};lengths={};lineview=[]
    for name,edges in paths.items():
        for a,b in zip(edges,edges[1:]):
            assert (a.valueAt(a.LastParameter)-b.valueAt(b.FirstParameter)).Length<1e-7
            assert (a.tangentAt(a.LastParameter)-b.tangentAt(b.FirstParameter)).Length<1e-7
        lengths[name]=sum(e.Length for e in edges)
        for i,e in enumerate(edges):
            bare=name=='W078' and i==len(edges)-1
            radius=math.sqrt(.823/math.pi) if bare else (1.5 if name=='W078' else 1.7)
            s=Part.Wire([e]).makePipeShell([Part.Wire([Part.makeCircle(radius,e.valueAt(e.FirstParameter),e.tangentAt(e.FirstParameter))])],True,False)
            assert s.isValid() and len(s.Solids)==1
            key=f'{name}_{i}';pieces[key]=s
            s.exportBrep(str(OUT/(key+'_DESIGN.brep')));e.exportBrep(str(OUT/(key+'_CENTERLINE.brep')))
            lineview.append(dict(name=key,points=[list(p) for p in e.discretize(Deflection=.2)]))
    assert lengths['W043']+14+8<=LIMITS['W043'],lengths
    assert lengths['W077']+8<=LIMITS['W077'],lengths
    assert lengths['W078']+20<=LIMITS['W078'],lengths
    owners,hashes=C.current_owners()
    holder=Part.makeBox(51,17.7,22,A.Vector(*HOLDER[:3]));owners['F_PI_closed_project_reserve']=holder
    rows=[]
    for n,s in {**pieces,'F_PI_candidate':holder}.items():
        for m,t in owners.items():
            if n=='F_PI_candidate' and m in ('Deck_R41','F_PI_closed_project_reserve'):continue
            if n in ('W043_2','W077_0') and m=='F_PI_closed_project_reserve':continue # own moulded lead entry only
            if n=='W078_'+str(len(paths['W078'])-1) and m=='MAIN/SupplierFamilyReference':continue # own copper landing
            for i,q in enumerate(s.Solids):
                for j,v in enumerate(t.Solids):
                    if q.BoundBox.intersect(v.BoundBox):rows.append(dict(part=n,owner=m,solid=i,owner_solid=j,hit_mm3=q.common(v).Volume))
    hits=[r for r in rows if r['hit_mm3']>1e-5];end=datetime.now(timezone.utc)
    M.save(OUT/'checks.json',dict(status='REJECTED' if hits else 'ROUTES_CLEAR_NEED_INSULATION_AND_RESTRAINTS',
        hits=hits,rows=rows,lengths_mm=lengths,radius_bounds_mm=bounds,source_sha256=hashes,
        physical_pass=False,selected=False,W5_complete=False,restraints_complete=False,
        script_sha256=M.sha(Path(__file__)),started_utc=begin.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds()))
    holder.exportBrep(str(OUT/'F_PI_candidate_DESIGN.brep'));M.save(OUT/'preview-lines.json',lineview)
    print(json.dumps(dict(hits=hits,lengths=lengths,radii=bounds,pairs=len(rows))),flush=True)

LIMITS={'W043':40,'W077':80,'W078':180}
if __name__=='__main__':main()
