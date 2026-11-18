"""Land the independent audio plug on the second real Pi USB-A footprint and keep the complete data mate."""
from pathlib import Path
import json
import FreeCAD as A,FreeCADGui as G,Part
P=Path(__file__).parent;D=A.ActiveDocument;V=A.Vector
assert Path(D.FileName).resolve()==(P/"open-front.FCStd").resolve()
assert not (P/"audio-port-binding.json").exists()
field=D.INSERT_AUDIO_USB_A_FULL_MATE_FIELD;old=field.Shape.BoundBox
primary=D.CF17_PI_PRIMARY_USB_A_front.Shape.BoundBox
y=primary.Center.y
# The selected alternate front stack is source-defined in XY. The lower
# height follows the existing lower DATA receptacle as an installation datum.
shell_z=104.1
pl=A.Placement(V(0,y-old.Center.y,shell_z-old.Center.z),A.Rotation())
field.Placement=pl.multiply(field.Placement)
def b(s):
    a=s.BoundBox;return [a.XMin,a.YMin,a.ZMin,a.XMax,a.YMax,a.ZMax]
usb=[[6,y,shell_z],[13,y,shell_z],[60,y,shell_z],[60,52,shell_z],[60,52,156],[60,74,156],[62,74,171],[62,69,171]]
btl=json.loads((P/"audio-connections.json").read_bytes())["BTL"]["free_region"]
def line(pts):return Part.makePolygon([V(*p) for p in pts])
D.OPEN_AUDIO_CONNECTIONS.Shape=Part.makeCompound([line(usb),line(btl)])
data=D.Pi_USB_DATA_Delock_mating.Shape
record=dict(chosen_primary="CF17_PI_PRIMARY_USB_A_front",primary_bounds=b(D.CF17_PI_PRIMARY_USB_A_front.Shape),
    prior_field_at_Ethernet=[old.XMin,old.YMin,old.ZMin,old.XMax,old.YMax,old.ZMax],
    audio_field=b(field.Shape),fixed_DATA_mate=b(data),audio_vs_full_DATA_mate_mm3=field.Shape.common(data).Volume,
    USB_AUDIO_illustrative_free_region=usb,free_rectilinear_mm=sum(sum(abs(a-b) for a,b in zip(q,r)) for q,r in zip(usb,usb[1:])),
    full_audio_plug_fields={"A_length":26,"C_length":26},raw_audio_length=None,source_lower_slot_height="Project; actual stacked plug height and delivered mould unknown",
    support="Both separate complete body entries retained. Mating-field overlap falsifies simultaneous use of these two project bounds. No reduction of DATA stock, boots, or selected profile.",
    actual_fit=None,physical_PASS=False)
(P/"audio-port-binding.json").write_bytes((json.dumps(record,indent=1)+"\n").encode())
D.recompute();G.runCommand("Std_Save")
