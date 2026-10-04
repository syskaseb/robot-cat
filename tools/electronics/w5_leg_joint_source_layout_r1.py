"""One coupled change: vertical leg loops, high outer trunks and W064 exit.

R2 witnesses locate conflicts with DATA, MTA bodies and the W064 departure.
Retain all electrical nets. Exchange two labels of the SAME P_FRONT potential:
logical .1 uses the previously NC fourth physical cage; .4 becomes NC.
The moved W064 Carrier passage/seat is OPEN until native construction exists.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,math
import w5_leg_outward_loops_r1 as template
import w5_source_grips_native_r1 as owners_module
from servo_fuse_inputs_r1 import save,sha

ROOT=template.ROOT
OUT=ROOT/'hardware/electronics/full-cat/w5-leg-joint-source-layout-r1'
source=Path(template.__file__).read_text(encoding='utf-8')
for old,new in (
    ('22 if row[\'role\']==\'D\' else 32','90'),
    ('side*24.5','side*29.5'),
    ('-20*math.sin(theta)','+20*math.sin(theta)'),
    ('-10*math.sin(theta)','+10*math.sin(theta)'),
    ("(52 if row['role']=='D' else 64)","(70 if row['role']=='D' else 84)"),
    ("(137 if row['role']=='D' else 149)","(159 if row['role']=='D' else 174)"),
    ('straight_cage_entry_mm=6','straight_cage_entry_mm=1'),
):
    assert old in source,old
    source=source.replace(old,new)
old="[escape,outer,loop_end[2]],[escape,outer,high],"
assert old in source
source=source.replace(old,"[loop_end[0],outer,high],")
# The old W064 band cannot remain on a newly routed wire. No PETG is omitted.
needle="source=Path(base.__file__).read_text(encoding='utf-8')"
assert needle in source
source=source.replace(needle,needle+"\n    source=source.replace(\"for wire in ('W064','W065','W067','W068'):\",\"for wire in ('W065','W067','W068'):\")")
context=dict(__file__=template.__file__,__name__='joint_source_definition')
exec(compile(source,template.__file__,'exec'),context)
context['OUT']=OUT
plan=context['plan']


def source_edges(rows):
    edges=json.loads(json.dumps(next(r for r in rows if r['wire']=='W064')['edges']))
    assert edges[0]['start']==[-39,11,113.5]
    for e in edges[:3]:
        for key in ('start','mid','end'):
            if key in e:e[key][0]+=22.5
    edges[3]['start'][0]+=22.5
    assert edges[0]['start']==[-16.5,11,113.5]
    return edges


def main():
    import FreeCAD as A,Part
    import w5_exact_separation as prune
    started=datetime.now(timezone.utc)
    assert not (OUT/'checks.json').exists()
    OUT.mkdir(parents=True,exist_ok=True)
    graph_path=ROOT/'hardware/electronics/power-platform/wiring-p0.json'
    graph=json.loads(graph_path.read_text(encoding='utf-8'))
    assert not any('P_FRONT.4' in (w['a'],w['b']) for w in graph['wires'])
    original_intent=ROOT/'hardware/electronics/full-cat/w5-s1-source-layout-r8/intent.json'
    rows=json.loads(original_intent.read_text(encoding='utf-8'))['routes']
    edges=[]
    for e in source_edges(rows):
        edge=Part.makeLine(A.Vector(*e['start']),A.Vector(*e['end'])) if e['kind']=='line' else Part.Arc(
            A.Vector(*e['start']),A.Vector(*e['mid']),A.Vector(*e['end'])).toShape()
        if e['kind']=='arc':assert abs(edge.Curve.Radius-25.2)<1e-6
        edges.append(edge)
    for a,b in zip(edges,edges[1:]):
        assert (a.valueAt(a.LastParameter)-b.valueAt(b.FirstParameter)).Length<1e-6
        assert (a.tangentAt(a.LastParameter)-b.tangentAt(b.FirstParameter)).Length<1e-6
    path=Part.Wire(edges);assert path.isValid()
    pieces=[Part.Wire([e]).makePipeShell([Part.Wire([Part.makeCircle(2.1,e.valueAt(e.FirstParameter),e.tangentAt(e.FirstParameter))])],True,False) for e in edges]
    assert all(s.isValid() and len(s.Solids)==1 for s in pieces)
    shape=Part.makeCompound(pieces)
    file=OUT/'W064_WORLD.brep';shape.exportBrep(str(file))
    path.exportBrep(str(OUT/'W064_CENTERLINE_WORLD.brep'))
    original=owners_module.current_owners
    captured={}
    def changed(A,Part):
        owners,pins=original(A,Part)
        assert 'W064' in owners
        owners['W064']=shape
        pins.extend((file,original_intent,graph_path,Path(__file__)))
        captured.update(owners)
        return owners,pins
    owners_module.current_owners=changed
    context['main']()
    p=OUT/'checks.json';receipt=json.loads(p.read_text(encoding='utf-8'))
    hits=[];errors=[];pairs=0
    captured.pop('W064')
    for key in ('source-switch-restraints-r2/P_SYS_seat_DESIGN','source-switch-restraints-r2/P_SYS_tie_DESIGN'):
        captured.pop(key)
    # Received cover/carrier and all source hoods remain actual obstacles.
    for label,rel in (
        ('SourceCarrier','hardware/cad/studies/w5-source-cage-access-native-r1/Carrier_WORLD.brep'),
        ('SourceCover','hardware/cad/studies/w5-source-cage-access-native-r1/Cover_WORLD.brep'),
        ('SourceWestHood','hardware/cad/studies/w5-source-roof-native-r5/WestHood_WORLD.brep'),
        ('SourceEastHood','hardware/cad/studies/w5-source-roof-native-r5/EastHood_WORLD.brep')):
        captured[label]=Part.read(str(ROOT/rel))
    for wire in ('W065','W067','W068'):
        captured[wire+'_band']=Part.read(str(ROOT/f'hardware/electronics/full-cat/w5-source-grips-native-r2/{wire}_T18I_WORLD.brep'))
    for q in (ROOT/'hardware/electronics/full-cat/w5-source-roof-native-r3').glob('*WORLD.brep'):
        if q.name.startswith(('Bolt','Nut','Washers')):
            captured['SourceHoodHardware/'+q.stem]=Part.read(str(q))
    fanouts=Part.read(str(OUT/'FANOUTS_WORLD.brep')).childShapes()
    captured.update({r['wire']:s for r,s in zip(receipt['routes'],fanouts)})
    for key,t in captured.items():
        for a in shape.Solids:
            for b in t.Solids:
                if not a.BoundBox.intersect(b.BoundBox):continue
                pairs+=1
                if prune.separated(a,b):continue
                try:
                    c=a.common(b)
                    if c.Volume>1e-5:
                        bb=c.BoundBox
                        hits.append(dict(wire='W064',owner=key,mm3=c.Volume,
                            bounds_mm=[getattr(bb,q) for q in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]))
                except Exception as exc:errors.append(dict(wire='W064',owner=key,error=str(exc)))
    receipt['hits'].extend(hits);receipt['errors'].extend(errors);receipt['pairs']+=pairs
    receipt['status']='JOINT_SOURCE_FANOUT_REJECTED' if receipt['hits'] or receipt['errors'] else 'JOINT_SOURCE_FANOUT_STATIC_CLEAR_NATIVE_SUPPORTS_OPEN'
    receipt.update(P_FRONT_same_potential_cage_exchange={'logical.1':'physical4','logical.4':'physical1/NC'},
        W064_external_mm=path.Length,W064_trial_blank_mm=math.ceil((path.Length+14+8.73+30)/10)*10,
        W064_Carrier_passage_and_seat_new_x_mm=-16.5,W064_native_support_complete=False,
        first_straight_prototype_allowance_mm=1,not_a_delivered_bend_measurement=True,
        all_source_hoods_retained=True,selected=False,W5_complete=False,physical_pass=False,
        worker_wall_seconds=(datetime.now(timezone.utc)-started).total_seconds())
    receipt['source_sha256'][Path(__file__).relative_to(ROOT).as_posix()]=sha(Path(__file__))
    receipt['files'][file.relative_to(ROOT).as_posix()]=sha(file)
    centreline=OUT/'W064_CENTERLINE_WORLD.brep'
    receipt['files'][centreline.relative_to(ROOT).as_posix()]=sha(centreline)
    receipt.pop('initial_six_mm_straight_and_arc_tangency_checked')
    receipt['initial_one_mm_straight_and_arc_tangency_checked']=True
    save(p,receipt)
    print('JOINT_SOURCE_RESULT',receipt['pairs'],len(receipt['hits']),len(receipt['errors']),flush=True)


if __name__=='__main__':main()
