from pathlib import Path
P=Path(__file__).parent;F=P.parent/'day19-connected-servo-usb-and-closure'
s=(F/'sections.py').read_text(encoding='utf8')
s=s.replace("exec(s.replace(", """s=s.replace("fig,axes=plt.subplots", "hardware.remove('E1_populated_prototype_board');hardware.extend(['G19_PermaProto1608']);groups[3][1].extend([n for n in D.members if n.startswith(('G19_Lay_','G19_PitchFan','G19_H3_mate','G19_MIC_C_PlugAllow'))]);fig,axes=plt.subplots")
exec(s.replace(""").replace('whole-cat19F.FCStd','whole-cat19G.FCStd').replace('[-101,-25,65,162]','[-78,2,162,197]')
exec(s)
