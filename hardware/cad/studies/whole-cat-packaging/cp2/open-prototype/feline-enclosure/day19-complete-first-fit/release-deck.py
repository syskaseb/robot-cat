from pathlib import Path
P=Path(__file__).parent;E=P.parent/'day19-simple-box-common-core'
exec((E/'core.py').read_text().split('# Each board/power cluster')[0].replace('19E.FCStd','19I.FCStd'))
# Extend the service opening in +X only. The two cup return bridges flank the two jackets.
n='E19_RearLid';s=sh(n);relief=box(28.8,-35.3,170.72,37.2,10.6,3.38)
s=s.cut(relief).removeSplitter()
assert s.isValid() and len(s.Solids)==1
D.getObject(n).Shape=s;D.recompute();D.save()
wr('deck-service-parting.json',dict(native_volume=s.Volume,bounds=bounds(s),minimum_flank_y=[-35.5,-23.9],mouth=bounds(relief),service_order='head at neutral, off, two top caps off, then release both insulated XT60 bodies'))
