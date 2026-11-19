from pathlib import Path
P=Path(__file__).parent;E=P.parent/'day19-simple-box-common-core'
exec((E/'core.py').read_text().split('# Each board/power cluster')[0].replace('19E.FCStd','19I.FCStd'))
# Protect the opening between the fixed side wall and the moving cheek. A straight
# fixed return beside the mouth transfers into the existing wall along its full edge.
poly=[(-177,114),(-170,100.2),(-143,100.2),(-143,111.4),(-152.5,111.4),(-152.5,198.7),(-166,198.7),(-177,180)]
def leaf(poly,y,thick):
 pts=[V(x,y,z) for x,z in poly];return Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(0,thick,0))
wing=leaf(poly,-114,1.55)
wing=wing.fuse(box(-169.3,-114,100.25,25.9,13.8,1.6)).fuse(box(-165.8,-114,197.1,13.25,12.5,1.55)).removeSplitter()
frame=sh('H19_FrontFrame');s=frame.Solids[0].fuse(wing,.00001).removeSplitter()
assert s.isValid() and len(s.Solids)==1
wr('neck-return.json',dict(added_volume=s.Volume-frame.Volume,material_bounds=bounds(wing),wall_join_mm3=wing.Volume+frame.Volume-s.Volume,existing_fixed_wall_x=-154,front_edge_x=-177,leg_upper_bound=96.62))
wing.exportBrep(str(P/'neck-material.tmp.brep'));D.getObject('H19_FrontFrame').Shape=s;D.recompute();D.save()
