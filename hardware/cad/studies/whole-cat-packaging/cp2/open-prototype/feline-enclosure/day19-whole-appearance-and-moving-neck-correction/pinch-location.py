"""Locate interference of the named pitch-back and yaw-hood joint at neutral."""
from pathlib import Path
import runpy,json
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepBndLib import BRepBndLib
from OCP.Bnd import Bnd_Box
P=Path(__file__).parent;D=runpy.run_path(str(P.parent/"day18-front-insert-correction/saved-front.py"))["Saved"](P/"whole-cat19D.FCStd")
shape=BRepAlgoAPI_Common(D.shape("D19D_PitchBack"),D.shape("D19D_YawHood")).Shape();b=Bnd_Box();BRepBndLib.AddOptimal_s(shape,b,False,False)
(P/"pinch-location.json").write_bytes((json.dumps(dict(a="D19D_PitchBack",b="D19D_YawHood",neutral_common_bounds=[*b.CornerMin().Coord(),*b.CornerMax().Coord()]),indent=1)+"\n").encode())

