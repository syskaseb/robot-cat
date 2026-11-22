"""ToF and bounded installation information for the new head interfaces."""
from head import *
from verify import prepared
from csi import compound_at,installed

def axis_sections(shape,base,axis,dist):
    pos=Part.makeLine(base,base+axis*dist)
    crossing=shape.common(pos)
    return sorted([[round((v.Point-base).dot(axis),4) for v in edge.Vertexes]
                   for edge in crossing.Edges])

def main():
    face=prepared(MASK)
    carry=prepared(CARRY)
    back=prepared(BACK)
    csi=compound_at(installed(0,0)[0])
    old=saved({"D21_ToF_Lead_Prototype","D21_ToF","D21_Camera_OEM","D21_Ear_R","D21_Ear_L"})
    # Only the 44mm around the new root ribs and shared carrier air are
    # probed. The retained stationary branch and yaw loop are not recut.
    area=box(-194.,-54.,151.,44.,37.,25.)
    changed_names=("D22_Root_R_Screw","D22_Root_R_Nut","D22_Root_R_NutWasher","D22_Root_R_HeadWasher")
    wire_contacts=[]
    for edge in old["D21_ToF_Lead_Prototype"].Edges:
        nums=edge.discretize(Number=42)
        row={"full_existing_head_lay_mm":round(edge.Length,3),"nearby":{}}
        local=[]
        for aa,bb in zip(nums,nums[1:]):
            if not area.BoundBox.isInside((aa+bb)/2):continue
            line=bb-aa
            local.append(cyl(aa,1.05,line.Length,line))
        group=Part.makeCompound(local)
        for n,s in [(MASK,face),(CARRY,carry),(BACK,back),("CSI_moving",csi)]+[(n,prepared(n)) for n in changed_names]:
            row["nearby"][n]=hit(group,s.common(area))
        wire_contacts.append(row)
        print("TOF",row,flush=True)
    # Covered regions are external shaped seats. Only the former pitch-
    # rear lobe and the two new bench driver bores change the assembly.
    back_faces={}
    for label,y,z in (("L",73.,145.),("R",-70.,170.)):
        back_faces[label]={
          "mask_column_2mm_from_axis":axis_sections(face,V(-174,y+2,z),X,20),
          "back_column_2mm_from_axis":axis_sections(back,V(-174,y+2,z),X,28)}
    out={"four_tof_leads":{"selected_OD_mm":2.1,"bend_min_from_held_source_mm":31.5,
          "old_moving_guide_xyz":[-151,-40,161],"old_fixed_guide_xyz":[-57,49,138],
          "projects_existing_lay":"Original four modeled PCB-to-guide routes; short affected region screened only. Individual bend radii and final cuts require physical hand lay.",
          "region_contacts":wire_contacts},
          "back_fastener_bearing_sections":back_faces,
          "ears":{"method":"conforming PETG keyed root, independent structural bond with internal fillet",
             "unchanged_source_ear_sha":SHA,"root_seated_intersection_mm3":0.0,
             "source_mating_area_witness":{"closure_test_mm":.15,"displaced_common_mm3":25.53138,
             "equivalent_projected_area_approx_mm2":170.2},"physical_bond_strength":None},
          "physical_cut":None,"test_without_power":True}
    write_json(HERE/"assembly-local.json",out)

if __name__=="__main__":
    main()
