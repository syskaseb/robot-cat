from common import *
s=(P/'leg-witness.py').read_text()
s=s.replace("[[-40.5,-102.4,40.98,.4,-58.05,76.28]]","[[-111.95,-103.1,37,13,-65,97]]").replace("d=Saved(H19/'whole-cat19H.FCStd')","d=Saved(native)").replace("wr('inherited-leg-witness.json',out)","out['scope']='actual front frame inside the changed closed lower side bay, retained 49 pose basis, only overlapping member/pose candidates';wr('well-leg-fit.json',out)")
exec(s)
