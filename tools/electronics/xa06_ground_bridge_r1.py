"""Construct the fixed G_AUX-to-G_TAIL bridge above the XB11 splice.

Single new route, with end restraints on existing WAGO mount ties. No new
print, old route rerun, body-wall hole or moving-cable assumption.
"""
import json, math, sys
from pathlib import Path
import xb11_upstream_route as recipe
sys.path.insert(0,str(recipe.ROOT/'tools/cad'))
from check_main_p0_placement import SavedShapes,prop
A,Part,ROOT=recipe.A,recipe.Part,recipe.ROOT
OUT=ROOT/'hardware/electronics/full-cat/xa06-ground-bridge-r1'
def dump(n,v):(OUT/n).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')

def main():
    assert not (OUT/'checks.json').exists(),'Preserve saved geometry'
    OUT.mkdir(exist_ok=True)
    plan=dict(from_endpoint='G_TAIL.1',to_endpoint='G_AUX.5',electrical_direction='G_AUX.5 -> G_TAIL.1 (geometry built in reverse)',
        wire='HELU23501 black1mm2 OD2.5',rail='power GND; NOT signal-only return',
        fixed_radius_mm=15,waypoints_mm=[[19.5,-72,113.5],[45,-72,113.5],[45,-72,145],
                [80,-72,145],[80,-72,113.5],[95,-72,113.5]],
        final='two opposite R15 arcs from X95/Y-72 to Y-69, then straight to X110.5/Y-69/Z113.5',
        source_cage_positions_provisional=True,
        restraints='Two new T18I around insulated leads immediately outside terminal mouths, interlinked to existing G_TAIL/G_AUX mounting ties. No unsupported standalone wire tie.',
        support='91mm mouth-to-mouth span shaped as a raised fixed arch; restrained at both terminal bodies. Keep arch away from PCB/covers; delivered silicone springback/sag dry-fit before power.',
        protection='Combined tail/PWM return; positive AUX6/PWM5 never joined. Return ampacity and source/branch fault coordination still require closure.',
        new_stls=0,new_fcstd=0,new_skus=0,additional_ties=2,physical_pass=False,phase1_complete=False)
    dump('plan.json',plan)
    pv=[A.Vector(*p) for p in plan['waypoints_mm']];p=recipe.rounded(pv,15);edges=list(p.Edges)
    theta=math.acos(1-3/30);r=15;start=A.Vector(95,-72,113.5)
    mid=A.Vector(95+r*math.sin(theta),-72+r*(1-math.cos(theta)),113.5)
    end=A.Vector(95+2*r*math.sin(theta),-69,113.5)
    c1=A.Vector(95,-57,113.5);c2=A.Vector(end.x,-84,113.5)
    def arc(a,b,c):return Part.Arc(a,c+((a-c)+(b-c)).normalize()*r,b).toShape()
    edges.extend([arc(start,mid,c1),arc(mid,end,c2),Part.makeLine(end,A.Vector(110.5,-69,113.5))])
    path=Part.Wire(edges);assert path.isValid()
    tube=path.makePipeShell([Part.Wire([Part.makeCircle(1.25,pv[0],A.Vector(1,0,0))])],True,False)
    assert tube.isValid() and len(tube.Solids)==1
    tube.exportBrep(str(OUT/'XA06_DESIGN.brep'))
    reader=SavedShapes();rows=[]
    def test(name,s):
        for i,solid in enumerate(s.Solids):
            if not recipe.overlap(solid.BoundBox,tube.BoundBox):continue
            assert solid.isValid(),name
            v=recipe.volume(solid.common(tube))
            rows.append(dict(obstacle=name,solid=i,positive_mm3=v,
                distance_mm=solid.distToShape(tube)[0] if v<1e-5 else 0))
    e6=ROOT/'hardware/cad/assembly/RobotCatNarrowRimEars.FCStd';objects=reader.doc(e6)
    for link in prop(objects['RobotCatAssembly24'],'Group').findall('.//Link'):
        wrapper=link.get('value')
        if not wrapper.startswith('Rigid_'):continue
        name=prop(objects[wrapper],'Group').findall('.//Link')[0].get('value')
        if name in ('ShellMounted20','Part__Feature038'):continue
        s=reader.shape(e6,name);s.Placement=reader.placement(objects[wrapper])*s.Placement
        test(name,s)
    for file,name in [('hardware/cad/studies/xb11-hangers-r2/DeckXB11Hangers.FCStd','Deck'),
            ('hardware/cad/studies/aux-splice-shelf-r2/AuxSpliceShelfR2.FCStd','Shelf'),
            ('hardware/cad/studies/upper-cover-mount-r1/RaisedUpperCoverMount.FCStd','CoverMountHole4')]:
        test(file+'#'+name,reader.shape(ROOT/file,name))
    s=reader.shape(ROOT/'hardware/cad/studies/full-cat-board-carrier/service-access-r1/CarrierServicePorts.FCStd','Carrier')
    s.translate(A.Vector(21,0,144));test('selectedCarrier_world21_0_144',s)
    for name,b in {'G_TAIL_design':[.5,-87,109,19.5,-57,118],
        'G_AUX_design':[110.5,-84,109,129.5,-54,118], 'XB11_design':[50,-81.5,105,68.3,-68.5,113.15],
        'F_HY_design':[0,-85.6,90,20,-64.4,102]}.items():test(name,recipe.box(b))
    for file in ('hardware/electronics/full-cat/xb11-upstream-route-r3/XB11_DESIGN.brep',
                 'hardware/cad/studies/aux-splice-shelf-r2/HELU23502_DESIGN.brep',
                 'hardware/cad/studies/aux-splice-shelf-r2/factory16AWG_DESIGN.brep'):
        s=Part.Shape();s.read(str(ROOT/file));test(file,s);reader.hashes[file]=recipe.sha(ROOT/file)
    hits=[r for r in rows if r['positive_mm3']>1e-5]
    assert all(recipe.sha(ROOT/n)==h for n,h in reader.hashes.items())
    samples=[[v.x,v.y,v.z] for e in path.Edges for v in e.discretize(Deflection=.1)]
    dump('checks.json',dict(status='ROUTE_REJECTED' if hits else 'NOMINAL_FIXED_BRIDGE_CANDIDATE',
        source_sha256=reader.hashes,plan_sha256=recipe.sha(OUT/'plan.json'),
        script_sha256=recipe.sha(Path(__file__)),path_length_mm=path.Length,exact_pairs=rows,hits=hits,
        geometry_nominal_clear=not hits,centerline_samples_mm=samples,new_stls=0,
        physical_pass=False,phase1_complete=False))
    print(json.dumps(dict(hits=hits,path_length_mm=path.Length,pairs=len(rows))),flush=True)

if __name__=='__main__':main()
