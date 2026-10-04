"""One shared twelve-loom moving-side layout on selected R53.

Read saved rigid carriers and inspect all new corridors together. No solver,
whole E6 recompute, changes to bought parts or inferred connector pin order.
Body fan-outs, fixed/moving grips and motion remain explicit unfinished work.
"""
from datetime import datetime, timezone
from pathlib import Path
import json, math, sys
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'tools/electronics'), str(ROOT / 'tools/cad')]
from servo_fuse_inputs_r1 import save, sha
from check_main_p0_placement import SavedShapes, prop
OUT = ROOT / 'hardware/electronics/full-cat/w5-leg-corridors-r1'
MAP = ROOT / 'hardware/electronics/full-cat/w5-leg-source-map-r1/interface.json'
SEL = ROOT / 'hardware/manufacturing/one-batch-prototype-r53/selection.json'


def components(objects):
    parent = {}
    def find(n):
        parent.setdefault(n, n)
        if parent[n] != n: parent[n] = find(parent[n])
        return parent[n]
    for obj in objects.values():
        kind = prop(obj, 'JointType')
        if kind is None: continue
        labels = [x.get('value') for x in kind.findall('./CustomEnumList/Enum')]
        if labels[int(kind[0].get('value'))] != 'Fixed': continue
        suppressed = prop(obj, 'Suppressed')
        if suppressed is not None and suppressed[0].get('value') == 'true': continue
        refs = [prop(obj, 'Reference'+str(i))[0] for i in (1,2)]
        assert all(not r.get('file') for r in refs)
        a, b = [r.get('name') for r in refs]
        parent[find(a)] = find(b)
    return find


def fillet_path(A, Part, points, radius=10):
    pts = []
    for p in points:
        if not pts or (p-pts[-1]).Length > 1e-7: pts.append(p)
    edges, current = [], pts[0]
    for i in range(1, len(pts)-1):
        p = pts[i]; u = p-pts[i-1]; v = pts[i+1]-p
        lu, lv = u.Length, v.Length; u.normalize(); v.normalize()
        dot = max(-1, min(1, u.dot(v))); angle = math.acos(dot)
        if angle < 1e-7: continue
        assert angle < math.pi-1e-7, 'Reverse tangent requires a real service loop'
        cut = radius * math.tan(angle/2)
        assert 2*cut < min(lu,lv)-1e-7, 'Adjacent R10 bends overlap'
        before, after = p-u*cut, p+v*cut
        normal = v-u*dot; normal.normalize()
        center = before+normal*radius
        mid = center+((before-center)+(after-center)).normalize()*radius
        if (before-current).Length > 1e-7: edges.append(Part.makeLine(current,before))
        edges.append(Part.Arc(before,mid,after).toShape()); current=after
    if (pts[-1]-current).Length > 1e-7: edges.append(Part.makeLine(current,pts[-1]))
    path = Part.Wire(edges)
    assert path.isValid()
    for a,b in zip(edges,edges[1:]):
        assert (a.valueAt(a.LastParameter)-b.valueAt(b.FirstParameter)).Length < 1e-6
        assert (a.tangentAt(a.LastParameter)-b.tangentAt(b.FirstParameter)).Length < 1e-6
    return path


def main():
    import FreeCAD as A
    import Part
    import w5_bus_restraints_r3 as bus
    from w5_selected_owners_r52 import cached
    begin = datetime.now(timezone.utc)
    assert not (OUT/'checks.json').exists(), 'Keep completed attempts'
    source = json.loads(MAP.read_text(encoding='utf-8'))
    selected = json.loads(SEL.read_text(encoding='utf-8'))
    assert selected['BUS_local_complete'] and not selected['W5_complete']
    assert all(sha(ROOT/k)==v for k,v in source['source_sha256'].items())
    reader = SavedShapes(); entry = ROOT/'hardware/cad/assembly/RobotCatNarrowRimEars.FCStd'
    objects = reader.doc(entry); component = components(objects)
    axes_rel = ROOT/'hardware/simulation/p0/e6-leg-compatibility.json'
    axes = json.loads(axes_rel.read_text(encoding='utf-8'))['axes']
    planned = []
    for row in source['looms']:
        carriers = sorted({c['reference'] for a in axes if a['physical_leg']==row['physical_leg']
            for c in a['connectors'] if component(c['reference'])==component('Rigid_'+row['pcb'])})
        assert carriers, 'PCB must be attached to a real rigid leg carrier'
        p = A.Vector(*row['connector_reservation_world_mm'][0]); direction=A.Vector(*row['cable_exit_world_axis'])
        start=p+direction*8; lead=start+direction*40
        front=row['loom'].startswith('F'); side=1 if row['loom'][1]=='L' else -1
        x=min(-140,lead.x-25) if front else max(182,lead.x+25)
        y=side*(108+12*int(row['loom'][2]))
        points=[start,lead,A.Vector(x,lead.y,lead.z),A.Vector(x,y,lead.z),A.Vector(x,y,85)]
        planned.append(dict(loom=row['loom'],carriers=carriers,wire_roles=row['electrical'],
            waypoints_mm=[list(v) for v in points],fixed_breakout_provisional_mm=[x,y,85],
            cable_exit_projection_assumption_mm=8,free_initial_length_assumption_mm=40,
            port_choice=0,port_choice_is_not_pin_assignment=True))
    OUT.mkdir(parents=True,exist_ok=True)
    save(OUT/'intent.json',dict(status='TWELVE_CORRIDORS_SAVED_BEFORE_CHECK',routes=planned,
        nominal_bundle_OD_mm=5,nominal_static_radius_mm=10,dynamic_radius_mm=None,
        assumptions='One continuous factory three-core loom per servo; bundle OD5/R10/static/plug8 are editable prototype envelopes, not a manufacturer cable rating.',
        scope='Only source plug to provisional external fixed breakout. No new electrical junction or splice is introduced at the breakout.',
        body_fanouts_complete=False,grips_complete=False,motion_qualified=False,selected=False,W5_complete=False,physical_pass=False))
    owners,cache=cached()
    for key in bus.removed_owners():
        assert key in owners; del owners[key]
    deck=ROOT/selected['current_deck_world']; owners['CandidateDeck']=Part.read(str(deck))
    intent_path=ROOT/'hardware/electronics/full-cat/w5-bus-pair-r52-r4/intent.json'
    bi=json.loads(intent_path.read_text(encoding='utf-8'))
    sx=sum(bi['source_lead_datums'][k][0] for k in ('W002','W003'))/2
    owners.update({'R53BUS/'+k:s for k,s in bus.restraints(A,Part,sx).items()})
    for w in ('W002','W003'):
        owners['R53BUS/'+w]=Part.read(str(intent_path.parent/(w+'_DESIGN.brep')))
    hits,errors,paths,bundles,rows=[],[],[],[],[]; pairs=0
    def check(loom,index,s,key,o):
        nonlocal pairs
        if not s.BoundBox.intersect(o.BoundBox):return
        pairs+=1
        try:
            witness=s.common(o)
            if witness.Volume>1e-5:
                hits.append(dict(loom=loom,segment=index,owner=key,mm3=witness.Volume,
                    bounds_mm=[getattr(witness.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]))
        except Exception as ex:errors.append(dict(loom=loom,segment=index,owner=key,error=str(ex)))
    for row in planned:
        try:
            path=fillet_path(A,Part,[A.Vector(*p) for p in row['waypoints_mm']])
            pieces=[Part.Wire([e]).makePipeShell([Part.Wire([Part.makeCircle(2.5,e.valueAt(e.FirstParameter),e.tangentAt(e.FirstParameter))])],True,False) for e in path.Edges]
            assert all(s.isValid() and len(s.Solids)==1 for s in pieces)
            shape=Part.makeCompound(pieces);paths.append(path);bundles.append(shape)
            rows.append(dict(loom=row['loom'],path_mm=path.Length,whole_lead_cut_mm=None,
                factory_usable_mm=None,body_fanout_mm=None,prepared=False))
            for i,s in enumerate(pieces):
                for key,o in owners.items():check(row['loom'],i,s,key,o)
            print('LEG_CORRIDOR',row['loom'],'hits',len(hits),'errors',len(errors),flush=True)
        except Exception as ex:
            errors.append(dict(loom=row['loom'],stage='construction',error=str(ex)))
            print('LEG_BUILD_ERROR',row['loom'],str(ex),flush=True)
    for i,a in enumerate(bundles):
        for j,b in enumerate(bundles[i+1:],i+1):check(rows[i]['loom'],None,a,rows[j]['loom'],b)
    files=[]
    for name,shapes in [('CENTERLINES_WORLD.brep',paths),('CORRIDORS_WORLD.brep',bundles)]:
        if shapes:
            file=OUT/name;Part.makeCompound(shapes).exportBrep(str(file));files.append(file)
    end=datetime.now(timezone.utc)
    pins=[MAP,SEL,deck,intent_path,axes_rel,Path(__file__),ROOT/'tools/electronics/w5_bus_restraints_r3.py',
        ROOT/'hardware/electronics/full-cat/w5-installed-r52/owners.json',ROOT/'hardware/electronics/full-cat/w5-installed-r52/installed.brep']
    save(OUT/'checks.json',dict(status='LEG_CORRIDORS_REJECTED' if hits or errors or len(rows)!=12 else 'LEG_CORRIDORS_STATIC_CLEAR_FULL_LOOMS_OPEN',
        routes=rows,hits=hits,errors=errors,pairs=pairs,source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in pins},
        files={p.relative_to(ROOT).as_posix():sha(p) for p in files+[OUT/'intent.json']},
        started_utc=begin.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds(),
        motion_qualified=False,body_fanouts_complete=False,grips_complete=False,selected=False,W5_complete=False,physical_pass=False))
    print('LEG_CORRIDORS_RESULT',len(rows),len(hits),len(errors),flush=True)


if __name__=='__main__':main()
