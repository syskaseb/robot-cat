from pathlib import Path
P=Path(__file__).parent
F=P.parent/'day19-connected-servo-usb-and-closure'
s=(F/'print-index.py').read_text()
s=s.replace("D=P.parent/'day19-simple-box-common-core'", "D=P.parent/'day19-connected-servo-usb-and-closure'").replace("P/'whole-cat19F.FCStd'; src=D/'whole-cat19E.FCStd'", "P/'whole-cat19G.FCStd'; src=D/'whole-cat19F.FCStd'").replace("(E/coupon","(F/coupon").replace("(E/q['step']","(F/q['step']").replace("source_19E_sha256","source_19F_sha256").replace("'F19_ForeCap','F19_RearCap','E19_ForeBase'","'F19_ForeCap','F19_RearCap','E19_RearBase'")
exec(s)
