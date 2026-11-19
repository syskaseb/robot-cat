from common import *
s=(E/'core-sections.py').read_text(encoding='utf8').replace('whole-cat19E.FCStd','whole-cat19H.FCStd').replace("'E19_ForeBase'","'H19_FrontFrame'").replace("'E19_FrontShroud',","").replace("'E1_populated_prototype_board'","'G19_PermaProto1608'")
s=s.replace("fig,axes=plt.subplots", """groups[1][1].extend(['F19_ForeCap','F19_RearCap'])
groups[3][1]=[] if False else groups[3][1]
fig,axes=plt.subplots""".replace("groups[3][1]=[] if False else groups[3][1]","groups[3][1][:]=[n for n in D.members if n.startswith(('F19_Field_','H19_Wires_'))]+['C19_FFC190','D19D_ToF']"))
exec(s.replace('[-110,-60,48,140]','[-92,15,92,176]').replace('(-110,113)','(-122,117)'))
