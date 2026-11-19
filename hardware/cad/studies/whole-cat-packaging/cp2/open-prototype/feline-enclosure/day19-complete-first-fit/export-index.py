from common import *
code=(E/'print-components.py').read_text()
pre=code[:code.index('ret=[')].replace("D=P.parent/'day19-whole-appearance-and-moving-neck-correction'","D=P.parent/'day19-shared-open-trunk-and-body-parting'").replace("P/'whole-cat19E.FCStd'; src=D/'whole-cat19D.FCStd'","P/'whole-cat19I.FCStd'; src=D/'whole-cat19H.FCStd'")
exec(pre)
changed=['H19_FrontFrame','E19_RearBase','E19_ForeLid','E19_RearLid','E19_UpperYawCover'];ret=changed
exec(code[code.index('rows=[];steps=[]'):code.index("new=['E19_KeyedTail")])
for n in changed:
 prev=next(q for q in base['parts'] if q['part']==n)
 rows.append(dict(part=n,qty=1,hardware_use=prev['hardware_use']))
# Each installed instance has its own placement and solid in the assembly.
bands=sorted(n for n in S.members if n.startswith('I19_FuseBand_'))
if bands:
 rows.append(dict(part=bands[0],qty=len(bands),installed_instances=bands,hardware_use='one snap-over transverse keeper per listed fuse station; two hooks under the bearing rung; remove before rare fuse case service'))
coupon=dict(base['off_robot']);p=(D/coupon['stl']).resolve();assert h(p)==coupon['sha256'];coupon['stl']=rel(p)
for q in base['steps']:
 if q['part'] not in changed:
    p=(D/q['step']).resolve();assert h(p)==q['sha256'];steps.append(dict(q,step=rel(p)))
tail=code[code.index("folder=P/'components'"):].replace('source_19D_sha256','source_19H_sha256').replace(']+[coupon]:',']:').replace("if n in ['E19_ForeBase','E19_RearBase','E19_KeyedTail']:","if n in ['H19_FrontFrame','E19_RearBase']:")
exec(tail.replace("mat=trimesh.geometry.align_vectors", "if n.startswith('I19_FuseBand_'):normal=m.facets_normal[np.argmax(m.facets_area)]\n    mat=trimesh.geometry.align_vectors"))
idx=rd(P/'material-index.json');idx['replaces_prior_geometry']=idx.pop('retired');idx['retired_prints']=['E19_ForeBase','E19_FrontShroud'];wr('material-index.json',idx)
if not next(q for q in rows if q['part']=='H19_FrontFrame')['stl']:exec((H19/'frame-export.py').read_text())
