"""Allow for the full insulated tube around segmented service footprints.

R2 leaves a real0.671mm3 diagonal W053 tube-corner contact. Face rectangles
are not a sufficient sweep envelope for the enclosed conductor volume.
Retain each existing route; add its declared CAD insulation radius in XY,
not an unexplained exemption or another bend. Keep the original mount zones.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_cover_main_service_r2.py')
raw=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert raw.rstrip().endswith(tail)
ns=dict(__file__=str(parent),__name__='r2_definition_only')
exec(compile(raw.rstrip()[:-len(tail)],str(parent),'exec'),ns)
code=ns['code'].replace('servo-fuse-cover-main-service-r2','servo-fuse-cover-main-service-r3')
def replace(old,new):
    global code
    assert old in code,old[:100]
    code=code.replace(old,new)
replace("        for key,s in chosen.items():\n            covered.append(key)", "        radii={}\n        for key,s in chosen.items():\n            covered.append(key)\n            radius=2.5 if 'factory' in key else 2.1 if 'extension' in key else 0.0\n            radii[key]=radius")
replace("dims=[max(q.XLength,.001),max(q.YLength,.001),q.ZMax-bottom]", "dims=[max(q.XLength,.001)+2*radius,max(q.YLength,.001)+2*radius,q.ZMax-bottom]")
replace("(q.XMin,q.YMin,bottom)", "(q.XMin-radius,q.YMin-radius,bottom)")
replace("[q.XMin-.3,q.YMin-.3,bottom-.3,q.XMax+.3,q.YMax+.3,q.ZMax+.3]", "[q.XMin-radius-.3,q.YMin-radius-.3,bottom-.3,q.XMax+radius+.3,q.YMax+radius+.3,q.ZMax+.3]")
replace("lo,hi=sorted((side*85,side*97))", "lo,hi=sorted((side*88,side*102))")
replace("assembly_ties_cut=49,mounts=mounts,", "assembly_ties_cut=49,mounts=mounts,declared_CAD_tube_radii_mm=radii,")
replace("individual wire-face projections extended to bottom", "segmented wire-face projections plus declared insulation radius in XY extended to bottom")
replace("        # Read the completed R8 recipe", "        pins['tools/electronics/servo_fuse_cover_main_service_r2.py']=sha(ROOT/'tools/electronics/servo_fuse_cover_main_service_r2.py')\n        # Read the completed R8 recipe")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
