"""Sample actual planar sections of the bench hardware for the fit sheet."""
from head import *
from verify import prepared

def sample(s, plane, height, coords):
    return [[[round(getattr(p,c),4) for c in coords]
             for p in edge.discretize(Deflection=.05)]
            for wire in s.slice(plane,height) for edge in wire.Edges]

names=(MASK,BACK,CARRY,"D22_Root_L_Screw","D22_Root_R_Screw",
       "D22_Root_L_Nut","D22_Root_R_Nut","D22_Back_L_Screw","D22_Back_R_Screw",
       "D22_Back_L_Nut","D22_Back_R_Nut","D22_CSI_ParkingClip","D22_FFC_Parked")
shapes={n:prepared(n) for n in names}
figures=[
  {"name":"Maska i nośnik | Z = 155 mm","coords":"xy","window":[-195,-165,-45,45],
   "groups":(MASK,CARRY,"D22_Root_L_Screw","D22_Root_R_Screw","D22_Root_L_Nut","D22_Root_R_Nut"),"height":155.},
  {"name":"Tył, lewy zamek | Z = 145 mm","coords":"xy","window":[-175,-144,65,81],
   "groups":(MASK,BACK,"D22_Back_L_Screw","D22_Back_L_Nut"),"height":145.},
  {"name":"Tył, prawy zamek | Z = 170 mm","coords":"xy","window":[-175,-144,-81,-61],
   "groups":(MASK,BACK,"D22_Back_R_Screw","D22_Back_R_Nut"),"height":170.},
  {"name":"Zapas CSI | Y = −16,5 mm","coords":"xz","window":[-138,-56,98,180],
   "groups":("D22_CSI_ParkingClip","D22_FFC_Parked"),"height":-16.5}]
for p in figures:
    coord=p["coords"]
    ax=Z if coord=="xy" else Y
    p["traces"]={n:sample(shapes[n],ax,p["height"],coord) for n in p.pop("groups")}
write_json(KIT/"cutaway-profiles.json",figures)
