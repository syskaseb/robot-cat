from common import *
s=(G/'side-clearance.py').read_text();a=s.index('skirts=');b=s.index(';pairs=[]',a)
s=s[:a]+"skirts=[[-40.5,-102.4,40.98,.4,-58.05,76.28]]"+s[b:]
a=s.index(' for i,n,h,t in pairs:');s=s[:a]+''' from OCP.Bnd import Bnd_Box
 from OCP.BRepBndLib import BRepBndLib
 d=Saved(H19/'whole-cat19H.FCStd')
 material=BRepAlgoAPI_Common(d.shape('H19_FrontFrame'),solid[0]).Shape()
 for i,n,h,t in pairs:
    tr=gp_Trsf();tr.SetValues(*t[:3,:].flatten());sh=old.shape(n).Moved(TopLoc_Location(tr))
    result=BRepAlgoAPI_Common(sh,material).Shape();pr=GProp_GProps();BRepGProp.VolumeProperties_s(result,pr)
    if pr.Mass()>.00001:
        bb=Bnd_Box();BRepBndLib.AddOptimal_s(result,bb,False,False)
        out['material_intersections'].append(dict(pose=i,member=n,common_mm3=pr.Mass(),extent=[*bb.CornerMin().Coord(),*bb.CornerMax().Coord()]))
wr('inherited-leg-witness.json',out);print(len(out['material_intersections']))
'''
exec(s)
