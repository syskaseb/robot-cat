from common import *
# Recompute only the affected lower-bay volume. Freeze the upper H routing field outside this slab.
s=(H19/'space-map.py').read_text();s=s.replace('whole-cat19H.FCStd','whole-cat19I.FCStd').replace('origin=np.array([-120,-106,38]);step=2.;N=np.array([167,107,94])','origin=np.array([-120,-106,38]);step=2.;N=np.array([145,107,67])')
exec(s)
