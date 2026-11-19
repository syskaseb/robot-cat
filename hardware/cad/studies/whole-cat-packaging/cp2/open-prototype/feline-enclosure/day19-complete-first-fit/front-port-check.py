from common import *
s=(P/'branch-fit.py').read_text().replace("rd(P/'changed-branch-lays.json')","dict(rows=rd(P/'front-service-lay.json'))").replace("wr('changed-branch-fit.json'","wr('front-port-check.json'")
exec(s)
