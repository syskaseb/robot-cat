from pathlib import Path
P=Path(__file__).parent;F=P.parent/'day19-connected-servo-usb-and-closure'
s=(F/'interfaces.py').read_text();s=s[:s.index("old=json.loads((D19")]
s=s.replace('whole-cat19F.FCStd','whole-cat19G.FCStd').replace("P/'service-lay.json'","F/'service-lay.json'").replace("P/'occupied-check.json'","P/'retained-runs.json'")
s=s[:s.index('parts=dict')]+"""parts=dict(fixed=['E19_RearBase','E19_ForeLid','E19_RearLid','F19_ForeCap','F19_RearCap','E19_FrontShroud','E19_ReSpeakerSource','G19_PermaProto1608','G19_H3_mate_allowance','G19_MIC_C_PlugAllow','G19_PiAudioBoot'],yaw=['E19_UpperYawCover','G19_RemoteR_pitch'],pitch=[])
"""+s[s.index('def write'):];s=s.replace("q.get('branches',[])","([] if name=='JR_pitch' else q.get('branches',[]))")
exec(s)
