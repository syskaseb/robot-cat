import FreeCAD as A,Part,json,pathlib
D=A.ActiveDocument;P=pathlib.Path(__file__).parent;V=A.Vector
def wr(n,x):(P/n).write_bytes((json.dumps(x,indent=2)+'\n').encode())
o=D.getObject('F2_COMMON_PI_BUS_PCA_RECEIVER');old=o.Shape.copy()
# The raw126 is exactly the lower PCA bridge at Z130..131 inside a PROJECT24-high install box.
# Replace that crossing bridge by an upper load rib, retaining the full install opening and all four PCB pads.
cut=Part.makeBox(42.5,3.2,3.2,V(7.75,25.45,129.9))
s=old.cut(cut).fuse(Part.makeBox(6,3,31.225,V(38.055,25.55,131.775))).removeSplitter()
# Actual complete standard countersunk heads provide nominal conical bearing seats. They are not cut/shrunk.
heads=[q for q in D.Objects if q.Name.startswith('CF17_BUS_CSK10_') and q.ViewObject.Visibility]
for q in heads:s=s.cut(q.Shape)
s=s.removeSplitter();o.Shape=s;D.recompute();D.save()
board=D.getObject('N17_PRIMARY_BUS_BOARD_NO_EXTRA_BOM').Shape
rows=[]
for x in [10.5,47.5]:
 for y in [22.5,50.5]:
  pad=Part.makeCylinder(4,3,V(x,y,104)).cut(Part.makeCylinder(1.1,3,V(x,y,104)))
  if x<11:pad=pad.cut(Part.makeBox(8,50,10,V(0,10,100)))
  slice=Part.makeCylinder(4,.002,V(x,y,107))
  rows.append(dict(axis=[x,y],nominal_PCB_contact_area_mm2=board.common(s.common(slice)).Volume/.002,board_common_mm3=board.common(s).Volume))
root=P.parents[6]/'electronics/full-cat/pi-bus-primary-r1'
# Resolve the cached reference from the known mechanical repository, never import/heal its invalid117 aggregate.
root=pathlib.Path(r'C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/electronics/full-cat/pi-bus-primary-r1')
cull=json.loads((P/'BUS-primary-underpad-numeric-cull.json').read_text());local=[]
for row in cull['underboard_parts_bbox_candidates']:
 f=root/(row['name']+'.brep')
 if not f.exists():local.append(dict(name=row['name'],status='NO_CACHED_BREP'));continue
 q=Part.Shape();q.read(str(f));q.translate(V(8,20,108.6))
 if not q.isValid():local.append(dict(name=row['name'],status='INVALID_NOT_BOP'));continue
 local.append(dict(name=row['name'],gap=s.distToShape(q)[0],common=s.common(q).Volume))
r=dict(raw_126_retained_in_prior='current-receiver-selected-neighbors.json in frozen638',raw_cause='PCA lower bridge inside installation allocation130..131, not delivered component contact',source_primary_board_bounds=[7.98790452,19.98790452,107.00000066,50.0120826,53.0120752,108.6],source_all117_bounds_only=[7.9879,19.1958,105,50.0121,53.0121,119.6],replacement='open lower BUS access, add X38.055..44.055 upper rib to real PCA rail; sourcePCB and sourcefullsteel unchanged',current_install_field_common=s.common(D.getObject('BUS25514_installed').Shape).Volume,valid=s.isValid(),solids=len(s.Solids),planned_old_bridge_retired_mm3=old.common(cut).Volume,old_material_missing_outside_explicit_bridge_and_full_conical_seats_mm3=old.cut(s).cut(cut).cut(Part.makeCompound([q.Shape for q in heads])).Volume,source_Pi_carrier_missing_mm3=D.getObject('D18C_COMMON_PI_OPEN_CARRIER').Shape.cut(s).Volume,pads=rows,nearby_valid_source_components=local,complete_CSK_steel=[dict(name=q.Name,common=s.common(q.Shape).Volume) for q in heads],physical_PASS=False)
wr('BUS-real-primary-interface-and-fullsteel.json',r);print(json.dumps(r))
