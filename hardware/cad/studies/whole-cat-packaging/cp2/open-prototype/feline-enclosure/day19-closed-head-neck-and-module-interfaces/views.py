from pathlib import Path
import FreeCAD as A,FreeCADGui as G,json
P=Path(__file__).parent;D=A.ActiveDocument;V=A.Vector
assert Path(D.FileName).name=="whole-cat19C.FCStd"
v=G.activeDocument().activeView()
skins=["C19_OpenRearHelmet","C19_FixedShoulderShell","C19_FaceAndEars","C19_Iris_L","C19_Iris_R","C19_Pupil_L","C19_Pupil_R","C19_Nose","C19_Ear_1","C19_Ear_2","D19_ROUNDED_REAR_COWL"]
fields=["C19_ToFLeadSet","C19_FFC190","C19_HeadFactory250Pair","C19_JR300HeadPair","B19_TailJRUnderBank","B19_TailLaps"]
air=["Pi_components_and_cooling","CAMERA_FULL_INSTALLATION_CAPACITY_RELOCATED_NOT_PRINT","TOF_FULL14x26x26_INSTALLATION_CAPACITY_NOT_PRINT","D19_AUX_POPULATED_9P5_RESERVE","D19_MIC_FULL_HEIGHT_RESERVE"]
def show(ns,value):
    for n in ns:
        o=D.getObject(n)
        if o:o.ViewObject.Visibility=value
def draw(n,p,inside):
    show(skins,not inside);show(fields,inside);show(air,inside)
    z=V(*p);z.normalize();x=V(0,0,1).cross(z);x.normalize()
    v.setCameraOrientation(A.Rotation(x,z.cross(x),z,"ZXY").Q);v.fitAll();v.redraw();G.updateGui()
    v.saveImage(str(P/(n+".png")),1440,960,"White")
for n,p,inside in [("front",(-1,0,.035),False),("side",(0,-1,.035),False),("interior",(-1,-1,1.1),True),("three-quarter",(-1.4,-1,.55),False)]:draw(n,p,inside)
D.recompute();G.runCommand("Std_Save")
(P/"views-receipt.json").write_bytes((json.dumps(dict(objects=len(D.Objects),separate_installation_fields=fields,shells=skins,physical_PASS=False),indent=1)+"\n").encode())

