from pathlib import Path
P=Path(__file__).parent;E=P.parent/'day19-simple-box-common-core'
s=(E/'final-motion.py').read_text().replace('whole-cat19E.FCStd','whole-cat19F.FCStd').replace("'S0_body','B19_TailMatedPair'","'F19_RearCap','B19_TailMatedPair','E19_BUS_PCB','E19_BUS_population'").replace("'E19_FrontShroud','E19_ForeLid'","'E19_FrontShroud','E19_ForeLid','F19_ForeCap'")
s=s.replace('cache={n:mesh(n)',"pairs.append(('BR_FLANK_HP_PAIR',['E19_ForeBase','E19_FrontShroud','E19_ForeLid','F19_ForeCap'],[-130,0,127],[-20,0,20]))\ncache={n:mesh(n)")
exec(s)
