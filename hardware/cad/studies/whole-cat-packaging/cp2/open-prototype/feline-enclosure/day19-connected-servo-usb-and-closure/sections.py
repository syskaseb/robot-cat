"""Named sections of the installed movable half, full pairs, upper deck and media boards."""
from pathlib import Path
P=Path(__file__).parent;E=P.parent/'day19-simple-box-common-core'
s=(E/'core-sections.py').read_text(encoding='utf8').replace('whole-cat19E.FCStd','whole-cat19F.FCStd')
i=s.index('fig,axes')
s=s[:i]+"""hardware.extend(['BR_FLANK_HP_PAIR','B19_TailMatedPair','TTP223_touch'])
groups[1][1].extend(['F19_ForeCap','F19_RearCap'])
groups[3][1][:]=[n for n in groups[3][1] if not n.startswith(('E19_FieldMG','E19_FieldJR','E19_FieldDATA','B19_Tail'))]+[n for n in D.members if n.startswith('F19_Field_')]
"""+s[i:]
exec(s.replace('[-110,-60,48,140]','[-101,-25,65,162]').replace('(-110,113)','(-122,117)'))
