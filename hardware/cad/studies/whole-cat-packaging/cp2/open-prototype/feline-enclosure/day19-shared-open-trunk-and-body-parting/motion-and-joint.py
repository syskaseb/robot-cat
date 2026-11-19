from common import *
s=(F/'interfaces.py').read_text().replace('whole-cat19F.FCStd','whole-cat19H.FCStd').replace("P/'service-lay.json'","F/'service-lay.json'").replace("P/'occupied-check.json'","P/'stock-and-joint.json'")
a=s.index('parts=dict');b=s.index('def write():',a);s=s[:a]+"""parts={'fixed':['H19_FrontFrame','E19_RearBase','E19_ForeLid','E19_RearLid','XT60H_mated_with_boots','WAGO415_data__1_0','H19_DATA_A_Boot','E19_ReSpeakerSource'],'yaw':[],'pitch':[]}
"""+s[b:];s=s.replace("q.get('branches',[])","([] if name=='JR_pitch' else q.get('branches',[]))")
a=s.index("parts['fixed']=",s.index("old=json.loads"));b=s.index("for q in old['motion']",a);s=s[:a]+s[b:];s=s[:s.index('for y in [-20',s.index("for q in old['motion']"))] if 'for y in [-20' in s[s.index("for q in old['motion']"):] else s
s=s.split('# Resolve')[0];exec(s);write()
s=(E/'final-motion.py').read_text().replace('whole-cat19E.FCStd','whole-cat19H.FCStd').replace("'S0_body','B19_TailMatedPair'","'F19_RearCap','B19_TailMatedPair'").replace("'E19_ForeBase','E19_FrontShroud','E19_ForeLid'","'H19_FrontFrame','E19_ForeLid','F19_ForeCap'").replace('cache={n:mesh(n)',"pairs.append(('BR_FLANK_HP_PAIR',['H19_FrontFrame','E19_ForeLid','F19_ForeCap'],[-130,0,127],[-20,0,20]))\ncache={n:mesh(n)")
exec(s)
