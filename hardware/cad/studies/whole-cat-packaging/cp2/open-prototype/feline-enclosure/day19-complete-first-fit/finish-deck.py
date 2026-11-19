from pathlib import Path
P=Path(__file__).parent;E=P.parent/'day19-simple-box-common-core'
exec((E/'core.py').read_text().split('# Each board/power cluster')[0].replace('19E.FCStd','19I.FCStd'))
s=sh('E19_RearLid').Solids[0];tray=Part.Shape();tray.read(str(P/'tail-tray.tmp.brep'))
end=box(207.18,-47.8,175.5,1.8,18.8,3.18);tool=tray.common(end)
t=s.cut(tool,.000001).removeSplitter()
assert t.isValid() and len(t.Solids)==1
wr('rear-cap-bearing.json',dict(earlier_overlap=10.9243,removed_from_tray=tool.Volume,remaining_tray=tray.Volume-tool.Volume,post_common_mm3=t.common(sh('F19_RearCap')).Volume,host_volume=t.Volume))
D.E19_RearLid.Shape=t;tray.cut(tool).exportBrep(str(P/'tail-final.tmp.brep'))
# Previous stage already drew the installed grounds and pack. Render the final saved geometry without generating new components.
s=(P/'views-and-runs.py').read_text();exec(s[s.index('skins='):])
