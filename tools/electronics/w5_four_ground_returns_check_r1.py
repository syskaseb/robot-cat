"""Build/check the four current ground nets together, without selecting W5.

Keep the source/leg cages and W061. Use actual R21 arcs, including the
reversed leg half-turn, and all installed obstacles plus the explicitly
unselected source/fanout family. A clear route alone is not a complete grip,
lever-access, moving-loom, removal or stock qualification.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, math
from servo_fuse_inputs_r1 import save, sha
from w5_four_ground_returns_plan import plan, provisional_blank, RADIUS, OD, STRAIGHT

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/electronics/full-cat/w5-four-ground-returns-check-r1'
RECEIVED=ROOT/'hardware/electronics/full-cat/w5-joint-source-carrier-native-r1/checks.json'


def path_for(A,Part,row):
    from w5_rounded_path import rounded
    radius=RADIUS; half=math.sqrt(.5)
    s=A.Vector(*row['source_entry_mm']); a=s+A.Vector(0,STRAIGHT,0)
    b=a+A.Vector(0,radius,radius); c=b+A.Vector(0,radius,radius)
    first=Part.Arc(a,a+A.Vector(0,radius*half,radius*(1-half)),b).toShape()
    second=Part.Arc(b,b+A.Vector(0,radius*(1-half),radius*half),c).toShape()
    leg=A.Vector(*row['leg_entry_mm']); side=row['leg_side']
    q=leg+A.Vector(0,-side*STRAIGHT,0); top=q+A.Vector(0,0,2*radius)
    mid=q+A.Vector(0,-side*radius,radius)
    middle=rounded(A,Part,[A.Vector(*p) for p in row['middle_mm']],radius)
    assert (middle.Edges[0].valueAt(middle.Edges[0].FirstParameter)-c).Length<1e-6
    assert (middle.Edges[-1].valueAt(middle.Edges[-1].LastParameter)-top).Length<1e-6
    edges=[Part.makeLine(s,a),first,second,*middle.Edges,
           Part.Arc(top,mid,q).toShape(),Part.makeLine(q,leg)]
    for previous,current in zip(edges,edges[1:]):
        assert (previous.valueAt(previous.LastParameter)-current.valueAt(current.FirstParameter)).Length<1e-6
        assert (previous.tangentAt(previous.LastParameter)-current.tangentAt(current.FirstParameter)).Length<1e-6
    for edge in edges:
        if isinstance(edge.Curve,Part.Circle): assert abs(edge.Curve.Radius-radius)<1e-6
    path=Part.Wire(edges); assert path.isValid()
    return path


def main():
    import FreeCAD as A, Part
    from w5_source_grips_native_r1 import current_owners
    from w5_exact_separation import separated, STATS
    begin=datetime.now(timezone.utc); assert not (OUT/'checks.json').exists()
    OUT.mkdir(parents=True,exist_ok=True)
    receipt=json.loads(RECEIVED.read_text(encoding='utf-8'))
    assert receipt['closed_STL'] and receipt['relocated_reopen'] and not receipt['hits'] and not receipt['errors']
    assert all(sha(ROOT/k)==v for k,v in {**receipt['source_sha256'],**receipt['files']}.items())
    rows=plan(); graph_file=ROOT/'hardware/electronics/power-platform/wiring-p0.json'
    graph=json.loads(graph_file.read_text(encoding='utf-8'))
    for row in rows:
        actual=next(w for w in graph['wires'] if w['id']==row['wire'])
        assert {actual['a'],actual['b']}=={row['source_end'],row['leg_end']}
    owners,pins=current_owners(A,Part)
    for key in ('source-switch-restraints-r2/P_SYS_seat_DESIGN','source-switch-restraints-r2/P_SYS_tie_DESIGN'):
        owners.pop(key)
    for label,rel in (
        ('W064','hardware/electronics/full-cat/w5-leg-joint-source-layout-r1/W064_WORLD.brep'),
        ('SourceCarrier','hardware/cad/studies/w5-joint-source-carrier-native-r1/Carrier_WORLD.brep'),
        ('SourceCover','hardware/cad/studies/w5-source-cage-access-native-r1/Cover_WORLD.brep'),
        ('SourceWestHood','hardware/cad/studies/w5-source-roof-native-r5/WestHood_WORLD.brep'),
        ('SourceEastHood','hardware/cad/studies/w5-source-roof-native-r5/EastHood_WORLD.brep')):
        p=ROOT/rel; owners[label]=Part.read(str(p)); pins.append(p)
    for wire in ('W064','W065','W067','W068'):
        p=RECEIVED.parent/(wire+'_T18I_WORLD.brep'); owners[wire+'_band']=Part.read(str(p)); pins.append(p)
    for p in (ROOT/'hardware/electronics/full-cat/w5-source-roof-native-r3').glob('*WORLD.brep'):
        if p.name.startswith(('Bolt','Nut','Washers')):
            owners['SourceHoodHardware/'+p.stem]=Part.read(str(p)); pins.append(p)
    fanout_folder=ROOT/'hardware/electronics/full-cat/w5-leg-joint-source-layout-r1'
    fanout=json.loads((fanout_folder/'checks.json').read_text(encoding='utf-8'))
    shapes=Part.read(str(fanout_folder/'FANOUTS_WORLD.brep')).childShapes()
    assert len(shapes)==len(fanout['routes'])==36
    owners.update({'ProvisionalFanout/'+row['wire']:s for row,s in zip(fanout['routes'],shapes)})
    pins.extend((fanout_folder/'checks.json',fanout_folder/'FANOUTS_WORLD.brep'))
    save(OUT/'intent.json',dict(routes=rows,source_family_unselected=True,
        fanout_family_received_status=fanout['status'],new_splices=0,
        existing_W061_unchanged=True,selected=False,physical_pass=False))
    hits=[]; errors=[]; pairs=0; built=[]; geometries=[]; files=[OUT/'intent.json']
    def check(wire,s,key,t):
        nonlocal pairs
        for a in s.Solids:
            for b in t.Solids:
                if not a.BoundBox.intersect(b.BoundBox): continue
                pairs+=1
                if separated(a,b): continue
                try:
                    c=a.common(b)
                    if c.Volume>1e-5:
                        bb=c.BoundBox; hits.append(dict(wire=wire,owner=key,mm3=c.Volume,
                            bounds_mm=[getattr(bb,n) for n in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]))
                except Exception as exc: errors.append(dict(wire=wire,owner=key,error=str(exc)))
    for row in rows:
        path=path_for(A,Part,row)
        pieces=[Part.Wire([e]).makePipeShell([Part.Wire([Part.makeCircle(OD/2,
            e.valueAt(e.FirstParameter),e.tangentAt(e.FirstParameter))])],True,False) for e in path.Edges]
        assert all(s.isValid() and len(s.Solids)==1 and not s.check(True) for s in pieces)
        shape=Part.makeCompound(pieces); wire=row['wire']
        for suffix,s in (('WORLD',shape),('CENTERLINE_WORLD',path)):
            p=OUT/(wire+'_'+suffix+'.brep'); s.exportBrep(str(p)); files.append(p)
        for key,t in owners.items(): check(wire,shape,key,t)
        for prior,t in zip(built,geometries): check(wire,shape,prior['wire'],t)
        built.append(dict(wire=wire,external_mm=path.Length,
            nominal_trial_blank_mm=provisional_blank(path.Length,'615' if wire in ('W025','W036') else '415'),
            static_radius_mm=RADIUS,source_end=row['source_end'],leg_end=row['leg_end']))
        geometries.append(shape)
        save(OUT/'progress.json',dict(completed_routes=len(built),pairs=pairs,hits=hits,errors=errors))
        print('FOUR_GROUND_ROUTE',wire,round(path.Length,1),pairs,len(hits),len(errors),flush=True)
    finish=datetime.now(timezone.utc)
    pins.extend((Path(__file__),RECEIVED,graph_file,
        ROOT/'tools/electronics/w5_four_ground_returns_plan.py',ROOT/'tools/electronics/w5_rounded_path.py',
        ROOT/'tools/electronics/w5_exact_separation.py',ROOT/'tools/electronics/w5_source_grips_native_r1.py',
        ROOT/'hardware/electronics/full-cat/body-ground-bridge-finish-r5/interface.json'))
    save(OUT/'checks.json',dict(status='FOUR_GROUND_RETURNS_REJECTED' if hits or errors else 'FOUR_GROUND_RETURNS_STATIC_CLEAR_GRIPS_OPEN',
        routes=built,hits=hits,errors=errors,pairs=pairs,surface_prune_counts=dict(STATS),
        core_OD_mm=OD,static_radius_mm=RADIUS,continuous_tangents_checked=True,
        block_placements_unchanged=True,new_splices=0,existing_W061_unchanged=True,
        restraints_complete=False,motion_qualified=False,stock_selected=False,
        fanout_family_received_status=fanout['status'],whole_joint_family_qualified=False,
        selected=False,W5_complete=False,physical_pass=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in dict.fromkeys(pins)},
        files={p.relative_to(ROOT).as_posix():sha(p) for p in files},
        started_utc=begin.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-begin).total_seconds()))


if __name__=='__main__': main()
