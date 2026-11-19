from pathlib import Path
import sys
P=Path(__file__).parent;E=P.parent/'day19-simple-box-common-core'
s=(E/'final-motion.py').read_text().replace('whole-cat19E.FCStd','whole-cat19G.FCStd').replace("'S0_body','B19_TailMatedPair'","'F19_RearCap'").replace("cache={","pairs.append(('BR_FLANK_HP_PAIR',['E19_FrontShroud','E19_ForeLid'],[-130,0,127],[-20,0,20]))\ncache={")
exec(s)
