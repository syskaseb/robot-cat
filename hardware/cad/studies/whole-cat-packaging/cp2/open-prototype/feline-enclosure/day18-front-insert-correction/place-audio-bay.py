"""Move complete audio groups and collect the occupied boundaries of the top-accessible bay."""
from pathlib import Path
import json
import FreeCAD as App
import Part

D=App.ActiveDocument
P=Path(__file__).parent
V=App.Vector
assert Path(D.FileName).resolve()==(P/"front-insert.FCStd").resolve()
assert not (P/"audio-bay.json").exists()
delta={}
def bbox(o):
    b=o.Shape.BoundBox
    return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def move(names,datum,center,rot):
    transform=App.Placement(V(*center)-rot.multVec(datum),rot)
    for n in names:
        obj=D.getObject(n)
        before=bbox(obj)
        obj.Placement=transform.multiply(obj.Placement)
        delta[n]=dict(before=before,after=bbox(obj),matrix=list(transform.toMatrix().A))
def single(n,center,rot):
    move([n],D.getObject(n).Shape.BoundBox.Center,center,rot)
# Both acoustic normals originally point outward from their old side walls.
# Bring the positive side to +Z, the negative side to +Z with inverse rotations.
single("Speaker",(56,52.5,161.0),App.Rotation(V(1,0,0),90))
mic=D.ReSpeakerLite_on_REMOVABLE_back
mic_names=[mic.Name]+[o.Name for o in D.Objects if o.Name.startswith("HB_MIC_") and o.ViewObject.Visibility]
move(mic_names,mic.Shape.BoundBox.Center,(60,-44.5,157.0),App.Rotation(V(1,0,0),-90))
# Put the amplifier next to the speaker but keep its original two mounting
# sets and sides together. Front connector wires then approach the dorsal bay.
amp=D.MAX98357A_amp
amp_names=[amp.Name]+[o.Name for o in D.Objects if o.Name.startswith("CB_AMP_") and o.ViewObject.Visibility]
move(amp_names,amp.Shape.BoundBox.Center,(23,5,151),App.Rotation(V(1,0,0),90))
# Reorient all eight previously high rear terminals to a single service row.
names=[pre+str(i) for pre in ("WAGO415_data__1_","WAGO415_data_1_") for i in (2,3,6,7)]
for i,n in enumerate(names):
    single(n,(49+i*11,-7,154.5),App.Rotation(V(0,0,1),90))
# Make full nominal mated-space references explicit. Values are design
# allocations at unbound ports, not caliper readings of a particular cable.
def field(n,lo,sz):
    obj=D.addObject("PartDesign::Feature",n)
    obj.Shape=Part.makeBox(*sz,V(*lo))
    obj.ViewObject.Visibility=False
    return obj
field("INSERT_AUDIO_USB_C_FULL_MATE_FIELD",(-9,-53,151),(26,16,12))
field("INSERT_AUDIO_USB_A_FULL_MATE_FIELD",(-20,14,101),(26,14,13))
field("INSERT_SPEAKER_TWO_BTL_TABS_FIELD",(-1,32,150),(9,16,13))
# Explicit approach from upper side for assembly, first 18 mm above the
# equipment, with the access cover removed; board bodies stay in the native.
field("INSERT_MIC_ACOUSTIC_FACE",(17,-62,162),(86,35,.6))
field("INSERT_SPEAKER_ACOUSTIC_FACE",(6,30,171.5),(100,45,.6))
(P/"audio-bay.json").write_bytes((json.dumps(dict(moves=delta,
    speaker_BTL=["EXT023 OUT+","EXT024 OUT-"],mic_USB="EXT025 USB_AUDIO separate USB-A to USB-C DATA; delivered length and plug sizes unknown",
    port_field_status="assumed full mating-space screens until independent physical sample; no change of supplier geometry",
    preserved_short_pair=["PBAY_P_REAR","PBAY_F_AUX"],soldered=["PCA9685_Adafruit815_PCB","E1_populated_prototype_board"],
    physical_PASS=False),indent=1)+"\n").encode())
D.Label="DAY18 FRONT INSERT - DORSAL AUDIO BAY TRIAL"
D.recompute()
D.save()
print("Audio bay and approaches saved",len(delta))
