"""Export and independently reopen grounded first-fit meshes, no slicer."""
from pathlib import Path
import json
from collections import Counter
from struct import Struct
from head import *
import Mesh
import MeshPart

ROOT=HERE/"STL"
FPS=(
    (MASK,"22_Face","D19D_Face","graphite","rear rim down, face up"),
    (BACK,"22_PitchBack","D19D_PitchBack","graphite","front mating rim down"),
    (CARRY,"22_OpticsCarrier","D19D_OpticsCarrier","graphite","lowest load foot down"),
    ("D21_Ear_L","22_Ear_L","D19D_Ear_L","graphite","inner bowl up"),
    ("D21_Ear_R","22_Ear_R","D19D_Ear_R","graphite","inner bowl up"),
    ("D21_Ear_Inset_L","22_Ear_Inlay_L",None,"dark graphite","back of inlay down"),
    ("D21_Ear_Inset_R","22_Ear_Inlay_R",None,"dark graphite","back of inlay down"),
    ("D21_Nose","22_Nose","D19D_Nose","brown-black","stem down"),
    ("D21_Rim_Cam","22_Iris_Cam_L","D19D_Iris_L","amber","flat seating face down"),
    ("D21_Rim_ToF","22_Iris_ToF_R","D19D_Iris_R","amber","flat seating face down"),
    ("D21_Insert_Cam","22_Insert_Cam_L","D19D_Pupil_L","charcoal","rear pad down"),
    ("D21_Insert_ToF","22_Insert_ToF_R","D19D_Pupil_R","charcoal","rear pad down"),
    ("D22_CSI_ParkingClip","22_CSI_ParkingClip",None,"graphite","side of riser down"))
MOUNTS={
  MASK:"Four M2×16 stations in the complete moving head. Two transverse joints to carrier; two axial joints to rear rim. Root hardware installed during bench assembly.",
  BACK:"Two M2×16, two AF4 nuts, four OD5×0.5 washers. Bearing tabs and two driver passages. Negative screw lies above retained factory pitch-lead opening.",
  CARRY:"Source pitch shaft, horn and crosspin, two transversely seated mask M2×16; reuse two M2×12 camera assemblies and two M2×10 ToF assemblies with source washers and nuts.",
  "D22_CSI_ParkingClip":"Positive-Y lip of existing D20_POST_Aft_Slotted rail. Form-fitting shoe and thin cured compatible adhesive. Soft closure ties leave full cable slip.",
  "D21_Ear_L":"Matching temple seating perimeter and bonded hidden root/fillet.",
  "D21_Ear_R":"Matching temple seating perimeter and bonded hidden root/fillet.",
  "D21_Nose":"Existing Ø6.10 locating stem in Ø6.48 hole. Bond post and rear shoulder.",
  "D21_Ear_Inset_L":"Existing positive stopped pocket, roughen hidden back and bond inlay to ear shell.",
  "D21_Ear_Inset_R":"Existing positive stopped pocket, roughen hidden back and bond inlay to ear shell.",
  "D21_Rim_Cam":"Existing toroidal front ring, spigot Ø38.20 in Ø38.74 seat. Glue at three concealed land points.",
  "D21_Rim_ToF":"Existing toroidal front ring, spigot Ø38.20 in Ø38.74 seat. Glue at three concealed land points.",
  "D21_Insert_Cam":"Dark insert Ø34.56, keyed by ring bore and stepped mask; tiny compatible adhesive beads on perimeter, outside field.",
  "D21_Insert_ToF":"Dark insert Ø34.56, keyed by ring bore and stepped mask; tiny compatible adhesive beads on perimeter, outside both ToF windows."}
OPS={
  MASK:["Dry-fit carrier with steel; gauge Ø2.32 holes; trim or ream by hand if required.","Deburr captive square nut and washer pockets; keep outside finish. Install inserts and bonded ears before optics."],
  BACK:["Clear both Ø5.5 driver entries and bore only if printed undersize. Do not fill the negative MG lead relief."],
  CARRY:["Clean the through M2 holes and flat washers seats at both optical modules; retain source stand-off heights."],
  "D22_CSI_ParkingClip":["Deburr shoe and wet-sand slip slot edges. Verify 7 mm movement in guide before applying adhesive.","Keep epoxy and tie out of POST adjustment and release envelope."]}
COMMON_OP=["Remove supports and burrs only on intended underside; dry-fit the original positive stops before adhesive."]

def shape(n,unchanged):
    if n in unchanged:return unchanged[n]
    s=Part.Shape()
    s.importBrepFromString((KIT/(n+".brep")).read_text("ascii"))
    return s

def orientation(n):
    if n==BACK:return App.Rotation(X,Z)
    if n==CARRY:return App.Rotation()
    if n=="D22_CSI_ParkingClip":return App.Rotation(Y,Z)
    return App.Rotation(X,-Z)

def mesh_details(path):
    data=path.read_bytes()
    facet=Struct("<12fH")
    assert len(data)>84 and len(data)==84+50*int.from_bytes(data[80:84],"little"),path
    edges=Counter()
    signed=0.
    mm=[[],[],[]]
    for row in facet.iter_unpack(data[84:]):
        pts=[tuple(round(p,5) for p in row[i:i+3]) for i in (3,6,9)]
        assert len(set(pts))==3
        for i in range(3):
            mm[i].extend(q[i] for q in pts)
        for a,b in zip(pts,pts[1:]+pts[:1]):
            edges[tuple(sorted((a,b)))]+=1
        a,b,c=(V(*q) for q in pts)
        signed+=a.dot(b.cross(c))/6
    assert edges and set(edges.values())=={2},(path,len(edges),Counter(edges.values()))
    reopened=Mesh.Mesh(str(path))
    assert reopened.isSolid() and reopened.CountFacets==len(data[84:])//50 and signed>0.,path
    # A print has one connected material body. A fully enclosed cavity
    # appears as a second, inward-oriented shell (the two hollow cheeks).
    # Reject an extra outward shell rather than incorrectly rejecting voids.
    shell_volumes=[]
    for shell in reopened.getSeparateComponents():
        points,facets=shell.Topology
        volume=sum(points[i].dot(points[j].cross(points[k])) for i,j,k in facets)/6
        shell_volumes.append(round(volume,3))
    assert sum(v>0 for v in shell_volumes)==1 and not any(v==0 for v in shell_volumes),(path,shell_volumes)
    return {"triangles":reopened.CountFacets,"watertight":True,"material_components":1,
         "surface_shell_signed_volumes_mm3":shell_volumes,"positive_mesh_mm3":round(signed,3),
         "stl_bbox_mm":[round(min(v),5) for v in mm]+[round(max(v),5) for v in mm]}

def retired_reference_names():
    return [f"F3_HEAD_{group}_{side}_{tag}"
            for group,length in (("BACK",16),("ROOT",12))
            for side in ("1","m1")
            for tag in (f"FULL_M2x{length}","FULL_NUT","HEAD_WASHER","NUT_WASHER")]

def export():
    ROOT.mkdir(exist_ok=True)
    unchanged=saved(ASSORTMENT)
    done=[]
    moving_mass=[]
    for name,stem,old,colour,face in FPS:
        s=solid(shape(name,unchanged),name)
        if name!="D22_CSI_ParkingClip":
            moving_mass.append((s.Volume,s.Solids[0].CenterOfMass))
        rot=orientation(name)
        p=moved(s,App.Placement(V(),rot))
        bb=p.optimalBoundingBox()
        translation=V(-bb.XMin,-bb.YMin,-bb.ZMin)
        p.translate(translation)
        for linear,angular in ((.065,.12),(.09,.19),(.045,.10)):
            m=MeshPart.meshFromShape(Shape=p.cleaned(),LinearDeflection=linear,
                                     AngularDeflection=angular,Relative=False)
            meshing={"linear_mm":linear,"angular_rad":angular,"raw_solid":m.isSolid()}
            if not m.isSolid():
                count=m.CountFacets
                m.fixIndices()
                m.removeDuplicatedPoints()
                m.removeDuplicatedFacets()
                m.fixDegenerations()
                m.harmonizeNormals()
                meshing.update(cleaned_facets=count-m.CountFacets)
            print("mesh",name,m.CountFacets,m.isSolid(),meshing,flush=True)
            if m.isSolid():break
        assert m.isSolid(),name
        # Ground the actual mesh, not only the analytical surface.
        b=m.BoundBox
        m.translate(-b.XMin,-b.YMin,-b.ZMin)
        f=ROOT/(stem+".stl")
        m.write(str(f))
        proof=mesh_details(f)
        dims=[round(proof["stl_bbox_mm"][i+3]-proof["stl_bbox_mm"][i],4) for i in range(3)]
        assert abs(proof["stl_bbox_mm"][2])<.0001
        limits=[dims[0]+16,dims[1]+16,dims[2]+8]
        assert max(limits)<256
        assert .98<proof["positive_mesh_mm3"]/p.Volume<1.02,(name,p.Volume,proof)
        bed=[list(rot.Q),list(translation)]
        done.append({"filename":f.relative_to(HERE).as_posix(),"object":name,
            "quantity":1,"replaces":None if old is None else "STL/"+old+".stl",
            "material":"PETG (verify adhesive compatibility with actual filament)","colour":colour,
            "orientation":face,"native_to_bed_rotation_xyzw_and_translation_mm":bed,
            "stl_bounding_mm":dims,"actual_with_allowance_mm":limits,
            "allowances":{"brim_per_side_mm":8,"additional_support_height_mm":8},
            "mounts":MOUNTS[name],"required_ops":OPS.get(name,COMMON_OP),
            "volume_mm3":round(s.Volume,3),"meshing":meshing,"sha256":sha(f),**proof})
        print(stem,dims,proof["triangles"],flush=True)
    volume=sum(v for v,_ in moving_mass)
    cg=sum((p*v for v,p in moving_mass),V())/volume
    r=(cg-V(-159,0,121)).Length
    datum={"printed_moving_parts_solid_volume_cm3":round(volume/1000,3),
           "solid_petg_reference_density_g_cm3":1.27,
           "fully_dense_printed_mass_reference_g":round(volume*.00127,2),
           "printed_solid_centroid_working_frame_mm":list(cg),
           "distance_to_pitch_datum_mm":round(r,2),
           "actual_printed_mass_g":None,"actual_motion_and_load":None}
    write_json(HERE/"head-print-index.json",{"name":"22 head first-fit replacement set",
        "basis_20H_unchanged_outside_exact_replacements":True,
        "native":"whole-cat22-head-first-fit.FCStd","units":"mm",
        "parts":done,"moving_mass_reference":datum,"conditional_prototype_first_fit":True,
        "retired_print_slugs":[r["replaces"] for r in done if r["replaces"]],
        "retired_native_names":["D19D_Face","D19D_OpticsCarrier","D19D_Ear_L","D19D_Ear_R",
          "D19D_Iris_L","D19D_Iris_R","D19D_Pupil_L","D19D_Pupil_R","D19D_Nose",
          "D21_FFC_Screen_Unqualified","D21_Mask_M2_reference_L","D21_Mask_M2_reference_R",*retired_reference_names()],
        "superseded_existing_native_geometry":[MASK,BACK,CARRY],
        "stock_needs":{"M2x16":4,"M2_AF4_nuts":4,"OD5x0.5_M2_washers":8,
        "selected_camera_M2x12_reused":2,"selected_ToF_M2x10_reused":2,
        "CSI_Standard_Standard_300mm":1,"inventory_verified":False},
        "actual_cut":None,"actual_fit":None,"actual_supplementary_steel_inventory":None,
        "physical_pass":False})

if __name__=="__main__":
    export()
