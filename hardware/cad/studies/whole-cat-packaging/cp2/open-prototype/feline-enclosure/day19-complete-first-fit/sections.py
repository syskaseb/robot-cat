from common import *
s=(H19/'sections.py').read_text().replace("whole-cat19H.FCStd","whole-cat19I.FCStd").replace("[-92,15,92,176]","[-78,-7,27,61]").replace("'H19_Wires_'","'H19_Wires_','I19_FiveGround','I19_HPInput'").replace("groups[1][1].extend(","groups[0][1].extend([n for n in D.members if n.startswith('I19_FuseBand_')]); groups[1][1].extend(")
exec(s)
