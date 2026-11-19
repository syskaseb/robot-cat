from common import *
s=(P/'front-port-check.py').read_text().replace('front-service-lay.json','fl-hand-space.json').replace('front-port-check.json','fl-hand-check.json')
exec(s)
