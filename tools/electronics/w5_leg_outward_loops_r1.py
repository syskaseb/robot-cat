"""24 genuine tilted R10 half-turns, then separate outward D/G channels.

Do not place a polygon with a reversed tangent or shrink the bend radius.
The lower attempt struck P0. The planar escape occupies other source cages
and superposes its three wires. This family turns outward before travelling
along the body; each three-core family has separate lanes and oblique planes.
"""
from pathlib import Path
import json, math
import w5_leg_lower_fanouts_r1 as base
import w5_source_grips_native_r1 as owners_module
import w5_rounded_path as paths_module
from servo_fuse_inputs_r1 import save, sha
ROOT=base.ROOT
OUT=ROOT/'hardware/electronics/full-cat/w5-leg-outward-loops-r1'
RECIPES={}


def plan(rows):
    result=[]
    for old in rows:
        row=dict(old)
        if row['role']=='V': result.append(row); continue
        leg=row['loom'][:2]; side=1 if leg.endswith('L') else -1
        outward=-1 if leg.startswith('F') else 1
        peers=sorted((q for q in rows if q['loom'][:2]==leg and q['role']==row['role']),key=lambda q:q['waypoints_mm'][0][0])
        index=next(i for i,q in enumerate(peers) if q['wire']==row['wire'])
        rank=index if outward<0 else 2-index
        end=list(row['waypoints_mm'][0]); end[1]=side*30.5
        tail=list(row['waypoints_mm'][-1])
        theta=math.radians(22 if row['role']=='D' else 32)
        start=[end[0],side*24.5,end[2]]
        loop_end=[start[0]+outward*20*math.cos(theta),start[1],start[2]-20*math.sin(theta)]
        outer=side*((52 if row['role']=='D' else 64)+3*rank)
        escape=tail[0]-outward*25
        high=(137 if row['role']=='D' else 149)+3*rank
        points=[end,start,loop_end,[loop_end[0],outer,loop_end[2]],
            [escape,outer,loop_end[2]],[escape,outer,high],
            [tail[0],outer,high],[tail[0],tail[1],high],tail]
        row['waypoints_mm']=points
        row['body_entry_tangent']=[0,-side,0]
        row['ground_orientation_180_same_footprint']=False
        row['real_half_turn']=dict(radius_mm=10,tilt_deg=math.degrees(theta),straight_cage_entry_mm=6,
            centre=[start[0]+outward*10*math.cos(theta),start[1],start[2]-10*math.sin(theta)],
            note='points[1]..points[2] is a genuine arc, NOT a chord or a filleted reversal')
        RECIPES[tuple(tuple(p) for p in points)]=(side,outward,theta)
        result.append(row)
    assert len(result)==36
    return result


def main():
    import FreeCAD as A, Part
    import w5_exact_separation as prune
    synthetic=prune.validate(A,Part)
    original_rounded=paths_module.rounded
    def curved(A,Part,points,radius=10):
        key=tuple(tuple(float(v) for v in p) for p in points)
        if key not in RECIPES: return original_rounded(A,Part,points,radius)
        side,outward,theta=RECIPES[key]; assert radius==10
        end,start,finish=points[:3]
        mid=start+A.Vector(outward*10*math.cos(theta),-side*10,-10*math.sin(theta))
        arc=Part.Arc(start,mid,finish).toShape()
        rest=original_rounded(A,Part,points[2:],radius)
        edges=[Part.makeLine(end,start),arc,*rest.Edges]
        for a,b in zip(edges,edges[1:]):
            assert (a.valueAt(a.LastParameter)-b.valueAt(b.FirstParameter)).Length<1e-6
            assert (a.tangentAt(a.LastParameter)-b.tangentAt(b.FirstParameter)).Length<1e-6
        assert abs(arc.Curve.Radius-10)<1e-7
        wire=Part.Wire(edges); assert wire.isValid(); return wire
    original_owners=owners_module.current_owners
    def with_hoods(A,Part):
        owners,pins=original_owners(A,Part)
        for label,rel in (
            ('SourceWestHood','hardware/cad/studies/w5-source-roof-native-r5/WestHood_WORLD.brep'),
            ('SourceEastHood','hardware/cad/studies/w5-source-roof-native-r5/EastHood_WORLD.brep')):
            p=ROOT/rel; owners[label]=Part.read(str(p)); pins.append(p)
        for p in (ROOT/'hardware/electronics/full-cat/w5-source-roof-native-r3').glob('*WORLD.brep'):
            if p.name.startswith(('Bolt','Nut','Washers')):
                owners['SourceHoodHardware/'+p.stem]=Part.read(str(p)); pins.append(p)
        return owners,pins
    owners_module.current_owners=with_hoods; paths_module.rounded=curved
    # Use the same complete checker with exact conservative pruning, without
    # modifying its source while the previous worker is using that source.
    source=Path(base.__file__).read_text(encoding='utf-8')
    needle='                pairs+=1\n                try:'
    assert source.count(needle)==1
    source=source.replace(needle,'                pairs+=1\n                if _separated(a,b): continue\n                try:')
    context=dict(__file__=base.__file__,__name__='outward_checker_definition')
    exec(compile(source,base.__file__,'exec'),context)
    context.update(OUT=OUT,plan=plan,_separated=prune.separated)
    context['main']()
    p=OUT/'checks.json'; receipt=json.loads(p.read_text(encoding='utf-8'))
    receipt['status']=receipt['status'].replace('LOWER_FANOUT','OUTWARD_LOOP_FANOUT')
    receipt['source_sha256'][Path(__file__).relative_to(ROOT).as_posix()]=sha(Path(__file__))
    receipt['source_sha256'][Path(prune.__file__).relative_to(ROOT).as_posix()]=sha(Path(prune.__file__))
    receipt['all_new_source_hoods_included']=True
    receipt['nominal_half_turn_radius_mm']=10
    receipt['initial_six_mm_straight_and_arc_tangency_checked']=True
    receipt['surface_bounds_and_connected_solid_containment']=dict(prune.STATS)
    receipt['surface_prune_exact_kernel_validation']=synthetic
    save(p,receipt)


if __name__=='__main__': main()
