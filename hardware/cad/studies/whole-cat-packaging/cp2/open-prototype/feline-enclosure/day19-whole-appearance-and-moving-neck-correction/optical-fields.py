"""Carry both full clock-bound source optical solids to the new face and two rotating seams."""
from pathlib import Path
P=Path(__file__).parent;C=P.parent/"day19-closed-head-neck-and-module-interfaces"
s=(C/"optical-apertures.py").read_text().replace("whole-cat19C.FCStd","whole-cat19D.FCStd")
for a,b in {"C19_FaceAndEars":"D19D_Face","C19_MovingOpticsCarrier":"D19D_OpticsCarrier","C19_OpenRearHelmet":"D19D_PitchBack","C19_Nose":"D19D_Nose","C19_Ear_1":"D19D_Ear_R","C19_Ear_2":"D19D_Ear_L","C19_Iris_":"D19D_Iris_","C19_Pupil_":"D19D_Pupil_","C19_FixedShoulderShell":"D19D_Shoulder"}.items():s=s.replace(a,b)
s=s.replace('out=dict(source=', '''    for p in [-10,0,10]:
        R,T=transforms(0,p)["pitch"];tr=gp_Trsf();tr.SetValues(*(np.column_stack([R,T]).ravel().tolist()))
        moved=BRepBuilderAPI_Transform(shape,tr,False).Shape()
        rows.append(dict(field=f,member="D19D_YawHood",pitch=p,common_mm3=common(moved,D.shape("D19D_YawHood"))))
out=dict(source=''')
exec(s)

